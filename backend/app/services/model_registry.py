from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict, Optional


class ModelRegistry:
    """
    管理用户上传的模型文件路径。
    """

    def __init__(self) -> None:
        self._models: Dict[str, Path] = {}
        self._lock = asyncio.Lock()

    async def set_model(self, user_id: str, path: Path) -> None:
        async with self._lock:
            self._models[user_id] = path

    async def get_model(self, user_id: str) -> Optional[Path]:
        async with self._lock:
            return self._models.get(user_id)

    async def remove_model(self, user_id: str) -> Optional[Path]:
        async with self._lock:
            return self._models.pop(user_id, None)

    async def list_users(self) -> Dict[str, Path]:
        async with self._lock:
            return dict(self._models)


registry = ModelRegistry()

