# Supabase Anon Key 配置指南

## 问题描述
您遇到的错误："登录失败: AuthApiError: Invalid API key" 是因为 Supabase 配置中的 anon key 无效。

## 获取正确 Anon Key 的步骤

### 1. 登录 Supabase 控制台
- 访问：https://supabase.com/dashboard
- 使用您的账户登录

### 2. 选择项目
- 点击您的项目：`wlajtijojwlfthpgfcgo`

### 3. 获取 API Key
- 在左侧菜单中选择 **Settings**
- 点击 **API** 子菜单
- 找到 **Project API keys** 部分
- 复制 **anon public** key（注意：不是 service_role key）
- anon key 通常以 "eyJ" 开头，很长的一串

### 4. 更新配置
获取到正确的 anon key 后，需要更新项目根目录的 `.env` 文件：

```bash
# 替换这一行：
VITE_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY_HERE

# 替换为实际获得的 key，例如：
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5. 重启服务
配置更新后，需要重启前端服务：

1. 在终端中按 `Ctrl+C` 停止前端服务
2. 重新运行：`npm run dev`

## 验证配置
重启服务后，访问 http://localhost:3000 尝试登录，如果错误消失，说明配置正确。

## 注意事项
- 永远不要在前端使用 `service_role` key，只使用 `anon public` key
- 确保 anon key 是完整的 JWT token
- 配置更改后必须重启开发服务器

## 如果仍然有问题
请检查：
1. Supabase URL 是否正确：`https://wlajtijojwlfthpgfcgo.supabase.co`
2. 确保复制的是完整的 anon key，没有被截断
3. 检查控制台是否有其他错误信息