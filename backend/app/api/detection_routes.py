from __future__ import annotations

import json
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
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from app.api.common import (
    auth_service,
    detection_service,
    get_supabase_client,
    get_supabase_client_from_websocket,
    local_state,
    logger,
    model_registry,
    model_weights_service,
    resolve_model_path,
    run_local_cleanup_for_app,
    settings,
    storage_service,
)
from app.services import validators

router = APIRouter()


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

    temp_model_path = settings.model_dir / f"temp_{user_id}_{model.filename}"

    try:
        validators.save_upload_file(
            model, temp_model_path, max_size=settings.max_upload_size_bytes
        )

        file_size = temp_model_path.stat().st_size

        if supabase_client:
            storage_path = model_weights_service.upload_weight_to_supabase(
                supabase_client,
                temp_model_path,
                user_id=user_id,
                bucket=settings.model_weights_bucket,
                logger=logger,
            )

            if storage_path:
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
                detail="请先上传模型文件或确保默认权重已配置",
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
        local_result_url = f"/api/results/{result_path.name}"

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
        else:
            persisted_original_path = storage_service.persist_local_upload(
                input_path,
                user_id=user_id,
                destination_dir=settings.upload_dir,
                logger=logger,
            )
            local_state.save_detection_record(
                settings.local_history_store_file,
                user_id=user_id,
                file_type=type,
                original_url=f"/api/uploads/{persisted_original_path.name}",
                result_url=local_result_url,
                detections=detections,
                params=detection_params,
            )
            run_local_cleanup_for_app(
                request.app,
                logger=logger,
            )

        metrics = detection_service.build_result_metrics(detections, type)
        response_payload = {
            "success": True,
            "resultUrl": local_result_url,
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
