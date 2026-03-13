from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_payload() -> dict[str, Any]:
    return {
        "app_settings": {},
        "user_settings": {},
        "history_records": [],
        "history_archives": [],
    }


def _read_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _default_payload()

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _default_payload()


def _write_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_user_settings_map(path: Path) -> dict[str, dict[str, Any]]:
    with _LOCK:
        payload = _read_payload(path)
        return dict(payload.get("user_settings") or {})


def load_app_settings(path: Path) -> dict[str, Any]:
    with _LOCK:
        payload = _read_payload(path)
        return dict(payload.get("app_settings") or {})


def save_app_settings(path: Path, app_settings_payload: dict[str, Any]) -> dict[str, Any]:
    with _LOCK:
        payload = _read_payload(path)
        payload["app_settings"] = app_settings_payload
        _write_payload(path, payload)
        return app_settings_payload


def save_user_settings(path: Path, user_id: str, settings_payload: dict[str, Any]) -> dict[str, Any]:
    with _LOCK:
        payload = _read_payload(path)
        user_settings = dict(payload.get("user_settings") or {})
        user_settings[user_id] = settings_payload
        payload["user_settings"] = user_settings
        _write_payload(path, payload)
        return settings_payload


def save_detection_record(
    path: Path,
    *,
    user_id: str,
    file_type: str,
    original_url: str,
    result_url: str,
    detections: list,
    params: dict,
) -> dict[str, Any]:
    with _LOCK:
        payload = _read_payload(path)
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "file_type": file_type,
            "original_file": original_url,
            "result_file": result_url,
            "detections": detections,
            "params": params,
            "created_at": _utc_now_iso(),
        }
        history_records = list(payload.get("history_records") or [])
        history_records.append(record)
        payload["history_records"] = history_records
        _write_payload(path, payload)
        return record


def list_detection_records(path: Path, *, user_id: str) -> list[dict[str, Any]]:
    with _LOCK:
        payload = _read_payload(path)
        records = [
            record
            for record in payload.get("history_records") or []
            if record.get("user_id") == user_id
        ]
        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)


def archive_detection_record(
    path: Path,
    *,
    user_id: str,
    history_id: str,
    deleted_by: str,
) -> dict[str, Any] | None:
    with _LOCK:
        payload = _read_payload(path)
        history_records = list(payload.get("history_records") or [])
        record = next(
            (
                item
                for item in history_records
                if item.get("id") == history_id and item.get("user_id") == user_id
            ),
            None,
        )
        if not record:
            return None

        history_records = [item for item in history_records if item.get("id") != history_id]
        archives = list(payload.get("history_archives") or [])
        archived_record = {
            "archive_id": str(uuid.uuid4()),
            "original_history_id": record.get("id"),
            "user_id": record.get("user_id"),
            "file_type": record.get("file_type"),
            "original_file": record.get("original_file"),
            "result_file": record.get("result_file"),
            "detections": record.get("detections"),
            "params": record.get("params"),
            "original_created_at": record.get("created_at"),
            "deleted_at": _utc_now_iso(),
            "deleted_by": deleted_by,
            "is_restored": False,
            "restored_at": None,
            "restored_by": None,
        }
        archives.append(archived_record)
        payload["history_records"] = history_records
        payload["history_archives"] = archives
        _write_payload(path, payload)
        return archived_record


def list_archived_detection_records(
    path: Path,
    *,
    user_id: str,
    include_restored: bool = False,
) -> list[dict[str, Any]]:
    with _LOCK:
        payload = _read_payload(path)
        archives = [
            record
            for record in payload.get("history_archives") or []
            if record.get("user_id") == user_id
            and (include_restored or not bool(record.get("is_restored")))
        ]
        return sorted(archives, key=lambda item: item.get("deleted_at", ""), reverse=True)


def restore_archived_detection_record(
    path: Path,
    *,
    user_id: str,
    archive_id: str,
    restore_by: str,
) -> dict[str, Any]:
    with _LOCK:
        payload = _read_payload(path)
        archives = list(payload.get("history_archives") or [])
        archived_record = next(
            (
                item
                for item in archives
                if item.get("archive_id") == archive_id and item.get("user_id") == user_id
            ),
            None,
        )
        if not archived_record:
            return {"status": "not_found", "item": None}
        if bool(archived_record.get("is_restored")):
            return {"status": "already_restored", "item": None}

        restored_record = {
            "id": archived_record.get("original_history_id"),
            "user_id": archived_record.get("user_id"),
            "file_type": archived_record.get("file_type"),
            "original_file": archived_record.get("original_file"),
            "result_file": archived_record.get("result_file"),
            "detections": archived_record.get("detections"),
            "params": archived_record.get("params"),
            "created_at": archived_record.get("original_created_at"),
        }
        history_records = list(payload.get("history_records") or [])
        history_records.append(restored_record)
        archived_record["is_restored"] = True
        archived_record["restored_at"] = _utc_now_iso()
        archived_record["restored_by"] = restore_by
        payload["history_records"] = history_records
        payload["history_archives"] = archives
        _write_payload(path, payload)
        return {"status": "ok", "item": restored_record}
