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
from app.services import model_weights as model_weights_service
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

        # 优先从 Supabase 获取活跃权重
        model_path = None
        if supabase_client:
            active_weight = model_weights_service.get_active_weight(
                supabase_client,
                user_id=user_id,
                logger=logger,
            )

            if active_weight:
                # 检查本地缓存
                cache_filename = active_weight["file_path"].split("/")[-1]
                cache_path = settings.model_cache_dir / user_id / cache_filename

                if not cache_path.exists():
                    # 从 Supabase 下载权重
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

        # 如果没有 Supabase 权重，尝试使用本地注册表
        if not model_path:
            model_path = await model_registry.registry.get_model(user_id)

        # 如果用户没有自己的权重，使用默认权重
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

        response_payload = {
            "success": True,
            "resultUrl": f"/api/results/{result_path.name}",
            "originalUrlSupabase": original_url,
            "resultUrlSupabase": result_url_supabase,
            "detections": detections,
            "description": description,
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

    # 删除数据库记录
    storage_path = model_weights_service.delete_weight(
        supabase_client,
        user_id=user_id,
        weight_id=weight_id,
        logger=logger,
    )

    if not storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权重不存在",
        )

    # 删除 Supabase Storage 中的文件
    model_weights_service.delete_weight_from_supabase(
        supabase_client,
        storage_path,
        bucket=settings.model_weights_bucket,
        logger=logger,
    )

    # 清理本地缓存
    cache_path = settings.model_cache_dir / user_id / storage_path.split("/")[-1]
    if cache_path.exists():
        storage_service.remove_file(cache_path, logger)

    return {
        "success": True,
        "message": "权重已删除",
    }
