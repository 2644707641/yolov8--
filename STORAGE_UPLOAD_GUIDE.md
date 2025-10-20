# 存储桶上传功能说明

本文档说明如何配置和使用YOLOv8识别系统的存储桶上传功能。

## 功能概述

系统现在支持将**原始图片**和**识别后的图片**都自动上传到Supabase存储桶，具体流程如下：

1. 用户上传图片/视频到后端
2. 后端使用YOLOv8进行识别处理
3. **后端自动上传原始文件到Supabase存储桶**
4. **后端自动上传识别结果文件到Supabase存储桶**
5. 后端将检测记录保存到Supabase数据库
6. 前端显示结果（优先使用Supabase URL）

## 配置步骤

### 1. 后端配置

在 `backend/.env` 文件中添加Supabase配置：

```bash
# Supabase配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
```

**重要：** 
- 必须使用 **service_role key**（服务角色密钥），而不是 anon key
- service_role key 在 Supabase控制台 Settings > API > Service role 中获取
- 该密钥拥有绕过RLS策略的权限，请妥善保管，不要泄露

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

新增的依赖包括：
- `supabase==2.3.0` - Supabase Python客户端

### 3. Supabase存储桶配置

按照 `SUPABASE_SETUP.md` 中的说明创建 `detection-files` 存储桶。

文件将按以下结构存储：

```
detection-files/
├── {user_id}/
│   ├── images/
│   │   ├── original/          # 原始图片
│   │   │   └── {timestamp}.jpg
│   │   └── results/           # 识别后的图片
│   │       └── {timestamp}.jpg
│   └── videos/
│       ├── original/          # 原始视频
│       │   └── {timestamp}.mp4
│       └── results/           # 识别后的视频
│           └── {timestamp}.mp4
```

## 工作流程

### 后端处理流程

1. **接收文件**：接收用户上传的图片/视频
2. **YOLOv8检测**：进行目标检测
3. **保存结果到本地**：临时保存识别结果
4. **上传到Supabase**：
   - 上传原始文件到 `{user_id}/{type}s/original/` 路径
   - 上传结果文件到 `{user_id}/{type}s/results/` 路径
5. **保存到数据库**：将检测记录和文件URL保存到 `detection_history` 表
6. **清理本地文件**：删除临时的原始文件
7. **返回结果**：返回包含Supabase URL的响应

### API响应格式

```json
{
  "success": true,
  "resultUrl": "/api/results/result_xxx.jpg",          // 本地API URL（备用）
  "originalUrlSupabase": "https://xxx.supabase.co/...", // 原始文件的Supabase URL
  "resultUrlSupabase": "https://xxx.supabase.co/...",   // 结果文件的Supabase URL
  "detections": [...],
  "processTime": 1.23,
  "params": {...}
}
```

### 前端处理流程

前端现在简化了逻辑：

1. **发送请求**：将文件发送到后端API
2. **接收响应**：获取包含Supabase URL的响应
3. **显示结果**：优先使用 `originalUrlSupabase` 和 `resultUrlSupabase`
4. **加载历史记录**：从数据库获取历史记录

## 优势

### ✅ 相比之前的改进

**之前的方案（前端上传）：**
- 前端异步上传，可能失败
- 网络问题导致上传不稳定
- 重复下载结果文件再上传，浪费带宽

**现在的方案（后端上传）：**
- 后端直接上传，更可靠
- 原始文件和结果文件都在后端处理，无需重复传输
- 统一的错误处理
- 自动清理临时文件

### ✅ 主要优势

1. **可靠性高**：后端处理确保上传成功
2. **性能好**：减少网络传输，节省带宽
3. **管理方便**：所有文件统一存储在Supabase
4. **可追溯**：数据库记录完整的检测历史
5. **支持分享**：公共URL可以直接访问

## 故障排查

### 问题：文件上传失败

**可能原因：**
1. Supabase配置错误
2. 存储桶不存在或权限配置错误
3. 网络连接问题

**解决方法：**
1. 检查 `backend/.env` 中的配置是否正确
2. 确认使用的是 service_role key
3. 检查 Supabase 控制台中存储桶是否已创建
4. 查看后端日志获取详细错误信息

### 问题：图片无法显示

**可能原因：**
1. 存储桶未设置为公开
2. URL格式错误

**解决方法：**
1. 在 Supabase 控制台将 `detection-files` 存储桶设置为 Public
2. 检查返回的URL是否正确

### 调试模式

后端会输出详细日志，包括：
- `[INFO] 正在上传文件到Supabase: {path}`
- `[INFO] 文件上传成功: {url}`
- `[ERROR] 上传文件到Supabase失败: {error}`

## 注意事项

1. **Service Role Key安全**：
   - 不要将 service_role key 提交到版本控制
   - 不要在前端代码中使用 service_role key
   - 定期轮换密钥

2. **存储空间管理**：
   - Supabase免费计划有存储限制
   - 定期清理不需要的文件
   - 考虑实现文件过期自动删除功能

3. **成本考虑**：
   - 大量上传会消耗带宽和存储空间
   - 根据实际使用情况选择合适的Supabase计划

4. **备用方案**：
   - 如果Supabase未配置，系统会自动降级到本地存储
   - 本地结果仍可通过 `/api/results/{filename}` 访问

## 测试

### 测试上传功能

1. 启动后端：
   ```bash
   cd backend
   python main.py
   ```

2. 启动前端：
   ```bash
   npm run dev
   ```

3. 上传模型并进行检测

4. 检查：
   - 后端日志中是否显示上传成功
   - Supabase存储桶中是否有文件
   - 数据库中是否有记录
   - 前端是否正确显示结果

## 未来改进

- [ ] 实现文件自动压缩
- [ ] 支持批量上传
- [ ] 添加文件过期自动删除
- [ ] 实现文件下载功能
- [ ] 添加上传进度显示
- [ ] 支持更多文件格式
