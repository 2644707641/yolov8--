import logging
import os


def setup_logging() -> logging.Logger:
    """
    配置全局日志，默认输出到标准输出。
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("yolov8")

