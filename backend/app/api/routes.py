from __future__ import annotations

import json
import logging
import time
from typing import Optional

import anyio
from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import FileResponse

from app.core.config import settings
from app.services import auth as auth_service
from app.services import detection as detection_service
from app.services import model_registry
from app.services import model_weights as model_weights_service
from app.services import storage as storage_service
from app.services import validators

logger = logging.getLogger("yolov8.api")

router = APIRouter()


def get_supabase_client(request: Request):
    return getattr(request.app.state, "supabase", None)


def get_supabase_client_from_websocket(websocket: WebSocket):
    return getattr(websocket.app.state, "supabase", None)


async def resolve_model_path(user_id: str, supabase_client):
    """
    解析用户当前可用权重路径。
    优先级：用户激活权重 > 本地注册权重 > 默认权重。
    """
    model_path = None
    if supabase_client:
        active_weight = model_weights_service.get_active_weight(
            supabase_client,
            user_id=user_id,
            logger=logger,
        )

        if active_weight:
            cache_filename = active_weight["file_path"].split("/")[-1]
            cache_path = settings.model_cache_dir / user_id / cache_filename

            if not cache_path.exists():
                logger.info("权重未缓存，开始下载: %s", active_weight["file_path"])
                success = model_weights_service.download_weight_from_supabase(
                    supabase_client,
                    active_weight["file_path"],
                    cache_path,
                    bucket=settings.model_weights_bucket,
                    logger=logger,
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="权重下载失败",
                    )
            else:
                logger.info("使用缓存权重: %s", cache_path)

            model_path = cache_path

    if not model_path:
        model_path = await model_registry.registry.get_model(user_id)

    if not model_path and supabase_client:
        logger.info("用户没有自定义权重，尝试使用默认权重")
        model_path = model_weights_service.get_default_weight(
            supabase_client,
            default_path=settings.default_model_path,
            cache_dir=settings.model_cache_dir,
            bucket=settings.model_weights_bucket,
            logger=logger,
        )
        if model_path:
            logger.info("使用默认权重: %s", settings.default_model_name)

    return model_path


@router.get("/")
async def root():
    return {
        "message": settings.api_title,
        "version": "1.1.0",
        "endpoints": {
            "upload_model": "/api/upload-model",
            "detect": "/api/detect",
            "detect_live_ws": "/ws/detect-live",
        },
    }


@router.post("/api/upload-model")
async def upload_model(
    request: Request,
    model: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    validators.validate_extension(
        model.filename,
        settings.allowed_model_extensions,
        "仅支持上传 .pt 或 .pth 模型文件",
    )

    # 保存到临时位置
    temp_model_path = settings.model_dir / f"temp_{user_id}_{model.filename}"

    try:
        validators.save_upload_file(
            model, temp_model_path, max_size=settings.max_upload_size_bytes
        )

        file_size = temp_model_path.stat().st_size

        # 如果有 Supabase 客户端，上传到云端
        if supabase_client:
            # 上传到 Supabase Storage
            storage_path = model_weights_service.upload_weight_to_supabase(
                supabase_client,
                temp_model_path,
                user_id=user_id,
                bucket=settings.model_weights_bucket,
                logger=logger,
            )

            if storage_path:
                # 创建数据库记录
                weight_name = name if name else model.filename
                weight_record = model_weights_service.create_weight_record(
                    supabase_client,
                    user_id=user_id,
                    name=weight_name,
                    file_path=storage_path,
                    file_size=file_size,
                    description=description,
                    logger=logger,
                )

                if weight_record:
                    logger.info(
                        "用户 %s 上传模型到 Supabase 成功: %s (权重ID: %s)",
                        user_id,
                        storage_path,
                        weight_record.get("id"),
                    )

                    return {
                        "success": True,
                        "message": "模型上传并保存成功",
                        "weight": {
                            "id": weight_record.get("id"),
                            "name": weight_record.get("name"),
                            "file_path": weight_record.get("file_path"),
                            "file_size": weight_record.get("file_size"),
                            "is_active": weight_record.get("is_active"),
                            "created_at": weight_record.get("created_at"),
                        },
                    }

        # 降级到本地存储（无 Supabase 或上传失败）
        model_path = settings.model_dir / f"{user_id}_{model.filename}"
        temp_model_path.rename(model_path)

        previous_model = await model_registry.registry.remove_model(user_id)
        if previous_model:
            storage_service.remove_file(previous_model, logger)

        await model_registry.registry.set_model(user_id, model_path)

        logger.info("用户 %s 上传模型到本地: %s", user_id, model_path)

        return {
            "success": True,
            "message": "模型上传成功（本地存储）",
            "model_path": str(model_path),
            "user_id": user_id,
        }
    finally:
        # 清理临时文件
        if temp_model_path.exists():
            storage_service.remove_file(temp_model_path, logger)


@router.post("/api/detect")
async def detect(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    type: str = Form(...),
    params: str = Form(...),
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    try:
        detection_params = json.loads(params)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"检测参数格式错误: {exc}",
        ) from exc

    type = type.lower()
    if type not in {"image", "video"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="type 仅支持 image 或 video",
        )

    allowed_extensions = (
        settings.allowed_image_extensions
        if type == "image"
        else settings.allowed_video_extensions
    )
    validators.validate_extension(
        file.filename,
        allowed_extensions,
        f"{type} 文件类型不受支持",
    )

    input_path = settings.upload_dir / f"{user_id}_{file.filename}"

    try:
        validators.save_upload_file(
            file, input_path, max_size=settings.max_upload_size_bytes
        )

        model_path = await resolve_model_path(user_id, supabase_client)

        if not model_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="请先上传模型文件或确保默认权重已配置"
            )

        result_path, detections, elapsed, description = await detection_service.run_detection(
            user_id=user_id,
            model_path=model_path,
            file_path=input_path,
            file_type=type,
            params=detection_params,
            result_dir=settings.result_dir,
            logger=logger,
        )

        original_url = None
        result_url_supabase = None

        if supabase_client:
            try:
                original_url = storage_service.upload_file_to_supabase(
                    supabase_client,
                    input_path,
                    user_id=user_id,
                    file_type=type,
                    bucket=settings.supabase_bucket,
                    logger=logger,
                    is_result=False,
                )
                result_url_supabase = storage_service.upload_file_to_supabase(
                    supabase_client,
                    result_path,
                    user_id=user_id,
                    file_type=type,
                    bucket=settings.supabase_bucket,
                    logger=logger,
                    is_result=True,
                )
                if original_url and result_url_supabase:
                    background_tasks.add_task(
                        storage_service.save_detection_record,
                        supabase_client,
                        user_id=user_id,
                        file_type=type,
                        original_url=original_url,
                        result_url=result_url_supabase,
                        detections=detections,
                        params=detection_params,
                        logger=logger,
                    )
            except Exception as exc:
                logger.warning("保存到 Supabase 失败: %s", exc)

        metrics = detection_service.build_result_metrics(detections, type)
        response_payload = {
            "success": True,
            "resultUrl": f"/api/results/{result_path.name}",
            "originalUrlSupabase": original_url,
            "resultUrlSupabase": result_url_supabase,
            "detections": detections,
            "totalDetections": metrics["totalDetections"],
            "uniqueTargetCount": metrics["uniqueTargetCount"],
            "classCounts": metrics["classCounts"],
            "uniqueClassCounts": metrics["uniqueClassCounts"],
            "countMode": metrics["countMode"],
            "maxTargetsPerFrame": metrics["maxTargetsPerFrame"],
            "description": description,
            "processTime": elapsed,
            "params": detection_params,
        }
        return response_payload
    finally:
        storage_service.remove_file(input_path, logger)


@router.websocket("/ws/detect-live")
async def detect_live(websocket: WebSocket):
    await websocket.accept()

    supabase_client = get_supabase_client_from_websocket(websocket)
    token = websocket.query_params.get("token")

    try:
        user_id = await auth_service.validate_token(token, supabase_client)
    except HTTPException as exc:
        await websocket.send_json(
            {
                "type": "error",
                "detail": exc.detail,
            }
        )
        await websocket.close(code=4401)
        return

    model = None
    detection_params = None
    processed_frames = 0
    total_detections = 0
    frame_index = 0
    record_enabled = False
    record_fps = 8.0
    record_path = None
    record_writer = None
    peak_targets_per_frame = 0
    unique_track_ids_by_class: dict[str, set[str]] = {}
    peak_class_counts: dict[str, int] = {}
    class_counts_output: dict[str, int] = {}
    count_mode = "frame_peak"

    try:
        while True:
            message = await websocket.receive()
            message_type = message.get("type")
            if message_type == "websocket.disconnect":
                break

            text_payload = message.get("text")
            frame_bytes = message.get("bytes")

            if text_payload is not None:
                try:
                    payload = json.loads(text_payload)
                except json.JSONDecodeError:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "detail": "消息格式错误，仅支持 JSON 控制消息",
                        }
                    )
                    continue

                command = payload.get("type")
                if command == "start":
                    params = payload.get("params", {})
                    recording = payload.get("recording", {}) or {}
                    detection_params = detection_service.normalize_params(params)
                    model_path = await resolve_model_path(user_id, supabase_client)

                    if not model_path:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "detail": "请先上传模型文件或确保默认权重已配置",
                            }
                        )
                        await websocket.close(code=4400)
                        return

                    model = await anyio.to_thread.run_sync(
                        detection_service.load_model_sync, model_path
                    )
                    record_enabled = bool(recording.get("enabled", False))
                    record_fps = float(recording.get("fps", 8.0) or 8.0)
                    if record_fps <= 0:
                        record_fps = 8.0
                    record_path = None
                    if record_writer is not None:
                        record_writer.release()
                    record_writer = None

                    logger.info("实时检测模型加载成功: user=%s model=%s", user_id, model_path)
                    await websocket.send_json(
                        {
                            "type": "ready",
                            "message": "实时识别已启动",
                        }
                    )
                elif command == "end":
                    result_url = None
                    download_url = None
                    if record_writer is not None:
                        record_writer.release()
                        record_writer = None

                    if record_path and record_path.exists() and record_path.stat().st_size > 0:
                        detection_service.optimize_video_file_sync(record_path, logger)
                        result_url = f"/api/results/{record_path.name}"
                        download_url = f"/api/results/{record_path.name}?download=1"

                    if unique_track_ids_by_class:
                        class_counts_output = dict(
                            sorted(
                                (
                                    (class_name, len(track_ids))
                                    for class_name, track_ids in unique_track_ids_by_class.items()
                                ),
                                key=lambda item: item[1],
                                reverse=True,
                            )
                        )
                        unique_target_count = sum(class_counts_output.values())
                        count_mode = "tracking_unique"
                    else:
                        class_counts_output = dict(
                            sorted(
                                peak_class_counts.items(),
                                key=lambda item: item[1],
                                reverse=True,
                            )
                        )
                        unique_target_count = peak_targets_per_frame
                        count_mode = "frame_peak"

                    await websocket.send_json(
                        {
                            "type": "done",
                            "processedFrames": processed_frames,
                            "totalDetections": total_detections,
                            "uniqueTargetCount": unique_target_count,
                            "classCounts": class_counts_output,
                            "countMode": count_mode,
                            "maxTargetsPerFrame": peak_targets_per_frame,
                            "resultUrl": result_url,
                            "downloadUrl": download_url,
                            "description": (
                                f"实时识别完成，共处理 {processed_frames} 帧，"
                                f"{'估计独立目标' if count_mode == 'tracking_unique' else '单帧峰值目标'} "
                                f"{unique_target_count} 个，累计检测框 {total_detections} 个。"
                            ),
                        }
                    )
                    await websocket.close(code=1000)
                    return
                continue

            if frame_bytes is None:
                continue

            if model is None or detection_params is None:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "会话未初始化，请先发送 start 消息",
                    }
                )
                continue

            frame_index += 1
            try:
                annotated_frame, detections, elapsed = await anyio.to_thread.run_sync(
                    lambda: detection_service.infer_live_frame_sync(
                        model=model,
                        frame_bytes=frame_bytes,
                        detection_params=detection_params,
                    )
                )
                annotated_bytes = await anyio.to_thread.run_sync(
                    detection_service.encode_frame_to_jpeg_sync,
                    annotated_frame,
                    80,
                )
            except Exception as exc:
                logger.warning("实时检测帧处理失败: user=%s err=%s", user_id, exc)
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": f"帧处理失败: {exc}",
                    }
                )
                continue

            if record_enabled:
                if record_writer is None:
                    h, w = annotated_frame.shape[:2]
                    record_path = settings.result_dir / f"live_result_{user_id}_{int(time.time())}.mp4"
                    writer, codec = detection_service.create_video_writer_sync(
                        result_path=record_path,
                        fps=record_fps,
                        width=w,
                        height=h,
                        logger=logger,
                    )
                    if writer is None:
                        logger.warning("实时录制初始化失败，自动关闭录制: user=%s", user_id)
                        record_enabled = False
                    else:
                        logger.info(
                            "实时录制启动: user=%s fps=%.2f codec=%s file=%s",
                            user_id,
                            record_fps,
                            codec,
                            record_path.name,
                        )
                        record_writer = writer

                if record_writer is not None:
                    record_writer.write(annotated_frame)

            processed_frames += 1
            total_detections += len(detections)
            peak_targets_per_frame = max(peak_targets_per_frame, len(detections))

            current_frame_class_counts: dict[str, int] = {}
            for det in detections:
                class_name = det.get("class", "未知")
                current_frame_class_counts[class_name] = (
                    current_frame_class_counts.get(class_name, 0) + 1
                )

                track_id = det.get("track_id")
                if track_id is not None:
                    unique_track_ids_by_class.setdefault(class_name, set()).add(
                        str(track_id)
                    )

            for class_name, frame_count_value in current_frame_class_counts.items():
                previous = peak_class_counts.get(class_name, 0)
                if frame_count_value > previous:
                    peak_class_counts[class_name] = frame_count_value

            if unique_track_ids_by_class:
                class_counts_output = dict(
                    sorted(
                        (
                            (class_name, len(track_ids))
                            for class_name, track_ids in unique_track_ids_by_class.items()
                        ),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                )
                unique_target_count = sum(class_counts_output.values())
                count_mode = "tracking_unique"
            else:
                class_counts_output = dict(
                    sorted(
                        peak_class_counts.items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                )
                unique_target_count = peak_targets_per_frame
                count_mode = "frame_peak"

            frame_meta = {
                "type": "frame",
                "frameIndex": frame_index,
                "processedFrames": processed_frames,
                "detectionCount": len(detections),
                "inferTime": elapsed,
                "totalDetections": total_detections,
                "uniqueTargetCount": unique_target_count,
                "classCounts": class_counts_output,
                "countMode": count_mode,
                "maxTargetsPerFrame": peak_targets_per_frame,
            }
            meta_bytes = json.dumps(frame_meta, ensure_ascii=False).encode("utf-8")
            payload = len(meta_bytes).to_bytes(4, "big") + meta_bytes + annotated_bytes
            await websocket.send_bytes(payload)
    except WebSocketDisconnect:
        logger.info("实时检测连接断开: user=%s", user_id)
    except Exception as exc:
        logger.exception("实时检测异常: user=%s err=%s", user_id, exc)
        try:
            await websocket.send_json({"type": "error", "detail": str(exc)})
            await websocket.close(code=1011)
        except Exception:
            pass
    finally:
        if record_writer is not None:
            try:
                record_writer.release()
            except Exception:
                pass


@router.get("/api/results/{filename}")
async def get_result(filename: str, download: bool = False):
    file_path = settings.result_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    if download:
        return FileResponse(
            file_path,
            filename=filename,
            media_type="application/octet-stream",
        )
    return FileResponse(file_path)


@router.delete("/api/cleanup/{user_id}")
async def cleanup(user_id: str):
    removed_model = await model_registry.registry.remove_model(user_id)
    if removed_model:
        storage_service.remove_file(removed_model, logger)

    for directory in [settings.upload_dir, settings.result_dir]:
        for file_path in directory.glob(f"{user_id}_*"):
            storage_service.remove_file(file_path, logger)

    return {"success": True, "message": "清理完成"}


@router.get("/api/model-weights")
async def list_model_weights(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """列出用户的所有模型权重"""
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase 服务不可用",
        )

    weights = model_weights_service.list_user_weights(
        supabase_client,
        user_id=user_id,
        logger=logger,
    )

    # 始终添加默认权重到列表（如果已配置）
    if settings.default_model_path:
        # 检查用户是否有激活的自定义权重
        has_active_custom = any(w.get("is_active") for w in weights)
        
        # 添加默认权重
        default_weight = {
            "id": "default",
            "name": settings.default_model_name,
            "file_path": settings.default_model_path,
            "file_size": 0,
            "is_active": not has_active_custom,  # 只有在没有激活的自定义权重时才激活
            "is_default": True,
            "description": "系统提供的默认权重，所有用户均可使用",
            "created_at": None,
        }
        
        # 将默认权重添加到列表末尾
        weights.append(default_weight)
        logger.info("添加默认权重到列表，激活状态: %s", default_weight["is_active"])

    return {
        "success": True,
        "weights": weights,
    }


@router.get("/api/model-weights/deleted")
async def list_deleted_model_weights(
    request: Request,
    include_restored: bool = Query(False),
    authorization: Optional[str] = Header(None),
):
    """列出用户归档（已删除）的模型权重"""
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase 服务不可用",
        )

    archived_weights = model_weights_service.list_archived_weights(
        supabase_client,
        user_id=user_id,
        include_restored=include_restored,
        logger=logger,
    )

    return {
        "success": True,
        "weights": archived_weights,
    }


@router.post("/api/model-weights/deleted/{archive_id}/restore")
async def restore_deleted_model_weight(
    archive_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """恢复已归档的模型权重"""
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase 服务不可用",
        )

    restore_result = model_weights_service.restore_archived_weight(
        supabase_client,
        user_id=user_id,
        archive_id=archive_id,
        restore_by=user_id,
        logger=logger,
    )

    restore_status = restore_result.get("status")
    if restore_status == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="归档记录不存在",
        )
    if restore_status == "already_restored":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="归档记录已恢复，请勿重复恢复",
        )
    if restore_status != "ok":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="恢复权重失败",
        )

    return {
        "success": True,
        "message": "权重已恢复",
        "weight": restore_result.get("weight"),
    }


@router.get("/api/model-weights/{weight_id}")
async def get_model_weight(
    weight_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """获取指定模型权重的详情"""
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase 服务不可用",
        )

    weight = model_weights_service.get_weight_by_id(
        supabase_client,
        user_id=user_id,
        weight_id=weight_id,
        logger=logger,
    )

    if not weight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权重不存在",
        )

    return {
        "success": True,
        "weight": weight,
    }


@router.put("/api/model-weights/{weight_id}/activate")
async def activate_model_weight(
    weight_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """激活指定的模型权重"""
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase 服务不可用",
        )

    # 激活默认权重：取消所有自定义权重的激活状态
    if weight_id == "default":
        logger.info("用户激活默认权重，取消所有自定义权重的激活状态")
        try:
            # 取消所有用户自定义权重的激活状态
            supabase_client.table("model_weights").update(
                {"is_active": False}
            ).eq("user_id", user_id).execute()
            logger.info("已取消用户所有自定义权重的激活状态")
        except Exception as exc:
            logger.error("取消自定义权重激活状态失败: %s", exc)
        
        return {
            "success": True,
            "message": "已切换到默认权重",
        }

    success = model_weights_service.activate_weight(
        supabase_client,
        user_id=user_id,
        weight_id=weight_id,
        logger=logger,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="激活权重失败",
        )

    return {
        "success": True,
        "message": "权重已激活",
    }


@router.delete("/api/model-weights/{weight_id}")
async def delete_model_weight(
    weight_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """删除指定的模型权重"""
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase 服务不可用",
        )

    # 防止删除默认权重
    if weight_id == "default":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="默认权重无法删除，这是系统级权重",
        )

    # 归档后删除主表记录，存储文件保留用于后续恢复。
    archived_weight = model_weights_service.archive_weight(
        supabase_client,
        user_id=user_id,
        weight_id=weight_id,
        deleted_by=user_id,
        logger=logger,
    )

    if not archived_weight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权重不存在",
        )

    # 清理本地缓存
    storage_path = archived_weight.get("file_path")
    if storage_path:
        cache_path = settings.model_cache_dir / user_id / storage_path.split("/")[-1]
        if cache_path.exists():
            storage_service.remove_file(cache_path, logger)

    return {
        "success": True,
        "message": "权重已删除（可恢复）",
    }
