# 视频同步播放功能

## 📝 功能说明

在Dashboard的视频对比预览模式下，新增了视频同步播放控制功能，允许用户同时播放原始视频和识别结果视频，实现完美的对比效果。

## ✨ 新增功能

### 1. 视频控制按钮组
- **位置**: 预览弹窗顶部控制栏（缩放控制和关闭按钮之间）
- **显示条件**: 仅在视频对比模式（`previewMode === 'both'`）时显示
- **包含按钮**:
  - **同步播放/暂停**：
    - 播放状态：▶ 三角形播放图标（蓝色主题）
    - 暂停状态：⏸ 双竖线暂停图标（红色主题）
  - **回到原点** ⭐新增：
    - 图标：↺ 返回箭头
    - 灰色主题（slate色系）

### 2. 视觉效果
- **播放状态**:
  - 蓝色主题 (`border-primary-400/30 bg-primary-500/20 text-primary-300`)
  - 显示"同步播放"文字
  
- **暂停状态**:
  - 红色主题 (`border-red-400/30 bg-red-500/20 text-red-300`)
  - 显示"暂停"文字

### 3. 交互逻辑

#### 播放行为（智能同步）
- 点击"同步播放"按钮时，系统会智能判断：
  1. **所有视频已播放完毕** → 从头开始播放
  2. **视频位置不同步** → 同步到第一个视频的位置继续播放
  3. **暂停后继续** → 从当前暂停位置继续播放
- 状态切换为"暂停"
- 按钮变为红色主题

#### 暂停行为
- 点击"暂停"按钮时：
  - 两个视频立即暂停
  - 状态切换为"同步播放"
  - 按钮变为蓝色主题

#### 回到原点行为 ⭐新增
- 点击"回到原点"按钮时：
  - 两个视频立即暂停
  - 播放位置重置到 `00:00`（`currentTime = 0`）
  - 播放状态重置为暂停
- **使用场景**：
  - 快速重新开始对比
  - 重置到初始状态
  - 清除单独控制造成的位置不同步

#### 关闭预览时
- 自动暂停所有视频
- 重置播放状态

## 🔧 技术实现

### 新增状态变量
```javascript
const originalVideoRef = ref(null)  // 原始视频DOM引用
const resultVideoRef = ref(null)    // 结果视频DOM引用
const isVideoPlaying = ref(false)   // 播放状态标记
```

### 核心函数

#### 同步播放/暂停函数
```javascript
const toggleVideoPlayback = () => {
  if (fileType.value !== 'video') return
  
  const videos = []
  if (previewMode.value === 'both' || previewMode.value === 'original') {
    if (originalVideoRef.value) videos.push(originalVideoRef.value)
  }
  if (previewMode.value === 'both' || previewMode.value === 'result') {
    if (resultVideoRef.value) videos.push(resultVideoRef.value)
  }
  
  if (videos.length === 0) return
  
  if (isVideoPlaying.value) {
    // 暂停所有视频
    videos.forEach(video => video.pause())
    isVideoPlaying.value = false
  } else {
    // 智能同步播放
    const allEnded = videos.every(video => video.ended)
    
    if (allEnded) {
      // 所有视频都播放完了，从头开始
      videos.forEach(video => {
        video.currentTime = 0
        video.play()
      })
    } else if (videos.length > 1) {
      // 多个视频时，同步到第一个视频的位置
      const syncTime = videos[0].currentTime
      videos.forEach(video => {
        video.currentTime = syncTime
        video.play()
      })
    } else {
      // 单个视频，直接播放
      videos[0].play()
    }
    
    isVideoPlaying.value = true
  }
}
```

#### 回到原点函数 ⭐新增
```javascript
const resetVideos = () => {
  if (fileType.value !== 'video') return
  
  const videos = []
  if (previewMode.value === 'both' || previewMode.value === 'original') {
    if (originalVideoRef.value) videos.push(originalVideoRef.value)
  }
  if (previewMode.value === 'both' || previewMode.value === 'result') {
    if (resultVideoRef.value) videos.push(resultVideoRef.value)
  }
  
  // 重置所有视频到开始位置并暂停
  videos.forEach(video => {
    video.pause()
    video.currentTime = 0
  })
  
  isVideoPlaying.value = false
}
```

### DOM元素修改
```vue
<!-- 原始视频添加ref -->
<video
  ref="originalVideoRef"
  :src="detectionStore.currentResult.originalUrl"
  controls
  class="max-h-full max-w-full rounded-2xl"
></video>

<!-- 结果视频添加ref -->
<video
  ref="resultVideoRef"
  :src="detectionStore.currentResult.resultUrl"
  controls
  class="max-h-full max-w-full rounded-2xl"
></video>
```

## 📋 使用方法

1. **上传视频并完成检测**
   - 在Dashboard上传视频文件
   - 调整检测参数并执行识别

2. **进入对比预览**
   - 在步骤4识别结果页面
   - 点击"🔄 对比预览"按钮

3. **使用同步播放**
   - 预览弹窗自动显示同步播放按钮
   - 点击"同步播放"按钮，两个视频将同时从头开始播放
   - 点击"暂停"按钮可随时暂停播放
   - 视频仍保留原生controls控制条，可单独控制

## 🎯 优势

✅ **完美同步** - 两个视频从同一时间点开始播放  
✅ **一键控制** - 单个按钮控制两个视频  
✅ **视觉反馈** - 清晰的颜色和图标状态指示  
✅ **自动清理** - 关闭预览时自动暂停和重置  
✅ **灵活控制** - 保留原生controls，支持单独控制  

## 🔮 未来改进建议

- [ ] 添加播放速度控制（0.5x, 1x, 2x）
- [ ] 实现播放进度同步（不仅是开始同步）
- [ ] 添加循环播放选项
- [ ] 显示当前播放时间和总时长
- [ ] 支持拖动进度条同步跳转

## 🔧 问题修复

### 修复单独视频播放问题 (2025-10-30)

**问题描述**：
添加同步播放功能后，视频的原生controls无法正常使用，无法单独播放视频。

**问题原因**：
容器div上的拖动事件监听器（`@mousedown`, `@mousemove`等）干扰了video元素controls的鼠标交互。

**解决方案**：
1. 将拖动事件监听器改为条件绑定，只在图片模式下生效
2. 视频模式下不绑定拖动事件，保证controls正常工作
3. 更新光标样式，只在图片模式显示`cursor-move`
4. 更新提示文字，视频模式显示"视频播放"而不是"拖拽以平移"

**修改内容**：
```vue
<!-- 修改前 -->
<div @mousedown="startDrag" @mousemove="onDrag">

<!-- 修改后 -->
<div 
  @mousedown="fileType === 'image' ? startDrag : null"
  @mousemove="fileType === 'image' ? onDrag : null"
  :class="fileType === 'image' ? 'cursor-move' : ''"
>
```

现在视频可以正常使用原生controls进行单独播放，同时保留了同步播放按钮的功能。

### 改进智能同步播放逻辑 (2025-10-30)

**问题描述**：
暂停后再点击同步播放时，视频总是从头开始，而不是从暂停位置继续播放。

**解决方案**：
实现智能同步播放逻辑，根据不同情况采取不同策略：

1. **所有视频已播放完毕** → 从头开始播放（`video.ended === true`）
2. **视频位置不同步** → 同步到第一个视频的当前位置
3. **暂停后继续** → 从当前位置继续播放

**优势**：
- ✅ 暂停后可以从当前位置继续
- ✅ 播放完毕后自动从头开始
- ✅ 单独控制某个视频后，点击同步播放会自动对齐位置
- ✅ 更符合用户的直觉操作

### 新增回到原点按钮 (2025-10-30)

**功能描述**：
添加"回到原点"按钮，一键将两个视频重置到开始位置并暂停。

**实现内容**：
1. 新增 `resetVideos()` 函数
2. 在UI中添加回到原点按钮（灰色主题，返回箭头图标）
3. 按钮位置：同步播放按钮右侧
4. 按钮行为：暂停视频 + 重置到00:00

**使用场景**：
- 视频播放到中间，想快速重新开始
- 单独控制某个视频后，位置不同步，需要一键重置
- 对比完一轮后，快速准备第二轮对比

### 历史记录页面同步实现 (2025-10-30)

**功能描述**：
将Dashboard中的完整视频控制功能同步实现到History.vue历史记录页面。

**实现内容**：
1. 添加相同的视频ref引用和状态管理
2. 实现完整的视频控制函数（toggleVideoPlayback, resetVideos）
3. 添加视频控制按钮组UI
4. 修复拖动事件仅在图片模式生效
5. 更新提示文字根据文件类型显示

**结果**：
历史记录页面现在拥有与Dashboard完全一致的视频对比预览体验。

### 修复图片缩放滚轮事件 (2025-10-30)

**问题描述**：
图片对比预览时，鼠标滚轮缩放功能失效。

**问题原因**：
Vue事件绑定使用了三元表达式 `@wheel.prevent="condition ? handler : null"`，这种写法会导致事件无法正常触发。

**解决方案**：
改用逻辑与运算符：`@wheel.prevent="condition && handler"`

**修改内容**：
```vue
<!-- 修改前（错误） -->
@mousedown="fileType === 'image' ? startDrag : null"
@wheel.prevent="fileType === 'image' ? onWheel : null"

<!-- 修改后（正确） -->
@mousedown="fileType === 'image' && startDrag"
@wheel.prevent="fileType === 'image' && onWheel"
```

现在图片的拖拽平移和滚轮缩放功能恢复正常。

## 📅 更新日期

- 初始版本：2025-10-30
- 修复单独播放问题：2025-10-30
- 改进智能同步播放：2025-10-30
- 新增回到原点按钮：2025-10-30
- 历史记录页面同步实现：2025-10-30
- 修复图片缩放滚轮事件：2025-10-30

## 👤 开发者

系统自动生成
