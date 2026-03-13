from __future__ import annotations

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import anyio
import cv2
import numpy as np

from app.core.config import settings
from app.core.pytorch_patch import ensure_torch_patch

ensure_torch_patch()

from ultralytics import YOLO  # noqa: E402

from app.services import system_monitor

DetectionResult = Tuple[Path, List[dict], float, str]
LiveFrameResult = Tuple[bytes, List[dict], float]
LiveFrameInferenceResult = Tuple[np.ndarray, List[dict], float]

_DETECTION_SEMAPHORE = asyncio.Semaphore(settings.max_concurrent_detections)


def _sort_counts_desc(counts: Dict[str, int]) -> Dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def build_result_metrics(detections: List[dict], file_type: str) -> Dict[str, Any]:
    """
    构建结果统计：
    - totalDetections: 累计检测框数量（逐帧累加）
    - uniqueTargetCount: 去重后目标数（优先 tracking id，否则回退单帧峰值）
    - classCounts: 累计分类计数
    - uniqueClassCounts: 去重分类计数（tracking）或单帧峰值分类计数（回退）
    - countMode: tracking_unique | frame_peak | single_frame
    """
    if not detections:
        return {
            "totalDetections": 0,
            "uniqueTargetCount": 0,
            "classCounts": {},
            "uniqueClassCounts": {},
            "maxTargetsPerFrame": 0,
            "countMode": "single_frame" if file_type != "video" else "frame_peak",
        }

    cumulative_class_counts: Dict[str, int] = {}
    frame_counts: Dict[int, int] = {}
    frame_class_counts: Dict[int, Dict[str, int]] = {}
    track_ids_by_class: Dict[str, set[str]] = {}

    for det in detections:
        class_name = det.get("class", "未知")
        cumulative_class_counts[class_name] = cumulative_class_counts.get(class_name, 0) + 1

        frame_idx = det.get("frame")
        if isinstance(frame_idx, int):
            frame_counts[frame_idx] = frame_counts.get(frame_idx, 0) + 1
            per_frame = frame_class_counts.setdefault(frame_idx, {})
            per_frame[class_name] = per_frame.get(class_name, 0) + 1

        track_id = det.get("track_id")
        if track_id is not None:
            track_ids_by_class.setdefault(class_name, set()).add(str(track_id))

    total_detections = len(detections)
    max_targets_per_frame = max(frame_counts.values()) if frame_counts else total_detections

    if track_ids_by_class:
        unique_class_counts = {
            class_name: len(track_ids)
            for class_name, track_ids in track_ids_by_class.items()
        }
        unique_target_count = sum(unique_class_counts.values())
        count_mode = "tracking_unique"
    elif file_type == "video":
        peak_class_counts: Dict[str, int] = {}
        for per_frame_counts in frame_class_counts.values():
            for class_name, count in per_frame_counts.items():
                previous = peak_class_counts.get(class_name, 0)
                if count > previous:
                    peak_class_counts[class_name] = count

        unique_class_counts = peak_class_counts or dict(cumulative_class_counts)
        unique_target_count = max_targets_per_frame
        count_mode = "frame_peak"
    else:
        unique_class_counts = dict(cumulative_class_counts)
        unique_target_count = total_detections
        count_mode = "single_frame"

    return {
        "totalDetections": total_detections,
        "uniqueTargetCount": unique_target_count,
        "classCounts": _sort_counts_desc(cumulative_class_counts),
        "uniqueClassCounts": _sort_counts_desc(unique_class_counts),
        "maxTargetsPerFrame": max_targets_per_frame,
        "countMode": count_mode,
    }


def _extract_track_ids(result) -> List[int | None]:
    boxes = result.boxes
    if boxes.id is None:
        return [None for _ in range(len(boxes))]
    return [int(track_id) for track_id in boxes.id.int().cpu().tolist()]


def _generate_description(detections: List[dict], file_type: str) -> str:
    """生成检测结果的文字描述"""
    if not detections:
        return "未检测到任何目标"

    metrics = build_result_metrics(detections, file_type)
    # 视频优先展示去重（或峰值）分类计数；图片展示累计分类计数。
    class_counts = (
        metrics["uniqueClassCounts"] if file_type == "video" else metrics["classCounts"]
    )
    total_confidence = 0.0

    for det in detections:
        total_confidence += det.get("confidence", 0.0)

    avg_confidence = total_confidence / max(1, len(detections))
    description_parts = []

    if file_type == "video":
        if metrics["countMode"] == "tracking_unique":
            description_parts.append(
                f"视频累计检测到 {metrics['totalDetections']} 个目标框，估计独立目标 {metrics['uniqueTargetCount']} 个"
            )
        else:
            description_parts.append(
                f"视频累计检测到 {metrics['totalDetections']} 个目标框，单帧峰值目标 {metrics['uniqueTargetCount']} 个"
            )
    else:
        description_parts.append(f"共检测到 {metrics['totalDetections']} 个目标")

    if class_counts:
        class_details = []
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            class_details.append(f"{count} 个{class_name}")
        description_parts.append("，其中包括 " + "、".join(class_details))

    description_parts.append(f"，平均置信度为 {avg_confidence:.2%}")

    if file_type == "video":
        if metrics["countMode"] == "tracking_unique":
            description_parts.append("（按目标跟踪去重）")
        else:
            description_parts.append("（按单帧峰值统计）")

    return "".join(description_parts) + "。"


async def run_detection(
    *,
    user_id: str,
    model_path: Path,
    file_path: Path,
    file_type: str,
    params: Dict,
    result_dir: Path,
    logger,
) -> DetectionResult:
    system_monitor.increment_active_tasks()
    try:
        async with _DETECTION_SEMAPHORE:
            logger.info(
                "开始检测: user=%s type=%s file=%s params=%s",
                user_id,
                file_type,
                file_path.name,
                params,
            )
            return await anyio.to_thread.run_sync(
                _process_detection_sync,
                user_id,
                model_path,
                file_path,
                file_type,
                params,
                result_dir,
                logger,
            )
    finally:
        system_monitor.decrement_active_tasks()


def _process_detection_sync(
    user_id: str,
    model_path: Path,
    file_path: Path,
    file_type: str,
    params: Dict,
    result_dir: Path,
    logger,
) -> DetectionResult:
    model = load_model_sync(model_path)
    logger.info("模型加载成功: %s", model_path)

    detection_params = _normalize_params(params)
    start_time = time.time()

    if file_type == "image":
        result_path, detections, description = _detect_image(
            model=model,
            user_id=user_id,
            file_path=file_path,
            result_dir=result_dir,
            detection_params=detection_params,
            logger=logger,
        )
    else:
        result_path, detections, description = _detect_video(
            model=model,
            user_id=user_id,
            file_path=file_path,
            result_dir=result_dir,
            detection_params=detection_params,
            logger=logger,
        )

    elapsed = time.time() - start_time
    logger.info("检测完成: user=%s 用时=%.2fs", user_id, elapsed)
    return result_path, detections, elapsed, description


def _normalize_params(raw: Dict) -> Dict:
    return {
        "imgsz": int(raw.get("imgSize", 640)),
        "confidence": float(raw.get("confidence", 0.25)),
        "iou": float(raw.get("iouThreshold", 0.45)),
        "max_det": int(raw.get("maxDetections", 300)),
        "frame_skip": max(1, int(raw.get("frameSkip", 1))),
    }


def load_model_sync(model_path: Path) -> YOLO:
    """同步加载 YOLO 模型，供批量检测与实时检测复用。"""
    return YOLO(str(model_path))


def create_video_writer_sync(
    *,
    result_path: Path,
    fps: float,
    width: int,
    height: int,
    logger,
):
    """
    创建视频写入器，返回 (writer, codec_name)。
    """
    return _create_video_writer(result_path, fps, width, height, logger)


def optimize_video_file_sync(result_path: Path, logger) -> None:
    """对已生成视频执行可选的 ffmpeg 优化。"""
    _optimize_video_with_ffmpeg(result_path, logger)


def normalize_params(raw: Dict) -> Dict:
    """对外暴露检测参数标准化，供 API 层实时接口复用。"""
    return _normalize_params(raw)


def infer_live_frame_sync(
    *,
    model: YOLO,
    frame_bytes: bytes,
    detection_params: Dict,
) -> LiveFrameInferenceResult:
    """
    对单帧 JPEG 数据进行实时推理，返回标注帧矩阵、检测结果与耗时。
    """
    frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("无法解码视频帧，请确认输入为有效 JPEG")

    start_time = time.time()
    use_tracking = getattr(model, "_codex_tracking_enabled", True)
    if use_tracking:
        try:
            results = model.track(
                source=frame,
                imgsz=detection_params["imgsz"],
                conf=detection_params["confidence"],
                iou=detection_params["iou"],
                max_det=detection_params["max_det"],
                save=False,
                verbose=False,
                persist=True,
                tracker="bytetrack.yaml",
            )
        except Exception:
            # 跟踪不可用时自动回退，不影响主流程。
            setattr(model, "_codex_tracking_enabled", False)
            results = model.predict(
                source=frame,
                imgsz=detection_params["imgsz"],
                conf=detection_params["confidence"],
                iou=detection_params["iou"],
                max_det=detection_params["max_det"],
                save=False,
                verbose=False,
            )
    else:
        results = model.predict(
            source=frame,
            imgsz=detection_params["imgsz"],
            conf=detection_params["confidence"],
            iou=detection_params["iou"],
            max_det=detection_params["max_det"],
            save=False,
            verbose=False,
        )
    elapsed = time.time() - start_time

    annotated = results[0].plot()
    detections: List[dict] = []
    track_ids = _extract_track_ids(results[0])
    for idx, box in enumerate(results[0].boxes):
        detections.append(
            {
                "class": results[0].names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "bbox": box.xyxy[0].tolist(),
                "track_id": track_ids[idx],
            }
        )

    return annotated, detections, elapsed


def encode_frame_to_jpeg_sync(frame: np.ndarray, quality: int = 80) -> bytes:
    """将 OpenCV 帧编码为 JPEG 字节。"""
    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise RuntimeError("实时检测结果编码失败")
    return encoded.tobytes()


def detect_live_frame_sync(
    *,
    model: YOLO,
    frame_bytes: bytes,
    detection_params: Dict,
) -> LiveFrameResult:
    """
    对单帧 JPEG 数据进行实时推理。
    返回：(标注后 JPEG 字节, 当前帧检测结果, 当前帧推理耗时秒)。
    """
    annotated, detections, elapsed = infer_live_frame_sync(
        model=model,
        frame_bytes=frame_bytes,
        detection_params=detection_params,
    )
    return encode_frame_to_jpeg_sync(annotated), detections, elapsed


def _detect_image(
    *,
    model: YOLO,
    user_id: str,
    file_path: Path,
    result_dir: Path,
    detection_params: Dict,
    logger,
) -> Tuple[Path, List[dict], str]:
    results = model.predict(
        source=str(file_path),
        imgsz=detection_params["imgsz"],
        conf=detection_params["confidence"],
        iou=detection_params["iou"],
        max_det=detection_params["max_det"],
        save=False,
        verbose=False,
    )

    boxes = results[0].boxes
    logger.info("图片检测到 %d 个目标", len(boxes))

    annotated = results[0].plot()
    result_filename = f"result_{user_id}_{int(time.time())}.jpg"
    result_path = result_dir / result_filename
    cv2.imwrite(str(result_path), annotated)

    detections: List[dict] = []
    for box in boxes:
        detections.append(
            {
                "class": results[0].names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "bbox": box.xyxy[0].tolist(),
            }
        )

    description = _generate_description(detections, "image")
    return result_path, detections, description


def _detect_video(
    *,
    model: YOLO,
    user_id: str,
    file_path: Path,
    result_dir: Path,
    detection_params: Dict,
    logger,
) -> Tuple[Path, List[dict], str]:
    cap = cv2.VideoCapture(str(file_path))
    if not cap.isOpened():
        raise RuntimeError("无法读取视频文件")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps == 0 or width == 0 or height == 0:
        cap.release()
        raise RuntimeError("视频信息无效，可能损坏或格式不支持")

    result_filename = f"result_{user_id}_{int(time.time())}.mp4"
    result_path = result_dir / result_filename

    out, codec = _create_video_writer(result_path, fps, width, height, logger)
    if out is None:
        cap.release()
        raise RuntimeError("无法创建视频输出文件，请检查编码器配置")

    frame_skip = detection_params["frame_skip"]
    frame_count = 0
    detections: List[dict] = []
    tracking_enabled = True

    logger.info("视频处理开始，编码器=%s，帧间隔=%s", codec, frame_skip)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
            if tracking_enabled:
                try:
                    results = model.track(
                        source=frame,
                        imgsz=detection_params["imgsz"],
                        conf=detection_params["confidence"],
                        iou=detection_params["iou"],
                        max_det=detection_params["max_det"],
                        save=False,
                        verbose=False,
                        persist=True,
                        tracker="bytetrack.yaml",
                    )
                except Exception as exc:
                    tracking_enabled = False
                    logger.warning("视频跟踪不可用，回退逐帧检测: %s", exc)
                    results = model.predict(
                        source=frame,
                        imgsz=detection_params["imgsz"],
                        conf=detection_params["confidence"],
                        iou=detection_params["iou"],
                        max_det=detection_params["max_det"],
                        save=False,
                        verbose=False,
                    )
            else:
                results = model.predict(
                    source=frame,
                    imgsz=detection_params["imgsz"],
                    conf=detection_params["confidence"],
                    iou=detection_params["iou"],
                    max_det=detection_params["max_det"],
                    save=False,
                    verbose=False,
                )
            annotated_frame = results[0].plot()
            track_ids = _extract_track_ids(results[0])
            for idx, box in enumerate(results[0].boxes):
                detections.append(
                    {
                        "class": results[0].names[int(box.cls[0])],
                        "confidence": float(box.conf[0]),
                        "bbox": box.xyxy[0].tolist(),
                        "frame": frame_count,
                        "track_id": track_ids[idx],
                    }
                )
        else:
            annotated_frame = frame

        out.write(annotated_frame)
        frame_count += 1

    cap.release()
    out.release()

    if not result_path.exists() or result_path.stat().st_size == 0:
        raise RuntimeError("生成的视频文件无效")

    _optimize_video_with_ffmpeg(result_path, logger)

    description = _generate_description(detections, "video")
    return result_path, detections, description


def _create_video_writer(result_path, fps, width, height, logger):
    options = [
        ("avc1", "H264"),
        ("H264", "H264"),
        ("XVID", "XVID"),
        ("MJPG", "MJPEG"),
        ("mp4v", "MPEG-4"),
    ]

    for codec_code, codec_name in options:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec_code)
            writer = cv2.VideoWriter(str(result_path), fourcc, fps, (width, height))
            if writer.isOpened():
                return writer, codec_name
        except Exception as exc:
            logger.warning("编码器 %s 初始化失败: %s", codec_name, exc)

    return None, None


def _optimize_video_with_ffmpeg(result_path: Path, logger) -> None:
    temp_path = result_path.with_suffix(".temp.mp4")
    cmd = [
        "ffmpeg",
        "-i",
        str(result_path),
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-y",
        str(temp_path),
    ]

    try:
        completed = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        if completed.returncode == 0 and temp_path.exists():
            result_path.unlink()
            temp_path.rename(result_path)
            logger.info("FFmpeg 优化完成")
        elif temp_path.exists():
            temp_path.unlink()
            logger.warning("FFmpeg 优化失败，保留原始视频")
    except FileNotFoundError:
        logger.info("未检测到 FFmpeg，跳过视频优化")
    except subprocess.TimeoutExpired:
        logger.warning("FFmpeg 优化超时")
    except Exception as exc:
        logger.warning("FFmpeg 优化出错: %s", exc)
        if temp_path.exists():
            temp_path.unlink()
