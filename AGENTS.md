# 仓库指南

## 项目结构与模块
- 前端（Vue 3 + Vite）：`src/`，入口 `src/main.js`，根组件 `src/App.vue`，视图在 `src/views/`，状态在 `src/stores/`，路由在 `src/router/`，样式在 `src/style.css`，静态资源在 `public/`。配置文件：`vite.config.js`、`tailwind.config.js`、`postcss.config.js`。
- 后端（FastAPI + YOLOv8）：`backend/`，API 位于 `backend/main.py`，工具位于 `backend/video_fix_utils.py`，依赖 `backend/requirements.txt`，容器 `backend/Dockerfile`。
- 数据：上传在 `backend/uploads/`，结果在 `backend/results/`。模型权重在运行时上传到 `backend/models/`。

## 构建、测试与开发
- 一次性安装（Windows）：`./setup.bat` 安装 Node 与 Python 依赖。
- 启动开发服务器：`./start.bat`（前端 `http://localhost:3000`，后端 `http://localhost:8000`，接口文档在 `/docs`）。
- 手动运行：
  - 前端：`npm run dev`
  - 后端：激活虚拟环境后执行 `python backend/main.py`
- 前端构建：`npm run build`（输出到 `dist/`），使用 `npm run preview` 进行预览。
- 后端 Docker：`docker build -f backend/Dockerfile -t yolo-backend .`，然后 `docker run -p 8000:8000 yolo-backend`。
- FFmpeg 检查：`python backend/check_ffmpeg.py`（如未安装可通过 `install_ffmpeg.bat` 安装）。

## 代码风格与命名
- JavaScript/Vue：2 空格缩进；变量/函数使用 `camelCase`；组件文件使用 `PascalCase`（例如 `src/views/Dashboard.vue`）；Tailwind 类名保持原子化且可读。
- Python：遵循 PEP 8、4 空格缩进；函数/变量使用 `snake_case`；在可行处优先使用类型注解；除 `backend/main.py` 中定义外避免全局状态。
- 保持最小变更；避免无关重构或噪声式重新格式化。

## 测试指南
- 目前无正式测试套件。后端改动请在 `backend/tests/` 下添加最小的 `pytest` 测试，使用 `httpx` 访问 FastAPI 端点（例如 `/api/detect`）。测试文件命名为 `test_*.py`。
- 前端如引入测试，优先使用 Vitest 做组件级测试；否则请在 PR 中提供简短的手动测试计划。

## 提交与拉取请求
- 使用 Conventional Commits：`feat:`、`fix:`、`docs:`、`refactor:`、`chore:`。
- PR 应包含：清晰摘要、关联问题、验证步骤（命令或 cURL）、UI 截图或检测结果文件，以及对配置/环境的影响说明。
- 保持 PR 聚焦且小；当行为变更时更新相关文档（`README.md`、根目录的指南）。

## 安全与配置
- 前端环境：在 `.env`（Vite）中设置 `VITE_SUPABASE_URL` 与 `VITE_SUPABASE_ANON_KEY`。
- 后端环境：在 `backend/.env` 中设置 `SUPABASE_URL` 与 `SUPABASE_KEY`。切勿提交任何密钥。
- 如出现 PyTorch 权重加载错误，请使用提供的修复脚本（`fix_pytorch.bat` / `fix_pytorch_venv.bat`）。
