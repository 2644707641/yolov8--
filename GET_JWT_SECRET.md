# 🔑 获取 Supabase JWT Secret 指南

## 快速步骤

1. **访问 Supabase 控制台**
   - 打开: https://app.supabase.com
   - 登录您的账户

2. **选择项目**
   - 选择项目: `wlajtijojwlfthpgfcgo`

3. **进入设置**
   - 点击左侧菜单的 **Settings** (齿轮图标)
   - 选择 **API**

4. **复制 JWT Secret**
   - 在页面中找到 **"JWT Settings"** 部分
   - 找到 **"JWT Secret"** 字段
   - 点击复制按钮复制完整的密钥

5. **更新后端配置**
   - 打开文件: `backend\.env`
   - 找到这一行: `SUPABASE_JWT_SECRET=your-jwt-secret-here`
   - 替换为: `SUPABASE_JWT_SECRET=你复制的JWT密钥`

6. **重启后端服务**
   - 在终端中按 `Ctrl+C` 停止后端
   - 重新运行: `.venv\Scripts\python.exe backend\main.py`

## 示例

正确的配置应该类似这样：

```bash
SUPABASE_JWT_SECRET=your-super-long-jwt-secret-key-from-supabase-dashboard
```

**注意**: JWT Secret 通常是一个很长的字符串！
