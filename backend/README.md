# YOLOv8 Detection API Backend

FastAPI后端服务，提供YOLOv8模型推理功能。

## 功能

- YOLOv8模型上传和管理
- 图片目标检测
- 视频目标检测
- 多用户支持
- 结果文件管理

## 本地开发

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行服务

```bash
# 开发模式（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python main.py
```

访问 http://localhost:8000/docs 查看API文档

## API端点

### 上传模型
```
POST /api/upload-model
Content-Type: multipart/form-data

Body:
- model: 模型文件 (.pt 或 .pth)

Headers:
- Authorization: Bearer {user_id}
```

### 执行检测
```
POST /api/detect
Content-Type: multipart/form-data

Body:
- file: 图片或视频文件
- type: "image" 或 "video"
- params: JSON格式的检测参数

Headers:
- Authorization: Bearer {user_id}
```

### 获取结果
```
GET /api/results/{filename}
```

## Docker部署

```bash
# 构建镜像
docker build -t yolov8-api .

# 运行容器
docker run -p 8000:8000 yolov8-api
```

## 环境变量

```bash
PORT=8000              # 服务端口
HOST=0.0.0.0          # 监听地址
SUPABASE_URL=...      # Supabase URL（可选）
SUPABASE_KEY=...      # Supabase密钥（可选）
```

## 性能调优

### 视频处理优化

默认每5帧处理一次，可以在main.py中调整：

```python
if frame_count % 5 == 0:  # 修改此数字
```

### 内存管理

- 处理完成后自动清理临时文件
- 可以调用 `/api/cleanup/{user_id}` 手动清理

## 支持的YOLOv8模型

- YOLOv8n (Nano) - 最快
- YOLOv8s (Small)
- YOLOv8m (Medium)
- YOLOv8l (Large)
- YOLOv8x (Extra Large) - 最准确

也支持自定义训练的模型。

## 故障排除

### ImportError: libGL.so.1

这是OpenCV的依赖问题，解决方法：

```bash
# Ubuntu/Debian
sudo apt-get install libgl1-mesa-glx

# 或在Dockerfile中添加
RUN apt-get update && apt-get install -y libgl1-mesa-glx
```

### 内存不足

确保服务器至少有512MB可用内存，推荐1GB以上。

### 处理速度慢

- 使用较小的模型（如yolov8n.pt）
- 降低输入图片尺寸
- 减少视频帧率处理频率

## 许可证

MIT
