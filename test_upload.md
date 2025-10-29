# 权重上传问题诊断和测试指南

## 问题总结

您上传了两次权重文件，但只看到最近的一次。通过诊断脚本确认：**数据库中确实只有 1 条权重记录**。

## 根本原因分析

从数据库记录来看：
- **创建时间**: 2025-10-28 21:49:47（第一次上传）
- **更新时间**: 2025-10-29 12:12:59（后续被更新）

**可能的原因：**
1. 第二次上传时发生了错误，没有成功创建记录
2. 网络问题导致上传到 Supabase 失败（诊断显示存储桶检查超时）
3. 上传过程中前端显示成功，但后端实际失败了

## 测试步骤

### 步骤 1：启动后端（带详细日志）

在项目根目录打开终端，运行：

```powershell
.\.venv\Scripts\Activate.ps1
python backend/main.py
```

后端现在会输出详细的日志，包括：
- 权重上传过程
- 数据库操作详情
- 任何错误信息

### 步骤 2：启动前端

在另一个终端窗口运行：

```powershell
npm run dev
```

### 步骤 3：测试上传

1. 打开浏览器访问 `http://localhost:5173`
2. 登录您的账号
3. 进入"模型权重管理"页面
4. 上传一个**新的**权重文件（不要用之前上传过的 best.pt）
5. **注意观察**：
   - 前端是否显示"上传成功"
   - 浏览器控制台的日志输出
   - 后端终端的日志输出

### 步骤 4：检查结果

上传完成后：

**前端控制台应该显示：**
```
📤 上传响应数据: { success: true, weight: {...} }
✅ 权重上传成功，权重信息: {...}
📦 API返回的权重数据: { success: true, weights: [...] }
📊 权重列表数量: 2
✅ 已加载到界面的权重数量: 2
```

**后端终端应该显示：**
```
INFO | 上传权重文件到 Supabase: 071d6f23-.../1234567_filename.pt
INFO | 权重文件上传成功: ...
INFO | 创建权重记录: user=... name=...
INFO | ✅ 权重记录创建成功:
INFO |   - ID: ...
INFO |   - Name: filename.pt
INFO |   - Is Active: False
INFO | 用户 ... 上传模型到 Supabase 成功: ...
```

### 步骤 5：再次运行诊断

上传完成后，运行诊断脚本确认：

```powershell
python backend/debug_weights.py
```

应该显示 **2 条权重记录**。

## 如果上传失败

### 检查点 1：网络连接

如果看到类似 "timeout" 或 "connection" 错误：
- 检查网络连接
- 检查 Supabase 服务是否正常
- 尝试在浏览器访问您的 Supabase URL

### 检查点 2：文件大小

如果看到文件大小相关错误：
- Supabase 免费计划单文件限制 50MB
- 检查您上传的文件大小：`ls -lh best.pt`

### 检查点 3：Supabase 配置

确认环境变量正确配置：

**前端 `.env`：**
```
VITE_SUPABASE_URL=https://wlajtijojwlfthpgfcgo.supabase.co
VITE_SUPABASE_ANON_KEY=你的anon key
VITE_API_URL=http://localhost:8000
```

**后端 `backend/.env`：**
```
SUPABASE_URL=https://wlajtijojwlfthpgfcgo.supabase.co
SUPABASE_KEY=你的service role key (不是 anon key)
MODEL_WEIGHTS_BUCKET=model-weights
```

### 检查点 4：存储桶配置

登录 Supabase 控制台确认：
1. 存储桶 `model-weights` 已创建
2. 存储桶设置为 **Private**
3. RLS 策略已正确配置（参考 MODEL_STORAGE_SETUP.md）

## 常见错误及解决方法

### 错误 1：前端显示成功但数据库没有记录

**原因**：后端处理失败但没有正确返回错误

**解决**：
- 检查后端日志中的错误信息
- 确认 Supabase Service Role Key 配置正确

### 错误 2：上传超时

**原因**：网络问题或文件过大

**解决**：
- 检查网络连接
- 尝试上传更小的文件测试
- 检查 Supabase 服务状态

### 错误 3：权重列表只显示一个

**原因**：
1. 数据库中确实只有一条记录（通过诊断脚本确认）
2. 前端缓存问题
3. RLS 策略限制

**解决**：
- 运行诊断脚本确认数据库实际记录数
- 清除浏览器缓存并刷新
- 检查 Supabase RLS 策略

## 预防措施

为了避免将来出现类似问题：

1. **总是查看日志**：上传时关注前端控制台和后端日志
2. **验证结果**：上传后点击"刷新"按钮确认
3. **网络稳定**：确保网络连接稳定
4. **文件命名**：使用不同的文件名，方便区分

## 下一步

1. 按照上述步骤重新测试上传功能
2. 如果仍有问题，请提供：
   - 前端控制台的完整日志
   - 后端终端的完整日志
   - 诊断脚本的输出结果

这将帮助我们更准确地定位问题。
