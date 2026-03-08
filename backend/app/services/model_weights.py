"""
模型权重管理服务

负责处理模型权重文件的上传、下载、管理等操作
"""
from __future__ import annotations

from datetime import datetime, timezone
import time
from pathlib import Path
from typing import Any, Optional

from supabase import Client

MODEL_WEIGHTS_TABLE = "model_weights"
MODEL_WEIGHTS_ARCHIVE_TABLE = "model_weights_archive"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
            supabase_client.table(MODEL_WEIGHTS_TABLE)
            .select("id")
            .eq("user_id", user_id)
            .execute()
        )

        is_active = len(existing.data) == 0

        # 如果设置为活跃，先取消其他权重的活跃状态
        if is_active:
            supabase_client.table(MODEL_WEIGHTS_TABLE).update(
                {"is_active": False}
            ).eq("user_id", user_id).execute()

        response = (
            supabase_client.table(MODEL_WEIGHTS_TABLE)
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
            supabase_client.table(MODEL_WEIGHTS_TABLE)
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
            supabase_client.table(MODEL_WEIGHTS_TABLE)
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
        supabase_client.table(MODEL_WEIGHTS_TABLE).update(
            {"is_active": False}
        ).eq("user_id", user_id).execute()

        # 激活指定权重
        response = (
            supabase_client.table(MODEL_WEIGHTS_TABLE)
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
            supabase_client.table(MODEL_WEIGHTS_TABLE)
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
        supabase_client.table(MODEL_WEIGHTS_TABLE).delete().eq(
            "id", weight_id
        ).eq("user_id", user_id).execute()

        logger.info("权重记录删除成功: weight_id=%s", weight_id)
        return file_path
    except Exception as exc:
        logger.error("删除权重失败: %s", exc)
    return None


def archive_weight(
    supabase_client: Client,
    *,
    user_id: str,
    weight_id: str,
    deleted_by: Optional[str] = None,
    logger,
) -> Optional[dict]:
    """
    将指定权重归档后从主表删除。

    Returns:
        归档记录，失败或记录不存在返回 None
    """
    deleted_by = deleted_by or user_id
    archived_weight = None

    try:
        logger.info("归档删除权重: user=%s weight_id=%s", user_id, weight_id)

        response = (
            supabase_client.table(MODEL_WEIGHTS_TABLE)
            .select("id,user_id,name,file_path,file_size,description,created_at,is_active")
            .eq("id", weight_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        data = getattr(response, "data", None)
        if not data:
            logger.warning("待归档权重不存在: weight_id=%s", weight_id)
            return None

        current_weight = data[0]
        archive_payload = {
            "original_weight_id": str(current_weight.get("id")),
            "user_id": current_weight.get("user_id"),
            "name": current_weight.get("name"),
            "file_path": current_weight.get("file_path"),
            "file_size": current_weight.get("file_size") or 0,
            "description": current_weight.get("description"),
            "original_created_at": current_weight.get("created_at"),
            "was_active": bool(current_weight.get("is_active")),
            "deleted_at": _utc_now_iso(),
            "deleted_by": deleted_by,
            "is_restored": False,
            "restored_at": None,
            "restored_by": None,
        }

        archive_response = (
            supabase_client.table(MODEL_WEIGHTS_ARCHIVE_TABLE)
            .insert(archive_payload)
            .execute()
        )
        archive_data = getattr(archive_response, "data", None)
        if not archive_data:
            logger.error("归档写入失败: weight_id=%s", weight_id)
            return None

        archived_weight = archive_data[0]

        # 主表删除放在归档写入成功之后，避免数据丢失。
        try:
            supabase_client.table(MODEL_WEIGHTS_TABLE).delete().eq(
                "id", weight_id
            ).eq("user_id", user_id).execute()
        except Exception as exc:
            archive_id = archived_weight.get("archive_id")
            if archive_id:
                try:
                    supabase_client.table(MODEL_WEIGHTS_ARCHIVE_TABLE).delete().eq(
                        "archive_id", archive_id
                    ).eq("user_id", user_id).execute()
                except Exception as rollback_exc:
                    logger.warning(
                        "主表删除失败且归档回滚失败: weight_id=%s archive_id=%s err=%s",
                        weight_id,
                        archive_id,
                        rollback_exc,
                    )
            logger.error("主表删除失败，归档已回滚: %s", exc)
            return None

        logger.info(
            "权重归档删除成功: weight_id=%s archive_id=%s",
            weight_id,
            archived_weight.get("archive_id"),
        )
        return archived_weight
    except Exception as exc:
        logger.error("归档删除权重失败: %s", exc)
    return None


def list_archived_weights(
    supabase_client: Client,
    *,
    user_id: str,
    include_restored: bool = False,
    logger,
) -> list[dict]:
    """
    查询用户的归档权重列表。
    """
    try:
        logger.info(
            "查询用户归档权重: user=%s include_restored=%s",
            user_id,
            include_restored,
        )
        query = (
            supabase_client.table(MODEL_WEIGHTS_ARCHIVE_TABLE)
            .select("*")
            .eq("user_id", user_id)
            .order("deleted_at", desc=True)
        )
        if not include_restored:
            query = query.eq("is_restored", False)

        response = query.execute()
        data = getattr(response, "data", None)
        if data:
            logger.info("查询到 %d 条归档权重记录", len(data))
            return data

        logger.info("未查询到归档权重数据")
    except Exception as exc:
        logger.error("查询归档权重失败: %s", exc)
    return []


def restore_archived_weight(
    supabase_client: Client,
    *,
    user_id: str,
    archive_id: str,
    restore_by: Optional[str] = None,
    logger,
) -> dict[str, Any]:
    """
    从归档表恢复权重到主表。

    恢复激活策略：
    - was_active=False -> 恢复后不激活
    - was_active=True 且当前已有激活权重 -> 恢复后不激活
    - was_active=True 且当前无激活权重 -> 恢复后激活
    """
    restore_by = restore_by or user_id

    try:
        logger.info("恢复归档权重: user=%s archive_id=%s", user_id, archive_id)
        response = (
            supabase_client.table(MODEL_WEIGHTS_ARCHIVE_TABLE)
            .select("*")
            .eq("archive_id", archive_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        data = getattr(response, "data", None)
        if not data:
            logger.warning("归档记录不存在: archive_id=%s", archive_id)
            return {"status": "not_found", "weight": None}

        archived_weight = data[0]
        if bool(archived_weight.get("is_restored")):
            logger.warning("归档记录已恢复: archive_id=%s", archive_id)
            return {"status": "already_restored", "weight": None}

        active_response = (
            supabase_client.table(MODEL_WEIGHTS_TABLE)
            .select("id")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
        has_active_weight = bool(getattr(active_response, "data", None))
        should_activate = bool(archived_weight.get("was_active")) and not has_active_weight

        restore_payload = {
            "user_id": archived_weight.get("user_id"),
            "name": archived_weight.get("name"),
            "file_path": archived_weight.get("file_path"),
            "file_size": archived_weight.get("file_size") or 0,
            "is_active": should_activate,
            "description": archived_weight.get("description"),
        }

        restore_response = (
            supabase_client.table(MODEL_WEIGHTS_TABLE)
            .insert(restore_payload)
            .execute()
        )
        restored_data = getattr(restore_response, "data", None)
        if not restored_data:
            logger.error("恢复写入主表失败: archive_id=%s", archive_id)
            return {"status": "error", "weight": None}

        restored_weight = restored_data[0]

        supabase_client.table(MODEL_WEIGHTS_ARCHIVE_TABLE).update(
            {
                "is_restored": True,
                "restored_at": _utc_now_iso(),
                "restored_by": restore_by,
            }
        ).eq("archive_id", archive_id).eq("user_id", user_id).execute()

        logger.info(
            "归档权重恢复成功: archive_id=%s restored_weight_id=%s is_active=%s",
            archive_id,
            restored_weight.get("id"),
            restored_weight.get("is_active"),
        )
        return {"status": "ok", "weight": restored_weight}
    except Exception as exc:
        logger.error("恢复归档权重失败: %s", exc)
    return {"status": "error", "weight": None}


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
            supabase_client.table(MODEL_WEIGHTS_TABLE)
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
