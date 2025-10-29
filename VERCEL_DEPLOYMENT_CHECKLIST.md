# Vercel部署检查清单

## ⚠️ 重要提示

**本项目不能完全部署到Vercel！**

- ✅ 前端可以部署到Vercel
- ❌ 后端必须部署到Railway/Render等支持Docker的平台

---

## 📋 部署前检查清单

### 前端部署到Vercel

- [x] `vercel.json` 配置文件已创建
- [x] `package.json` 构建脚本已配置
- [ ] 在Vercel中配置以下环境变量：
  ```
  VITE_SUPABASE_URL=你的Supabase项目URL
  VITE_SUPABASE_ANON_KEY=你的Supabase匿名密钥
  VITE_API_URL=你的后端API地址（Railway/Render部署后获得）
  ```

### 后端部署到Railway/Render

- [x] `Dockerfile` 已创建
- [x] `requirements.txt` 已配置
- [ ] 在Railway/Render中配置以下环境变量：
  ```
  PORT=8000
  HOST=0.0.0.0
  SUPABASE_URL=你的Supabase项目URL
  SUPABASE_KEY=你的Supabase Service Role Key（不是anon key！）
  SUPABASE_BUCKET=detection-files
  MODEL_WEIGHTS_BUCKET=model-weights
  ```
- [ ] 设置Root Directory为 `backend`（如果需要）

### Supabase配置

- [ ] 已创建 `detection-files` 存储桶
- [ ] 已创建 `model-weights` 存储桶
- [ ] 已配置存储桶RLS策略（参见SUPABASE_SETUP.md）
- [ ] 已创建数据库表（参见SUPABASE_SETUP.md）
- [ ] 在Authentication > URL Configuration中添加前端URL

### Git仓库清理

- [x] `.gitignore` 已更新（排除.pt模型文件）
- [ ] 移除根目录的 `best.pt` 和 `best (1).pt` 文件
- [ ] 确认 `.env` 和 `.env.local` 不会被提交
- [ ] 推送代码到GitHub

---

## 🚀 部署步骤

### 步骤1: 清理大文件

```powershell
# 移除根目录的模型文件（避免Git提交大文件）
Remove-Item "best.pt" -ErrorAction SilentlyContinue
Remove-Item "best (1).pt" -ErrorAction SilentlyContinue

# 如果已经提交过，从Git历史中移除
git rm --cached "*.pt"
git commit -m "Remove large model files from Git"
```

### 步骤2: 部署后端到Railway

1. 访问 https://railway.app
2. 点击 "New Project" > "Deploy from GitHub repo"
3. 选择你的仓库
4. 配置环境变量（见上方清单）
5. 等待部署完成，记录Railway提供的URL

### 步骤3: 部署前端到Vercel

1. 访问 https://vercel.com
2. 点击 "Import Project"
3. 选择你的GitHub仓库
4. 配置环境变量，特别是 `VITE_API_URL`（使用Railway的URL）
5. 点击 "Deploy"

### 步骤4: 验证部署

1. 访问Vercel提供的前端URL
2. 测试注册/登录功能
3. 上传YOLOv8模型（会保存到Supabase Storage）
4. 上传测试图片进行检测
5. 检查历史记录功能

---

## 💰 成本估算

### 免费套餐

- **Vercel**: 100GB带宽/月（前端）
- **Railway**: $5额度/月（后端）
- **Supabase**: 500MB数据库 + 1GB存储

### 注意事项

- YOLOv8推理需要至少512MB内存
- Railway免费额度可能不够长期运行，建议升级到Hobby计划（$5/月）
- 模型文件和检测结果会占用Supabase存储空间，注意定期清理

---

## 🔧 替代方案

### 方案1: 全部部署到Render

- 前端和后端都部署到Render
- 使用Render的Static Site服务部署前端
- 使用Render的Web Service部署后端

### 方案2: 使用VPS

- 购买云服务器（如AWS EC2、DigitalOcean Droplet）
- 使用Docker Compose同时运行前后端
- 适合需要更多控制权和资源的情况

### 方案3: 本地部署

```powershell
# 使用Docker Compose在本地运行
docker-compose up -d
```

---

## ❓ 常见问题

### Q: 为什么后端不能部署到Vercel？

A: Vercel专注于前端和轻量级serverless函数。YOLOv8模型推理需要：
- 长时间运行的进程
- 较大的内存和计算资源
- 大型模型文件（超出50MB限制）

### Q: 模型文件应该如何存储？

A: 
1. **不要**提交到Git（已在.gitignore中排除）
2. **应该**通过前端上传到Supabase Storage
3. 后端从Supabase下载并缓存到本地

### Q: 如何减少部署成本？

A: 
1. 定期清理旧的检测结果
2. 对模型推理实现缓存机制
3. 使用较小的YOLOv8模型（如yolov8n.pt而非yolov8x.pt）
4. 设置请求限流

---

## 📚 相关文档

- [DEPLOYMENT.md](./DEPLOYMENT.md) - 详细部署指南
- [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) - Supabase配置
- [MODEL_STORAGE_SETUP.md](./MODEL_STORAGE_SETUP.md) - 模型存储配置

---

✅ 完成检查清单后，你的项目就可以成功部署了！
