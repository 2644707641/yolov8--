# 部署指南

本文档提供详细的部署步骤和最佳实践。

## 前提条件

- GitHub账户
- Vercel账户（用于前端部署）
- Railway/Render账户（用于后端部署）
- Supabase账户（已按照SUPABASE_SETUP.md配置完成）

## 部署架构

```
用户浏览器
    ↓
Vercel (前端 - Vue3应用)
    ↓
Railway/Render (后端 - FastAPI服务)
    ↓
Supabase (数据库 + 存储)
```

## 步骤1: 准备代码仓库

### 1.1 初始化Git仓库

```bash
git init
git add .
git commit -m "Initial commit: YOLOv8 Detection System"
```

### 1.2 推送到GitHub

```bash
# 在GitHub上创建新仓库
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

## 步骤2: 部署后端到Railway

### 2.1 创建Railway项目

1. 访问 https://railway.app
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择你的仓库
5. Railway会自动检测到Dockerfile

### 2.2 配置环境变量

在Railway项目设置中添加：

```
PORT=8000
HOST=0.0.0.0
SUPABASE_URL=你的Supabase URL
SUPABASE_KEY=你的Supabase服务密钥
```

### 2.3 配置根目录

如果Railway没有自动检测到backend目录：

1. 进入Settings
2. 在 "Root Directory" 设置为 `backend`

### 2.4 获取部署URL

部署完成后，Railway会提供一个公开URL，类似：
```
https://your-app-name.up.railway.app
```

记下这个URL，后面会用到。

## 步骤3: 部署前端到Vercel

### 3.1 导入项目

1. 访问 https://vercel.com
2. 点击 "Add New Project"
3. 从GitHub导入你的仓库
4. Vercel会自动检测到Vite项目

### 3.2 配置环境变量

在Vercel项目设置中添加环境变量：

```
VITE_SUPABASE_URL = 你的Supabase URL
VITE_SUPABASE_ANON_KEY = 你的Supabase匿名密钥
VITE_API_URL = 你的Railway后端URL (如: https://your-app.up.railway.app)
```

### 3.3 配置构建设置

Vercel通常会自动配置，但请确认：

- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### 3.4 部署

点击 "Deploy" 开始部署。

## 步骤4: 配置Supabase

### 4.1 更新CORS设置

在Supabase项目设置中：

1. 进入 Authentication > URL Configuration
2. 在 "Site URL" 添加你的Vercel部署URL
3. 在 "Redirect URLs" 添加：
   - `https://your-vercel-app.vercel.app/*`

### 4.2 验证存储权限

确保 `detection-files` 存储桶的策略正确配置（参见SUPABASE_SETUP.md）

## 步骤5: 测试部署

### 5.1 测试流程

1. 访问你的Vercel应用URL
2. 注册新用户
3. 上传YOLOv8模型
4. 上传测试图片
5. 检查检测结果
6. 验证历史记录功能

### 5.2 检查日志

**Vercel日志**:
- 在Vercel项目页面点击 "Deployments"
- 选择最新部署，查看 "Runtime Logs"

**Railway日志**:
- 在Railway项目页面点击 "Deployments"
- 查看实时日志

**Supabase日志**:
- 在Supabase项目中点击 "Logs"
- 查看API请求和错误日志

## 备选部署方案

### 后端部署到Render

#### 1. 创建Web Service

1. 访问 https://render.com
2. 点击 "New +" > "Web Service"
3. 连接GitHub仓库

#### 2. 配置设置

- **Name**: yolov8-detection-api
- **Environment**: Python 3
- **Region**: 选择最近的区域
- **Branch**: main
- **Root Directory**: backend
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 3. 环境变量

```
SUPABASE_URL=你的Supabase URL
SUPABASE_KEY=你的Supabase服务密钥
```

#### 4. 实例类型

选择至少 512MB RAM 的实例，因为YOLOv8需要一定的内存。

### 使用Docker Compose本地部署

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/models:/app/models
      - ./backend/results:/app/results

  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - VITE_SUPABASE_URL=${VITE_SUPABASE_URL}
      - VITE_SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY}
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
```

运行：
```bash
docker-compose up -d
```

## 性能优化建议

### 前端优化

1. **代码分割**: Vue Router已配置懒加载
2. **图片优化**: 使用WebP格式
3. **CDN**: Vercel自动提供CDN加速
4. **缓存**: 配置适当的缓存策略

### 后端优化

1. **模型缓存**: 加载一次模型，多次使用
2. **异步处理**: 对于大视频文件，考虑使用任务队列
3. **限流**: 添加请求限流防止滥用
4. **文件清理**: 定期清理旧的临时文件

### 数据库优化

1. **索引**: 已在表上创建索引
2. **分页**: 历史记录添加分页
3. **定期清理**: 删除旧的检测记录

## 监控和维护

### 性能监控

**Vercel Analytics**:
- 在Vercel项目中启用Analytics
- 监控页面加载时间和Web Vitals

**Railway Metrics**:
- 查看CPU和内存使用情况
- 设置告警

**Supabase Monitoring**:
- 监控API请求数
- 检查存储空间使用

### 日志管理

设置日志聚合服务，如：
- Sentry（错误跟踪）
- LogTail（日志管理）
- DataDog（全面监控）

### 备份策略

**Supabase数据**:
- 启用自动备份
- 定期导出数据

**存储文件**:
- 配置存储桶复制
- 定期下载重要文件

## 故障排除

### 常见问题

**问题1: CORS错误**
```
解决方案：
1. 检查后端CORS配置
2. 确保前端API_URL正确
3. 验证Supabase URL配置
```

**问题2: 模型加载失败**
```
解决方案：
1. 检查服务器内存是否足够（至少512MB）
2. 验证模型文件完整性
3. 查看后端日志详细错误
```

**问题3: 文件上传失败**
```
解决方案：
1. 检查Supabase存储桶权限
2. 验证文件大小限制
3. 确认网络连接稳定
```

**问题4: 部署后环境变量未生效**
```
解决方案：
1. 重新部署应用
2. 清除浏览器缓存
3. 检查变量名称是否正确
```

### 获取帮助

如果遇到问题：
1. 检查项目日志
2. 查看README.md常见问题部分
3. 在GitHub提交Issue
4. 查看Vercel/Railway/Supabase官方文档

## 安全检查清单

- [ ] 环境变量正确配置
- [ ] Supabase RLS策略已启用
- [ ] CORS配置为特定域名
- [ ] API请求有适当的认证
- [ ] 文件上传有大小限制
- [ ] 定期更新依赖包
- [ ] 启用HTTPS
- [ ] 配置安全头部

## 成本估算

### 免费套餐使用情况

**Vercel**:
- 免费套餐包含100GB带宽/月
- 适合个人项目和小型应用

**Railway**:
- 免费套餐提供$5额度/月
- 够用于开发和测试

**Supabase**:
- 免费套餐包含500MB数据库，1GB存储
- 50,000次月活跃用户

### 升级建议

当应用扩展时考虑升级：
- Vercel Pro: $20/月
- Railway Hobby: $5/月
- Supabase Pro: $25/月

## 下一步

部署成功后，可以考虑：

1. 添加更多功能（批量处理、模型对比等）
2. 优化UI/UX
3. 添加数据分析面板
4. 实现API限流和配额
5. 添加自动化测试
6. 设置CI/CD流程

恭喜！你的YOLOv8智能识别系统现已成功部署！🎉
