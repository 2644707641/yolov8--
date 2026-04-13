from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Header, Request

from app.api.common import (
    API_VERSION,
    get_supabase_client,
    local_state,
    logger,
    model_registry,
    model_weights_service,
    resolve_authenticated_user_id,
    settings,
    storage_service,
)
from app.services import system_monitor

router = APIRouter()


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def _count_daily_detection(records: list[dict]) -> tuple[int, int]:
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    today_count = 0
    yesterday_count = 0
    for item in records:
        parsed = _parse_iso_datetime(item.get("created_at"))
        if not parsed:
            continue
        if parsed.date() == today:
            today_count += 1
        elif parsed.date() == yesterday:
            yesterday_count += 1
    return today_count, yesterday_count


async def _resolve_active_model_count(supabase_client, user_id: str) -> int:
    if supabase_client:
        weights = model_weights_service.list_user_weights(
            supabase_client,
            user_id=user_id,
            logger=logger,
        )
        active_custom_count = sum(1 for w in weights if bool(w.get("is_active")))
        if active_custom_count > 0:
            return active_custom_count
        return 1 if bool(settings.default_model_path) else 0

    model_path = await model_registry.registry.get_model(user_id)
    return 1 if model_path else 0


@router.get("/")
async def root():
    return {
        "message": settings.api_title,
        "version": API_VERSION,
        "endpoints": {
            "upload_model": "/api/upload-model",
            "detect": "/api/detect",
            "detect_live_ws": "/ws/detect-live",
            "system_status": "/api/system/status",
            "system_overview": "/api/system/overview",
        },
    }


@router.get("/api/system/status")
async def get_system_status():
    """获取系统健康状态"""
    status = system_monitor.get_system_status()
    return {
        "success": True,
        "data": {
            "gpu_utilization": status["gpu_utilization"],
            "memory_used": status["memory_used"],
            "memory_percent": status["memory_percent"],
            "queue_backlog": status["queue_backlog"],
            "success_rate": status["success_rate"],
        },
    }


@router.get("/api/system/overview")
async def get_system_overview(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await resolve_authenticated_user_id(request, authorization)

    if supabase_client:
        records = storage_service.list_detection_records(
            supabase_client,
            user_id=user_id,
            logger=logger,
        )
    else:
        records = local_state.list_detection_records(
            settings.local_history_store_file,
            user_id=user_id,
        )

    today_count, yesterday_count = _count_daily_detection(records)
    active_model_count = await _resolve_active_model_count(supabase_client, user_id)
    status = system_monitor.get_system_status()

    return {
        "success": True,
        "data": {
            "today_detection_count": today_count,
            "yesterday_detection_count": yesterday_count,
            "avg_inference_time": status["avg_inference_time"],
            "active_model_count": active_model_count,
            "online_stream_count": status["active_live_streams"],
        },
    }
