from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from supabase import Client

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv"}


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
            supabase_client.table("detection_history")
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


def remove_file(path: Path, logger) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except Exception as exc:
        logger.warning("删除文件 %s 失败: %s", path, exc)
