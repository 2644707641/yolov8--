from __future__ import annotations

import logging
import threading
from typing import Any, Dict

import psutil

logger = logging.getLogger("yolov8.system")

_detection_stats_lock = threading.Lock()
_detection_stats: Dict[str, Any] = {
    "total_tasks": 0,
    "failed_tasks": 0,
    "queue_backlog": 0,
    "active_tasks": 0,
}


def get_system_status() -> Dict[str, Any]:
    """
    获取系统健康状态，包括：
    - gpu_utilization: GPU 利用率 (%)
    - memory_used: 内存占用 (GB)
    - memory_percent: 内存占用百分比
    - queue_backlog: 队列积压数
    - error_rate: 错误率 (%)
    """
    memory = psutil.virtual_memory()
    memory_used_gb = memory.used / (1024**3)
    memory_percent = memory.percent

    gpu_info = _get_gpu_info()

    with _detection_stats_lock:
        total = _detection_stats["total_tasks"]
        failed = _detection_stats["failed_tasks"]
        active = _detection_stats["active_tasks"]
        error_rate = (failed / total * 100) if total > 0 else 0.0

    queue_backlog = max(0, active - 2)

    return {
        "gpu_utilization": gpu_info["utilization"],
        "gpu_memory": gpu_info["memory_used"],
        "memory_used": round(memory_used_gb, 1),
        "memory_percent": round(memory_percent, 1),
        "queue_backlog": queue_backlog,
        "error_rate": round(error_rate, 1),
    }


def _get_gpu_info() -> Dict[str, Any]:
    """
    获取 GPU 信息。优先使用 torch 提供的 GPU 信息，
    如果没有 GPU 或出错则返回 0。
    """
    try:
        import torch

        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            if device_count > 0:
                utilization = 0
                memory_used = 0
                try:
                    import pynvml

                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    utilization = util.gpu
                    memory_used = mem_info.used / (1024**3)
                    pynvml.nvmlShutdown()
                except Exception:
                    memory_used = torch.cuda.memory_allocated() / (1024**3)
                return {
                    "utilization": utilization,
                    "memory_used": round(memory_used, 1),
                }
    except Exception as e:
        logger.debug("获取 GPU 信息失败: %s", e)

    return {
        "utilization": 0,
        "memory_used": 0,
    }


def record_detection_task(success: bool) -> None:
    """记录检测任务结果，用于计算错误率。"""
    with _detection_stats_lock:
        _detection_stats["total_tasks"] += 1
        if not success:
            _detection_stats["failed_tasks"] += 1


def update_queue_backlog(count: int) -> None:
    """更新队列积压数量。"""
    with _detection_stats_lock:
        _detection_stats["queue_backlog"] = count


def increment_active_tasks() -> None:
    """增加活跃任务计数。"""
    with _detection_stats_lock:
        _detection_stats["active_tasks"] += 1


def decrement_active_tasks() -> None:
    """减少活跃任务计数。"""
    with _detection_stats_lock:
        _detection_stats["active_tasks"] = max(0, _detection_stats["active_tasks"] - 1)
