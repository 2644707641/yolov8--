from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request, status

from app.api.common import (
    get_supabase_client,
    local_state,
    logger,
    resolve_authenticated_user_id,
    settings,
    storage_service,
)

router = APIRouter()


@router.get("/api/history")
async def list_history(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await resolve_authenticated_user_id(request, authorization)

    if supabase_client:
        items = storage_service.list_detection_records(
            supabase_client,
            user_id=user_id,
            logger=logger,
        )
    else:
        items = local_state.list_detection_records(
            settings.local_history_store_file,
            user_id=user_id,
        )
    return {
        "success": True,
        "items": items,
    }


@router.delete("/api/history/{history_id}")
async def delete_history(
    history_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await resolve_authenticated_user_id(request, authorization)

    if supabase_client:
        archived = storage_service.archive_detection_record(
            supabase_client,
            user_id=user_id,
            history_id=history_id,
            deleted_by=user_id,
            logger=logger,
        )
    else:
        archived = local_state.archive_detection_record(
            settings.local_history_store_file,
            user_id=user_id,
            history_id=history_id,
            deleted_by=user_id,
        )
    if not archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="历史记录不存在",
        )

    return {
        "success": True,
        "message": "历史记录已删除（可恢复）",
        "archive": archived,
    }


@router.get("/api/history/deleted")
async def list_deleted_history(
    request: Request,
    include_restored: bool = Query(False),
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await resolve_authenticated_user_id(request, authorization)

    if supabase_client:
        items = storage_service.list_archived_detection_records(
            supabase_client,
            user_id=user_id,
            include_restored=include_restored,
            logger=logger,
        )
    else:
        items = local_state.list_archived_detection_records(
            settings.local_history_store_file,
            user_id=user_id,
            include_restored=include_restored,
        )
    return {
        "success": True,
        "items": items,
    }


@router.post("/api/history/deleted/{archive_id}/restore")
async def restore_deleted_history(
    archive_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await resolve_authenticated_user_id(request, authorization)

    if supabase_client:
        restore_result = storage_service.restore_archived_detection_record(
            supabase_client,
            user_id=user_id,
            archive_id=archive_id,
            restore_by=user_id,
            logger=logger,
        )
    else:
        restore_result = local_state.restore_archived_detection_record(
            settings.local_history_store_file,
            user_id=user_id,
            archive_id=archive_id,
            restore_by=user_id,
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
            detail="恢复历史记录失败",
        )

    return {
        "success": True,
        "message": "历史记录已恢复",
        "item": restore_result.get("item"),
    }
