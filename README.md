# YOLOv8 智能识别停车位系统

一个基于YOLOv8的图像和视频目标检测Web应用，使用Vue3 + FastAPI构建，支持用户认证、历史记录管理等功能。

## 🆕 最近更新 (2025-10-19)

### 🎉 v1.2.0 - 参数扩展 & 视频优化 ⭐

**重大更新**：
- ✨ **参数范围扩展** - 图片大小160-1920、置信度0.01-0.99、IOU 0.05-0.95、最大检测数10-2000
- 🎬 **视频帧间隔控制** ⭐新增 - frameSkip参数1-10可调，1=最流畅
- ✅ **修复视频卡顿** - 默认每帧检测，检测框不再跳跃
- 📦 **FFmpeg优化** - 视频更流畅、文件更小
- 📚 **完整文档** - PARAMETER_GUIDE.md、VIDEO_OPTIMIZATION.md

📝 详细说明: [VERSION_1.2.0_NOTES.md](./VERSION_1.2.0_NOTES.md)

---

### 🔄 v1.1.0 - 重新开始功能 (2025-10-18)
- ✨ 重新开始按钮
- 🐛 修复文件输入框bug
- 🔧 默认参数优化

### 🎉 全新左右联动式交互界面

重构了Dashboard页面，采用现代化的左右分栏布局：

- **左侧导航栏** (固定320px宽度)：
  - 清晰的步骤引导：① 上传模型 → ② 上传文件 → ③ 调整参数 → ④ 识别结果
  - 实时进度显示：已完成的步骤显示绿色✅勾选标记
  - 当前步骤高亮显示：蓝色背景 + 阴影效果
  - 操作提示卡片：帮助用户理解流程

- **右侧主展示区** (自适应宽度)：
  - **步骤1 - 上传模型权重**：大型拖拽上传区域 + 状态反馈 + 自动跳转
  - **步骤2 - 上传文件**：图片/视频选择卡片 + 文件选择器 + 自动跳转
  - **步骤3 - 调整参数**：美观的参数滑块 + 实时预览 + 操作按钮
  - **步骤4 - 识别结果**：处理动画 + 统计卡片 + 对比展示 + 预览功能

- **交互体验优化**：
  - 点击左侧导航，右侧即时显示对应内容
  - 完成一步后自动进入下一步
  - 支持随时切换任意步骤
  - 流程式操作，新手友好

## ✨ 功能特性

### 🎨 界面交互
- 🎉 **左右联动布局** - 现代化分栏设计，左侧导航，右侧展示
- 📌 **步骤引导** - 4步流程式操作，清晰直观
- ✅ **进度跟踪** - 实时显示当前步骤和完成状态
- 🎭 **智能跳转** - 完成一步自动进入下一步

### 🔧 核心功能
- 🔐 **用户认证系统** - 基于Supabase的注册/登录功能
- 📤 **模型上传** - 支持上传自定义YOLOv8权重文件 (.pt, .pth)
- 🎛️ **参数调节** - 可视化调整检测参数：
  - 图片大小 (160-1920px) ✨扩展
  - 置信度阈值 (0.01-0.99) ✨精度提升
  - IOU阈值 (0.05-0.95) ✨精度提升
  - 最大检测数 (10-2000) ✨扩展
  - 视频帧间隔 (1-10) ⭐新增
- 🖼️ **图片检测** - 上传图片进行目标检测
- 🎬 **视频检测** - 上传视频进行实时目标检测
- 📊 **结果展示** - 对比显示原始文件和检测结果
- 📋 **历史记录** - 查看和管理所有检测历史
- ☁️ **云存储** - 后端自动将原始图片和识别后图片都上传到Supabase存储桶

## 🛠️ 技术栈

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue状态管理
- **Vue Router** - 路由管理
- **Tailwind CSS** - 实用优先的CSS框架
- **Supabase** - 后端即服务平台

### 后端
- **FastAPI** - 现代Python Web框架
- **Ultralytics YOLOv8** - 最先进的目标检测模型
- **OpenCV** - 计算机视觉库
- **Python 3.10+** - 编程语言

## 📋 环境要求

- Node.js 16+
- Python 3.10+
- npm 或 yarn
- Supabase账户

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd yolov8预测停车位
```

### 2. 配置Supabase

请参考 [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) 完成Supabase配置。

### 3. 前端设置

```bash
# 安装依赖
npm install

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入Supabase配置
# VITE_SUPABASE_URL=你的Supabase URL
# VITE_SUPABASE_ANON_KEY=你的Supabase匿名密钥
# VITE_API_URL=http://localhost:8000

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动

### 4. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入Supabase配置
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your_service_role_key

# 启动后端服务
python main.py
```

后端将在 http://localhost:8000 启动

**重要：** 后端必须配置Supabase环境变量才能实现文件上传功能。详细配置请查看 [STORAGE_UPLOAD_GUIDE.md](./STORAGE_UPLOAD_GUIDE.md)

## 📱 使用指南

### 🚀 快速上手

#### 1️⃣ 注册/登录
- 访问应用并注册新账户
- 使用邮箱和密码登录

#### 2️⃣ 步骤1：上传模型权重
- 点击左侧“上传模型权重”按钮
- 在右侧拖拽或点击上传YOLOv8模型文件 (.pt 或 .pth)
- 等待上传成功，显示绿色✅后点击“下一步”

#### 3️⃣ 步骤2：上传文件
- 点击左侧“上传文件”按钮
- 选择文件类型：🖼️ 图片 或 🎬 视频
- 上传要检测的文件
- 选择完成后点击“下一步”

#### 4️⃣ 步骤3：调整参数
- 点击左侧“调整参数”按钮
- 根据需要调整以下参数：
  - **图片大小** (160-1920px)：较大的尺寸可以检测更小的物体
  - **置信度阈值** (0.01-0.99)：较高的阈值减少误检
  - **IOU阈值** (0.05-0.95)：用于去除重叠检测框
  - **最大检测数** (10-2000)：限制检测数量
  - **视频帧间隔** (1-10) ⭐新增：仅视频可用，1=最流畅，10=最快
- 点击“开始识别 🚀”按钮

💡 **参数选择技巧**: 查看 [PARAMETER_GUIDE.md](./PARAMETER_GUIDE.md) 获取详细说明

#### 5️⃣ 步骤4：查看识别结果
- 系统自动跳转到结果页面
- 查看检测统计信息：检测数量、置信度、处理时间
- 对比原图与识别结果
- 使用操作按钮：
  - 🔍 查看原图
  - 🔍 查看结果
  - 🔄 对比预览

### 📊 查看历史记录
- 点击顶部导航栏的“历史记录”
- 浏览所有检测历史
- 点击“查看详情”查看完整结果
- 点击“删除”移除不需要的记录

## 🌐 部署

### 前端部署到Vercel

1. 将代码推送到GitHub

2. 在Vercel中导入项目

3. 配置环境变量：
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_API_URL`

4. 部署

### 后端部署选项

#### 选项1: Railway

1. 访问 [Railway.app](https://railway.app)
2. 从GitHub导入项目
3. 选择 `backend` 目录
4. 配置环境变量
5. 部署

#### 选项2: Render

1. 访问 [Render.com](https://render.com)
2. 创建新的Web Service
3. 连接GitHub仓库
4. 设置构建命令和启动命令
5. 配置环境变量
6. 部署

#### 选项3: Docker部署

```bash
cd backend
docker build -t yolov8-api .
docker run -p 8000:8000 yolov8-api
```

## 📂 项目结构

```
yolov8预测停车位/
├── src/                      # 前端源代码
│   ├── components/          # Vue组件
│   ├── views/              # 页面视图
│   ├── stores/             # Pinia状态管理
│   ├── router/             # Vue Router配置
│   ├── config/             # 配置文件
│   ├── App.vue             # 根组件
│   ├── main.js             # 入口文件
│   └── style.css           # 全局样式
├── backend/                 # 后端源代码
│   ├── main.py             # FastAPI应用
│   ├── requirements.txt    # Python依赖
│   ├── check_ffmpeg.py     # FFmpeg检查工具 ✨
│   ├── video_fix_utils.py  # 视频优化工具 ✨
│   ├── Dockerfile          # Docker配置
│   └── .env.example        # 环境变量示例
├── public/                  # 静态资源
├── package.json            # npm配置
├── vite.config.js          # Vite配置
├── tailwind.config.js      # Tailwind CSS配置
├── vercel.json             # Vercel配置
├── .env.example            # 前端环境变量示例
├── best.pt                 # YOLOv8训练模型
├── 停车.mp4                # 测试视频
├── install_ffmpeg.bat      # FFmpeg安装脚本 ✨
├── SUPABASE_SETUP.md       # Supabase配置指南
├── STORAGE_UPLOAD_GUIDE.md # 存储桶上传功能说明
├── PARAMETER_GUIDE.md      # 参数完整指南 ⭐新增
├── VIDEO_OPTIMIZATION.md   # 视频优化指南 ⭐新增
├── VERSION_1.2.0_NOTES.md  # v1.2.0更新说明 ⭐新增
└── README.md               # 项目文档
```

## 🔧 配置说明

### 检测参数详解

| 参数 | 范围 | 默认值 | 说明 |
|------|------|--------|------|
| imgSize | **160-1920** ✨ | 640 | 输入图片尺寸，影响检测精度和速度 |
| confidence | **0.01-0.99** ✨ | 0.5 | 置信度阈值，过滤低可信度的检测 |
| iouThreshold | **0.05-0.95** ✨ | 0.6 | IOU阈值，用于NMS去除重叠框 |
| maxDetections | **10-2000** ✨ | 300 | 单张图片最大检测数量 |
| frameSkip | **1-10** ⭐ | 1 | 视频帧间隔，1=每帧检测（最流畅） |

📖 **详细参数说明**: 查看 [PARAMETER_GUIDE.md](./PARAMETER_GUIDE.md)

### API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/upload-model` | POST | 上传YOLOv8模型 |
| `/api/detect` | POST | 执行检测 |
| `/api/results/{filename}` | GET | 获取结果文件 |
| `/api/cleanup/{user_id}` | DELETE | 清理用户临时文件 |

## 🐛 常见问题

### Q: 模型上传失败？
A: 请确保上传的是有效的YOLOv8模型文件（.pt或.pth格式），可以先使用官方预训练模型测试。

### Q: 检测速度很慢？
A: 可以尝试：
- 减小图片尺寸
- 降低视频帧率处理
- 使用更快的YOLOv8模型（如yolov8n.pt）

### Q: 视频播放卡顿或检测框跳跃？
A: 
- 设置 `frameSkip=1`（每帧检测）获得最流畅效果
- 安装FFmpeg以优化视频编码：运行 `install_ffmpeg.bat`
- 查看 [VIDEO_OPTIMIZATION.md](./VIDEO_OPTIMIZATION.md)

### Q: 部署到生产环境需要注意什么？
A: 
- 修改CORS配置，只允许特定域名
- 使用环境变量管理敏感信息
- 配置文件大小限制
- 设置自动清理机制删除旧文件

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题，请提交Issue或联系项目维护者。

## 🙏 致谢

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Vue.js](https://vuejs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Supabase](https://supabase.com/)
- [Tailwind CSS](https://tailwindcss.com/)
