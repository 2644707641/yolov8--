# Repository Guidelines

## 项目概述
- 本项目是一个基于 `YOLOv8` 的停车位检测应用，采用 `FastAPI` 后端与 `Vue 3 + Vite` 前端分离架构。
- 项目支持两类运行模式：
  - 启用 `Supabase` 时，使用云端鉴权、数据库与对象存储。
  - 未启用 `Supabase` 时，部分数据可退化到本地 JSON 与本地文件系统。
- 前端登录依赖 `Supabase`，后端负责校验来自前端会话的 `JWT`。

## 目录结构规范
- `backend/`：后端服务目录。
  - `backend/app/api/`：接口路由与接口层公共依赖。
  - `backend/app/services/`：业务服务、检测流程、鉴权、存储、运行时状态等核心逻辑。
  - `backend/app/core/`：配置、补丁、核心初始化逻辑。
  - `backend/sql/`：数据库初始化或归档相关 SQL 脚本。
  - `backend/tests/` 或 `backend/test_*.py`：后端测试文件。
- `frontend/`：前端应用目录。
  - `frontend/src/views/`：页面级视图。
  - `frontend/src/components/`：通用组件与业务组件。
  - `frontend/src/layouts/`：页面布局壳层。
  - `frontend/src/stores/`：Pinia 状态管理。
  - `frontend/src/utils/`：工具函数。
  - `frontend/src/router/`：前端路由。
  - `frontend/src/config/`：配置与客户端初始化。
- `models/`：模型与缓存目录。
- `uploads/`、`results/`、`runtime/`、`logs/`、`runs/`：运行产物目录，不作为业务源码目录使用。
- 根目录下的 `best.pt`、媒体文件、运行日志、临时结果等都属于运行资产，不应与功能代码改动混合提交。

## 后端架构规则
- 后端入口为 `backend/main.py`，负责创建 `FastAPI` 应用、初始化共享状态、注册路由及基础依赖。
- 配置统一收敛在 `backend/app/core/config.py`，从仓库根目录 `.env` 读取环境变量。
- 路由职责要求明确：
  - 检测相关接口放在检测路由文件中。
  - 历史记录、设置、文件访问、模型权重、AI 分析、系统状态等分别保持独立模块。
- 业务逻辑不得堆叠在路由层，复杂逻辑应下沉到 `backend/app/services/`。
- 与模型推理、视频处理、并发控制、缓存、流式输出、WebSocket 协议相关的核心逻辑，优先在服务层维护统一实现，避免在多个路由中重复。
- 公共依赖解析逻辑，例如当前用户、模型路径、设置读取、清理任务协调，应集中在公共依赖文件中维护。

## 前端架构规则
- 前端使用 `Vue 3 + Vite + Pinia + Vue Router`。
- 页面职责划分：
  - `views/` 负责页面编排与路由级容器。
  - `components/` 负责可复用 UI 与局部业务块。
  - `stores/` 负责跨组件状态、接口调用流程和业务状态流转。
- 登录、会话恢复、登出、用户态相关逻辑集中在认证 store。
- 检测流程、进度流、历史记录、AI 分析等状态应集中在检测相关 store，避免组件各自维护重复状态。
- 受保护路由必须通过统一路由守卫控制，禁止在多个页面重复实现鉴权判断。

## 开发与运行命令
- 推荐优先使用 `运行项目.bat` 启动项目。
- 前端开发：
  - `frontend` 下执行 `pnpm install`
  - `frontend` 下执行 `pnpm dev`
  - `frontend` 下执行 `pnpm build`
  - `frontend` 下执行 `pnpm test`
- 后端开发：
  - `backend` 下使用虚拟环境 Python 执行 `pip install -r requirements.txt`
  - `backend` 下使用虚拟环境 Python 执行 `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
  - `backend` 下使用虚拟环境 Python 执行 `pytest test_*.py -v`
- 所有 Python 相关命令默认要求使用 `backend/.venv` 中的解释器执行。

## 环境与配置规则
- 项目使用仓库根目录下单一 `.env` 文件作为主要环境变量来源。
- 新环境应从 `.env.example` 或 `.env.local.example` 复制生成，不得直接提交真实密钥。
- 关键环境变量包括但不限于：
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `SUPABASE_JWT_SECRET`
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
  - `AI_API_URL`
  - `AI_API_KEY`
  - `AI_MODEL`
- 涉及外部服务时，必须通过环境变量注入密钥，禁止硬编码到源码、前端页面或可提交文件中。

## 编码规范
- 严格遵循 `.editorconfig`：`UTF-8`、去除行尾空格、文件末尾保留换行。
- 缩进规范：
  - `Python` 使用 4 空格。
  - `JavaScript`、`Vue`、`JSON`、`YAML` 使用 2 空格。
- 命名规范：
  - Python 模块、函数、变量使用 `snake_case`。
  - Vue 单文件组件使用 `PascalCase`。
  - JavaScript 变量和函数使用 `camelCase`。
- 公共接口、公共服务函数优先补充明确的类型信息或参数约束。
- 注释应简洁，只解释非显然逻辑、边界条件或设计意图，不保留无效兼容代码与过时说明。

## API 与数据流规则
- 后端接口响应优先返回结构稳定的 JSON，错误信息使用清晰、可直接展示的中文 `detail` 文本。
- 检测进度流使用统一 `SSE` 数据格式，不得在不同接口中随意改变字段命名。
- 实时检测的 `WebSocket` 二进制协议、模型选择优先级、结果文件访问方式等属于全局约定，修改时必须同步检查前后端调用链。
- 模型权重解析优先级保持一致：
  - Supabase 当前激活权重
  - 本地注册模型
  - 默认模型路径

## 测试规则
- 前端测试使用 `Vitest + @vue/test-utils + jsdom`。
- 前端测试文件放在邻近模块的 `__tests__/` 目录下，命名为 `*.spec.js`。
- 后端测试使用 `pytest` 风格或现有脚本风格，文件命名遵循 `test_*.py`。
- 新增或修改以下能力时，应补充相应测试或至少验证主要链路：
  - API 合约
  - 检测流程
  - 鉴权逻辑
  - 存储逻辑
  - 历史记录与设置读写
- 自动化执行单项测试时，建议单次命令超时控制在 60 秒以内。

## 提交与变更规则
- 提交信息建议使用：`feat:`、`fix:`、`docs:`、`chore:` 等前缀，必要时增加作用域。
- 单次提交保持聚焦，不要把后端逻辑、前端样式、生成文件和运行产物混在同一个提交中。
- 涉及 UI 变化时，提交说明或合并请求中应附带截图或录屏证据。
- 不要提交敏感配置、上传文件、检测结果、模型权重缓存及无关运行日志。

## 安全规则
- 所有认证、密钥、外部 API 配置均通过环境变量管理。
- 涉及 Supabase 的功能变更，必须同时核对鉴权、存储桶访问与数据库使用路径是否一致。
- 文件访问接口必须考虑鉴权与路径安全，避免未授权访问上传文件或结果文件。
- 任何可能暴露用户令牌、服务端密钥或本地敏感路径的日志输出都应避免。

## 协作规则
- 修改前先判断变更属于前端、后端还是全链路，避免在错误层级修补问题。
- 若变更触及共享约定，例如接口字段、状态结构、WebSocket/SSE 协议、模型选择逻辑，必须同步检查所有调用方。
- 优先修复根因，不只修补表现层问题。
- 对大改动优先保持最小必要变更，避免无关重构。

## 特殊说明
- Windows 环境下开发时，优先兼容现有批处理与虚拟环境启动方式。
- 视频编码、平台差异、模型加载补丁、实时流处理等逻辑属于高风险区域，修改前应先确认上下游依赖。
- 前端开发服务与后端服务端口约定如有变化，必须同步更新代理配置、环境变量和文档说明。

