from __future__ import annotations

import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from supabase import Client

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv"}
DETECTION_HISTORY_TABLE = "detection_history"
DETECTION_HISTORY_ARCHIVE_TABLE = "detection_history_archive"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def upload_file_to_supabase(
    supabase_client: Client,
    file_path: Path,
    *,
    user_id: str,
    file_type: str,
    bucket: str,
    logger,
    is_result: bool = False,
) -> Optional[str]:
    folder = "results" if is_result else "original"
    storage_path = (
        f"{user_id}/{file_type}s/{folder}/{int(time.time())}{file_path.suffix}"
    )

    try:
        with file_path.open("rb") as handle:
            file_content = handle.read()

        suffix = file_path.suffix.lower()
        if suffix in IMAGE_SUFFIXES:
            content_type = "image/jpeg"
        elif suffix in VIDEO_SUFFIXES:
            content_type = "video/mp4"
        else:
            content_type = "application/octet-stream"

        logger.info("上传文件到 Supabase: %s", storage_path)

        supabase_client.storage.from_(bucket).upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": content_type},
        )

        public_url = supabase_client.storage.from_(bucket).get_public_url(storage_path)
        if not public_url:
            logger.warning("未获取到公共 URL")
            return None
        return public_url
    except Exception as exc:
        logger.warning("上传至 Supabase 失败: %s", exc)
        return None


def save_detection_record(
    supabase_client: Client,
    *,
    user_id: str,
    file_type: str,
    original_url: str,
    result_url: str,
    detections: list,
    params: dict,
    logger,
) -> Optional[dict]:
    logger.info("保存检测记录到 Supabase 数据库")
    try:
        response = (
            supabase_client.table(DETECTION_HISTORY_TABLE)
            .insert(
                {
                    "user_id": user_id,
                    "file_type": file_type,
                    "original_file": original_url,
                    "result_file": result_url,
                    "detections": detections,
                    "params": params,
                }
            )
            .execute()
        )
        data = getattr(response, "data", None)
        if data:
            return data[0]
    except Exception as exc:
        logger.warning("保存检测记录失败: %s", exc)
    return None


def list_detection_records(
    supabase_client: Client,
    *,
    user_id: str,
    logger,
) -> list[dict]:
    logger.info("查询用户历史记录: user=%s", user_id)
    try:
        response = (
            supabase_client.table(DETECTION_HISTORY_TABLE)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        data = getattr(response, "data", None)
        return data or []
    except Exception as exc:
        logger.warning("查询历史记录失败: %s", exc)
        return []


def archive_detection_record(
    supabase_client: Client,
    *,
    user_id: str,
    history_id: str,
    deleted_by: Optional[str] = None,
    logger,
) -> Optional[dict]:
    deleted_by = deleted_by or user_id
    logger.info("归档删除历史记录: user=%s history_id=%s", user_id, history_id)
    try:
        response = (
            supabase_client.table(DETECTION_HISTORY_TABLE)
            .select("*")
            .eq("id", history_id)
            .eq("user_id", user_id)
            .execute()
        )
        data = getattr(response, "data", None)
        if not data:
            logger.warning("待归档历史记录不存在: history_id=%s", history_id)
            return None

        current_record = data[0]
        archive_payload = {
            "original_history_id": str(current_record.get("id")),
            "user_id": current_record.get("user_id"),
            "file_type": current_record.get("file_type"),
            "original_file": current_record.get("original_file"),
            "result_file": current_record.get("result_file"),
            "detections": current_record.get("detections"),
            "params": current_record.get("params"),
            "original_created_at": current_record.get("created_at"),
            "deleted_at": _utc_now_iso(),
            "deleted_by": deleted_by,
            "is_restored": False,
            "restored_at": None,
            "restored_by": None,
        }

        archive_response = (
            supabase_client.table(DETECTION_HISTORY_ARCHIVE_TABLE)
            .insert(archive_payload)
            .execute()
        )
        archive_data = getattr(archive_response, "data", None)
        if not archive_data:
            logger.error("历史记录归档写入失败: history_id=%s", history_id)
            return None

        archived_record = archive_data[0]
        try:
            supabase_client.table(DETECTION_HISTORY_TABLE).delete().eq(
                "id", history_id
            ).eq("user_id", user_id).execute()
        except Exception as exc:
            archive_id = archived_record.get("archive_id")
            if archive_id:
                try:
                    supabase_client.table(DETECTION_HISTORY_ARCHIVE_TABLE).delete().eq(
                        "archive_id", archive_id
                    ).eq("user_id", user_id).execute()
                except Exception as rollback_exc:
                    logger.warning(
                        "历史记录主表删除失败且归档回滚失败: history_id=%s archive_id=%s err=%s",
                        history_id,
                        archive_id,
                        rollback_exc,
                    )
            logger.warning("历史记录主表删除失败，归档已回滚: %s", exc)
            return None

        return archived_record
    except Exception as exc:
        logger.warning("归档删除历史记录失败: %s", exc)
        return None


def list_archived_detection_records(
    supabase_client: Client,
    *,
    user_id: str,
    include_restored: bool = False,
    logger,
) -> list[dict]:
    logger.info("查询归档历史记录: user=%s include_restored=%s", user_id, include_restored)
    try:
        query = (
            supabase_client.table(DETECTION_HISTORY_ARCHIVE_TABLE)
            .select("*")
            .eq("user_id", user_id)
            .order("deleted_at", desc=True)
        )
        if not include_restored:
            query = query.eq("is_restored", False)

        response = query.execute()
        data = getattr(response, "data", None)
        return data or []
    except Exception as exc:
        logger.warning("查询归档历史记录失败: %s", exc)
        return []


def restore_archived_detection_record(
    supabase_client: Client,
    *,
    user_id: str,
    archive_id: str,
    restore_by: Optional[str] = None,
    logger,
) -> dict:
    restore_by = restore_by or user_id
    logger.info("恢复归档历史记录: user=%s archive_id=%s", user_id, archive_id)
    try:
        response = (
            supabase_client.table(DETECTION_HISTORY_ARCHIVE_TABLE)
            .select("*")
            .eq("archive_id", archive_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        data = getattr(response, "data", None)
        if not data:
            return {"status": "not_found", "item": None}

        archived_record = data[0]
        if bool(archived_record.get("is_restored")):
            return {"status": "already_restored", "item": None}

        restore_payload = {
            "id": archived_record.get("original_history_id"),
            "user_id": archived_record.get("user_id"),
            "file_type": archived_record.get("file_type"),
            "original_file": archived_record.get("original_file"),
            "result_file": archived_record.get("result_file"),
            "detections": archived_record.get("detections"),
            "params": archived_record.get("params"),
            "created_at": archived_record.get("original_created_at"),
        }

        restore_response = (
            supabase_client.table(DETECTION_HISTORY_TABLE)
            .insert(restore_payload)
            .execute()
        )
        restored_data = getattr(restore_response, "data", None)
        if not restored_data:
            return {"status": "error", "item": None}

        restored_record = restored_data[0]
        supabase_client.table(DETECTION_HISTORY_ARCHIVE_TABLE).update(
            {
                "is_restored": True,
                "restored_at": _utc_now_iso(),
                "restored_by": restore_by,
            }
        ).eq("archive_id", archive_id).eq("user_id", user_id).execute()

        return {"status": "ok", "item": restored_record}
    except Exception as exc:
        logger.warning("恢复归档历史记录失败: %s", exc)
        return {"status": "error", "item": None}


def remove_file(path: Path, logger) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except Exception as exc:
        logger.warning("删除文件 %s 失败: %s", path, exc)


def persist_local_upload(
    source_path: Path,
    *,
    user_id: str,
    destination_dir: Path,
    logger,
) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"upload_{user_id}_{uuid.uuid4().hex}{source_path.suffix.lower()}"
    shutil.copy2(source_path, destination)
    logger.info("保存本地原始文件副本: %s", destination)
    return destination
