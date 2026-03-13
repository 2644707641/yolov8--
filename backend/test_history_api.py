import importlib.util
import json
import logging
import sys
import time
import uuid
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

import jwt
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.services import local_cleanup
from app.services import detection as detection_service
from app.services import model_registry

logger = logging.getLogger("yolov8.test")

APP_PATH = BASE_DIR / "backend" / "main.py"
spec = importlib.util.spec_from_file_location("yolov8_backend", APP_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = module.app


def make_token(user_id: str, secret: str = "test-secret") -> str:
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + 3600,
        "aud": "authenticated",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@contextmanager
def temporary_jwt_secret(secret: str):
    original = settings.supabase_jwt_secret
    settings.supabase_jwt_secret = secret
    try:
        yield
    finally:
        settings.supabase_jwt_secret = original


@contextmanager
def temporary_supabase_client(client):
    original = getattr(app.state, "supabase", None)
    app.state.supabase = client
    try:
        yield
    finally:
        app.state.supabase = original


@contextmanager
def temporary_local_store_paths():
    original_history = getattr(settings, "local_history_store_file", None)
    original_settings = getattr(settings, "user_settings_store_file", None)
    original_upload_dir = settings.upload_dir
    original_result_dir = settings.result_dir
    original_model_dir = settings.model_dir
    with TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        upload_dir = base / "uploads"
        result_dir = base / "results"
        model_dir = base / "models"
        upload_dir.mkdir(parents=True, exist_ok=True)
        result_dir.mkdir(parents=True, exist_ok=True)
        model_dir.mkdir(parents=True, exist_ok=True)

        settings.local_history_store_file = base / "history.json"
        settings.user_settings_store_file = base / "settings.json"
        settings.upload_dir = upload_dir
        settings.result_dir = result_dir
        settings.model_dir = model_dir
        try:
            yield {
                "base": base,
                "upload_dir": upload_dir,
                "result_dir": result_dir,
                "model_dir": model_dir,
            }
        finally:
            settings.local_history_store_file = original_history
            settings.user_settings_store_file = original_settings
            settings.upload_dir = original_upload_dir
            settings.result_dir = original_result_dir
            settings.model_dir = original_model_dir


@contextmanager
def patched_run_detection(result_dir: Path):
    original = detection_service.run_detection

    async def fake_run_detection(**kwargs):
        result_path = result_dir / "result_test-user_1700000000.jpg"
        result_path.write_bytes(b"fake-result")
        detections = [{"class": "car", "confidence": 0.91, "bbox": [1, 2, 3, 4]}]
        return result_path, detections, 0.12, "检测完成"

    detection_service.run_detection = fake_run_detection
    try:
        yield
    finally:
        detection_service.run_detection = original


@contextmanager
def registered_model(user_id: str, model_path: Path):
    with TestClient(app) as client:
        client.portal.call(model_registry.registry.set_model, user_id, model_path)
        try:
            yield
        finally:
            client.portal.call(model_registry.registry.remove_model, user_id)


class FakeSupabaseResponse:
    def __init__(self, data):
        self.data = data


class FakeTableQuery:
    def __init__(self, client, table_name):
        self._client = client
        self._table_name = table_name
        self._action = "select"
        self._filters = []
        self._order_by = None
        self._ascending = True
        self._payload = None

    @property
    def _records(self):
        if self._table_name == "detection_history":
            return self._client.history_records
        if self._table_name == "detection_history_archive":
            return self._client.archive_records
        raise AssertionError(f"unexpected table: {self._table_name}")

    def select(self, *_args, **_kwargs):
        self._action = "select"
        return self

    def delete(self, *_args, **_kwargs):
        self._action = "delete"
        return self

    def insert(self, payload):
        self._action = "insert"
        self._payload = payload
        return self

    def update(self, payload):
        self._action = "update"
        self._payload = payload
        return self

    def eq(self, field, value):
        self._filters.append((field, value))
        return self

    def order(self, field, desc=False):
        self._order_by = field
        self._ascending = not desc
        return self

    def limit(self, _value):
        return self

    def execute(self):
        matched = [
            record for record in self._records
            if all(record.get(field) == value for field, value in self._filters)
        ]

        if self._action == "select":
            if self._order_by:
                matched = sorted(
                    matched,
                    key=lambda item: item.get(self._order_by),
                    reverse=not self._ascending,
                )
            return FakeSupabaseResponse(deepcopy(matched))

        if self._action == "delete":
            deleted_ids = {record["id"] for record in matched}
            deleted_archive_ids = {record["archive_id"] for record in matched if "archive_id" in record}
            self._records[:] = [
                record for record in self._records
                if record.get("id") not in deleted_ids and record.get("archive_id") not in deleted_archive_ids
            ]
            return FakeSupabaseResponse(deepcopy(matched))

        if self._action == "insert":
            payload = deepcopy(self._payload)
            if self._table_name == "detection_history_archive" and not payload.get("archive_id"):
                payload["archive_id"] = str(uuid.uuid4())
            self._records.append(payload)
            return FakeSupabaseResponse([deepcopy(payload)])

        if self._action == "update":
            for record in matched:
                record.update(deepcopy(self._payload))
            return FakeSupabaseResponse(deepcopy(matched))

        raise AssertionError(f"unsupported action: {self._action}")


class FakeSupabaseClient:
    def __init__(self, history_records, archive_records=None):
        self.history_records = history_records
        self.archive_records = archive_records if archive_records is not None else []

    def table(self, name):
        return FakeTableQuery(self, name)


def test_history_list_returns_only_current_user_records():
    history_records = [
        {
            "id": "history-1",
            "user_id": "user-a",
            "file_type": "image",
            "created_at": "2026-03-13T02:00:00Z",
        },
        {
            "id": "history-2",
            "user_id": "user-b",
            "file_type": "video",
            "created_at": "2026-03-13T03:00:00Z",
        },
        {
            "id": "history-3",
            "user_id": "user-a",
            "file_type": "video",
            "created_at": "2026-03-13T04:00:00Z",
        },
    ]
    headers = {"Authorization": f"Bearer {make_token('user-a')}"}

    with temporary_jwt_secret("test-secret"), temporary_supabase_client(FakeSupabaseClient(history_records)):
        client = TestClient(app)
        response = client.get("/api/history", headers=headers)

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True
    assert [item["id"] for item in payload["items"]] == ["history-3", "history-1"]


def test_history_delete_rejects_other_users_record():
    history_records = [
        {
            "id": "history-1",
            "user_id": "user-a",
            "file_type": "image",
            "created_at": "2026-03-13T02:00:00Z",
        },
        {
            "id": "history-2",
            "user_id": "user-b",
            "file_type": "video",
            "created_at": "2026-03-13T03:00:00Z",
        },
    ]
    archive_records = []
    headers = {"Authorization": f"Bearer {make_token('user-a')}"}

    with temporary_jwt_secret("test-secret"), temporary_supabase_client(FakeSupabaseClient(history_records, archive_records)):
        client = TestClient(app)
        response = client.delete("/api/history/history-2", headers=headers)

    assert response.status_code == 404, response.text
    assert [item["id"] for item in history_records] == ["history-1", "history-2"]
    assert archive_records == []


def test_history_delete_archives_owner_record_instead_of_hard_delete():
    history_records = [
        {
            "id": "history-1",
            "user_id": "user-a",
            "file_type": "image",
            "original_file": "https://example.com/original.jpg",
            "result_file": "https://example.com/result.jpg",
            "detections": [{"class": "car"}],
            "params": {"confidence": 0.5},
            "created_at": "2026-03-13T02:00:00Z",
        },
        {
            "id": "history-2",
            "user_id": "user-b",
            "file_type": "video",
            "created_at": "2026-03-13T03:00:00Z",
        },
    ]
    archive_records = []
    headers = {"Authorization": f"Bearer {make_token('user-a')}"}

    with temporary_jwt_secret("test-secret"), temporary_supabase_client(FakeSupabaseClient(history_records, archive_records)):
        client = TestClient(app)
        response = client.delete("/api/history/history-1", headers=headers)

    assert response.status_code == 200, response.text
    assert response.json()["success"] is True
    assert [item["id"] for item in history_records] == ["history-2"]
    assert len(archive_records) == 1
    assert archive_records[0]["original_history_id"] == "history-1"
    assert archive_records[0]["user_id"] == "user-a"
    assert archive_records[0]["is_restored"] is False


def test_deleted_history_list_returns_only_active_archives():
    archive_records = [
        {
            "archive_id": "archive-1",
            "original_history_id": "history-1",
            "user_id": "user-a",
            "file_type": "image",
            "deleted_at": "2026-03-13T05:00:00Z",
            "is_restored": False,
        },
        {
            "archive_id": "archive-2",
            "original_history_id": "history-2",
            "user_id": "user-a",
            "file_type": "video",
            "deleted_at": "2026-03-13T04:00:00Z",
            "is_restored": True,
        },
        {
            "archive_id": "archive-3",
            "original_history_id": "history-3",
            "user_id": "user-b",
            "file_type": "image",
            "deleted_at": "2026-03-13T06:00:00Z",
            "is_restored": False,
        },
    ]
    headers = {"Authorization": f"Bearer {make_token('user-a')}"}

    with temporary_jwt_secret("test-secret"), temporary_supabase_client(FakeSupabaseClient([], archive_records)):
        client = TestClient(app)
        response = client.get("/api/history/deleted", headers=headers)

    assert response.status_code == 200, response.text
    assert [item["archive_id"] for item in response.json()["items"]] == ["archive-1"]


def test_restore_deleted_history_moves_record_back_to_main_table():
    history_records = []
    archive_records = [
        {
            "archive_id": "archive-1",
            "original_history_id": "history-1",
            "user_id": "user-a",
            "file_type": "image",
            "original_file": "https://example.com/original.jpg",
            "result_file": "https://example.com/result.jpg",
            "detections": [{"class": "car"}],
            "params": {"confidence": 0.5},
            "original_created_at": "2026-03-13T02:00:00Z",
            "deleted_at": "2026-03-13T05:00:00Z",
            "deleted_by": "user-a",
            "is_restored": False,
            "restored_at": None,
            "restored_by": None,
        }
    ]
    headers = {"Authorization": f"Bearer {make_token('user-a')}"}

    with temporary_jwt_secret("test-secret"), temporary_supabase_client(FakeSupabaseClient(history_records, archive_records)):
        client = TestClient(app)
        response = client.post("/api/history/deleted/archive-1/restore", headers=headers)

    assert response.status_code == 200, response.text
    assert len(history_records) == 1
    assert history_records[0]["id"] == "history-1"
    assert history_records[0]["user_id"] == "user-a"
    assert archive_records[0]["is_restored"] is True
    assert archive_records[0]["restored_by"] == "user-a"


def test_detect_and_history_work_without_supabase_by_using_local_store():
    user_id = "test-user"
    headers = {"Authorization": f"Bearer {make_token(user_id)}"}
    image_bytes = b"\x89PNG\r\n\x1a\n"

    with (
        temporary_jwt_secret("test-secret"),
        temporary_supabase_client(None),
        temporary_local_store_paths() as paths,
    ):
        model_path = paths["model_dir"] / "demo.pt"
        model_path.write_bytes(b"fake-model")

        with registered_model(user_id, model_path), patched_run_detection(paths["result_dir"]):
            client = TestClient(app)
            detect_response = client.post(
                "/api/detect",
                headers=headers,
                files={"file": ("demo.png", image_bytes, "image/png")},
                data={
                    "type": "image",
                    "params": '{"imgSize":640,"confidence":0.5,"iouThreshold":0.6,"maxDetections":300,"frameSkip":1}',
                },
            )

            assert detect_response.status_code == 200, detect_response.text

            history_response = client.get("/api/history", headers=headers)

    assert history_response.status_code == 200, history_response.text
    payload = history_response.json()
    assert payload["success"] is True
    assert len(payload["items"]) == 1
    assert payload["items"][0]["file_type"] == "image"
    assert payload["items"][0]["detections"][0]["class"] == "car"


def test_local_cleanup_prunes_expired_records_and_unreferenced_files():
    with temporary_local_store_paths() as paths:
        payload = {
            "user_settings": {},
            "history_records": [
                {
                    "id": "history-new",
                    "user_id": "user-a",
                    "file_type": "image",
                    "original_file": "/api/uploads/upload_user-a_keep.png",
                    "result_file": "/api/results/result_user-a_keep.jpg",
                    "detections": [],
                    "params": {},
                    "created_at": "2026-03-12T12:00:00+00:00",
                },
                {
                    "id": "history-old",
                    "user_id": "user-a",
                    "file_type": "image",
                    "original_file": "/api/uploads/upload_user-a_old.png",
                    "result_file": "/api/results/result_user-a_old.jpg",
                    "detections": [],
                    "params": {},
                    "created_at": "2026-01-01T12:00:00+00:00",
                },
            ],
            "history_archives": [],
        }
        settings.local_history_store_file.write_text(
            json.dumps(payload, ensure_ascii=False),
            encoding="utf-8",
        )

        keep_upload = paths["upload_dir"] / "upload_user-a_keep.png"
        keep_upload.write_bytes(b"keep")
        old_upload = paths["upload_dir"] / "upload_user-a_old.png"
        old_upload.write_bytes(b"old")
        orphan_upload = paths["upload_dir"] / "upload_user-a_orphan.png"
        orphan_upload.write_bytes(b"orphan")

        keep_result = paths["result_dir"] / "result_user-a_keep.jpg"
        keep_result.write_bytes(b"keep")
        old_result = paths["result_dir"] / "result_user-a_old.jpg"
        old_result.write_bytes(b"old")
        orphan_result = paths["result_dir"] / "result_user-a_orphan.jpg"
        orphan_result.write_bytes(b"orphan")

        summary = local_cleanup.cleanup_local_storage(
            settings.local_history_store_file,
            upload_dir=settings.upload_dir,
            result_dir=settings.result_dir,
            retention_days=30,
            max_records=10,
            logger=logger,
            now="2026-03-13T12:00:00+00:00",
        )

        saved_payload = json.loads(
            settings.local_history_store_file.read_text(encoding="utf-8")
        )
        assert summary["removed_records"] == 1
        assert saved_payload["history_records"][0]["id"] == "history-new"
        assert keep_upload.exists()
        assert keep_result.exists()
        assert not old_upload.exists()
        assert not old_result.exists()
        assert not orphan_upload.exists()
        assert not orphan_result.exists()


def run():
    test_history_list_returns_only_current_user_records()
    test_history_delete_rejects_other_users_record()
    test_history_delete_archives_owner_record_instead_of_hard_delete()
    test_deleted_history_list_returns_only_active_archives()
    test_restore_deleted_history_moves_record_back_to_main_table()
    test_detect_and_history_work_without_supabase_by_using_local_store()
    test_local_cleanup_prunes_expired_records_and_unreferenced_files()


if __name__ == "__main__":
    run()
