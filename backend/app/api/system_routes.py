from __future__ import annotations

from fastapi import APIRouter

from app.api.common import API_VERSION
from app.core.config import settings
from app.services import system_monitor

router = APIRouter()


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
            "error_rate": status["error_rate"],
        },
    }
