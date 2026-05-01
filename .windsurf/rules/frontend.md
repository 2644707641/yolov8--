---
trigger: glob
globs: frontend/**
---

# 🎨 前端开发规则 (Vue 3 + Vite + Tailwind)

## 架构概览

```
frontend/src/
├── views/          # 页面组件（路由级）
│   ├── Overview.vue       # 系统概览
│   ├── Dashboard.vue      # 识别工作台（核心页面）
│   ├── History.vue        # 历史记录中心
│   ├── ModelWeights.vue   # 模型权重管理
│   ├── Realtime.vue       # 实时监控
│   ├── Settings.vue       # 系统设置
│   ├── Login.vue          # 登录页
│   └── __tests__/         # 页面测试
├── components/     # 可复用组件
├── stores/         # Pinia 状态管理
│   ├── auth.js     # 认证状态（Supabase Auth）
│   └── detection.js # 检测状态与 API 交互
├── router/         # Vue Router
├── layouts/        # 布局（AppShell）
├── utils/          # 工具函数
└── config/         # 前端配置
```

## 编码规则

### Vue 组件
1. 使用 `<script setup>` 语法 + Composition API，不使用 Options API
2. 组件文件名使用 PascalCase（如 `AiAnalysisPanel.vue`）
3. 页面组件放 `views/`，可复用组件放 `components/`
4. 模板中使用 PascalCase 引用组件

### 状态管理 (Pinia)
1. Store 文件放 `stores/` 目录，按功能命名
2. 使用 `defineStore` + Setup Store 风格
3. 异步 API 调用封装在 store actions 中
4. 认证状态统一由 `auth.js` 管理，通过 `useAuthStore()` 访问

### 路由
1. 新页面必须添加到 `router/index.js` 的路由表中
2. 需要认证的页面设置 `meta: { requiresAuth: true }`
3. 页面组件使用 `() => import(...)` 懒加载
4. 页面标题通过 `meta.title` 设置（中文）

### 样式 (Tailwind CSS)
1. **优先使用 Tailwind 工具类**，避免自定义 CSS
2. 使用项目定义的色彩体系：
   - `primary-*`：青色系（#06b6d4 为主色）
   - `accent-*`：蓝色系
   - `success-*`：绿色系
3. 使用预设动画类：`animate-fade-in`, `animate-fade-in-up`, `animate-scale-in` 等
4. 使用预设阴影：`shadow-glow-sm`, `shadow-glow-md`, `shadow-glow-lg`
5. 严禁使用 Tailwind 魔法数值（如 `w-[137px]`），使用标准间距

### API 请求
1. 使用 Axios 发起请求
2. API 基础路径使用 `VITE_API_URL` 环境变量
3. 认证接口走 Supabase JS SDK（`@supabase/supabase-js`）
4. 业务接口走 `/api/` 前缀，开发时由 Vite 代理到后端

### 测试 (Vitest)
1. 测试文件放在对应目录的 `__tests__/` 子目录中
2. 使用 `@vue/test-utils` 进行组件测试
3. 运行：`pnpm test`（单次）/ `pnpm test:watch`（监听）

### 包管理
- **必须使用 pnpm**，禁止使用 npm 或 yarn
- 安装依赖：`pnpm add <package>`
- 安装开发依赖：`pnpm add -D <package>`
