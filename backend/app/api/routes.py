from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    Header,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.core.config import settings
from app.services import auth as auth_service
from app.services import detection as detection_service
from app.services import model_registry
from app.services import storage as storage_service
from app.services import validators

logger = logging.getLogger("yolov8.api")

router = APIRouter()


def get_supabase_client(request: Request):
    return getattr(request.app.state, "supabase", None)


@router.get("/")
async def root():
    return {
        "message": settings.api_title,
        "version": "1.1.0",
        "endpoints": {
            "upload_model": "/api/upload-model",
            "detect": "/api/detect",
        },
    }


@router.post("/api/upload-model")
async def upload_model(
    request: Request,
    model: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    validators.validate_extension(
        model.filename,
        settings.allowed_model_extensions,
        "仅支持上传 .pt 或 .pth 模型文件",
    )

    model_path = settings.model_dir / f"{user_id}_{model.filename}"

    previous_model = await model_registry.registry.remove_model(user_id)
    if previous_model:
        storage_service.remove_file(previous_model, logger)

    validators.save_upload_file(
        model, model_path, max_size=settings.max_upload_size_bytes
    )
    await model_registry.registry.set_model(user_id, model_path)

    logger.info("用户 %s 上传模型成功: %s", user_id, model_path)

    return {
        "success": True,
        "message": "模型上传成功",
        "model_path": str(model_path),
        "user_id": user_id,
    }


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

        model_path = await model_registry.registry.get_model(user_id)
        if not model_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="请先上传模型文件"
            )

        result_path, detections, elapsed = await detection_service.run_detection(
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

        response_payload = {
            "success": True,
            "resultUrl": f"/api/results/{result_path.name}",
            "originalUrlSupabase": original_url,
            "resultUrlSupabase": result_url_supabase,
            "detections": detections,
            "processTime": elapsed,
            "params": detection_params,
        }
        return response_payload
    finally:
        storage_service.remove_file(input_path, logger)


@router.get("/api/results/{filename}")
async def get_result(filename: str):
    file_path = settings.result_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
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
