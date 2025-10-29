from typing import Optional

import jwt
from fastapi import HTTPException, status
from supabase import Client

from app.core.config import settings


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

    # 方法1: 如果配置了 JWT Secret，直接验证 token
    if settings.supabase_jwt_secret:
        try:
            # 解码并验证 JWT token
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
                detail=f"授权验证失败: {str(exc)}",
            )
    
    # 方法2: 回退到解析 JWT payload（不验证签名，仅用于开发）
    # 这种方法安全性较低，仅在无法获取 JWT Secret 时使用
    try:
        # 不验证签名，仅解析 payload
        payload = jwt.decode(
            token,
            options={"verify_signature": False},
        )
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 中缺少用户 ID",
            )
        
        # 检查 token 是否过期
        import time
        exp = payload.get("exp")
        if exp and exp < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="授权令牌已过期",
            )
        
        return user_id
        
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="授权验证失败",
        ) from exc

