# 快速错误参考卡片 🚨

> 遇到问题？先查这里！快速定位和解决常见错误

## 🔥 最常见的5个错误

### 1. 🔴 "Invalid API key"

**快速诊断**:
```bash
# 检查 backend/.env
cat backend/.env | grep SUPABASE_KEY

# 密钥长度应该约 219 字符
```

**立即修复**:
1. 登录 Supabase → Settings → API
2. 复制 **service_role** key（不是 anon key！）
3. 更新 `backend/.env`:
```bash
SUPABASE_KEY=完整的service_role_key
```
4. 重启后端

---

### 2. 🔴 "ModuleNotFoundError: websockets"

**快速修复**:
```bash
cd backend
pip uninstall websockets -y
pip install websockets==13.0
pip install supabase==2.9.0
python main.py
```

---

### 3. 🔴 "Invalid type str" (参数类型错误)

**问题**: `'conf=0.4' is of invalid type str`

**修复位置**: `backend/main.py` 第 270-275 行

**修复代码**:
```python
# 确保参数是数字类型
img_size = int(detection_params.get('imgSize', 640))
confidence = float(detection_params.get('confidence', 0.25))
iou_threshold = float(detection_params.get('iouThreshold', 0.45))
max_det = int(detection_params.get('maxDetections', 300))
```

---

### 4. 🔴 登录输入框无法输入

**快速检查**: 查看 `src/views/Login.vue`

**修复**:
- 移除 `console.log` 调试代码
- 移除 `style="pointer-events: auto"` 等内联样式
- 移除不必要的 `@click` 事件

**正确代码**:
```vue
<input
  v-model="email"
  type="email"
  class="input-field"
  placeholder="your@email.com"
/>
```

---

### 5. 🔴 存储桶文件上传失败

**检查清单**:
- [ ] Supabase 存储桶已创建（名称：`detection-files`）
- [ ] 存储桶设置为公开访问
- [ ] RLS 策略已配置
- [ ] 使用 service_role key

**验证**:
```bash
# 查看后端启动日志
python main.py

# 应该看到：
# [INFO] Supabase客户端初始化成功
```

---

## ⚡ 快速命令

### 重启一切
```bash
# 1. 停止所有服务（Ctrl+C）

# 2. 重启后端
cd backend
python main.py

# 3. 重启前端（新终端）
npm run dev
```

### 检查环境
```bash
# Python 环境
python --version          # 应该 >= 3.8
pip list | grep supabase  # 应该 2.9.0

# Node 环境
node --version            # 应该 >= 16
npm list | grep vue       # 应该 3.x
```

### 查看日志
```bash
# 后端日志
cd backend
python main.py 2>&1 | tee backend.log

# 前端日志（浏览器控制台）
F12 → Console
```

---

## 🔍 故障排查流程

```
问题出现
    ↓
1. 查看控制台/终端错误信息
    ↓
2. 在本文档中搜索错误关键词
    ↓
3. 按照对应的"快速修复"操作
    ↓
4. 重启相关服务
    ↓
5. 问题解决？
    ├─ 是 → ✅ 完成
    └─ 否 → 查看 MODIFICATIONS_AND_ERRORS.md 详细文档
```

---

## 📞 紧急求助

如果以上方法都无法解决：

1. **检查环境变量**:
```bash
# 后端
cat backend/.env

# 前端
cat .env.local
```

2. **完全重装依赖**:
```bash
# 后端
cd backend
rm -rf .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 前端
rm -rf node_modules package-lock.json
npm install
```

3. **查看完整文档**: `MODIFICATIONS_AND_ERRORS.md`

---

## 💡 预防性检查

### 每次修改代码后

```bash
# 1. 搜索调试代码
grep -r "console.log" src/

# 2. 检查类型转换
grep -r "params.get(" backend/

# 3. 验证环境变量
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓')"
```

### 每次提交前

- [ ] 移除所有 console.log
- [ ] 检查 .env 不在 Git 中
- [ ] 测试基本功能（登录、识别、历史）
- [ ] 检查错误处理

---

## 📌 记住这些规则

| ❌ 错误做法 | ✅ 正确做法 |
|-----------|-----------|
| 使用 anon key 在后端 | 后端用 service_role key |
| 不转换参数类型 | `int()`, `float()` 显式转换 |
| 硬编码敏感信息 | 使用环境变量 |
| 不指定依赖版本 | 锁定版本号 |
| 保留调试代码 | 移除或用环境变量控制 |

---

**快速联系**:
- 详细文档: `MODIFICATIONS_AND_ERRORS.md`
- 存储指南: `STORAGE_UPLOAD_GUIDE.md`
- 项目说明: `PROJECT_SUMMARY.md`
