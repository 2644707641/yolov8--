import json
import time

import importlib.util
import jwt
from fastapi.testclient import TestClient
from pathlib import Path
from contextlib import contextmanager
from tempfile import TemporaryDirectory
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

APP_PATH = BASE_DIR / "backend" / "main.py"
spec = importlib.util.spec_from_file_location("yolov8_backend", APP_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = module.app

from app.core.config import settings


def make_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + 3600,
        "aud": "authenticated",
    }
    return jwt.encode(payload, "test-secret", algorithm="HS256")


@contextmanager
def temporary_jwt_secret(secret: str):
    original = settings.supabase_jwt_secret
    settings.supabase_jwt_secret = secret
    try:
        yield
    finally:
        settings.supabase_jwt_secret = original


@contextmanager
def temporary_settings_store_file():
    original_path = getattr(settings, "user_settings_store_file", None)
    original_history_path = getattr(settings, "local_history_store_file", None)
    original_upload_dir = settings.upload_dir
    original_result_dir = settings.result_dir
    original_user_settings = getattr(app.state, "user_settings", None)
    original_app_settings = getattr(app.state, "app_settings", None)
    with TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        upload_dir = base / "uploads"
        result_dir = base / "results"
        upload_dir.mkdir(parents=True, exist_ok=True)
        result_dir.mkdir(parents=True, exist_ok=True)
        settings.user_settings_store_file = base / "user-settings.json"
        settings.local_history_store_file = base / "history.json"
        settings.upload_dir = upload_dir
        settings.result_dir = result_dir
        if hasattr(app.state, "user_settings"):
            delattr(app.state, "user_settings")
        if hasattr(app.state, "app_settings"):
            delattr(app.state, "app_settings")
        try:
            yield {
                "settings_store_file": settings.user_settings_store_file,
                "history_store_file": settings.local_history_store_file,
                "upload_dir": upload_dir,
                "result_dir": result_dir,
            }
        finally:
            settings.user_settings_store_file = original_path
            settings.local_history_store_file = original_history_path
            settings.upload_dir = original_upload_dir
            settings.result_dir = original_result_dir
            if original_user_settings is not None:
                app.state.user_settings = original_user_settings
            elif hasattr(app.state, "user_settings"):
                delattr(app.state, "user_settings")
            if original_app_settings is not None:
                app.state.app_settings = original_app_settings
            elif hasattr(app.state, "app_settings"):
                delattr(app.state, "app_settings")


@contextmanager
def temporary_supabase_client(client):
    original = getattr(app.state, "supabase", None)
    app.state.supabase = client
    try:
        yield
    finally:
        app.state.supabase = original


def run():
    client = TestClient(app)
    token = make_token("test-user")
    headers = {"Authorization": f"Bearer {token}"}

    with (
        temporary_jwt_secret("test-secret"),
        temporary_settings_store_file() as paths,
        temporary_supabase_client(None),
    ):
        from datetime import datetime, timedelta, timezone

        now_utc = datetime.now(timezone.utc)
        recent_date = (now_utc - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        older_date = (now_utc - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        archive_date = (now_utc - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S+00:00")

        payload = {
            "app_settings": {},
            "user_settings": {},
            "history_records": [
                {
                    "id": "history-new",
                    "user_id": "test-user",
                    "file_type": "image",
                    "original_file": "/api/uploads/upload_test-user_keep.png",
                    "result_file": "/api/results/result_test-user_keep.jpg",
                    "detections": [],
                    "params": {},
                    "created_at": recent_date,
                },
                {
                    "id": "history-old",
                    "user_id": "test-user",
                    "file_type": "image",
                    "original_file": "/api/uploads/upload_test-user_old.png",
                    "result_file": "/api/results/result_test-user_old.jpg",
                    "detections": [],
                    "params": {},
                    "created_at": older_date,
                },
            ],
            "history_archives": [
                {
                    "archive_id": "archive-1",
                    "original_history_id": "history-archive",
                    "user_id": "test-user",
                    "file_type": "image",
                    "original_file": "https://example.com/original.jpg",
                    "result_file": "https://example.com/result.jpg",
                    "detections": [],
                    "params": {},
                    "deleted_at": archive_date,
                    "is_restored": False,
                }
            ],
        }
        paths["history_store_file"].write_text(
            json.dumps(payload, ensure_ascii=False),
            encoding="utf-8",
        )
        (paths["upload_dir"] / "upload_test-user_keep.png").write_bytes(b"keep")
        (paths["upload_dir"] / "upload_test-user_old.png").write_bytes(b"old")
        (paths["upload_dir"] / "upload_test-user_orphan.png").write_bytes(b"orphan")
        (paths["result_dir"] / "result_test-user_keep.jpg").write_bytes(b"keep-result")
        (paths["result_dir"] / "result_test-user_old.jpg").write_bytes(b"old-result")
        (paths["result_dir"] / "result_test-user_orphan.jpg").write_bytes(b"orphan-result")

        # GET should return defaults
        response = client.get("/api/settings", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["success"] is True
        defaults = data["settings"]["defaults"]
        assert "confidence" in defaults
        assert "imgSize" in defaults
        storage = data["settings"]["storage"]
        assert storage["mode"] == "local"
        assert storage["localCleanup"]["enabled"] == settings.local_history_cleanup_enabled
        assert storage["localCleanup"]["retentionDays"] == settings.local_history_retention_days
        assert storage["localCleanup"]["maxRecords"] == settings.local_history_max_records
        assert storage["localStats"]["historyRecordCount"] == 2
        assert storage["localStats"]["archiveRecordCount"] == 1
        assert storage["localStats"]["uploadsFileCount"] == 3
        assert storage["localStats"]["resultsFileCount"] == 3
        assert storage["localStats"]["lastCleanupAt"] is None

        # PUT updates defaults
        update_payload = {
            "defaults": {
                "confidence": 0.66,
                "imgSize": 512,
                "iouThreshold": 0.5,
                "maxDetections": 120,
                "frameSkip": 2,
            },
            "storage": {
                "localCleanup": {
                    "enabled": False,
                    "retentionDays": 14,
                    "maxRecords": 1,
                }
            },
        }
        update_response = client.put("/api/settings", headers=headers, json=update_payload)
        assert update_response.status_code == 200, update_response.text
        update_payload = update_response.json()["settings"]
        updated = update_payload["defaults"]
        assert updated["confidence"] == 0.66
        assert updated["imgSize"] == 512
        assert update_payload["storage"]["mode"] == "local"
        assert update_payload["storage"]["localCleanup"]["enabled"] is False
        assert update_payload["storage"]["localCleanup"]["retentionDays"] == 14
        assert update_payload["storage"]["localCleanup"]["maxRecords"] == 1

        # GET returns updated values
        response = client.get("/api/settings", headers=headers)
        assert response.status_code == 200, response.text
        current_settings = response.json()["settings"]
        defaults = current_settings["defaults"]
        assert defaults["confidence"] == 0.66
        assert defaults["imgSize"] == 512
        assert current_settings["storage"]["localCleanup"]["enabled"] is False
        assert current_settings["storage"]["localCleanup"]["retentionDays"] == 14
        assert current_settings["storage"]["localCleanup"]["maxRecords"] == 1

        cleanup_response = client.post("/api/settings/storage/cleanup", headers=headers)
        assert cleanup_response.status_code == 200, cleanup_response.text
        cleanup_payload = cleanup_response.json()
        assert cleanup_payload["success"] is True
        assert cleanup_payload["cleanup"]["removedRecords"] == 1
        assert cleanup_payload["cleanup"]["removedFiles"] == 4
        assert cleanup_payload["settings"]["storage"]["localStats"]["historyRecordCount"] == 1
        assert cleanup_payload["settings"]["storage"]["localStats"]["uploadsFileCount"] == 1
        assert cleanup_payload["settings"]["storage"]["localStats"]["resultsFileCount"] == 1
        assert cleanup_payload["settings"]["storage"]["localStats"]["lastCleanupAt"]

        # 内存状态丢失后仍然应能从持久化存储恢复
        if hasattr(app.state, "user_settings"):
            delattr(app.state, "user_settings")
        if hasattr(app.state, "app_settings"):
            delattr(app.state, "app_settings")

        restored_response = client.get("/api/settings", headers=headers)
        assert restored_response.status_code == 200, restored_response.text
        restored_settings = restored_response.json()["settings"]
        restored_defaults = restored_settings["defaults"]
        assert restored_defaults["confidence"] == 0.66
        assert restored_defaults["imgSize"] == 512
        assert restored_settings["storage"]["localCleanup"]["enabled"] is False
        assert restored_settings["storage"]["localCleanup"]["retentionDays"] == 14
        assert restored_settings["storage"]["localCleanup"]["maxRecords"] == 1
        assert restored_settings["storage"]["localStats"]["historyRecordCount"] == 1
        assert restored_settings["storage"]["localStats"]["uploadsFileCount"] == 1
        assert restored_settings["storage"]["localStats"]["resultsFileCount"] == 1
        assert restored_settings["storage"]["localStats"]["lastCleanupAt"]


if __name__ == "__main__":
    run()
