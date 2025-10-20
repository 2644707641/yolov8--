# 项目修改总结与错误须知

> 记录本次修改内容、遇到的问题及避免错误的最佳实践

## 📋 本次修改内容

### 1. ✅ Supabase 存储桶集成

**后端修改** (`backend/main.py`):
- 添加 Supabase 客户端初始化
- 实现文件上传到存储桶功能
- 实现检测记录保存到数据库
- 修改 `/api/detect` 端点自动上传文件

**关键依赖** (`backend/requirements.txt`):
```txt
supabase==2.9.0
httpx==0.27.0
websockets==13.0
```

**环境配置** (`backend/.env`):
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key  # 必须使用 service_role key
```

### 2. 🖼️ 历史记录页面优化 (`src/views/History.vue`)

**新增功能**:
- ✅ 原始图片和结果图片并排显示
- ✅ 图片预览模态框（支持三种模式：original / result / both）
- ✅ 图片缩放功能（50%-500%，按钮+滚轮）
- ✅ 图片拖动功能（鼠标拖拽）
- ✅ 智能边界处理（对比模式有边界，单图模式无边界）

### 3. 📊 Dashboard 页面优化 (`src/views/Dashboard.vue`)

**同步历史记录的所有预览功能**:
- 图片悬停效果
- 点击预览功能
- 对比预览按钮
- 完整的缩放和拖动功能

### 4. 🗑️ 批量删除功能 (`src/views/History.vue`)

**功能实现**:
- ✅ 批量管理模式开关
- ✅ 单选/全选功能
- ✅ 视觉反馈（选中边框高亮）
- ✅ 批量删除操作
- ✅ 删除前确认对话框

---

## 🐛 遇到的问题与解决方案

### 问题 1: Supabase 初始化失败 - "Invalid API key"

**错误信息**: `[WARNING] Supabase客户端初始化失败: Invalid API key`

**原因**:
1. 使用了 `anon` (public) key 而不是 `service_role` key
2. API key 被截断或不完整

**解决方案**:
```bash
# 确保使用完整的 service_role key（约 219 字符）
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3M...（完整密钥）

# 添加调试验证
print(f"[DEBUG] SUPABASE_KEY 长度: {len(supabase_key)} 字符")
```

**须知**:
- ❌ 不要使用 anon/public key 在后端
- ✅ 后端使用 service_role key，前端使用 anon key

---

### 问题 2: Websockets 版本兼容性错误

**错误信息**: 
```
TypeError: __init__() got an unexpected keyword argument 'proxy'
ModuleNotFoundError: No module named 'websockets.asyncio'
```

**解决方案**:
```bash
pip uninstall websockets -y
pip install websockets==13.0
pip install supabase==2.9.0
```

**须知**: 始终检查包依赖兼容性，使用固定版本号

---

### 问题 3: 检测参数类型错误

**错误信息**: `'conf=0.4' is of invalid type str`

**原因**: JSON 解析后参数可能是字符串，YOLOv8 要求数字类型

**解决方案**:
```python
# ❌ 错误
img_size = detection_params.get('imgSize', 640)

# ✅ 正确：显式类型转换
img_size = int(detection_params.get('imgSize', 640))
confidence = float(detection_params.get('confidence', 0.25))
iou_threshold = float(detection_params.get('iouThreshold', 0.45))
max_det = int(detection_params.get('maxDetections', 300))
```

**须知**: 对外部输入永远不要信任类型，始终显式转换

---

### 问题 4: 登录输入框无法输入

**原因**: 调试代码和内联样式干扰正常输入

**问题代码**:
```vue
<input
  @click="console.log('点击')"
  style="pointer-events: auto;"
/>
```

**解决方案**: 移除所有调试代码和不必要的内联样式

**须知**: 生产代码中应移除所有 console.log 和调试属性

---

### 问题 5: 图片预览边界处理

**需求**: 对比模式有边界，单图模式无边界

**解决方案**:
```vue
<div :class="[
  'relative cursor-move w-full h-full',
  previewMode === 'both' ? 'overflow-hidden' : ''
]">
  <img :style="{
    transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
    transformOrigin: 'center center'
  }" />
</div>
```

---

## ⚠️ 重要须知与最佳实践

### 1. 环境变量配置

```bash
# ❌ 错误：硬编码敏感信息
const SUPABASE_KEY = "eyJhbGciO..."

# ✅ 正确：使用环境变量
SUPABASE_KEY=eyJhbGciO...
```

**检查清单**:
- [ ] `.env` 文件存在且配置正确
- [ ] 使用 service_role key
- [ ] `.env` 已添加到 `.gitignore`
- [ ] 提供 `.env.example` 模板

### 2. 类型安全

```python
# ✅ Python：显式类型转换
size = int(params.get('size', 640))
conf = float(params.get('confidence', 0.25))

# ✅ 添加验证
if not 320 <= size <= 1280:
    raise ValueError("Size must be between 320 and 1280")
```

### 3. 错误处理

```python
# 后端：完整错误处理
try:
    result = model.predict(image)
    print(f"[INFO] 检测完成")
except Exception as e:
    print(f"[ERROR] 检测失败: {e}")
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=str(e))
```

```javascript
// 前端：友好错误提示
try {
  const result = await detectionStore.runDetection(file, type)
  if (!result.success) {
    alert(`识别失败: ${result.error}`)
  }
} catch (error) {
  console.error('[ERROR]', error)
  alert('识别过程中发生错误，请重试')
}
```

### 4. 调试代码管理

**生产环境前检查**:
```bash
# 搜索所有 console.log
grep -r "console.log" src/

# 搜索调试属性
grep -r "@click=\"console" src/
```

**使用环境变量控制**:
```javascript
const DEBUG = import.meta.env.DEV
if (DEBUG) {
  console.log('[DEBUG] 数据:', data)
}
```

### 5. 依赖管理

```txt
# ❌ 不指定版本
supabase
websockets

# ✅ 锁定版本
supabase==2.9.0
websockets==13.0
```

### 6. 用户体验

```javascript
// ✅ 显示加载状态
<div v-if="isLoading">正在处理中...</div>

// ✅ 重要操作需要确认
const message = `确定要删除这 ${count} 条记录吗？此操作不可恢复！`
if (!confirm(message)) return
```

---

## 📁 核心文件

```
yolov8预测停车位/
├── backend/
│   ├── main.py                  ⚠️ 主API文件
│   ├── requirements.txt         ⚠️ Python依赖
│   └── .env                    ⚠️ 环境变量
│
├── src/
│   ├── views/
│   │   ├── Dashboard.vue       ⚠️ 主页面
│   │   └── History.vue         ⚠️ 历史记录
│   └── stores/
│       └── detection.js        ⚠️ 检测状态
│
└── MODIFICATIONS_AND_ERRORS.md ⚠️ 本文档
```

---

## 🚀 部署检查清单

### 后端部署

```bash
# 1. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows

# 2. 安装依赖
cd backend
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 Supabase 凭据

# 4. 启动服务
python main.py
```

### 前端部署

```bash
# 1. 安装依赖
npm install

# 2. 配置环境变量
cp .env.example .env.local

# 3. 启动开发服务器
npm run dev

# 4. 构建生产版本
npm run build
```

---

## 🔐 安全检查

- [ ] `.env` 不在 Git 中
- [ ] 后端使用 service_role key
- [ ] 前端使用 anon key
- [ ] 文件类型验证
- [ ] 参数验证
- [ ] 使用参数化查询
- [ ] API keys 定期轮换

---

## 📚 相关文档

- `STORAGE_UPLOAD_GUIDE.md` - 存储桶上传详细指南
- `PROJECT_SUMMARY.md` - 项目总体说明
- `SUPABASE_SETUP.md` - Supabase 配置指南
- `README.md` - 项目介绍

---

**最后更新**: 2025-10-18
**维护者**: Cascade AI Assistant
