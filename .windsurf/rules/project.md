---
trigger: always
---

# 🅿️ YOLOv8 智能停车位检测系统 — Windsurf 项目规则

## 📌 项目概述

本项目是一个基于 YOLOv8 的智能停车位检测全栈应用，采用前后端分离架构。
- **前端**：Vue 3 + Vite + Tailwind CSS + Pinia
- **后端**：Python FastAPI + Ultralytics YOLOv8 + Supabase
- **认证**：Supabase Auth (JWT)
- **存储**：Supabase Storage + 本地文件系统
- **部署**：前端 Vercel，后端 Docker / Uvicorn

---

## 🏗️ 目录结构约定

```
根目录/
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── api/           # 路由层（按功能拆分 *_routes.py）
│   │   ├── core/          # 配置、日志、PyTorch 补丁
│   │   ├── services/      # 业务逻辑层（检测、存储、认证等）
│   │   └── middleware/     # 中间件
│   ├── sql/               # SQL 归档脚本
│   ├── tests/             # 后端测试
│   ├── main.py            # FastAPI 应用入口
│   └── requirements.txt   # Python 依赖
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── views/         # 页面级组件（Dashboard, History 等）
│   │   ├── components/    # 可复用 UI 组件
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── router/        # Vue Router 路由配置
│   │   ├── layouts/       # 布局组件（AppShell）
│   │   ├── utils/         # 工具函数
│   │   ├── config/        # 前端配置
│   │   └── tests/         # 前端测试
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
├── models/                # YOLOv8 模型权重
├── uploads/               # 上传文件临时存储
├── results/               # 检测结果输出
├── .env                   # 环境变量（不提交）
└── vercel.json            # Vercel 部署配置
```

---

## 🔧 技术栈与版本

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 运行环境 |
| FastAPI | 0.104.x | Web 框架 |
| Uvicorn | 0.24.x | ASGI 服务器 |
| Ultralytics | 8.0.220 | YOLOv8 推理引擎 |
| OpenCV | 4.8.x | 图像/视频处理 |
| Supabase | 2.9.x | 数据库 + 认证 + 存储 |
| httpx | 0.27.x | 异步 HTTP 客户端 |
| PyJWT | 2.8.x | JWT 验证 |

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.3.x | UI 框架 |
| Vite | 5.0.x | 构建工具 |
| Pinia | 2.1.x | 状态管理 |
| Vue Router | 4.2.x | 路由 |
| Tailwind CSS | 3.3.x | 样式 |
| Axios | 1.6.x | HTTP 请求 |
| GSAP | 3.14.x | 动画 |
| Three.js | 0.183.x | 3D 效果 |
| Vitest | 4.x | 单元测试 |

---

## 🚀 开发环境

### 启动命令
- **一键启动**：运行根目录 `运行项目.bat`
- **后端单独启动**：
  ```bash
  cd backend
  .venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000
  ```
- **前端单独启动**：
  ```bash
  cd frontend
  pnpm dev --host 0.0.0.0 --port 5173
  ```

### 端口分配
- **前端开发服务器**：`http://localhost:3000`（Vite 配置）或 `5173`（bat 脚本）
- **后端 API 服务器**：`http://localhost:8000`
- **API 代理**：前端 `/api` 路径代理到后端 `http://localhost:8000`

### 包管理器
- **前端**：pnpm（必须使用 pnpm，勿用 npm/yarn）
- **后端**：pip + venv（虚拟环境路径：`backend/.venv`）

---

## 📐 编码规范

### 后端 (Python)
1. **路由层**（`app/api/`）：只负责请求解析、参数校验和响应构造，业务逻辑下沉到 `services/`
2. **服务层**（`app/services/`）：封装核心业务（检测、存储、认证），保持无状态
3. **配置管理**：统一使用 `app/core/config.py` 的 `settings` 单例，通过环境变量注入
4. **Supabase 客户端**：通过 `app.state.supabase` 获取，可能为 `None`（未配置时）
5. **HTTP 客户端**：共享 `app.state.http_client`（httpx.AsyncClient），勿创建新实例
6. **日志**：使用 `app/core/logging_config.py` 的 `setup_logging()`
7. **异步优先**：API 路由函数使用 `async def`
8. **路由文件命名**：`{功能}_routes.py`，如 `detection_routes.py`
9. **测试文件命名**：`test_{功能}.py`，放在 `backend/` 根目录或 `tests/`

### 前端 (Vue 3)
1. **单文件组件**：使用 `<script setup>` + Composition API
2. **状态管理**：Pinia store 按功能拆分（`auth.js`, `detection.js`），勿滥用全局状态
3. **路由**：懒加载页面组件，`meta.requiresAuth` 控制认证保护
4. **样式**：优先使用 Tailwind 工具类，遵循 `tailwind.config.js` 中定义的 `primary`/`accent`/`success` 色彩体系
5. **动画**：使用 Tailwind 预设动画类（`animate-fade-in` 等）或 GSAP
6. **API 请求**：使用 Axios，基础 URL 通过 `VITE_API_URL` 环境变量配置
7. **路径别名**：`@` 映射到 `frontend/src/`
8. **测试**：Vitest + jsdom 环境，测试文件放在 `__tests__/` 目录

---

## 🔐 环境变量

环境变量在根目录 `.env` 统一管理（前后端共享），参考 `.env.example`：

### 前端变量（VITE_ 前缀）
- `VITE_SUPABASE_URL` — Supabase 项目 URL
- `VITE_SUPABASE_ANON_KEY` — Supabase 匿名密钥
- `VITE_API_URL` — 后端 API 地址

### 后端变量
- `SUPABASE_URL` / `SUPABASE_KEY` — Supabase 服务端连接
- `SUPABASE_JWT_SECRET` — JWT 验证密钥
- `SUPABASE_BUCKET` / `MODEL_WEIGHTS_BUCKET` — 存储桶名
- `UPLOAD_DIR` / `MODEL_DIR` / `RESULT_DIR` — 本地文件目录
- `AI_API_URL` / `AI_API_KEY` / `AI_MODEL` — AI 分析服务配置
- `MAX_UPLOAD_SIZE_MB` / `MAX_CONCURRENT_DETECTIONS` — 限制参数

⚠️ **绝对禁止将 `.env` 文件或任何密钥硬编码到代码中**

---

## 🧪 测试

- **后端测试**：`cd backend && python -m pytest` （超时上限 60s）
- **前端测试**：`cd frontend && pnpm test`
- **前端监听模式**：`cd frontend && pnpm test:watch`

---

## 📦 部署

### 前端（Vercel）
- 构建命令：`cd frontend && npm run build`
- 输出目录：`frontend/dist`
- SPA 重写：所有路由 fallback 到 `index.html`

### 后端（Docker）
- Dockerfile 位于 `backend/Dockerfile`
- 暴露端口 8000

---

## ⚠️ 注意事项

1. **模型文件**：`.pt` / `.pth` 文件体积大，已在 `.gitignore` 中排除，不要提交到 Git
2. **Supabase 可选**：系统设计为 Supabase 不可用时回退到本地模式（本地文件 + JSON 存储）
3. **PyTorch 补丁**：`app/core/pytorch_patch.py` 处理 PyTorch 兼容性问题，修改前需谨慎
4. **并发检测**：`MAX_CONCURRENT_DETECTIONS` 控制同时运行的推理任务数，避免 OOM
5. **视频处理**：大视频文件通过流式处理，注意 `MAX_UPLOAD_SIZE_MB` 限制
6. **中文支持**：UI 文案、日志消息均使用中文，保持一致
