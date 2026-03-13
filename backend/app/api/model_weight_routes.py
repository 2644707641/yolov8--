from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request, status

from app.api.common import (
    auth_service,
    get_supabase_client,
    logger,
    model_weights_service,
    settings,
    storage_service,
)

router = APIRouter()


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

    if settings.default_model_path:
        has_active_custom = any(w.get("is_active") for w in weights)
        default_weight = {
            "id": "default",
            "name": settings.default_model_name,
            "file_path": settings.default_model_path,
            "file_size": 0,
            "is_active": not has_active_custom,
            "is_default": True,
            "description": "系统提供的默认权重，所有用户均可使用",
            "created_at": None,
        }
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

    if weight_id == "default":
        logger.info("用户激活默认权重，取消所有自定义权重的激活状态")
        try:
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

    if weight_id == "default":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="默认权重无法删除，这是系统级权重",
        )

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

    storage_path = archived_weight.get("file_path")
    if storage_path:
        cache_path = settings.model_cache_dir / user_id / storage_path.split("/")[-1]
        if cache_path.exists():
            storage_service.remove_file(cache_path, logger)

    return {
        "success": True,
        "message": "权重已删除（可恢复）",
    }
