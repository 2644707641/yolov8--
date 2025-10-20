# 视频播放优化指南

## 🎬 问题说明

如果您发现检测后的视频：
- ✗ 播放卡顿、不流畅
- ✗ 画面闪烁或跳帧
- ✗ 浏览器无法正常播放

这是因为OpenCV默认的视频编码器（mp4v）兼容性较差。

## ✅ 解决方案

### 方案1：安装FFmpeg（推荐）

后端已经集成了FFmpeg自动优化功能。安装FFmpeg后，**生成的视频会自动优化为流畅的H264格式**。

#### Windows快速安装

**选项A：使用安装脚本（最简单）**
```bash
# 双击运行项目根目录下的：
install_ffmpeg.bat
```

**选项B：使用Scoop（推荐）**
```powershell
# 1. 安装Scoop包管理器
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# 2. 安装FFmpeg
scoop install ffmpeg
```

**选项C：使用Chocolatey**
```powershell
# 需要先安装Chocolatey
choco install ffmpeg -y
```

**选项D：手动安装**
1. 下载：https://github.com/BtbN/FFmpeg-Builds/releases
2. 选择：`ffmpeg-master-latest-win64-gpl.zip`
3. 解压到任意目录（如 `C:\ffmpeg`）
4. 添加到PATH：
   - 右键"此电脑" → 属性 → 高级系统设置
   - 环境变量 → 系统变量 → Path → 编辑
   - 新建 → 输入FFmpeg的bin目录路径（如 `C:\ffmpeg\bin`）
   - 确定保存

#### 验证安装

```bash
# 进入backend目录
cd backend

# 检查FFmpeg是否安装成功
python check_ffmpeg.py
```

如果看到 `✓ FFmpeg已安装`，说明安装成功！

### 方案2：不安装FFmpeg

如果不想安装FFmpeg，视频仍然可以播放，但可能会卡顿。您可以：

1. **下载后使用本地播放器播放**
   - 下载视频文件
   - 使用VLC、PotPlayer等播放器播放

2. **手动转换视频**
   - 使用在线工具转换为H264格式
   - 或使用格式工厂等软件转换

## 🔧 技术细节

### FFmpeg优化参数

后端自动应用的优化参数：

```bash
ffmpeg -i input.mp4 \
  -c:v libx264          # H.264编码（最兼容）
  -preset fast          # 快速编码
  -crf 23              # 质量因子（18-28，23为平衡）
  -pix_fmt yuv420p     # 像素格式（最佳兼容性）
  -movflags +faststart  # 优化网络播放
  output.mp4
```

### 优化效果

安装FFmpeg后：
- ✓ 视频文件可能减小30-50%
- ✓ 播放流畅度显著提升
- ✓ 兼容所有现代浏览器
- ✓ 支持快进/快退
- ✓ 移动端也能流畅播放

## 📊 性能对比

| 编码器 | 文件大小 | 播放流畅度 | 兼容性 | 编码速度 |
|--------|---------|-----------|--------|---------|
| mp4v (默认) | 大 | ⭐ 差 | ⭐⭐ 一般 | 快 |
| H264 (FFmpeg) | 小 | ⭐⭐⭐ 优秀 | ⭐⭐⭐ 完美 | 中等 |

## 🚀 使用流程

### 1. 安装FFmpeg

```bash
# 运行安装脚本
install_ffmpeg.bat
```

### 2. 重启后端

```bash
cd backend
python main.py
```

### 3. 上传视频检测

后端会自动：
1. 使用OpenCV进行视频检测
2. 自动调用FFmpeg优化视频
3. 输出流畅的H264格式

日志示例：
```
[INFO] 视频处理完成
[INFO] - 文件大小: 5.23 MB
[INFO] - 编码器: MJPEG
[INFO] 尝试使用FFmpeg优化视频...
[INFO] ✓ FFmpeg优化成功
[INFO] - 优化后大小: 2.45 MB
[INFO] - 视频将更加流畅
```

### 4. 播放视频

优化后的视频可以：
- ✓ 在浏览器中流畅播放
- ✓ 在移动设备上播放
- ✓ 快速加载和缓冲
- ✓ 支持拖动进度条

## ❓ 常见问题

### Q1: FFmpeg安装后还是卡顿？

**A:** 请确保：
1. 重启了命令行窗口
2. 重启了后端服务
3. 运行 `ffmpeg -version` 能显示版本信息

### Q2: 优化需要多长时间？

**A:** 
- 短视频（<1分钟）：几秒钟
- 中等视频（1-5分钟）：10-30秒
- 长视频（>5分钟）：30-60秒

优化是自动的，不需要等待。

### Q3: 不想安装FFmpeg怎么办？

**A:** 视频仍然可以使用，只是可能：
- 播放时会卡顿
- 文件较大
- 部分浏览器可能无法播放

建议下载后用本地播放器播放。

### Q4: FFmpeg会影响检测速度吗？

**A:** 不会！FFmpeg优化是在检测完成后才进行的，不影响检测速度。

### Q5: 可以禁用FFmpeg优化吗？

**A:** 可以。如果不想使用FFmpeg优化，卸载FFmpeg即可：
```bash
scoop uninstall ffmpeg
# 或
choco uninstall ffmpeg
```

## 💡 最佳实践

1. **推荐安装FFmpeg**
   - 获得最佳视频体验
   - 文件更小，上传更快
   - 兼容性最好

2. **视频参数调优**
   - 短视频：使用默认参数（frameSkip=5）
   - 长视频：增大frameSkip到10（减少处理时间）
   - 需要高精度：设置frameSkip=1（每帧检测）

3. **网络播放优化**
   - FFmpeg自动添加 `faststart` 标志
   - 支持渐进式下载
   - 可边下载边播放

## 📝 更新日志

### v1.1.0 (2025-10-19)
- ✨ 新增：FFmpeg自动优化功能
- ✨ 新增：多种编码器尝试机制
- 🔧 修复：视频卡顿问题
- 🔧 修复：检测框闪烁问题
- 📚 新增：完整的视频优化指南

---

**需要帮助？** 查看 [README.md](./README.md) 或提交 Issue
