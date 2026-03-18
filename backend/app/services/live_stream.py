from __future__ import annotations

from urllib.parse import urlparse

import cv2
from fastapi import HTTPException, status

ALLOWED_NETWORK_STREAM_SCHEMES = {"rtsp", "http", "https"}


def normalize_live_source(raw: dict | None) -> dict:
    if not raw:
        return {"type": "camera"}

    source_type = str(raw.get("type") or "camera").strip().lower()
    if source_type != "network":
        return {"type": "camera"}

    stream_url = str(raw.get("url") or "").strip()
    parsed = urlparse(stream_url)

    if (
        not stream_url
        or parsed.scheme.lower() not in ALLOWED_NETWORK_STREAM_SCHEMES
        or not parsed.netloc
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无线流仅支持可访问的 RTSP 或 MJPEG/HTTP(S) 地址",
        )

    return {
        "type": "network",
        "url": stream_url,
    }


def open_network_capture_sync(stream_url: str):
    capture = cv2.VideoCapture(stream_url)
    if capture.isOpened():
        return capture

    capture.release()
    raise RuntimeError("无法连接无线视频流，请确认手机推流地址可访问")


def read_network_frame_sync(capture):
    ok, frame = capture.read()
    if not ok or frame is None:
        return None
    return frame
