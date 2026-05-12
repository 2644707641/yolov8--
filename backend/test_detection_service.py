import logging
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from app.services import detection as detection_service

logger = logging.getLogger("yolov8.test")


class FakeVideoWriter:
    def __init__(self, codec_code):
        self.codec_code = codec_code

    def isOpened(self):
        return True

    def release(self):
        return None


@contextmanager
def patched_video_writer_environment(platform_name: str):
    original_platform = detection_service.sys.platform
    original_fourcc = detection_service.cv2.VideoWriter_fourcc
    original_writer = detection_service.cv2.VideoWriter

    def fake_fourcc(*chars):
        return "".join(chars)

    def fake_writer(_path, codec_code, _fps, _size):
        return FakeVideoWriter(codec_code)

    detection_service.sys.platform = platform_name
    detection_service.cv2.VideoWriter_fourcc = fake_fourcc
    detection_service.cv2.VideoWriter = fake_writer
    try:
        yield
    finally:
        detection_service.sys.platform = original_platform
        detection_service.cv2.VideoWriter_fourcc = original_fourcc
        detection_service.cv2.VideoWriter = original_writer


def test_create_video_writer_prefers_mp4v_on_windows():
    with patched_video_writer_environment("win32"):
        writer, codec_name = detection_service.create_video_writer_sync(
            result_path=Path("demo.mp4"),
            fps=12.0,
            width=1280,
            height=720,
            logger=logger,
        )

    assert writer is not None
    assert writer.codec_code == "mp4v"
    assert codec_name == "MPEG-4"


class FakeBoxes:
    id = None

    def __len__(self):
        return 0

    def __iter__(self):
        return iter(())


class FakeResult:
    def __init__(self, frame: np.ndarray):
        self.orig_img = frame
        self._frame = frame
        self.boxes = FakeBoxes()
        self.names = {}

    def plot(self):
        return self._frame


class FakeRealtimeModel:
    def __init__(self):
        self.last_source = None
        self._codex_tracking_enabled = False

    def predict(self, *, source, **_kwargs):
        if not source.flags.c_contiguous:
            raise RuntimeError(
                "view size is not compatible with input tensor's size and stride"
            )
        self.last_source = source
        return [FakeResult(source)]


@contextmanager
def patched_imdecode(frame: np.ndarray):
    original_imdecode = detection_service.cv2.imdecode
    detection_service.cv2.imdecode = lambda *_args, **_kwargs: frame
    try:
        yield
    finally:
        detection_service.cv2.imdecode = original_imdecode


def test_infer_live_frame_makes_decoded_frame_contiguous():
    model = FakeRealtimeModel()
    contiguous = np.arange(4 * 4 * 3, dtype=np.uint8).reshape(4, 4, 3)
    non_contiguous = contiguous[:, ::2, :]
    assert non_contiguous.flags.c_contiguous is False

    with patched_imdecode(non_contiguous):
        annotated, detections, elapsed = detection_service.infer_live_frame_sync(
            model=model,
            frame_bytes=b"fake-jpeg",
            detection_params={
                "imgsz": 640,
                "confidence": 0.25,
                "iou": 0.45,
                "max_det": 300,
            },
        )

    assert model.last_source is not None
    assert model.last_source.flags.c_contiguous is True
    assert annotated.flags.c_contiguous is True
    assert detections == []
    assert elapsed >= 0
