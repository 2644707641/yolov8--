from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.common import run_local_cleanup_for_app
from app.api.routes import router
from app.core.config import (
    create_supabase_client,
    ensure_directories,
    settings,
)
from app.core.logging_config import setup_logging
from app.services import local_state

logger = setup_logging()
ensure_directories()

supabase_client = None
try:
    supabase_client = create_supabase_client()
    if supabase_client:
        logger.info("Supabase 客户端初始化成功")
    else:
        logger.warning("未配置 Supabase，相关功能将被禁用")
except Exception as exc:
    logger.warning("Supabase 客户端初始化失败: %s", exc)


@asynccontextmanager
async def lifespan(app):
    # 启动：创建共享 httpx 客户端
    app.state.http_client = httpx.AsyncClient(
        timeout=60.0,
        follow_redirects=True,
        http2=True,
    )
    logger.info("共享 HTTP 客户端初始化完成")

    # 启动时执行本地清理
    run_local_cleanup_for_app(app, logger=logger)
    logger.info("YOLOv8 Detection API 启动完成")

    yield

    # 关闭：释放 httpx 客户端
    await app.state.http_client.aclose()
    logger.info("共享 HTTP 客户端已关闭")


app = FastAPI(title=settings.api_title, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

app.state.supabase = supabase_client
app.state.app_settings = local_state.load_app_settings(settings.user_settings_store_file)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

