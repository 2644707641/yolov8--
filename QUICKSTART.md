# 快速开始指南

5分钟快速启动YOLOv8智能识别系统。

## 前置要求

- ✅ Node.js 16+ 已安装
- ✅ Python 3.10+ 已安装
- ✅ Supabase账户（免费）

## 步骤1: 克隆或下载项目

```bash
cd yolov8预测停车位
```

## 步骤2: 快速设置（Windows）

双击运行 `setup.bat`，它会自动安装所有依赖。

**或手动安装：**

```bash
# 安装前端依赖
npm install

# 安装后端依赖
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cd ..
```

## 步骤3: 配置Supabase

### 3.1 创建Supabase项目

1. 访问 https://supabase.com
2. 点击 "New Project"
3. 填写项目信息并创建

### 3.2 获取API密钥

在Supabase项目设置 > API 中复制：
- Project URL
- anon public key

### 3.3 配置数据库

在Supabase SQL Editor中执行以下SQL：

```sql
-- 创建检测历史表
CREATE TABLE detection_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  file_type VARCHAR(10) NOT NULL,
  original_file TEXT NOT NULL,
  result_file TEXT NOT NULL,
  detections JSONB,
  params JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 启用行级安全
ALTER TABLE detection_history ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY "Users can view own history"
  ON detection_history FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own history"
  ON detection_history FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own history"
  ON detection_history FOR DELETE
  USING (auth.uid() = user_id);
```

### 3.4 创建存储桶

1. 在Supabase Storage中创建名为 `detection-files` 的桶
2. 设置为 Public
3. 添加存储策略（在SUPABASE_SETUP.md中有详细说明）

## 步骤4: 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
VITE_SUPABASE_URL=你的Supabase项目URL
VITE_SUPABASE_ANON_KEY=你的Supabase匿名密钥
VITE_API_URL=http://localhost:8000
```

复制 `backend/.env.example` 为 `backend/.env`：

```bash
cp backend/.env.example backend/.env
```

## 步骤5: 启动服务

### 方式1: 使用启动脚本（Windows）

双击运行 `start.bat`

### 方式2: 手动启动

**终端1 - 后端：**
```bash
cd backend
venv\Scripts\activate  # Windows
python main.py
```

**终端2 - 前端：**
```bash
npm run dev
```

## 步骤6: 访问应用

打开浏览器访问：
- 前端：http://localhost:3000
- 后端API文档：http://localhost:8000/docs

## 步骤7: 开始使用

1. **注册账户** - 使用邮箱和密码注册
2. **下载YOLOv8模型** - 从 https://github.com/ultralytics/assets/releases 下载预训练模型（如yolov8n.pt）
3. **上传模型** - 在主界面上传下载的.pt文件
4. **调整参数** - 根据需要调整检测参数
5. **上传文件** - 上传图片或视频进行检测
6. **查看结果** - 查看检测结果和历史记录

## 常用命令

```bash
# 启动前端开发服务器
npm run dev

# 构建前端生产版本
npm run build

# 预览生产构建
npm run preview

# 启动后端服务
cd backend
python main.py

# 查看后端API文档
# 访问 http://localhost:8000/docs
```

## 获取YOLOv8模型

### 官方预训练模型

```bash
# YOLOv8n (最快，最小)
https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# YOLOv8s (小型)
https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt

# YOLOv8m (中型)
https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
```

### 使用Python下载

```python
from ultralytics import YOLO

# 自动下载并加载
model = YOLO('yolov8n.pt')
```

## 测试图片和视频

可以使用以下资源进行测试：
- 自己的照片或视频
- https://pixabay.com 免费图片和视频
- https://pexels.com 免费图片和视频

## 故障排除

### 问题：npm install 失败
```bash
# 清理缓存重试
npm cache clean --force
npm install
```

### 问题：Python依赖安装失败
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题：后端启动报错 libGL.so.1
```bash
# Windows通常不会遇到此问题
# Linux解决方法：
sudo apt-get install libgl1-mesa-glx
```

### 问题：Supabase连接失败
- 检查.env文件配置是否正确
- 确认Supabase项目URL和密钥是否正确
- 检查网络连接

### 问题：模型加载失败
- 确保上传的是有效的.pt或.pth文件
- 检查文件大小（至少几MB）
- 尝试使用官方预训练模型

## 下一步

- 📖 阅读完整的 [README.md](./README.md)
- 🚀 查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解如何部署到生产环境
- 🔧 查看 [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) 了解详细的Supabase配置

## 获取帮助

- 📝 查看文档
- 🐛 [提交Issue](../../issues)
- 💬 查看现有Issues中的常见问题

祝您使用愉快！🎉
