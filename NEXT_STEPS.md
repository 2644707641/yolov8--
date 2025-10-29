# 🚀 部署前的下一步操作

## 立即执行的命令

### 1. 清理大文件（避免Git提交）

```powershell
# 移除根目录的模型文件
Remove-Item "best.pt" -ErrorAction SilentlyContinue
Remove-Item "best (1).pt" -ErrorAction SilentlyContinue

# 如果这些文件已经被Git追踪，从Git中移除
git rm --cached "best.pt" "best (1).pt"
```

### 2. 提交更新的.gitignore

```powershell
git add .gitignore
git commit -m "chore: 更新.gitignore以排除模型文件"
```

### 3. 推送到GitHub

```powershell
git push origin main
```

---

## 部署顺序

### 第一步: 部署后端到Railway

1. 访问 https://railway.app
2. 连接GitHub仓库
3. 配置环境变量（参见VERCEL_DEPLOYMENT_CHECKLIST.md）
4. **记录Railway提供的URL**（例如: `https://your-app.up.railway.app`）

### 第二步: 部署前端到Vercel

1. 访问 https://vercel.com
2. 导入GitHub仓库
3. 配置环境变量，**特别注意**：
   ```
   VITE_API_URL=<Railway提供的后端URL>
   ```

### 第三步: 测试

1. 访问Vercel前端URL
2. 注册账户
3. 上传YOLOv8模型
4. 测试检测功能

---

## ⚠️ 重要提醒

- **不要**将 `.pt` 模型文件提交到Git
- **不要**在代码中硬编码API密钥
- **记得**在Supabase中配置正确的CORS设置
- **确保**使用 `SUPABASE_KEY`（service_role key）而非 anon key

---

## 💡 有用的命令

### 本地测试

```powershell
# 前端
npm install
npm run dev

# 后端
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

### 查看部署日志

- **Vercel**: 在项目页面 > Deployments > 选择部署 > Runtime Logs
- **Railway**: 在项目页面 > Deployments > View Logs

---

准备好了就可以开始部署了！🎉
