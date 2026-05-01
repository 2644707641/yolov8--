---
trigger: glob
globs: backend/**
---

# 🐍 后端开发规则 (FastAPI + YOLOv8)

## 架构分层

```
backend/app/
├── api/            # 路由层 — 请求/响应处理
│   ├── routes.py   # 总路由注册（APIRouter 聚合）
│   └── *_routes.py # 按功能拆分的子路由
├── core/           # 基础设施
│   ├── config.py   # Settings dataclass + 环境变量
│   └── logging_config.py
├── services/       # 业务逻辑层
│   ├── detection.py    # YOLOv8 推理核心
│   ├── storage.py      # Supabase Storage 操作
│   ├── auth.py         # JWT 认证
│   ├── ai_analysis.py  # AI 分析服务
│   ├── model_weights.py # 模型权重管理
│   ├── local_state.py  # 本地 JSON 持久化
│   └── local_cleanup.py # 本地文件清理
└── middleware/     # 中间件
```

## 编码规则

1. **新增 API 路由**时：
   - 在 `app/api/` 下创建 `{功能}_routes.py`
   - 在 `app/api/routes.py` 中注册子路由
   - 路由前缀统一 `/api/...`

2. **依赖注入**：
   - 通过 `request.app.state.supabase` 获取 Supabase 客户端
   - 通过 `request.app.state.http_client` 获取共享 httpx 客户端
   - 通过 `request.app.state.app_settings` 获取应用设置

3. **配置项**：
   - 新增配置必须加到 `Settings` dataclass，通过 `os.getenv()` 读取
   - 同步更新 `.env.example`

4. **错误处理**：
   - 使用 FastAPI 的 `HTTPException` 返回错误
   - 日志记录使用 `logger`，勿使用 `print()`

5. **文件操作**：
   - 上传文件存放 `uploads/`，结果存放 `results/`
   - 模型权重存放 `models/`，缓存在 `models/cache/`
   - 使用 `settings` 中的路径常量，勿硬编码路径

6. **Supabase 降级**：
   - 所有涉及 Supabase 的代码必须检查客户端是否为 `None`
   - 提供本地 fallback（JSON 文件存储）

7. **YOLOv8 推理**：
   - 检测服务在 `services/detection.py`
   - 注意并发控制 `MAX_CONCURRENT_DETECTIONS`
   - 模型加载和缓存逻辑在 `services/model_weights.py`

8. **测试**：
   - 测试文件命名 `test_*.py`
   - 使用 `pytest`，异步测试用 `pytest-asyncio`
   - 单测超时上限 60 秒
