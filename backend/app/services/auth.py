from typing import Optional

import jwt
from fastapi import HTTPException, status
from supabase import Client

from app.core.config import settings


async def validate_token(token: Optional[str], supabase_client: Optional[Client]) -> str:
    """
    校验 token 并返回用户 ID。
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="授权令牌为空",
        )

    if not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="服务端未配置 JWT 验证密钥",
        )

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 中缺少用户 ID",
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="授权令牌已过期",
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="授权验证失败",
        ) from exc


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
    return await validate_token(token, supabase_client)
