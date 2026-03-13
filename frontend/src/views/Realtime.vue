<template>
  <div class="space-y-8">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="section-title">实时监控</p>
        <h1 data-testid="realtime-title" class="mt-3 text-2xl font-semibold text-white">实时监控</h1>
        <p class="mt-2 text-sm text-slate-300/80">
          接入实时视频流，观察车位占用变化与识别结果。
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <button
          data-testid="realtime-connect"
          class="btn-secondary text-sm"
          :disabled="isConnecting || isConnected"
          @click="connectRealtime"
        >
          {{ isConnected ? '已连接' : (isConnecting ? '连接中…' : '连接实时流') }}
        </button>
        <button
          class="btn-primary text-sm"
          :disabled="!isConnected || isRunning"
          @click="startDetection"
        >
          {{ isRunning ? '识别中…' : '开启识别' }}
        </button>
        <button
          class="btn-secondary text-sm"
          :disabled="!isRunning"
          @click="stopDetection"
        >
          结束识别
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="rounded-2xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-100">
      {{ errorMessage }}
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <div class="card card--no-glow card--no-blur lg:col-span-2" data-testid="realtime-preview-card">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-white">实时画面预览</h2>
          <span class="text-xs text-slate-400">{{ statusLabel }}</span>
        </div>
        <div class="mt-6 grid gap-4 lg:grid-cols-2">
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">原始输入</p>
            <div class="mt-3 flex h-56 items-center justify-center overflow-hidden rounded-2xl border border-dashed border-white/15 bg-slate-900/40">
              <video
                ref="videoRef"
                class="h-full w-full object-cover"
                autoplay
                muted
                playsinline
              ></video>
            </div>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">识别输出</p>
            <div class="mt-3 flex h-56 items-center justify-center overflow-hidden rounded-2xl border border-dashed border-white/15 bg-slate-900/40">
              <img v-if="previewUrl" :src="previewUrl" class="h-full w-full object-cover" alt="识别结果" />
              <span v-else class="text-xs text-slate-400">等待识别结果</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card card--no-glow card--no-blur" data-testid="realtime-summary-card">
        <h2 class="text-lg font-semibold text-white">识别摘要</h2>
        <div class="mt-6 space-y-4 text-sm text-slate-300/80">
          <div class="flex items-center justify-between">
            <span>当前帧耗时</span>
            <span class="text-white">{{ metrics.inferTime.toFixed(2) }}s</span>
          </div>
          <div class="flex items-center justify-between">
            <span>当前检测数</span>
            <span class="text-white">{{ metrics.detectionCount }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span>累计检测数</span>
            <span class="text-white">{{ metrics.totalDetections }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span>估计目标</span>
            <span class="text-emerald-300">{{ metrics.uniqueTargetCount }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span>处理帧数</span>
            <span class="text-white">{{ metrics.processedFrames }}</span>
          </div>
        </div>
        <div class="mt-6 space-y-3">
          <label class="flex items-center justify-between text-xs text-slate-300/80">
            录制结果视频
            <input v-model="recordEnabled" type="checkbox" class="h-4 w-4" />
          </label>
          <label class="flex items-center justify-between text-xs text-slate-300/80">
            录制帧率
            <input v-model.number="recordFps" type="number" min="1" step="1" class="w-20 rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-right text-xs text-white" />
          </label>
          <label class="flex items-center justify-between text-xs text-slate-300/80">
            录制时长（秒）
            <input
              v-model.number="recordDurationSeconds"
              data-testid="realtime-duration"
              type="number"
              min="0"
              step="1"
              class="w-20 rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-right text-xs text-white"
            />
          </label>
          <p class="text-[11px] text-slate-500">填写 0 表示不限时。</p>
        </div>
        <a
          v-if="downloadUrl"
          :href="downloadUrl"
          class="mt-6 inline-flex w-full items-center justify-center rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-100 transition hover:bg-white/10"
        >
          下载录制结果
        </a>
      </div>
    </div>

    <div class="card">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-white">实时事件流</h2>
        <span class="text-xs text-slate-400">最近 30 分钟</span>
      </div>
      <div class="mt-6 space-y-4">
        <div
          v-for="event in events"
          :key="event.title"
          class="flex items-start gap-4 rounded-2xl border border-white/10 bg-white/5 p-4"
        >
          <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary-500/15 text-primary-200">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 12h16M12 4v16"></path>
            </svg>
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-white">{{ event.title }}</p>
            <p class="mt-2 text-xs text-slate-300/80">{{ event.desc }}</p>
          </div>
          <span class="text-xs text-slate-400">{{ event.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { supabase } from '../config/supabase'
import { useDetectionStore } from '../stores/detection'
import { buildProtectedApiUrl } from '../utils/protected-url'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const detectionStore = useDetectionStore()

const videoRef = ref(null)
const previewUrl = ref('')
const errorMessage = ref('')
const connectionState = ref('idle')
const recordEnabled = computed({
  get: () => detectionStore.realtimePrefs.recordEnabled,
  set: (value) => detectionStore.updateRealtimePrefs({ recordEnabled: value })
})
const recordFps = computed({
  get: () => detectionStore.realtimePrefs.recordFps,
  set: (value) => detectionStore.updateRealtimePrefs({ recordFps: value })
})
const recordDurationSeconds = computed({
  get: () => detectionStore.realtimePrefs.recordDurationSeconds,
  set: (value) => detectionStore.updateRealtimePrefs({ recordDurationSeconds: value })
})
const downloadUrl = ref('')
const pendingStart = ref(false)

const metrics = ref({
  processedFrames: 0,
  detectionCount: 0,
  inferTime: 0,
  totalDetections: 0,
  uniqueTargetCount: 0
})

const isConnecting = computed(() => connectionState.value === 'connecting')
const isConnected = computed(() => ['ready', 'running'].includes(connectionState.value))
const isRunning = computed(() => connectionState.value === 'running')
const statusLabel = computed(() => {
  if (connectionState.value === 'connecting') return '正在连接'
  if (connectionState.value === 'ready') return '连接就绪'
  if (connectionState.value === 'running') return '识别中'
  return '等待连接'
})

const events = ref([
  { title: '等待视频源', desc: '尚未检测到实时推流，请先配置摄像头。', time: '刚刚' },
  { title: '推理引擎待命', desc: '模型加载完成后会自动开始识别。', time: '2 分钟前' },
  { title: '系统监控已启用', desc: '实时状态同步中，准备记录事件。', time: '5 分钟前' }
])

let socket = null
let stream = null
let captureTimer = null
let captureCanvas = null
let lastPreviewUrl = ''
let recordTimer = null
let isDisposed = false
const socketHandlers = {
  open: null,
  message: null,
  close: null,
  error: null
}

const buildWsUrl = (token) => {
  if (API_URL.startsWith('https://')) {
    return API_URL.replace('https://', 'wss://') + `/ws/detect-live?token=${token}`
  }
  if (API_URL.startsWith('http://')) {
    return API_URL.replace('http://', 'ws://') + `/ws/detect-live?token=${token}`
  }
  return `ws://${API_URL}/ws/detect-live?token=${token}`
}

const getAuthToken = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.access_token) {
    throw new Error('未登录或会话已失效')
  }
  return session.access_token
}

const startCamera = async () => {
  if (stream) return
  stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
  if (videoRef.value) {
    videoRef.value.srcObject = stream
    await videoRef.value.play()
  }
}

const stopCamera = () => {
  if (!stream) return
  stream.getTracks().forEach(track => track.stop())
  stream = null
}

const detachSocketListeners = () => {
  if (!socket) return
  if (socketHandlers.open) socket.removeEventListener('open', socketHandlers.open)
  if (socketHandlers.message) socket.removeEventListener('message', socketHandlers.message)
  if (socketHandlers.close) socket.removeEventListener('close', socketHandlers.close)
  if (socketHandlers.error) socket.removeEventListener('error', socketHandlers.error)
  socketHandlers.open = null
  socketHandlers.message = null
  socketHandlers.close = null
  socketHandlers.error = null
}

const cleanupRealtime = () => {
  if (isDisposed) return
  isDisposed = true
  stopCapture()
  clearRecordTimer()
  stopCamera()
  if (socket) {
    detachSocketListeners()
    try {
      socket.close()
    } catch (error) {
      console.warn('关闭实时连接失败:', error)
    }
    socket = null
  }
  if (lastPreviewUrl) {
    URL.revokeObjectURL(lastPreviewUrl)
    lastPreviewUrl = ''
  }
  previewUrl.value = ''
  connectionState.value = 'idle'
}

const connectRealtime = async () => {
  if (isConnecting.value || isConnected.value) return
  errorMessage.value = ''
  connectionState.value = 'connecting'
  downloadUrl.value = ''

  try {
    await startCamera()
    const token = await getAuthToken()
    const wsUrl = buildWsUrl(token)
    socket = new WebSocket(wsUrl)
    socket.binaryType = 'arraybuffer'

    socketHandlers.open = () => {
      if (isDisposed) return
      connectionState.value = 'ready'
      if (pendingStart.value) {
        pendingStart.value = false
        startDetection()
      }
    }

    socketHandlers.message = (event) => {
      if (isDisposed) return
      handleSocketMessage(event)
    }

    socketHandlers.close = () => {
      if (isDisposed) return
      connectionState.value = 'idle'
      stopCapture()
    }

    socketHandlers.error = () => {
      if (isDisposed) return
      errorMessage.value = '实时连接失败，请检查服务状态'
      connectionState.value = 'error'
      stopCapture()
    }

    socket.addEventListener('open', socketHandlers.open)
    socket.addEventListener('message', socketHandlers.message)
    socket.addEventListener('close', socketHandlers.close)
    socket.addEventListener('error', socketHandlers.error)
  } catch (error) {
    errorMessage.value = error.message || '无法启动摄像头'
    connectionState.value = 'error'
  }
}

const startDetection = async () => {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    pendingStart.value = true
    await connectRealtime()
    return
  }

  connectionState.value = 'running'
  metrics.value = {
    processedFrames: 0,
    detectionCount: 0,
    inferTime: 0,
    totalDetections: 0,
    uniqueTargetCount: 0
  }

  socket.send(JSON.stringify({
    type: 'start',
    params: detectionStore.detectionParams,
    recording: {
      enabled: recordEnabled.value,
      fps: recordFps.value,
      durationSeconds: Number(recordDurationSeconds.value) || 0
    }
  }))

  startCapture()
  scheduleRecordStop()
}

const stopDetection = () => {
  if (!socket || socket.readyState !== WebSocket.OPEN) return
  clearRecordTimer()
  socket.send(JSON.stringify({ type: 'end' }))
  stopCapture()
}

const startCapture = () => {
  if (captureTimer) return
  captureCanvas = captureCanvas || document.createElement('canvas')
  captureTimer = window.setInterval(sendFrame, getCaptureInterval())
}

const stopCapture = () => {
  if (captureTimer) {
    window.clearInterval(captureTimer)
    captureTimer = null
  }
}

const scheduleRecordStop = () => {
  clearRecordTimer()
  const seconds = Number(recordDurationSeconds.value)
  if (!Number.isFinite(seconds) || seconds <= 0) return
  recordTimer = window.setTimeout(() => {
    recordTimer = null
    stopDetection()
  }, seconds * 1000)
}

const clearRecordTimer = () => {
  if (recordTimer) {
    window.clearTimeout(recordTimer)
    recordTimer = null
  }
}

const getCaptureInterval = () => {
  const fps = Number(recordFps.value)
  if (!Number.isFinite(fps) || fps <= 0) {
    return 120
  }
  return Math.max(80, Math.round(1000 / fps))
}

const sendFrame = async () => {
  if (isDisposed) return
  if (!socket || socket.readyState !== WebSocket.OPEN) return
  const videoEl = videoRef.value
  if (!videoEl || videoEl.readyState < 2) return

  try {
    const width = videoEl.videoWidth || 640
    const height = videoEl.videoHeight || 360
    captureCanvas.width = width
    captureCanvas.height = height

    const context = captureCanvas.getContext('2d')
    if (!context) return
    context.drawImage(videoEl, 0, 0, width, height)

    const blob = await new Promise(resolve =>
      captureCanvas.toBlob(resolve, 'image/jpeg', 0.8)
    )

    if (!blob) return
    const buffer = await blob.arrayBuffer()
    if (isDisposed || !socket || socket.readyState !== WebSocket.OPEN) return
    socket.send(buffer)
  } catch (error) {
    if (!isDisposed) {
      console.warn('发送实时帧失败:', error)
    }
  }
}

const handleSocketMessage = async (event) => {
  if (isDisposed) return
  try {
    if (typeof event.data === 'string') {
      const payload = JSON.parse(event.data)
      if (payload.type === 'ready') {
        connectionState.value = 'ready'
        return
      }
      if (payload.type === 'error') {
        errorMessage.value = payload.detail || '实时识别出错'
        connectionState.value = 'error'
        return
      }
      if (payload.type === 'done') {
        connectionState.value = 'ready'
        if (payload.downloadUrl) {
          downloadUrl.value = await buildProtectedApiUrl(payload.downloadUrl)
        }
        return
      }
    }

    const buffer = event.data instanceof Blob ? await event.data.arrayBuffer() : event.data
    if (!(buffer instanceof ArrayBuffer)) return
    if (buffer.byteLength < 4) return

    const view = new DataView(buffer)
    const metaLength = view.getUint32(0)
    if (buffer.byteLength < 4 + metaLength) return

    const metaBytes = new Uint8Array(buffer, 4, metaLength)
    const metaText = new TextDecoder('utf-8').decode(metaBytes)
    const meta = JSON.parse(metaText)
    const imageBytes = new Uint8Array(buffer, 4 + metaLength)

    const blob = new Blob([imageBytes], { type: 'image/jpeg' })
    if (lastPreviewUrl) {
      URL.revokeObjectURL(lastPreviewUrl)
    }
    lastPreviewUrl = URL.createObjectURL(blob)
    previewUrl.value = lastPreviewUrl

    metrics.value = {
      processedFrames: meta.processedFrames || 0,
      detectionCount: meta.detectionCount || 0,
      inferTime: meta.inferTime || 0,
      totalDetections: meta.totalDetections || 0,
      uniqueTargetCount: meta.uniqueTargetCount || 0
    }
  } catch (error) {
    console.warn('实时消息解析失败:', error)
  }
}

onBeforeUnmount(() => {
  cleanupRealtime()
})
</script>
