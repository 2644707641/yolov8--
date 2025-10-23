from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import (
    create_supabase_client,
    ensure_directories,
    settings,
)
from app.core.logging_config import setup_logging

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

app = FastAPI(title=settings.api_title)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

app.state.supabase = supabase_client


@app.on_event("startup")
async def log_startup() -> None:
    logger.info("YOLOv8 Detection API 启动完成")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

