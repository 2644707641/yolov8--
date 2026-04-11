# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YOLOv8 停车位检测应用 — 一个前后端分离的停车位检测平台。后端用 FastAPI + YOLOv8 做推理，前端用 Vue 3 做交互界面。支持图片/视频批量检测和实时摄像头/无线视频流监控。

## Commands

**后端：**
```bash
cd backend && uvicorn main:app --reload --port 8000
```
- 必须从 `backend/` 目录启动，代码使用相对路径
- Python 虚拟环境在 `backend/.venv/` 或项目根 `.venv/`
- 单个测试：`cd backend && python -m pytest test_auth.py -v --timeout=60`
- 全部测试：`cd backend && python -m pytest test_*.py -v --timeout=60`

**前端：**
```bash
cd frontend && pnpm dev          # 开发服务器
cd frontend && pnpm build        # 构建
cd frontend && pnpm test         # Vitest 单次运行
cd frontend && pnpm test:watch   # Vitest 监听模式
```

**一键启动（Windows）：** 双击 `运行项目.bat`，自动检测端口并启动前后端。

## Architecture

### 双模式运行机制

应用根据环境变量自动选择运行模式：

- **Supabase 云模式**：配置了 `SUPABASE_URL` + `SUPABASE_KEY` 时激活。文件存储、用户认证、模型权重管理走 Supabase。
- **本地 JSON 模式**：未配置 Supabase 时自动降级。历史记录和设置存储在 `backend/runtime/` 下的 JSON 文件中，认证依赖 JWT 本地校验。

这个决策贯穿整个后端，几乎所有 service 都有 `if supabase_client` 的分支逻辑。

### 后端结构 (`backend/`)

- `main.py` — FastAPI 入口，初始化 Supabase 客户端、加载本地设置、注册路由
- `app/core/config.py` — `Settings` dataclass，所有配置项的唯一定义处；`BASE_DIR` 指向项目根目录
- `app/core/pytorch_patch.py` — PyTorch 兼容性补丁，**必须在 import ultralytics 之前执行**（`ensure_torch_patch()` 在 `detection.py` 顶层调用）
- `app/api/routes.py` — 路由聚合，将 6 个子路由模块挂载到主 router
- `app/api/common.py` — 共享工具：认证解析、模型路径解析、本地存储策略构建、清理设置管理
- `app/services/detection.py` — 核心：YOLOv8 推理引擎，asyncio.Semaphore 控制并发（默认 2），支持 SSE 进度回调
- `app/services/live_stream.py` — 实时视频流：RTSP/MJPEG 连接与帧读取
- `app/services/local_state.py` — 本地 JSON 状态读写，线程安全（threading.Lock）
- `app/services/storage.py` — Supabase 文件上传/下载的统一封装
- `app/services/model_registry.py` — 内存中的用户→模型路径映射（asyncio.Lock）
- `app/services/model_weights.py` — Supabase 模型权重 CRUD 与缓存下载
- `app/services/auth.py` — JWT 校验（PyJWT），使用 Supabase JWT Secret
- `app/services/local_cleanup.py` — 本地历史记录过期清理

### 前端结构 (`frontend/`)

- `src/stores/auth.js` — Pinia store：Supabase 认证，含中文错误消息翻译
- `src/stores/detection.js` — Pinia store：检测参数、模型上传、SSE 流式检测、历史记录缓存（60s TTL）
- `src/config/supabase.js` — Supabase 客户端初始化，**启动时必须有 `VITE_SUPABASE_URL` 和 `VITE_SUPABASE_ANON_KEY`**
- `src/utils/protected-url.js` — 给后端 API URL 附加 token 参数用于鉴权
- `src/router/index.js` — 路由守卫，未认证用户重定向到 `/login`
- `src/layouts/AppShell.vue` — 需认证页面的公共布局壳

前端 `.env` 文件放在**项目根目录**（非 frontend/），`vite.config.js` 通过 `envDir: '..'` 读取。

### API 端点概览

| 路径 | 方法 | 用途 |
|------|------|------|
| `/api/upload-model` | POST | 上传模型权重 |
| `/api/detect` | POST | 批量检测（SSE 流式进度） |
| `/ws/detect-live` | WebSocket | 实时视频流检测 |
| `/api/history` | GET | 获取检测历史 |
| `/api/history/{id}` | DELETE | 删除/归档历史记录 |
| `/api/history/archive/{id}/restore` | POST | 恢复归档记录 |
| `/api/settings` | GET/PUT | 读取/更新用户设置 |
| `/api/system/status` | GET | 系统健康状态 |
| `/api/model-weights` | GET/POST | 模型权重列表/上传 |
| `/api/files/{path}` | GET | 受保护的文件访问（需 token 参数） |

### 数据流

1. 前端通过 Supabase JS SDK 完成登录，获取 JWT
2. 前端请求后端时在 `Authorization: Bearer <token>` 传入 JWT
3. 后端用 PyJWT + Supabase JWT Secret 校验，提取 `user_id`
4. 模型路径解析优先级：**Supabase 激活权重** → **本地注册权重** → **默认权重**
5. 检测结果：Supabase 模式存到 Storage bucket；本地模式存到 `backend/results/`

## Key Conventions

- 后端所有相对路径基于 `backend/` 工作目录（`BASE_DIR = Path(__file__).resolve().parents[3]` 指向项目根）
- 检测并发由 `MAX_CONCURRENT_DETECTIONS` 环境变量控制，默认 2
- 视频处理自动尝试 ByteTrack 跟踪，失败后静默降级到逐帧检测
- 视频编码优先 mp4v（Windows 兼容性），最终可选 ffmpeg 转码为 H264
- 前端检测进度通过 SSE（Server-Sent Events）推送，非 WebSocket
- 实时监控用 WebSocket（`/ws/detect-live`）
- 标注颜色：空车位=绿色，占用车位=红色（由 `_EMPTY_KEYWORDS` 关键词匹配决定）
- EditorConfig：JS/Vue 缩进 2 空格，Python 缩进 4 空格

## Environment Variables

后端 `.env` 放在项目根目录，`config.py` 通过 `load_dotenv(BASE_DIR / ".env")` 加载。关键变量见 `.env.example`。前端环境变量同理，Vite 从根目录读取（`VITE_` 前缀）。
