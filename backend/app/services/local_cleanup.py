from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Optional


def _read_payload(store_file: Path) -> dict[str, Any]:
    if not store_file.exists():
        return {
            "app_settings": {},
            "user_settings": {},
            "history_records": [],
            "history_archives": [],
        }
    try:
        return json.loads(store_file.read_text(encoding="utf-8"))
    except Exception:
        return {
            "app_settings": {},
            "user_settings": {},
            "history_records": [],
            "history_archives": [],
        }


def _write_payload(store_file: Path, payload: dict[str, Any]) -> None:
    store_file.parent.mkdir(parents=True, exist_ok=True)
    store_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _extract_local_filename(path_or_url: Optional[str], prefix: str) -> Optional[str]:
    if not path_or_url:
        return None
    marker = f"/api/{prefix}/"
    if marker not in path_or_url:
        return None
    return path_or_url.split(marker, 1)[1].split("?", 1)[0]


def _collect_referenced_files(records: Iterable[dict[str, Any]]) -> tuple[set[str], set[str]]:
    upload_files: set[str] = set()
    result_files: set[str] = set()

    for record in records:
        upload_name = _extract_local_filename(record.get("original_file"), "uploads")
        if upload_name:
            upload_files.add(upload_name)
        result_name = _extract_local_filename(record.get("result_file"), "results")
        if result_name:
            result_files.add(result_name)

    return upload_files, result_files


def _cleanup_directory(directory: Path, patterns: list[str], referenced: set[str], logger) -> int:
    removed = 0
    for pattern in patterns:
        for file_path in directory.glob(pattern):
            if file_path.name in referenced:
                continue
            try:
                file_path.unlink()
                removed += 1
            except FileNotFoundError:
                continue
            except Exception as exc:
                logger.warning("清理本地文件失败: %s (%s)", file_path, exc)
    return removed


def _collect_directory_stats(directory: Path, patterns: list[str]) -> dict[str, int]:
    file_count = 0
    total_bytes = 0
    for pattern in patterns:
        for file_path in directory.glob(pattern):
            if not file_path.is_file():
                continue
            file_count += 1
            try:
                total_bytes += file_path.stat().st_size
            except FileNotFoundError:
                continue
    return {
        "fileCount": file_count,
        "bytes": total_bytes,
    }


def get_local_storage_stats(
    store_file: Path,
    *,
    upload_dir: Path,
    result_dir: Path,
    last_cleanup_at: Optional[str] = None,
) -> dict[str, Any]:
    payload = _read_payload(store_file)
    upload_stats = _collect_directory_stats(upload_dir, ["upload_*"])
    result_stats = _collect_directory_stats(result_dir, ["result_*", "live_result_*"])
    return {
        "historyRecordCount": len(payload.get("history_records") or []),
        "archiveRecordCount": len(payload.get("history_archives") or []),
        "uploadsFileCount": upload_stats["fileCount"],
        "uploadsBytes": upload_stats["bytes"],
        "resultsFileCount": result_stats["fileCount"],
        "resultsBytes": result_stats["bytes"],
        "totalBytes": upload_stats["bytes"] + result_stats["bytes"],
        "lastCleanupAt": last_cleanup_at,
    }


def cleanup_local_storage(
    store_file: Path,
    *,
    upload_dir: Path,
    result_dir: Path,
    retention_days: int,
    max_records: int,
    logger,
    now: Optional[str] = None,
) -> dict[str, int]:
    payload = _read_payload(store_file)
    current_time = _parse_datetime(now) or datetime.now(timezone.utc)
    cutoff = None
    if retention_days > 0:
        cutoff = current_time - timedelta(days=retention_days)

    history_records = list(payload.get("history_records") or [])
    history_archives = list(payload.get("history_archives") or [])

    kept_records = []
    removed_records = []
    for record in history_records:
        created_at = _parse_datetime(record.get("created_at"))
        if cutoff and created_at and created_at < cutoff:
            removed_records.append(record)
        else:
            kept_records.append(record)

    kept_records.sort(
        key=lambda item: _parse_datetime(item.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    if max_records > 0 and len(kept_records) > max_records:
        removed_records.extend(kept_records[max_records:])
        kept_records = kept_records[:max_records]

    kept_archives = []
    removed_archives = []
    for record in history_archives:
        deleted_at = _parse_datetime(record.get("deleted_at"))
        if cutoff and deleted_at and deleted_at < cutoff:
            removed_archives.append(record)
        else:
            kept_archives.append(record)

    payload["history_records"] = kept_records
    payload["history_archives"] = kept_archives
    _write_payload(store_file, payload)

    referenced_uploads, referenced_results = _collect_referenced_files(
        [*kept_records, *kept_archives]
    )
    removed_files = 0
    removed_files += _cleanup_directory(
        upload_dir,
        ["upload_*"],
        referenced_uploads,
        logger,
    )
    removed_files += _cleanup_directory(
        result_dir,
        ["result_*", "live_result_*"],
        referenced_results,
        logger,
    )

    if removed_records or removed_archives or removed_files:
        logger.info(
            "本地历史清理完成: records=%s archives=%s files=%s",
            len(removed_records),
            len(removed_archives),
            removed_files,
        )

    return {
        "removed_records": len(removed_records),
        "removed_archives": len(removed_archives),
        "removed_files": removed_files,
    }
