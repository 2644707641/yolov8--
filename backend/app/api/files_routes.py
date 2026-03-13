from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request, status
from fastapi.responses import FileResponse

from app.api.common import (
    auth_service,
    extract_owned_file_owner_id,
    get_supabase_client,
    model_registry,
    resolve_authenticated_user_id,
    settings,
    storage_service,
    logger,
)

router = APIRouter()


@router.get("/api/results/{filename}")
async def get_result(
    filename: str,
    request: Request,
    download: bool = False,
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
):
    authenticated_user_id = await resolve_authenticated_user_id(
        request,
        authorization,
        token,
    )
    owner_user_id = extract_owned_file_owner_id(filename)
    if not owner_user_id or owner_user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问其他用户的结果文件",
        )

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


@router.get("/api/uploads/{filename}")
async def get_uploaded_file(
    filename: str,
    request: Request,
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
):
    authenticated_user_id = await resolve_authenticated_user_id(
        request,
        authorization,
        token,
    )
    owner_user_id = extract_owned_file_owner_id(filename)
    if not owner_user_id or owner_user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问其他用户的原始文件",
        )

    file_path = settings.upload_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    return FileResponse(file_path)


@router.delete("/api/cleanup/{user_id}")
async def cleanup(
    user_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    authenticated_user_id = await auth_service.validate_authorization(
        authorization,
        supabase_client,
    )

    if authenticated_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权清理其他用户的数据",
        )

    removed_model = await model_registry.registry.remove_model(user_id)
    if removed_model:
        storage_service.remove_file(removed_model, logger)

    cleanup_patterns = {
        settings.upload_dir: [f"{user_id}_*", f"upload_{user_id}_*"],
        settings.result_dir: [f"{user_id}_*", f"result_{user_id}_*", f"live_result_{user_id}_*"],
    }
    for directory, patterns in cleanup_patterns.items():
        for pattern in patterns:
            for file_path in directory.glob(pattern):
                storage_service.remove_file(file_path, logger)

    return {"success": True, "message": "清理完成"}
