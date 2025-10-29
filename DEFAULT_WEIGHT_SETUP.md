# 默认权重配置指南

本文档将指导您如何配置默认权重文件（`best.pt`），使每个新用户都可以自动使用该权重进行检测。

## 功能说明

配置默认权重后，系统将具有以下特性：

- **新用户无需上传权重**：注册后即可直接使用检测功能
- **自动降级机制**：用户没有自定义权重时，自动使用默认权重
- **灵活切换**：用户可以上传自己的权重来替代默认权重
- **节省存储**：所有用户共享一个默认权重文件

## 配置步骤

### 1. 准备权重文件

确保您有一个训练好的 YOLOv8 权重文件（例如 `best.pt`）。

### 2. 上传权重到 Supabase Storage

#### 方式A：通过 Supabase 控制台上传（推荐）

1. 登录 [Supabase](https://supabase.com) 控制台
2. 选择您的项目
3. 点击左侧的 **Storage**
4. 选择 `model-weights` 存储桶（如果不存在，请先创建）
5. 在存储桶中创建 `default` 文件夹
6. 点击 **Upload** 按钮，上传您的 `best.pt` 文件
7. 上传后，文件路径应该是：`default/best.pt`

#### 方式B：使用 Supabase CLI

```bash
# 安装 Supabase CLI
npm install -g supabase

# 登录
supabase login

# 上传文件
supabase storage upload model-weights/default/best.pt ./best.pt
```

#### 方式C：使用 Python 脚本

创建一个脚本 `upload_default_weight.py`：

```python
from supabase import create_client
import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 创建客户端
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 读取权重文件
weight_file_path = Path("best.pt")
with open(weight_file_path, "rb") as f:
    file_content = f.read()

# 上传到 Supabase
storage_path = "default/best.pt"
supabase.storage.from_("model-weights").upload(
    path=storage_path,
    file=file_content,
    file_options={"content-type": "application/octet-stream"},
)

print(f"✅ 默认权重上传成功: {storage_path}")
```

运行脚本：

```bash
python upload_default_weight.py
```

### 3. 配置环境变量

在项目根目录的 `.env` 文件中添加或确认以下配置：

```bash
# 默认权重配置
DEFAULT_MODEL_PATH=default/best.pt
DEFAULT_MODEL_NAME=默认停车位检测模型
```

如果您使用了不同的文件名或路径，请相应调整 `DEFAULT_MODEL_PATH`。

### 4. 重启后端服务

修改配置后，需要重启后端服务以使配置生效：

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
cd backend
python main.py

# 或使用提供的批处理文件
.\restart_backend.bat
```

### 5. 验证配置

#### 测试方法1：通过日志验证

1. 使用一个没有上传权重的新账户
2. 尝试进行检测
3. 查看后端日志，应该看到类似信息：

```
INFO: 用户没有自定义权重，尝试使用默认权重
INFO: 使用默认权重: 默认停车位检测模型
```

#### 测试方法2：通过API验证

发送检测请求，确保返回成功：

```bash
curl -X POST http://localhost:8000/api/detect \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@test_image.jpg" \
  -F "type=image" \
  -F "params={\"conf\":0.25,\"iou\":0.45}"
```

## 工作流程

系统查找权重的优先级顺序：

1. **用户自定义权重**：优先使用用户上传并激活的权重
2. **本地注册表权重**：如果没有 Supabase 权重，使用本地上传的权重
3. **默认权重**：如果用户没有任何自定义权重，使用默认权重
4. **报错**：如果默认权重也不存在，返回错误提示

```
┌─────────────────────────────┐
│   用户发起检测请求           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 是否有活跃的自定义权重？     │
└──────────┬──────────────────┘
           │
       ┌───┴───┐
      是        否
       │         │
       ▼         ▼
┌────────┐  ┌────────────┐
│使用自定│  │是否有本地权│
│义权重  │  │重？        │
└────────┘  └─────┬──────┘
                  │
              ┌───┴───┐
             是        否
              │         │
              ▼         ▼
        ┌────────┐  ┌─────────┐
        │使用本地│  │是否配置了│
        │权重    │  │默认权重？│
        └────────┘  └────┬────┘
                         │
                     ┌───┴───┐
                    是        否
                     │         │
                     ▼         ▼
              ┌─────────┐  ┌────────┐
              │使用默认│  │返回错误│
              │权重    │  └────────┘
              └─────────┘
```

## 更新默认权重

如果需要更新默认权重（例如使用新训练的模型）：

1. 在 Supabase Storage 中删除旧的 `default/best.pt`
2. 上传新的权重文件到相同路径
3. 清理本地缓存（可选）：

```bash
# 删除本地缓存的默认权重
rm -rf models/cache/default/
```

4. 用户下次检测时将自动下载新的默认权重

## 存储策略配置

确保 Supabase Storage 的权限配置正确，允许服务端访问默认权重：

```sql
-- 允许服务角色读取默认权重
CREATE POLICY "Service role can read default weights"
  ON storage.objects
  FOR SELECT
  TO service_role
  USING (
    bucket_id = 'model-weights' 
    AND name LIKE 'default/%'
  );
```

## 常见问题

### Q: 默认权重存储在哪里？

A: 默认权重存储在 Supabase Storage 的 `model-weights` 存储桶中，路径为 `default/best.pt`。系统首次使用时会下载到本地缓存 `models/cache/default/best.pt`。

### Q: 用户上传自己的权重后，还会使用默认权重吗？

A: 不会。一旦用户上传了自己的权重，系统会优先使用用户的自定义权重。只有在用户没有任何自定义权重时，才会使用默认权重。

### Q: 默认权重文件多大？

A: YOLOv8 权重文件通常在 6-50MB 之间，具体取决于模型大小（nano/small/medium/large/xlarge）。

### Q: 是否可以为不同用户设置不同的默认权重？

A: 当前版本所有用户共享同一个默认权重。如需为特定用户设置专用权重，可以通过管理员账户上传权重到该用户的账号下。

### Q: 默认权重下载失败怎么办？

A: 检查以下几点：
1. 确认 `DEFAULT_MODEL_PATH` 配置正确
2. 确认 Supabase Storage 中文件存在
3. 检查 Supabase 服务角色密钥是否配置正确
4. 查看后端日志获取详细错误信息

### Q: 如何禁用默认权重功能？

A: 如果您希望强制所有用户上传自己的权重，可以：
1. 不在 Supabase 中上传默认权重文件
2. 或将 `DEFAULT_MODEL_PATH` 设置为空字符串

## 优势

使用默认权重的优势：

- ✅ **降低用户门槛**：新用户无需了解模型训练即可使用
- ✅ **快速体验**：注册后立即可以测试检测功能
- ✅ **节省存储**：避免多个用户重复上传相同的权重
- ✅ **统一管理**：管理员可以集中管理和更新默认权重
- ✅ **灵活扩展**：用户可以随时上传自己的权重来提升检测效果

## 安全建议

1. **权限控制**：确保只有服务角色（Service Role）可以访问默认权重
2. **版本管理**：建议使用版本号命名权重文件，如 `default/best_v1.0.pt`
3. **备份**：定期备份默认权重文件到本地
4. **监控**：监控默认权重的下载次数和失败率

## 下一步

完成默认权重配置后，您可以：

1. 测试新用户注册并使用检测功能
2. 更新用户文档，说明默认权重功能
3. 考虑添加权重管理界面，让管理员可以在前端更新默认权重
4. 实现权重版本管理和回滚功能

如有问题，请查看项目的其他文档：
- [MODEL_STORAGE_SETUP.md](./MODEL_STORAGE_SETUP.md) - 权重存储详细配置
- [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) - Supabase 基础配置
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 故障排查指南
