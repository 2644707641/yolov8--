# 模型权重存储功能 - 快速开始

本指南将帮助您快速配置和使用模型权重的 Supabase 存储功能。

## 🎯 功能概述

现在，用户上传的 YOLOv8 权重文件将**自动保存到 Supabase Storage**，实现以下特性：

- ✅ **持久化存储**：权重文件永久保存在云端
- ✅ **无需重复上传**：用户只需上传一次，之后可以重复使用
- ✅ **多权重管理**：支持上传多个权重，灵活切换
- ✅ **自动缓存**：本地自动缓存，提升加载速度
- ✅ **用户隔离**：每个用户的权重文件独立存储

## 📋 配置步骤

### 1. 配置 Supabase 数据库

在 Supabase SQL Editor 中执行以下 SQL（完整 SQL 见 `MODEL_STORAGE_SETUP.md`）：

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

-- 启用 RLS
ALTER TABLE model_weights ENABLE ROW LEVEL SECURITY;

-- 创建策略（查看、插入、更新、删除）
-- [详细策略见 MODEL_STORAGE_SETUP.md]
```

### 2. 创建存储桶

1. 在 Supabase 控制台，进入 **Storage**
2. 创建名为 `model-weights` 的存储桶
3. 设置为 **Private**（私有访问）
4. 配置存储策略（见 `MODEL_STORAGE_SETUP.md`）

### 3. 配置环境变量

在 `backend/.env` 中添加（参考 `backend/.env.example`）：

```bash
# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key

# 存储桶配置
MODEL_WEIGHTS_BUCKET=model-weights
MODEL_CACHE_DIR=models/cache
```

### 4. 安装依赖（如需要）

后端已包含所需依赖，如果是新环境：

```bash
cd backend
pip install -r requirements.txt
```

## 🚀 使用方法

### 前端使用

#### 1. 上传权重

用户有两种方式上传权重：

**方法 A：通过控制台（Dashboard）**
1. 登录后进入控制台
2. 在"步骤 1: 上传模型权重"处上传 .pt 或 .pth 文件
3. 系统自动保存到 Supabase

**方法 B：通过权重管理页面**
1. 点击导航栏的"权重管理"按钮
2. 在权重管理页面上传文件
3. 可选填写权重描述

#### 2. 管理权重

在"权重管理"页面，用户可以：
- 查看所有上传的权重文件
- 切换当前使用的权重（点击"使用"按钮）
- 删除不需要的权重
- 查看文件大小和上传时间

#### 3. 使用权重进行检测

1. 在控制台选择要检测的文件
2. 系统自动使用当前激活的权重
3. 如果本地没有缓存，会自动从 Supabase 下载

### API 使用

#### 上传权重

```bash
POST /api/upload-model
Headers:
  Authorization: Bearer {token}
Body (multipart/form-data):
  model: {file}
  description: {optional description}
```

#### 列出权重

```bash
GET /api/model-weights
Headers:
  Authorization: Bearer {token}
```

#### 激活权重

```bash
PUT /api/model-weights/{weight_id}/activate
Headers:
  Authorization: Bearer {token}
```

#### 删除权重

```bash
DELETE /api/model-weights/{weight_id}
Headers:
  Authorization: Bearer {token}
```

## 🔄 工作流程

### 权重上传流程

```
用户上传权重文件
    ↓
后端接收并验证
    ↓
上传到 Supabase Storage
    ↓
创建数据库记录
    ↓
设置为活跃（如果是第一个权重）
    ↓
返回成功响应
```

### 检测时权重加载流程

```
用户发起检测请求
    ↓
查询用户的活跃权重
    ↓
检查本地缓存
    ↓
如果没有缓存 → 从 Supabase 下载
    ↓
加载模型权重
    ↓
执行检测
```

## 📁 文件存储结构

### Supabase Storage

```
model-weights/
├── {user_id}/
│   ├── 1730188800_best.pt
│   ├── 1730275200_yolov8n.pt
│   └── ...
```

### 本地缓存

```
models/cache/
├── {user_id}/
│   ├── 1730188800_best.pt
│   ├── 1730275200_yolov8n.pt
│   └── ...
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MODEL_WEIGHTS_BUCKET` | 权重存储桶名称 | `model-weights` |
| `MODEL_CACHE_DIR` | 本地缓存目录 | `models/cache` |
| `MAX_UPLOAD_SIZE_MB` | 最大上传大小 | `200` |

### 存储桶策略

- **上传权限**：仅认证用户可以上传到自己的目录
- **查看权限**：用户只能查看自己的权重文件
- **删除权限**：用户只能删除自己的权重文件

## 🔍 常见问题

### Q: 上传后在哪里查看权重？

**A:** 点击导航栏的"权重管理"按钮，进入权重管理页面。

### Q: 如何切换使用的权重？

**A:** 在权重管理页面，点击想要使用的权重旁边的"使用"按钮。

### Q: 权重文件会占用多少空间？

**A:** Supabase 免费计划提供 1GB 存储空间。YOLOv8 权重通常在 6-140MB 之间。

### Q: 如果删除了当前使用的权重会怎样？

**A:** 如果删除的是当前活跃的权重，下次检测时需要重新上传或激活其他权重。

### Q: 本地缓存在哪里？

**A:** 缓存在 `models/cache/{user_id}/` 目录下，可以手动清理。

### Q: 权重下载失败怎么办？

**A:** 检查：
1. Supabase 配置是否正确
2. 网络连接是否正常
3. 权重文件在存储桶中是否存在

## 🎨 界面说明

### 权重管理页面功能

- **上传区域**：支持点击上传和拖放上传
- **权重列表**：显示所有已上传的权重
- **状态标识**：当前使用的权重显示"当前使用"标签
- **操作按钮**：
  - **使用**：激活该权重用于检测
  - **删除**：删除该权重（需确认）

## 📊 数据流向图

```
┌─────────────┐
│  用户上传   │
└──────┬──────┘
       │
       ↓
┌─────────────┐      ┌──────────────┐
│   后端API   │─────→│   Supabase   │
└──────┬──────┘      │   Storage    │
       │             └──────────────┘
       ↓
┌─────────────┐      ┌──────────────┐
│  数据库记录 │─────→│   Supabase   │
└─────────────┘      │   Database   │
                     └──────────────┘

检测时：
┌─────────────┐
│  检测请求   │
└──────┬──────┘
       │
       ↓
┌─────────────┐      ┌──────────────┐
│  查询活跃   │─────→│   Database   │
│    权重     │      │    (记录)    │
└──────┬──────┘      └──────────────┘
       │
       ↓
┌─────────────┐
│  检查缓存   │
└──────┬──────┘
       │
       ↓ (无缓存)
┌─────────────┐      ┌──────────────┐
│  下载权重   │←─────│   Storage    │
└──────┬──────┘      │   (文件)     │
       │             └──────────────┘
       ↓
┌─────────────┐
│  加载模型   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  执行检测   │
└─────────────┘
```

## 🛠️ 故障排除

### 问题：权重上传失败

**检查项：**
- [ ] Supabase URL 和 Key 配置正确
- [ ] `model-weights` 存储桶已创建
- [ ] 文件大小不超过限制
- [ ] 后端日志中的错误信息

### 问题：检测时提示"请先上传模型"

**解决方法：**
1. 进入权重管理页面
2. 确认是否有权重，且至少一个处于"当前使用"状态
3. 如果没有，上传新权重或激活已有权重

### 问题：权重下载很慢

**优化建议：**
- 第一次下载会较慢，后续使用本地缓存会很快
- 选择距离用户较近的 Supabase 区域
- 检查网络连接质量

## 📚 相关文档

- **完整配置指南**：`MODEL_STORAGE_SETUP.md`
- **Supabase 设置**：`SUPABASE_SETUP.md`
- **API 文档**：见后端代码注释
- **项目总览**：`PROJECT_SUMMARY.md`

## 💡 最佳实践

1. **命名规范**：给权重文件起有意义的名称，并添加描述
2. **定期清理**：删除不再使用的旧权重，节省存储空间
3. **版本管理**：在描述中注明版本号，便于追踪
4. **测试验证**：上传新权重后先用小文件测试
5. **备份重要权重**：重要的权重文件建议在本地也保留备份

## 🎉 完成

现在您已经配置好了权重存储功能！用户上传的权重会自动保存到 Supabase，下次使用时无需重复上传。

如有问题，请查看完整文档 `MODEL_STORAGE_SETUP.md` 或提交 Issue。
