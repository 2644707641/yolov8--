from __future__ import annotations

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import anyio
import cv2

from app.core.config import settings
from app.core.pytorch_patch import ensure_torch_patch

ensure_torch_patch()

from ultralytics import YOLO  # noqa: E402

DetectionResult = Tuple[Path, List[dict], float]

_DETECTION_SEMAPHORE = asyncio.Semaphore(settings.max_concurrent_detections)


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


def _process_detection_sync(
    user_id: str,
    model_path: Path,
    file_path: Path,
    file_type: str,
    params: Dict,
    result_dir: Path,
    logger,
) -> DetectionResult:
    model = YOLO(str(model_path))
    logger.info("模型加载成功: %s", model_path)

    detection_params = _normalize_params(params)
    start_time = time.time()

    if file_type == "image":
        result_path, detections = _detect_image(
            model=model,
            user_id=user_id,
            file_path=file_path,
            result_dir=result_dir,
            detection_params=detection_params,
            logger=logger,
        )
    else:
        result_path, detections = _detect_video(
            model=model,
            user_id=user_id,
            file_path=file_path,
            result_dir=result_dir,
            detection_params=detection_params,
            logger=logger,
        )

    elapsed = time.time() - start_time
    logger.info("检测完成: user=%s 用时=%.2fs", user_id, elapsed)
    return result_path, detections, elapsed


def _normalize_params(raw: Dict) -> Dict:
    return {
        "imgsz": int(raw.get("imgSize", 640)),
        "confidence": float(raw.get("confidence", 0.25)),
        "iou": float(raw.get("iouThreshold", 0.45)),
        "max_det": int(raw.get("maxDetections", 300)),
        "frame_skip": max(1, int(raw.get("frameSkip", 1))),
    }


def _detect_image(
    *,
    model: YOLO,
    user_id: str,
    file_path: Path,
    result_dir: Path,
    detection_params: Dict,
    logger,
) -> Tuple[Path, List[dict]]:
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

    return result_path, detections


def _detect_video(
    *,
    model: YOLO,
    user_id: str,
    file_path: Path,
    result_dir: Path,
    detection_params: Dict,
    logger,
) -> Tuple[Path, List[dict]]:
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

    logger.info("视频处理开始，编码器=%s，帧间隔=%s", codec, frame_skip)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
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
            for box in results[0].boxes:
                detections.append(
                    {
                        "class": results[0].names[int(box.cls[0])],
                        "confidence": float(box.conf[0]),
                        "bbox": box.xyxy[0].tolist(),
                        "frame": frame_count,
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

    return result_path, detections


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

