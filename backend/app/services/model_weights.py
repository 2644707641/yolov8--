"""
模型权重管理服务

负责处理模型权重文件的上传、下载、管理等操作
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from supabase import Client


def upload_weight_to_supabase(
    supabase_client: Client,
    file_path: Path,
    *,
    user_id: str,
    bucket: str,
    logger,
) -> Optional[str]:
    """
    上传权重文件到 Supabase Storage

    Args:
        supabase_client: Supabase 客户端
        file_path: 本地文件路径
        user_id: 用户 ID
        bucket: 存储桶名称
        logger: 日志记录器

    Returns:
        存储路径，失败返回 None
    """
    storage_path = f"{user_id}/{int(time.time())}_{file_path.name}"

    try:
        with file_path.open("rb") as handle:
            file_content = handle.read()

        logger.info("上传权重文件到 Supabase: %s", storage_path)

        supabase_client.storage.from_(bucket).upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": "application/octet-stream"},
        )

        logger.info("权重文件上传成功: %s", storage_path)
        return storage_path
    except Exception as exc:
        logger.error("上传权重文件到 Supabase 失败: %s", exc)
        return None


def download_weight_from_supabase(
    supabase_client: Client,
    storage_path: str,
    local_path: Path,
    *,
    bucket: str,
    logger,
) -> bool:
    """
    从 Supabase Storage 下载权重文件

    Args:
        supabase_client: Supabase 客户端
        storage_path: Supabase 存储路径
        local_path: 本地保存路径
        bucket: 存储桶名称
        logger: 日志记录器

    Returns:
        是否下载成功
    """
    try:
        logger.info("从 Supabase 下载权重文件: %s -> %s", storage_path, local_path)

        # 确保父目录存在
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # 下载文件
        response = supabase_client.storage.from_(bucket).download(storage_path)

        # 保存到本地
        with local_path.open("wb") as handle:
            handle.write(response)

        logger.info("权重文件下载成功: %s (大小: %d bytes)", local_path, local_path.stat().st_size)
        return True
    except Exception as exc:
        logger.error("从 Supabase 下载权重文件失败: %s", exc)
        return False


def delete_weight_from_supabase(
    supabase_client: Client,
    storage_path: str,
    *,
    bucket: str,
    logger,
) -> bool:
    """
    从 Supabase Storage 删除权重文件

    Args:
        supabase_client: Supabase 客户端
        storage_path: Supabase 存储路径
        bucket: 存储桶名称
        logger: 日志记录器

    Returns:
        是否删除成功
    """
    try:
        logger.info("从 Supabase 删除权重文件: %s", storage_path)
        supabase_client.storage.from_(bucket).remove([storage_path])
        logger.info("权重文件删除成功: %s", storage_path)
        return True
    except Exception as exc:
        logger.error("从 Supabase 删除权重文件失败: %s", exc)
        return False


def create_weight_record(
    supabase_client: Client,
    *,
    user_id: str,
    name: str,
    file_path: str,
    file_size: int,
    description: Optional[str] = None,
    logger,
) -> Optional[dict]:
    """
    在数据库中创建权重记录

    Args:
        supabase_client: Supabase 客户端
        user_id: 用户 ID
        name: 权重文件名
        file_path: Supabase 存储路径
        file_size: 文件大小（字节）
        description: 权重描述
        logger: 日志记录器

    Returns:
        创建的记录，失败返回 None
    """
    try:
        logger.info("创建权重记录: user=%s name=%s", user_id, name)

        # 检查用户是否已有权重，如果没有则设置为活跃
        existing = (
            supabase_client.table("model_weights")
            .select("id")
            .eq("user_id", user_id)
            .execute()
        )

        is_active = len(existing.data) == 0

        # 如果设置为活跃，先取消其他权重的活跃状态
        if is_active:
            supabase_client.table("model_weights").update(
                {"is_active": False}
            ).eq("user_id", user_id).execute()

        response = (
            supabase_client.table("model_weights")
            .insert(
                {
                    "user_id": user_id,
                    "name": name,
                    "file_path": file_path,
                    "file_size": file_size,
                    "is_active": is_active,
                    "description": description,
                }
            )
            .execute()
        )

        data = getattr(response, "data", None)
        if data:
            weight_info = data[0]
            logger.info("✅ 权重记录创建成功:")
            logger.info("  - ID: %s", weight_info.get("id"))
            logger.info("  - Name: %s", weight_info.get("name"))
            logger.info("  - File Path: %s", weight_info.get("file_path"))
            logger.info("  - Is Active: %s", weight_info.get("is_active"))
            return weight_info
        else:
            logger.error("❌ 权重记录创建失败: response.data 为空")
    except Exception as exc:
        logger.error("创建权重记录失败: %s", exc)
    return None


def get_active_weight(
    supabase_client: Client,
    *,
    user_id: str,
    logger,
) -> Optional[dict]:
    """
    获取用户当前活跃的权重

    Args:
        supabase_client: Supabase 客户端
        user_id: 用户 ID
        logger: 日志记录器

    Returns:
        活跃的权重记录，没有返回 None
    """
    try:
        response = (
            supabase_client.table("model_weights")
            .select("*")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        data = getattr(response, "data", None)
        if data and len(data) > 0:
            return data[0]
    except Exception as exc:
        logger.error("获取活跃权重失败: %s", exc)
    return None


def list_user_weights(
    supabase_client: Client,
    *,
    user_id: str,
    logger,
) -> list[dict]:
    """
    列出用户的所有权重

    Args:
        supabase_client: Supabase 客户端
        user_id: 用户 ID
        logger: 日志记录器

    Returns:
        权重列表
    """
    try:
        logger.info("查询用户 %s 的权重列表", user_id)
        response = (
            supabase_client.table("model_weights")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        data = getattr(response, "data", None)
        if data:
            logger.info("查询到 %d 个权重记录", len(data))
            for idx, weight in enumerate(data):
                logger.info("  权重 %d: id=%s name=%s is_active=%s", 
                           idx + 1, weight.get("id"), weight.get("name"), weight.get("is_active"))
            return data
        else:
            logger.warning("未查询到权重数据，返回空列表")
    except Exception as exc:
        logger.error("列出用户权重失败: %s", exc)
    return []


def activate_weight(
    supabase_client: Client,
    *,
    user_id: str,
    weight_id: str,
    logger,
) -> bool:
    """
    激活指定的权重

    Args:
        supabase_client: Supabase 客户端
        user_id: 用户 ID
        weight_id: 权重 ID
        logger: 日志记录器

    Returns:
        是否激活成功
    """
    try:
        logger.info("激活权重: user=%s weight_id=%s", user_id, weight_id)

        # 先取消所有权重的活跃状态
        supabase_client.table("model_weights").update(
            {"is_active": False}
        ).eq("user_id", user_id).execute()

        # 激活指定权重
        response = (
            supabase_client.table("model_weights")
            .update({"is_active": True})
            .eq("id", weight_id)
            .eq("user_id", user_id)
            .execute()
        )

        data = getattr(response, "data", None)
        if data and len(data) > 0:
            logger.info("权重激活成功: weight_id=%s", weight_id)
            return True
    except Exception as exc:
        logger.error("激活权重失败: %s", exc)
    return False


def delete_weight(
    supabase_client: Client,
    *,
    user_id: str,
    weight_id: str,
    logger,
) -> Optional[str]:
    """
    删除指定的权重

    Args:
        supabase_client: Supabase 客户端
        user_id: 用户 ID
        weight_id: 权重 ID
        logger: 日志记录器

    Returns:
        被删除的权重的存储路径，失败返回 None
    """
    try:
        logger.info("删除权重: user=%s weight_id=%s", user_id, weight_id)

        # 先查询权重记录
        response = (
            supabase_client.table("model_weights")
            .select("file_path")
            .eq("id", weight_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        data = getattr(response, "data", None)
        if not data or len(data) == 0:
            logger.warning("权重不存在: weight_id=%s", weight_id)
            return None

        file_path = data[0].get("file_path")

        # 删除数据库记录
        supabase_client.table("model_weights").delete().eq(
            "id", weight_id
        ).eq("user_id", user_id).execute()

        logger.info("权重记录删除成功: weight_id=%s", weight_id)
        return file_path
    except Exception as exc:
        logger.error("删除权重失败: %s", exc)
    return None


def get_weight_by_id(
    supabase_client: Client,
    *,
    user_id: str,
    weight_id: str,
    logger,
) -> Optional[dict]:
    """
    获取指定的权重详情

    Args:
        supabase_client: Supabase 客户端
        user_id: 用户 ID
        weight_id: 权重 ID
        logger: 日志记录器

    Returns:
        权重记录，不存在返回 None
    """
    try:
        response = (
            supabase_client.table("model_weights")
            .select("*")
            .eq("id", weight_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        data = getattr(response, "data", None)
        if data and len(data) > 0:
            return data[0]
    except Exception as exc:
        logger.error("获取权重详情失败: %s", exc)
    return None


def get_default_weight(
    supabase_client: Client,
    *,
    default_path: str,
    cache_dir: Path,
    bucket: str,
    logger,
) -> Optional[Path]:
    """
    获取默认权重文件
    
    Args:
        supabase_client: Supabase 客户端
        default_path: 默认权重在 Supabase 中的路径
        cache_dir: 本地缓存目录
        bucket: 存储桶名称
        logger: 日志记录器
    
    Returns:
        本地权重文件路径，失败返回 None
    """
    try:
        # 构建本地缓存路径
        cache_filename = default_path.split("/")[-1]
        cache_path = cache_dir / "default" / cache_filename
        
        # 如果本地已有缓存，直接返回
        if cache_path.exists():
            logger.info("使用缓存的默认权重: %s", cache_path)
            return cache_path
        
        # 从 Supabase 下载默认权重
        logger.info("默认权重未缓存，开始下载: %s", default_path)
        success = download_weight_from_supabase(
            supabase_client,
            default_path,
            cache_path,
            bucket=bucket,
            logger=logger,
        )
        
        if success:
            logger.info("默认权重下载成功: %s", cache_path)
            return cache_path
        else:
            logger.error("默认权重下载失败")
            return None
    except Exception as exc:
        logger.error("获取默认权重失败: %s", exc)
        return None
