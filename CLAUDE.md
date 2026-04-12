# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YOLOv8 停车位检测应用 — 双端架构：FastAPI 后端负责 YOLOv8 推理与数据持久化，Vue 3 前端负责交互与展示。支持 Supabase 云模式（有 SUPABASE_URL/KEY）和本地 JSON 文件模式（无 Supabase 环境变量时自动降级）。

## Development Commands

**后端（必须在 `backend/` 目录下执行，所有相对路径依赖此工作目录）：**
```bash
cd backend
.\.venv\Scripts\python -m uvicorn main:app --reload --port 8000   # 启动
.\.venv\Scripts\python -m pytest test_*.py -v --timeout=60         # 测试
.\.venv\Scripts\python -m pytest test_auth.py -v --timeout=60      # 单个测试
```

**前端：**
```bash
cd frontend
pnpm install        # 安装依赖
pnpm dev            # 启动 (port 3000, proxy /api → localhost:8000)
pnpm build          # 构建
pnpm test           # Vitest 一次性运行
pnpm test:watch     # Vitest watch 模式
```

**一键启动（Windows）：** 运行根目录 `运行项目.bat`，同时启动前后端。

## Architecture

### 双模式运行机制

后端 `config.py` 检查 `SUPABASE_URL` + `SUPABASE_KEY` 是否存在：
- **云模式**：认证走 Supabase Auth + JWT 验证，文件存 Supabase Storage，历史记录存 Supabase 表
- **本地模式**：认证跳过（无需 JWT），文件存本地 `uploads/` + `results/`，历史记录存 `runtime/history.json`，用户设置存 `runtime/user-settings.json`

前端在 `supabase.js` 初始化时**硬性要求** `VITE_SUPABASE_URL` 和 `VITE_SUPABASE_ANON_KEY`，所以本地模式仍需配置 Supabase 前端变量（仅用于 Auth 登录流程），后端可无 Supabase。

### 后端关键数据流

```
Request → auth.py (JWT 校验) → routes.py → detection.py (推理) → storage.py (云) / local_state.py (本地)
```

- **模型权重解析优先级**（`common.py:resolve_model_path`）：Supabase 激活权重 > 本地注册权重 > 默认权重
- **推理并发**：`detection.py` 用 `asyncio.Semaphore(MAX_CONCURRENT_DETECTIONS)` 控制，默认 2
- **模型 LRU 缓存**：`detection.py` 中 `OrderedDict` 缓存最多 4 个 YOLO 实例，上传新模型时调用 `invalidate_model_cache()` 清除
- **PyTorch 兼容补丁**：`pytorch_patch.py` 在导入 ultralytics 前应用，修补 `torch.load` 的 `weights_only` 问题和非连续权重张量融合
- **实时检测**：WebSocket `/ws/detect-live`，客户端发送帧字节或网络流 URL，服务端返回标注帧（4 字节头 + JSON meta + JPEG 二进制）
- **视频编码**：Windows 优先 `mp4v` 编码器，最终可选 ffmpeg 转 H264

### 前端关键设计

- **Vite 代理**：`vite.config.js` 将 `/api` 代理到 `localhost:8000`，`envDir: '..'` 读取根目录 `.env`
- **认证流程**：`stores/auth.js` 使用 Supabase Auth SDK，路由守卫在 `router/index.js` 中检查 `requiresAuth` / `requiresGuest` meta
- **检测流程**：`stores/detection.js` 通过 `fetch` + SSE 流式接收进度，最终结果支持 JSON 和 SSE 两种协议
- **受保护的 API URL**：`utils/protected-url.js` 为同源 API 路径附加 `?token=` 查询参数，用于图片/视频结果展示
- **路由结构**：所有业务页面在 `AppShell` 布局下（需认证），`/login` 为独立页面

### API 路由模块

| 路由模块 | 路径前缀 | 功能 |
|---------|---------|------|
| `detection_routes.py` | `/api/detect`, `/api/upload-model`, `/ws/detect-live` | 图片/视频检测、模型上传、实时 WebSocket |
| `history_routes.py` | `/api/history` | 历史记录 CRUD、归档、恢复 |
| `settings_routes.py` | `/api/settings` | 用户设置、实时偏好、本地清理策略 |
| `model_weight_routes.py` | `/api/model-weights` | Supabase 模型权重管理 |
| `files_routes.py` | `/api/results`, `/api/uploads` | 静态文件服务（带 token 鉴权） |
| `system_routes.py` | `/api/system` | 系统信息、健康检查 |

## Environment Variables

根目录 `.env` 同时被前后端使用（后端 `config.py` 加载 `BASE_DIR/.env`，前端 Vite 读取 `VITE_` 前缀变量）：

```bash
# 前端
VITE_SUPABASE_URL=       # 必填
VITE_SUPABASE_ANON_KEY=  # 必填
VITE_API_URL=http://localhost:8000

# 后端
SUPABASE_URL=            # 可选，无则本地模式
SUPABASE_KEY=            # 可选，service_role key
SUPABASE_JWT_SECRET=     # 可选，本地模式不需要
MAX_CONCURRENT_DETECTIONS=2
DEFAULT_MODEL_PATH=default/best.pt
```

## Coding Conventions

- **EditorConfig**：JS/Vue/JSON 2 空格，Python 4 空格，UTF-8，LF
- **Vue 组件**：`PascalCase` 文件名（如 `ModelWeights.vue`），Store/工具用小写（如 `auth.js`）
- **Python**：`snake_case` 函数/模块，`PascalCase` 类
- **提交**：Conventional Commits（`feat:`, `fix:`, `chore:`，可加 scope 如 `feat(realtime):`）
- **前端测试**：`*.spec.js` 放在 `__tests__/` 子目录，Vitest + @vue/test-utils + jsdom
- **后端测试**：`test_*.py` 放在 `backend/` 根目录，pytest

## Deployment

- **Vercel**：`vercel.json` 配置前端 SPA 部署，环境变量通过 Vercel 注入
- **Docker**：`backend/Dockerfile` 基于 `python:3.10-slim`，含 OpenCV 系统依赖
