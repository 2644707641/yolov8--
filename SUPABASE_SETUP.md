# Supabase 配置指南

本文档将指导您如何配置Supabase以支持YOLOv8识别系统。

## 1. 创建Supabase项目

1. 访问 [Supabase](https://supabase.com) 并登录
2. 点击 "New Project" 创建新项目
3. 填写项目名称、数据库密码，选择区域
4. 等待项目创建完成

## 2. 获取API密钥

1. 在项目面板中，点击左侧的 "Settings" (设置)
2. 选择 "API"
3. 复制以下信息：
   - `Project URL` (项目URL)
   - `anon public` key (匿名公钥)

## 3. 创建数据库表

在Supabase控制台的SQL Editor中执行以下SQL语句：

```sql
-- 创建检测历史表
CREATE TABLE detection_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  file_type VARCHAR(10) NOT NULL CHECK (file_type IN ('image', 'video')),
  original_file TEXT NOT NULL,
  result_file TEXT NOT NULL,
  detections JSONB,
  params JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引以提高查询性能
CREATE INDEX idx_detection_history_user_id ON detection_history(user_id);
CREATE INDEX idx_detection_history_created_at ON detection_history(created_at DESC);

-- 启用行级安全策略 (RLS)
ALTER TABLE detection_history ENABLE ROW LEVEL SECURITY;

-- 创建策略：用户只能查看自己的记录
CREATE POLICY "Users can view their own detection history"
  ON detection_history
  FOR SELECT
  USING (auth.uid() = user_id);

-- 创建策略：用户只能插入自己的记录
CREATE POLICY "Users can insert their own detection history"
  ON detection_history
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 创建策略：用户只能删除自己的记录
CREATE POLICY "Users can delete their own detection history"
  ON detection_history
  FOR DELETE
  USING (auth.uid() = user_id);
```

## 4. 配置存储桶 (Storage Bucket)

1. 在Supabase控制台中，点击左侧的 "Storage"
2. 点击 "Create bucket"
3. 创建名为 `detection-files` 的存储桶
4. 设置为 **Public** (公开访问)

### 配置存储策略

在Storage Policies中添加以下策略：

```sql
-- 允许认证用户上传文件
CREATE POLICY "Authenticated users can upload files"
  ON storage.objects
  FOR INSERT
  TO authenticated
  WITH CHECK (bucket_id = 'detection-files' AND auth.uid()::text = (storage.foldername(name))[1]);

-- 允许所有人查看文件（因为是公开桶）
CREATE POLICY "Anyone can view files"
  ON storage.objects
  FOR SELECT
  TO public
  USING (bucket_id = 'detection-files');

-- 允许用户删除自己的文件
CREATE POLICY "Users can delete their own files"
  ON storage.objects
  FOR DELETE
  TO authenticated
  USING (bucket_id = 'detection-files' AND auth.uid()::text = (storage.foldername(name))[1]);
```

## 5. 配置认证

Supabase默认已启用邮箱/密码认证。您可以在以下位置进行额外配置：

1. 点击左侧的 "Authentication" > "Settings"
2. 配置以下选项：
   - **Email confirmations**: 如果需要邮箱验证，启用此选项
   - **Email templates**: 自定义注册/登录邮件模板
   - **Site URL**: 设置为您的应用URL

## 6. 配置环境变量

### 前端 (.env)

创建 `.env` 文件：

```bash
VITE_SUPABASE_URL=你的项目URL
VITE_SUPABASE_ANON_KEY=你的匿名公钥
VITE_API_URL=http://localhost:8000
```

### 后端 (backend/.env)

创建 `backend/.env` 文件：

```bash
PORT=8000
HOST=0.0.0.0
SUPABASE_URL=你的项目URL
SUPABASE_KEY=你的服务角色密钥
```

## 7. 测试配置

1. 启动后端服务：
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

2. 启动前端服务：
   ```bash
   npm install
   npm run dev
   ```

3. 访问 `http://localhost:3000` 并尝试：
   - 注册新用户
   - 登录
   - 上传模型和文件
   - 查看历史记录

## 8. 部署配置

### Vercel环境变量

在Vercel项目设置中添加以下环境变量：

- `VITE_SUPABASE_URL`: 你的Supabase项目URL
- `VITE_SUPABASE_ANON_KEY`: 你的Supabase匿名公钥
- `VITE_API_URL`: 你的后端API地址

## 常见问题

### Q: 用户注册后需要邮箱验证吗？
A: 默认情况下，Supabase会发送验证邮件。您可以在Authentication > Settings中禁用此功能。

### Q: 如何限制存储空间使用？
A: 在Storage设置中可以配置存储限制和文件大小限制。

### Q: 如何备份数据？
A: Supabase提供自动备份功能。在项目设置中可以配置备份策略。

### Q: 如何监控API使用情况？
A: 在项目首页的Dashboard中可以查看API请求、存储使用等统计信息。
