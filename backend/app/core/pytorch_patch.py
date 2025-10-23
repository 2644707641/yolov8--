import logging
import os
from functools import lru_cache

import torch

logger = logging.getLogger("yolov8.pytorch")


@lru_cache(maxsize=1)
def ensure_torch_patch() -> None:
    """
    确保在导入Ultralytics前应用兼容性补丁。
    """
    logger.info("初始化 PyTorch 兼容性补丁")
    os.environ.setdefault("TORCH_FORCE_WEIGHTS_ONLY_LOAD", "0")

    original_load = torch.load

    def _patched_torch_load(*args, **kwargs):
        kwargs["weights_only"] = False
        return original_load(*args, **kwargs)

    torch.load = _patched_torch_load  # type: ignore[assignment]
    logger.info("已应用 torch.load weights_only=False 补丁")

    try:
        import ultralytics.nn.tasks  # noqa: F401

        torch.serialization.add_safe_globals([ultralytics.nn.tasks.DetectionModel])  # type: ignore[attr-defined]
        logger.info("已将 Ultralytics DetectionModel 加入 PyTorch 安全列表")
    except Exception as exc:
        logger.warning("添加 Ultralytics 安全列表失败: %s", exc)

