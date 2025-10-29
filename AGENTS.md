# Repository Guidelines

## 项目结构与模块组织
- 前端代码位于 `src/`，核心 Vue 组件放在 `src/components/`，复用逻辑集中于 `src/composables/`，Pinia 状态存放在 `src/stores/`。
- 静态资源来自 `public/`，构建产物生成到 `dist/`，请勿手动修改。
- FastAPI 后端位于 `backend/`；`backend/main.py` 提供推理接口，YOLOv8 权重置于 `backend/models/`，运行时上传与结果分别写入 `backend/uploads/`、`backend/results/`，调试结束记得清理。
- 后端测试集中在 `backend/tests/`，文件命名遵循 `test_<feature>.py`。

## 构建、测试与开发命令
- `npm install`：安装前端依赖。
- `npm run dev`：启动 Vite 开发服务器（默认 `http://localhost:5173`）。
- `npm run build` / `npm run preview`：构建并本地验证生产包。
- `python -m venv .venv && source .venv/bin/activate`（PowerShell 使用 `.venv\Scripts\Activate.ps1`）：创建并激活虚拟环境。
- `pip install -r backend/requirements.txt`：安装后端依赖。
- `uvicorn backend.main:app --reload --port 8000` 或 `python backend/main.py`：本地运行推理服务。
- `pytest backend/tests`：执行后端测试套件。

## 编码风格与命名规范
- 遵循 `.editorconfig`，统一 UTF-8 与 LF。
- Vue/JS/TS 文件使用两个空格缩进，Python 文件使用四个空格。
- Vue 组件文件命名为 PascalCase，路由与静态资源采用 kebab-case。
- Python 变量与函数使用 snake_case，异步端点名称需以 `_async` 结尾。
- Supabase 密钥与模型参数仅可写入 `.env` 与 `backend/.env`。

## 测试规范
- 使用 `pytest backend/tests`，偏好轻量夹具，避免依赖真实权重或大型媒体。
- 覆盖 HTTP 状态码与响应结构，例如 `test_upload_validation.py` 检查上传流程。
- 确保测试可重复、无需外部服务即可通过 CI。

## 提交与 PR 要求
- 采用语义化前缀（如 `feat:`, `fix:`, `docs:`），主题使用祈使句且不超过 60 字符。
- 推送前先执行 `npm run build` 与 `pytest backend/tests`，确认无回归。
- PR 需关联 Issue，说明前后端影响，列出验证步骤及命令输出，并附上 UI 截图或 API 示例。

## 安全与配置提示
- 应用会先读取根目录 `.env`，再加载 `backend/.env`，部署新环境时同步更新。
- 调试或测试后及时清理 `backend/uploads/` 与 `backend/results/`，避免敏感信息泄露或磁盘占用。
