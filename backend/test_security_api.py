import importlib.util
import sys
import time
from contextlib import contextmanager
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
from app.services import model_registry

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
def temporary_jwt_secret(secret):
    original = settings.supabase_jwt_secret
    settings.supabase_jwt_secret = secret
    try:
        yield
    finally:
        settings.supabase_jwt_secret = original


@contextmanager
def temporary_storage_dirs():
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

        settings.upload_dir = upload_dir
        settings.result_dir = result_dir
        settings.model_dir = model_dir
        try:
            yield {
                "upload_dir": upload_dir,
                "result_dir": result_dir,
                "model_dir": model_dir,
            }
        finally:
            settings.upload_dir = original_upload_dir
            settings.result_dir = original_result_dir
            settings.model_dir = original_model_dir


def test_protected_endpoint_rejects_requests_without_jwt_secret():
    client = TestClient(app)
    token = make_token("missing-secret-user", secret="arbitrary-secret")

    with temporary_jwt_secret(None):
        response = client.get(
            "/api/settings",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 503, response.text
    assert response.json()["detail"] == "服务端未配置 JWT 验证密钥"


def test_cleanup_requires_authorization_and_keeps_files_untouched():
    client = TestClient(app)
    user_id = "cleanup-target"

    with temporary_storage_dirs() as dirs, temporary_jwt_secret("test-secret"):
        upload_file = dirs["upload_dir"] / f"{user_id}_sample.jpg"
        result_file = dirs["result_dir"] / f"{user_id}_result.jpg"
        model_file = dirs["model_dir"] / f"{user_id}_model.pt"
        upload_file.write_text("upload", encoding="utf-8")
        result_file.write_text("result", encoding="utf-8")
        model_file.write_text("model", encoding="utf-8")

        with TestClient(app) as inner_client:
            inner_client.portal.call(model_registry.registry.set_model, user_id, model_file)

            response = inner_client.delete(f"/api/cleanup/{user_id}")
            remaining_model = inner_client.portal.call(
                model_registry.registry.get_model,
                user_id,
            )

        assert response.status_code == 401, response.text
        assert upload_file.exists()
        assert result_file.exists()
        assert remaining_model == model_file


def test_cleanup_rejects_cross_user_access():
    client = TestClient(app)
    owner_id = "owner-user"
    intruder_id = "intruder-user"

    with temporary_storage_dirs() as dirs, temporary_jwt_secret("test-secret"):
        victim_upload = dirs["upload_dir"] / f"{owner_id}_sample.jpg"
        victim_result = dirs["result_dir"] / f"{owner_id}_result.jpg"
        victim_model = dirs["model_dir"] / f"{owner_id}_model.pt"
        victim_upload.write_text("upload", encoding="utf-8")
        victim_result.write_text("result", encoding="utf-8")
        victim_model.write_text("model", encoding="utf-8")

        headers = {"Authorization": f"Bearer {make_token(intruder_id)}"}

        with TestClient(app) as inner_client:
            inner_client.portal.call(model_registry.registry.set_model, owner_id, victim_model)

            response = inner_client.delete(f"/api/cleanup/{owner_id}", headers=headers)
            remaining_model = inner_client.portal.call(
                model_registry.registry.get_model,
                owner_id,
            )

        assert response.status_code == 403, response.text
        assert victim_upload.exists()
        assert victim_result.exists()
        assert remaining_model == victim_model


def test_cleanup_allows_owner_to_remove_own_files():
    owner_id = "cleanup-owner"

    with temporary_storage_dirs() as dirs, temporary_jwt_secret("test-secret"):
        upload_file = dirs["upload_dir"] / f"{owner_id}_sample.jpg"
        result_file = dirs["result_dir"] / f"{owner_id}_result.jpg"
        model_file = dirs["model_dir"] / f"{owner_id}_model.pt"
        upload_file.write_text("upload", encoding="utf-8")
        result_file.write_text("result", encoding="utf-8")
        model_file.write_text("model", encoding="utf-8")
        headers = {"Authorization": f"Bearer {make_token(owner_id)}"}

        with TestClient(app) as inner_client:
            inner_client.portal.call(model_registry.registry.set_model, owner_id, model_file)

            response = inner_client.delete(f"/api/cleanup/{owner_id}", headers=headers)
            remaining_model = inner_client.portal.call(
                model_registry.registry.get_model,
                owner_id,
            )

        assert response.status_code == 200, response.text
        assert not upload_file.exists()
        assert not result_file.exists()
        assert remaining_model is None


def test_result_download_requires_authorization():
    owner_id = "result-owner"
    filename = f"result_{owner_id}_{int(time.time())}.jpg"

    with temporary_storage_dirs() as dirs:
        result_file = dirs["result_dir"] / filename
        result_file.write_text("result", encoding="utf-8")

        client = TestClient(app)
        response = client.get(f"/api/results/{filename}")

        assert response.status_code == 401, response.text


def test_result_download_rejects_cross_user_access():
    owner_id = "result-owner"
    intruder_id = "result-intruder"
    filename = f"result_{owner_id}_{int(time.time())}.jpg"

    with temporary_storage_dirs() as dirs, temporary_jwt_secret("test-secret"):
        result_file = dirs["result_dir"] / filename
        result_file.write_text("secret-result", encoding="utf-8")
        headers = {"Authorization": f"Bearer {make_token(intruder_id)}"}

        client = TestClient(app)
        response = client.get(f"/api/results/{filename}", headers=headers)

        assert response.status_code == 403, response.text


def test_result_download_allows_owner_via_query_token():
    owner_id = "result-owner"
    filename = f"result_{owner_id}_{int(time.time())}.jpg"

    with temporary_storage_dirs() as dirs, temporary_jwt_secret("test-secret"):
        result_file = dirs["result_dir"] / filename
        result_file.write_text("secret-result", encoding="utf-8")
        token = make_token(owner_id)

        client = TestClient(app)
        response = client.get(f"/api/results/{filename}?token={token}")

        assert response.status_code == 200, response.text
        assert response.content == b"secret-result"


def run():
    test_protected_endpoint_rejects_requests_without_jwt_secret()
    test_cleanup_requires_authorization_and_keeps_files_untouched()
    test_cleanup_rejects_cross_user_access()
    test_cleanup_allows_owner_to_remove_own_files()
    test_result_download_requires_authorization()
    test_result_download_rejects_cross_user_access()
    test_result_download_allows_owner_via_query_token()


if __name__ == "__main__":
    run()
