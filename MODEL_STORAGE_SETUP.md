# 模型权重存储配置指南

本文档说明如何配置 Supabase 以支持模型权重文件的持久化存储。

## 功能概述

系统现在支持将用户上传的 YOLOv8 模型权重文件保存到 Supabase Storage，实现以下功能：

1. **权重持久化存储**：上传的权重文件保存在 Supabase，无需重复上传
2. **权重管理**：用户可以查看、选择和删除自己的权重文件
3. **多权重支持**：用户可以上传多个不同的权重文件并切换使用
4. **自动加载**：检测时自动从 Supabase 下载并缓存权重文件

## 数据库配置

### 1. 创建模型权重表

在 Supabase SQL Editor 中执行以下 SQL：

```sql
-- 创建模型权重表
CREATE TABLE model_weights (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  is_active BOOLEAN DEFAULT false,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_model_weights_user_id ON model_weights(user_id);
CREATE INDEX idx_model_weights_is_active ON model_weights(user_id, is_active);

-- 启用行级安全策略
ALTER TABLE model_weights ENABLE ROW LEVEL SECURITY;

-- 用户只能查看自己的权重
CREATE POLICY "Users can view their own model weights"
  ON model_weights
  FOR SELECT
  USING (auth.uid() = user_id);

-- 用户只能插入自己的权重
CREATE POLICY "Users can insert their own model weights"
  ON model_weights
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 用户只能更新自己的权重
CREATE POLICY "Users can update their own model weights"
  ON model_weights
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- 用户只能删除自己的权重
CREATE POLICY "Users can delete their own model weights"
  ON model_weights
  FOR DELETE
  USING (auth.uid() = user_id);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_model_weights_updated_at
  BEFORE UPDATE ON model_weights
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 创建唯一约束：每个用户只能有一个活跃权重
CREATE UNIQUE INDEX idx_model_weights_user_active 
  ON model_weights(user_id) 
  WHERE is_active = true;
```

### 2. 创建存储桶

1. 在 Supabase 控制台中，点击左侧的 "Storage"
2. 点击 "Create bucket"
3. 创建名为 `model-weights` 的存储桶
4. 设置为 **Private** (私有访问，仅认证用户可访问)

### 3. 配置存储策略

```sql
-- 允许认证用户上传权重文件
CREATE POLICY "Authenticated users can upload model weights"
  ON storage.objects
  FOR INSERT
  TO authenticated
  WITH CHECK (
    bucket_id = 'model-weights' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- 允许用户查看自己的权重文件
CREATE POLICY "Users can view their own model weights"
  ON storage.objects
  FOR SELECT
  TO authenticated
  USING (
    bucket_id = 'model-weights' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- 允许用户删除自己的权重文件
CREATE POLICY "Users can delete their own model weights"
  ON storage.objects
  FOR DELETE
  TO authenticated
  USING (
    bucket_id = 'model-weights' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );
```

## 文件存储结构

权重文件按以下结构存储：

```
model-weights/
├── {user_id}/
│   ├── {timestamp}_{filename}.pt
│   ├── {timestamp}_{filename}.pth
│   └── ...
```

## 工作流程

### 权重上传流程

1. **用户上传权重文件**：通过 `/api/upload-model` 接口上传
2. **验证文件**：检查文件格式和大小
3. **上传到 Supabase**：
   - 将文件上传到 `model-weights/{user_id}/` 路径
   - 获取文件的永久存储路径
4. **保存记录**：在 `model_weights` 表中记录权重信息
5. **设置为活跃**：如果是第一个权重或用户指定，设置为活跃状态
6. **返回结果**：返回权重信息和上传状态

### 权重使用流程

1. **检测请求**：用户发起检测请求
2. **获取活跃权重**：查询用户当前选择的活跃权重
3. **检查本地缓存**：查看本地是否已有该权重文件
4. **下载权重**：如果本地没有，从 Supabase 下载到本地缓存
5. **加载模型**：使用本地权重文件加载 YOLO 模型
6. **执行检测**：进行目标检测

### 权重管理流程

用户可以通过以下 API 管理权重：

- **列出权重**：`GET /api/model-weights` - 获取所有权重列表
- **设置活跃权重**：`PUT /api/model-weights/{id}/activate` - 切换使用的权重
- **删除权重**：`DELETE /api/model-weights/{id}` - 删除指定权重
- **获取权重详情**：`GET /api/model-weights/{id}` - 查看权重详细信息

## API 响应格式

### 上传权重响应

```json
{
  "success": true,
  "message": "模型上传并保存成功",
  "weight": {
    "id": "uuid",
    "name": "best.pt",
    "file_path": "user_id/timestamp_best.pt",
    "file_size": 12345678,
    "is_active": true,
    "created_at": "2025-10-29T00:00:00Z"
  }
}
```

### 权重列表响应

```json
{
  "success": true,
  "weights": [
    {
      "id": "uuid",
      "name": "parking_v1.pt",
      "file_size": 12345678,
      "is_active": true,
      "description": "停车位检测模型 v1",
      "created_at": "2025-10-29T00:00:00Z"
    }
  ]
}
```

## 配置环境变量

在 `backend/.env` 中添加：

```bash
# 权重存储配置
MODEL_WEIGHTS_BUCKET=model-weights
MODEL_CACHE_DIR=models/cache
```

## 优势

1. **持久化存储**：权重文件永久保存在云端，不会丢失
2. **无需重复上传**：用户只需上传一次，之后可以重复使用
3. **多权重管理**：支持上传多个权重文件，灵活切换
4. **自动缓存**：本地缓存机制，提高加载速度
5. **节省空间**：服务器端无需长期保存所有权重文件

## 本地缓存机制

为了提高性能，系统会在本地缓存从 Supabase 下载的权重文件：

1. **首次使用**：从 Supabase 下载到 `models/cache/{user_id}/`
2. **后续使用**：直接使用本地缓存，无需重复下载
3. **缓存清理**：可以通过 API 清理本地缓存，节省磁盘空间

## 注意事项

1. **文件大小限制**：
   - Supabase 免费计划单文件限制为 50MB
   - 建议使用压缩的权重文件或升级计划

2. **存储空间管理**：
   - 定期清理不需要的权重文件
   - 监控 Supabase 存储使用情况

3. **网络要求**：
   - 首次使用权重需要从 Supabase 下载
   - 下载速度取决于网络连接

4. **安全性**：
   - 权重文件存储在私有桶中，仅用户可访问
   - 使用 Service Role Key 进行服务端操作

## 故障排查

### 问题：权重上传失败

**可能原因：**
1. 文件过大
2. 存储桶未创建或权限配置错误
3. 网络连接问题

**解决方法：**
1. 检查文件大小是否超出限制
2. 确认 `model-weights` 存储桶已创建
3. 查看后端日志获取详细错误信息

### 问题：无法下载权重

**可能原因：**
1. Supabase 配置错误
2. 权重文件已被删除
3. 网络连接问题

**解决方法：**
1. 检查 `backend/.env` 中的 Supabase 配置
2. 确认权重记录在数据库中存在
3. 检查存储桶中是否有对应文件

### 问题：检测时提示"请先上传模型"

**可能原因：**
1. 用户没有活跃的权重
2. 权重下载失败
3. 本地缓存被误删

**解决方法：**
1. 上传新的权重文件或激活已有权重
2. 检查网络连接和 Supabase 配置
3. 重新下载权重文件

## 未来改进

- [ ] 支持权重文件版本管理
- [ ] 添加权重文件分享功能
- [ ] 实现权重文件压缩上传
- [ ] 添加权重文件预加载
- [ ] 支持权重文件导入导出
- [ ] 添加权重性能统计
