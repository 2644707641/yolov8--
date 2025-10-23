# Repository Guidelines

## 项目结构与模块组织
前端 采用 Vite + Vue 3 架构，核心 组件 位于 `src/`，状态 管理由 Pinia 模块 存放 在 `src/stores/`，可复用 逻辑 放在 `src/composables/`，静态 资源 位于 `public/`。`dist/` 为 构建 输出，禁止 手动 修改。后端 FastAPI 代码 存于 `backend/`，`main.py` 提供 推理 接口，`models/` 存放 YOLOv8 权重，`uploads/` 与 `results/` 保存 运行时 上传 与 结果，`tests/` 用于 自动化 验证。环境 模板 为 `.env.example` 与 `backend/.env.example`，根 目录 托管 支持 脚本。

## 构建与开发命令
前端 首次 执行 `npm install`，日常 调试 使用 `npm run dev` 访问 `http://localhost:5173`，`npm run build` 产出 生产 包，`npm run preview` 进行 本地 验证。后端 建议 创建 venv，运行 `pip install -r backend/requirements.txt` 安装 依赖，开发 态 使用 `uvicorn backend.main:app --reload --port 8000` 或 `python backend/main.py`。容器 化 场景 采用 `docker build -t yolov8-api backend` 以及 `docker run -p 8000:8000 yolov8-api`。

## 编码风格与命名约定
`.editorconfig` 统一 为 UTF-8 编码 与 LF 换行。Vue、JS、TS 文件 使用 两个 空格 缩进，Python 文件 采用 四个 空格。组件 文件 建议 PascalCase，路由 与 资源 名称 使用 kebab-case，Python 函数 与 变量 维持 snake_case，异步 端点 明确 以 `_async` 结尾。提交 前 请 手动 运行 `npm run build` 与 后端 服务，确保 无 格式 或 语法 回归。

## 测试规范
后端 测试 位于 `backend/tests/`，文件 按 `test_<feature>.py` 命名，使用 pytest 运行：`pytest backend/tests`。建议 为 权重 与 媒体 构建 轻量 夹具，避免 依赖 真实 模型 文件。前端 暂以 手工 回归 为主，如 添加 组件 级 测试，请 使用 `<Component>.spec.ts` 存放 于 `src/` 并 Mock Supabase 调用，同时 在 PR 中 说明 所需 示例 媒体。

## 提交与合并流程
遵循 语义 化 提交，如 `feat:`, `fix:`, `docs:`，主题 不超 60 字符，使用 祈使 语气。推送 前 清理 冗余 中间 提交。PR 应 关联 Issue，概述 前后端 影响，列出 核验 步骤（例如 `npm run build`, `pytest`, 手动 视频 演示），并 提供 UI 截图 或 API 请求 样例。敏感 配置 保留 在 本地 `.env`，若 需 数据 迁移 请 明确 说明。

## 配置与安全提示
Supabase 密钥 与 模型 参数 仅 存储 在 `.env` 系列 文件，禁止 写入 代码。`backend/uploads/` 与 `backend/results/` 仅 用于 临时 文件，测试 后 请 清理。更新 YOLO 权重 时，在 PR 中 标注 来源 链接 与 摘要 校验 信息，保障 推理 可复现。
