"""AI 分析路由 — 独立重试端点 + LLM 异步端点。"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel

from app.api.common import (
    auth_service,
    get_supabase_client,
    logger,
    settings,
)
from app.services import ai_analysis

router = APIRouter()


class AnalysisRequest(BaseModel):
    detections: list[dict]
    imgWidth: int = 1920
    imgHeight: int = 1080


@router.post("/api/ai/analyze")
async def analyze(
    request: Request,
    payload: AnalysisRequest,
    authorization: Optional[str] = Header(None),
):
    """全量分析端点（启发式 + LLM），用于完整重试。"""
    supabase_client = get_supabase_client(request)
    await auth_service.validate_authorization(authorization, supabase_client)

    if not payload.detections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="检测结果不能为空",
        )

    ai_config = None
    if settings.ai_api_url and settings.ai_api_key:
        ai_config = {
            "apiUrl": settings.ai_api_url,
            "apiKey": settings.ai_api_key,
            "model": settings.ai_model,
        }

    client = getattr(request.app.state, "http_client", None)
    result = await ai_analysis.run_full_analysis(
        detections=payload.detections,
        img_width=payload.imgWidth,
        img_height=payload.imgHeight,
        ai_config=ai_config,
        client=client,
    )
    return {"success": True, **result}


@router.post("/api/ai/analyze-llm")
async def analyze_llm(
    request: Request,
    payload: AnalysisRequest,
    authorization: Optional[str] = Header(None),
):
    """仅 LLM 分析端点，用于检测完成后异步获取 AI 建议。"""
    supabase_client = get_supabase_client(request)
    await auth_service.validate_authorization(authorization, supabase_client)

    if not payload.detections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="检测结果不能为空",
        )

    if not settings.ai_api_url or not settings.ai_api_key:
        return {"success": True, "spatial": None, "llm": None}

    ai_config = {
        "apiUrl": settings.ai_api_url,
        "apiKey": settings.ai_api_key,
        "model": settings.ai_model,
    }

    client = getattr(request.app.state, "http_client", None)
    result = await ai_analysis.run_llm_only(
        detections=payload.detections,
        img_width=payload.imgWidth,
        img_height=payload.imgHeight,
        ai_config=ai_config,
        client=client,
    )
    return {"success": True, **result}
