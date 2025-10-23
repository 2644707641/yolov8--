import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


@dataclass
class Settings:
    api_title: str = "YOLOv8 Detection API"
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))
    model_dir: Path = Path(os.getenv("MODEL_DIR", "models"))
    result_dir: Path = Path(os.getenv("RESULT_DIR", "results"))
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")
    supabase_bucket: str = os.getenv("SUPABASE_BUCKET", "detection-files")
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "200"))
    allowed_model_extensions: set[str] = field(
        default_factory=lambda: {".pt", ".pth"}
    )
    allowed_image_extensions: set[str] = field(
        default_factory=lambda: {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    )
    allowed_video_extensions: set[str] = field(
        default_factory=lambda: {".mp4", ".mov", ".avi", ".mkv"}
    )
    max_concurrent_detections: int = int(os.getenv("MAX_CONCURRENT_DETECTIONS", "2"))

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()


def ensure_directories() -> None:
    for directory in [settings.upload_dir, settings.model_dir, settings.result_dir]:
        directory.mkdir(parents=True, exist_ok=True)


def create_supabase_client() -> Optional[Client]:
    if not settings.supabase_url or not settings.supabase_key:
        return None

    return create_client(settings.supabase_url, settings.supabase_key)

