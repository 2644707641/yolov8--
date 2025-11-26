# Repository Guidelines

## Project Structure & Module Organization
前端源码集中在 `src/`（`components/`、`views/`、`stores/`、`router/`、`config/`）并由 `App.vue` 与 `main.js` 统筹挂载；静态资源位于 `public/`，构建产物写入 `dist/`。后端代码在 `backend/`，`main.py` 暴露 FastAPI 服务，`requirements.txt` 记录 Python 依赖，辅助脚本如 `check_ffmpeg.py`、`video_fix_utils.py` 和部署 Dockerfile 也存于此。根目录额外存放 YOLOv8 权重（`best.pt` 等）与部署/存储说明文档，`.env*` 管理跨端配置。

## Build, Test, and Development Commands
前端：`npm install` 安装依赖，`npm run dev` 以 Vite 启动本地 3000 端口，`npm run build` 生成生产包，`npm run preview` 校验构建输出。后端建议在 `.venv` 激活后执行 `pip install -r backend/requirements.txt`，再用 `python backend/main.py` 或 `uvicorn backend.main:app --reload` 于 8000 端口调试；`python backend/test_auth.py` 用于快速验证 Supabase service_role 配置。常见一键脚本包括 `start.ps1`（联动前后端）与 `restart_backend.bat`。

## Coding Style & Naming Conventions
Vue 代码使用 2 空格缩进、单引号、Composition API，并保持组件文件 `PascalCase.vue`、工具模块 `kebab-case.ts`。Pinia store 命名 `useXStore`，路由常量 `ROUTE_HOME`。Tailwind 工具类集中在模板中，额外样式写入 `style.css`。Python 遵循 PEP 8：4 空格缩进、`snake_case` 函数/变量、`PascalCase` 类；异步 IO 逻辑单独封装在 `services/` 或 `utils/` 中，YOLO 处理保持在 `backend/detection_*` 模块，确保推理函数具备 docstring。

## Testing Guidelines
当前重点是手动回归关键流程（模型上传、图/视频检测、Supabase 存储同步）。配置环境后先运行 `python backend/test_auth.py`，确认 service_role key 可用，再执行 `npm run dev`+`python backend/main.py` 联调。命名自动化测试文件为 `test_<module>.py` 并放在 `backend/tests/`（建议遵循 pytest 结构）；任何新的前端单测请放入 `src/__tests__/`，命名 `<Component>.spec.ts`，使用 Vitest 或 Cypress 视场景补齐。若改动涉及登陆或上传，附带截图或录像说明验证路径。

## Commit & Pull Request Guidelines
参考 `CONTRIBUTING.md`，采用语义化前缀：`feat`、`fix`、`docs`、`style`、`refactor`、`test`、`chore`，主题保持 50 字符以内（示例：`feat: 支持批量检测队列`），正文列出要点。分支命名 `feature/<short-topic>`、`fix/<issue-id>`；PR 模板需包含：问题背景、方案摘要、测试结果（命令输出或截图）、关联 Issue/任务链接，若 UI 变化请附前后对比图。提交前确认 `npm run build` 与后端启动无误，更新关联文档（README、PARAMETER_GUIDE.md 等）。

## Security & Configuration Tips
前后端 `.env` 均禁止提交，统一通过 `cp .env.example .env` 复制并填写 `VITE_SUPABASE_URL`、`VITE_API_URL`、`SUPABASE_URL`、`SUPABASE_KEY` 等键，service_role key 仅用于后端。部署前执行 `GET_JWT_SECRET.md` 中的指南生成新密钥，必要时运行 `install_ffmpeg.bat` 装配依赖。权重文件 (如 `best.pt`) 不要上传到公共 Fork，可利用私有对象存储并通过 `MODEL_STORAGE_SETUP.md` 配置下载逻辑。
