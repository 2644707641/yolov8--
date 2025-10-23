from typing import Optional

import anyio
from fastapi import HTTPException, status
from supabase import Client


async def validate_authorization(
    authorization: Optional[str], supabase_client: Optional[Client]
) -> str:
    """
    校验 Authorization 头部，返回用户 ID。
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少或无效的授权头",
        )

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="授权令牌为空",
        )

    if supabase_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase 未配置，无法验证用户身份",
        )

    try:
        response = await anyio.to_thread.run_sync(
            supabase_client.auth.get_user, token
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="授权验证失败",
        ) from exc

    user = getattr(response, "user", None)
    user_id = getattr(user, "id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户身份无效",
        )

    return user_id

