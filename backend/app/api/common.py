from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, WebSocket, status
from pydantic import BaseModel

from app.core.config import settings
from app.services import auth as auth_service
from app.services import detection as detection_service
from app.services import local_cleanup
from app.services import local_state
from app.services import model_registry
from app.services import model_weights as model_weights_service
from app.services import storage as storage_service

logger = logging.getLogger("yolov8.api")

API_VERSION = "1.1.0"
DEFAULT_STORAGE_POLICY = {
    "retentionDays": 30,
    "region": "CN-East-1",
    "backupTime": "02:00",
}


class SettingsUpdate(BaseModel):
    defaults: Optional[Dict[str, Any]] = None
    storage: Optional[Dict[str, Any]] = None


def get_default_local_cleanup_settings() -> Dict[str, Any]:
    return {
        "enabled": settings.local_history_cleanup_enabled,
        "retentionDays": settings.local_history_retention_days,
        "maxRecords": settings.local_history_max_records,
    }


def _normalize_positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} 必须是大于等于 1 的整数",
        )
    try:
        normalized = int(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} 必须是大于等于 1 的整数",
        ) from exc
    if normalized < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} 必须是大于等于 1 的整数",
        )
    return normalized


def normalize_local_cleanup_settings(
    payload: Optional[Dict[str, Any]],
    current: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    normalized = {
        **get_default_local_cleanup_settings(),
        **(current or {}),
    }
    if not payload:
        return normalized

    if "enabled" in payload:
        enabled = payload.get("enabled")
        if not isinstance(enabled, bool):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="enabled 必须是布尔值",
            )
        normalized["enabled"] = enabled
    if "retentionDays" in payload:
        normalized["retentionDays"] = _normalize_positive_int(
            payload.get("retentionDays"),
            "retentionDays",
        )
    if "maxRecords" in payload:
        normalized["maxRecords"] = _normalize_positive_int(
            payload.get("maxRecords"),
            "maxRecords",
        )
    return normalized


def get_app_settings_store(app) -> Dict[str, Any]:
    store = getattr(app.state, "app_settings", None)
    if store is None:
        store = local_state.load_app_settings(settings.user_settings_store_file)
        app.state.app_settings = store
    return store


def get_local_cleanup_settings(app) -> Dict[str, Any]:
    app_settings = get_app_settings_store(app)
    return normalize_local_cleanup_settings(app_settings.get("localCleanup"))


def get_local_cleanup_meta(app) -> Dict[str, Any]:
    app_settings = get_app_settings_store(app)
    meta = app_settings.get("localCleanupMeta") or {}
    summary = meta.get("lastSummary")
    if not isinstance(summary, dict):
        summary = None
    return {
        "lastRunAt": meta.get("lastRunAt"),
        "lastSummary": summary,
    }


def get_local_storage_stats(app) -> Dict[str, Any]:
    cleanup_meta = get_local_cleanup_meta(app)
    return local_cleanup.get_local_storage_stats(
        settings.local_history_store_file,
        upload_dir=settings.upload_dir,
        result_dir=settings.result_dir,
        last_cleanup_at=cleanup_meta.get("lastRunAt"),
    )


def get_default_local_storage_stats() -> Dict[str, Any]:
    return {
        "historyRecordCount": 0,
        "archiveRecordCount": 0,
        "uploadsFileCount": 0,
        "uploadsBytes": 0,
        "resultsFileCount": 0,
        "resultsBytes": 0,
        "totalBytes": 0,
        "lastCleanupAt": None,
    }


def _persist_app_settings(app, app_settings: Dict[str, Any]) -> Dict[str, Any]:
    app.state.app_settings = app_settings
    local_state.save_app_settings(settings.user_settings_store_file, app_settings)
    return app_settings


def save_local_cleanup_meta(
    app,
    summary: Dict[str, int],
    *,
    cleaned_at: Optional[str] = None,
) -> Dict[str, Any]:
    app_settings = get_app_settings_store(app)
    app_settings["localCleanupMeta"] = {
        "lastRunAt": cleaned_at or datetime.now(timezone.utc).isoformat(),
        "lastSummary": summary,
    }
    return _persist_app_settings(app, app_settings)


def run_local_cleanup_for_app(
    app,
    *,
    logger,
    force: bool = False,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    local_cleanup_settings = get_local_cleanup_settings(app)
    if not force and not local_cleanup_settings["enabled"]:
        return {
            "performed": False,
            "cleanedAt": None,
            "summary": {
                "removed_records": 0,
                "removed_archives": 0,
                "removed_files": 0,
            },
        }

    summary = local_cleanup.cleanup_local_storage(
        settings.local_history_store_file,
        upload_dir=settings.upload_dir,
        result_dir=settings.result_dir,
        retention_days=local_cleanup_settings["retentionDays"],
        max_records=local_cleanup_settings["maxRecords"],
        logger=logger,
        now=now,
    )
    cleaned_at = now or datetime.now(timezone.utc).isoformat()
    save_local_cleanup_meta(app, summary, cleaned_at=cleaned_at)
    return {
        "performed": True,
        "cleanedAt": cleaned_at,
        "summary": summary,
    }


def build_storage_policy(
    supabase_client,
    local_cleanup_settings: Optional[Dict[str, Any]] = None,
    local_cleanup_meta: Optional[Dict[str, Any]] = None,
    local_stats: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cleanup_meta = local_cleanup_meta or {}
    cleanup_settings = normalize_local_cleanup_settings(local_cleanup_settings)
    return {
        **DEFAULT_STORAGE_POLICY,
        "mode": "supabase" if supabase_client else "local",
        "localCleanup": {
            **cleanup_settings,
            "lastRunAt": cleanup_meta.get("lastRunAt"),
            "lastSummary": cleanup_meta.get("lastSummary"),
        },
        "localStats": {
            **get_default_local_storage_stats(),
            **(local_stats or {}),
        },
    }


def get_user_settings_store(app) -> Dict[str, Dict[str, Any]]:
    store = getattr(app.state, "user_settings", None)
    if store is None:
        store = local_state.load_user_settings_map(settings.user_settings_store_file)
        app.state.user_settings = store
    return store


def pack_detection_params(params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "imgSize": int(params.get("imgsz", 640)),
        "confidence": float(params.get("confidence", 0.25)),
        "iouThreshold": float(params.get("iou", 0.45)),
        "maxDetections": int(params.get("max_det", 300)),
        "frameSkip": int(params.get("frame_skip", 1)),
    }


def get_supabase_client(request: Request):
    return getattr(request.app.state, "supabase", None)


def get_supabase_client_from_websocket(websocket: WebSocket):
    return getattr(websocket.app.state, "supabase", None)


async def resolve_authenticated_user_id(
    request: Request,
    authorization: Optional[str],
    token: Optional[str] = None,
) -> str:
    supabase_client = get_supabase_client(request)
    if authorization:
        return await auth_service.validate_authorization(authorization, supabase_client)
    if token:
        return await auth_service.validate_token(token, supabase_client)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="缺少或无效的授权头",
    )


def extract_owned_file_owner_id(filename: str) -> Optional[str]:
    prefixes = ("live_result_", "result_", "upload_")

    for prefix in prefixes:
        if not filename.startswith(prefix):
            continue

        stem = Path(filename).stem
        owner_part = stem[len(prefix):]
        if "_" not in owner_part:
            return None

        owner_id, _, _ = owner_part.rpartition("_")
        return owner_id or None

    return None


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
