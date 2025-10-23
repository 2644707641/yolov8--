<template>
  <div class="relative min-h-screen overflow-hidden bg-slate-950">
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -top-24 left-1/2 h-[360px] w-[360px] -translate-x-1/2 rounded-full bg-primary-500/25 blur-3xl"></div>
      <div class="absolute top-1/2 -left-24 h-[420px] w-[420px] -translate-y-1/2 rounded-full bg-accent-500/20 blur-3xl"></div>
      <div class="absolute bottom-[-160px] right-0 h-[420px] w-[420px] rounded-full bg-primary-900/25 blur-3xl"></div>
    </div>
    <div class="relative z-10 min-h-screen">
    <!-- 导航栏 -->
    <nav class="sticky top-0 z-20 border-b border-white/10 bg-white/5 backdrop-blur-xl">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <div class="flex items-center space-x-4">
            <router-link to="/dashboard" class="text-slate-300/80 hover:text-white">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
            </router-link>
            <h1 class="text-xl font-bold text-white">识别历史记录</h1>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-sm text-slate-300/80">{{ authStore.user?.email }}</div>
            <button @click="authStore.logout" class="btn-secondary text-sm">
              退出登录
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 历史记录列表 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="card">
        <div class="flex justify-between items-center mb-6">
          <div class="flex items-center space-x-4">
            <h2 class="text-lg font-semibold">全部记录 ({{ detectionStore.detectionHistory.length }})</h2>
            <button
              v-if="!batchMode"
              @click="enterBatchMode"
              class="text-sm text-primary-200 hover:text-primary-100 font-medium"
            >
              批量管理
            </button>
            <div v-else class="flex items-center space-x-3">
              <label class="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                  class="mr-2 h-4 w-4 text-primary-600 rounded"
                />
                <span class="text-sm text-slate-200/90">全选</span>
              </label>
              <span class="text-sm text-slate-300/80">已选中 {{ selectedIds.length }} 条</span>
              <button
                @click="exitBatchMode"
                class="text-sm text-slate-300/80 hover:text-slate-200"
              >
                取消
              </button>
              <button
                v-if="selectedIds.length > 0"
                @click="handleBatchDelete"
                class="px-3 py-1 rounded-lg bg-red-500/80 px-3 py-1 text-sm text-white transition hover:bg-red-500"
              >
                删除所选 ({{ selectedIds.length }})
              </button>
            </div>
          </div>
          <button @click="detectionStore.loadHistory()" class="btn-secondary text-sm">
            刷新
          </button>
        </div>

        <div v-if="detectionStore.detectionHistory.length === 0" class="text-center py-12 text-slate-500/70">
          <svg class="mx-auto h-24 w-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p>暂无识别记录</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="item in detectionStore.detectionHistory"
            :key="item.id"
            :class="[
              'relative border border-white/10 rounded-2xl overflow-hidden transition-all duration-300 hover:border-primary-400/60 hover:shadow-[0_25px_60px_rgba(8,15,40,0.45)]',
              selectedIds.includes(item.id) ? 'border-primary-500 border-2 shadow-lg' : 'border-white/10'
            ]"
          >
            <!-- 批量选择复选框 -->
            <div v-if="batchMode" class="absolute top-2 left-2 z-20">
              <label class="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  :checked="selectedIds.includes(item.id)"
                  @change="toggleSelect(item.id)"
                  class="h-5 w-5 text-primary-600 rounded border-2 border-white shadow-lg"
                  @click.stop
                />
              </label>
            </div>
            
            <!-- 原始图片和结果图片对比 -->
            <div class="grid grid-cols-2 gap-1 rounded-xl border border-white/10 bg-white/5 p-2 backdrop-blur-sm">
              <!-- 原始图片 -->
              <div class="relative group cursor-pointer" @click="openPreview(item, 'original')">
                <img
                  v-if="item.file_type === 'image'"
                  :src="item.original_file"
                  class="w-full h-32 object-cover rounded"
                  alt="原始图片"
                />
                <video
                  v-else
                  :src="item.original_file"
                  class="w-full h-32 object-cover rounded"
                ></video>
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all rounded flex items-center justify-center">
                  <span class="text-white opacity-0 group-hover:opacity-100 text-xs font-medium">点击预览</span>
                </div>
                <div class="absolute bottom-1 left-1">
                  <span class="px-2 py-0.5 text-xs font-medium rounded bg-slate-900/70 text-white">
                    原始
                  </span>
                </div>
              </div>

              <!-- 结果图片 -->
              <div class="relative group cursor-pointer" @click="openPreview(item, 'result')">
                <img
                  v-if="item.file_type === 'image'"
                  :src="item.result_file"
                  class="w-full h-32 object-cover rounded"
                  alt="检测结果"
                />
                <video
                  v-else
                  :src="item.result_file"
                  class="w-full h-32 object-cover rounded"
                ></video>
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all rounded flex items-center justify-center">
                  <span class="text-white opacity-0 group-hover:opacity-100 text-xs font-medium">点击预览</span>
                </div>
                <div class="absolute bottom-1 left-1">
                  <span class="px-2 py-0.5 text-xs font-medium rounded bg-primary-500/100 text-white">
                    结果
                  </span>
                </div>
              </div>
            </div>

            <div class="absolute top-4 right-4 z-10">
              <span
                :class="['px-2 py-1 text-xs font-medium rounded shadow-lg', item.file_type === 'image' ? 'bg-primary-500/100 text-white' : 'bg-accent-500 text-white']"
              >
                {{ item.file_type === 'image' ? '图片' : '视频' }}
              </span>
            </div>

            <div class="p-4">
              <div class="flex justify-between items-start mb-3">
                <div>
                  <p class="text-sm font-medium text-white">
                    检测到 {{ item.detections?.length || 0 }} 个物体
                  </p>
                  <p class="text-xs text-slate-400/80 mt-1">
                    {{ formatDate(item.created_at) }}
                  </p>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-2 text-xs text-slate-300/80 mb-3">
                <div>
                  <span class="font-medium">置信度:</span> {{ item.params?.confidence || 'N/A' }}
                </div>
                <div>
                  <span class="font-medium">尺寸:</span> {{ item.params?.imgSize || 'N/A' }}px
                </div>
              </div>

              <div class="flex space-x-2">
                <button
                  @click="openPreview(item, 'both')"
                  class="flex-1 btn-primary text-xs text-center"
                >
                  对比预览
                </button>
                <button
                  @click="handleDelete(item.id)"
                  class="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-xs"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片预览模态框 -->
    <div
      v-if="previewItem"
      class="fixed inset-0 z-[70] flex items-center justify-center bg-slate-950/95 backdrop-blur-xl"
      @click="closePreview"
    >
      <div class="absolute top-6 right-8 z-[80] flex items-center gap-4">
        <div class="flex items-center gap-3 rounded-2xl border border-white/15 bg-white/10 px-4 py-2 shadow-[0_12px_35px_rgba(8,15,40,0.45)] backdrop-blur">
          <button
            @click.stop="zoomOut"
            class="text-slate-200 transition hover:text-white"
            title="缩小"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-5.197-5.197M4 10h7m0 0h7m-7 0V3m0 7v7" />
            </svg>
          </button>
          <span class="text-xs font-semibold tracking-[0.28em] text-slate-200 uppercase">{{ Math.round(scale * 100) }}%</span>
          <button
            @click.stop="zoomIn"
            class="text-slate-200 transition hover:text-white"
            title="放大"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 5v14m7-7H5" />
            </svg>
          </button>
          <button
            @click.stop="resetZoom"
            class="ml-1 text-slate-200 transition hover:text-white"
            title="复位"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4V2m0 20v-2m8-8h2M2 12h2m15.071 6.071l1.414 1.414M4.515 4.515l1.414 1.414m0 12.727l-1.414 1.414M19.071 4.929l1.414-1.414" />
            </svg>
          </button>
        </div>
        <button
          @click="closePreview"
          class="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/10 text-slate-200 transition hover:border-white/20 hover:text-white"
          title="关闭"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div
        :class="[
          'relative h-[80vh] w-full max-w-6xl rounded-3xl border border-white/10 bg-white/5 px-8 py-10 shadow-[0_35px_120px_rgba(8,15,40,0.55)]',
          previewMode === 'both' ? 'grid grid-cols-2 gap-6' : 'flex items-center justify-center'
        ]"
        @click.stop
      >
        <div
          v-if="previewMode === 'original' || previewMode === 'both'"
          class="relative flex h-full flex-col items-center"
        >
          <div class="flex w-full items-center justify-between text-xs uppercase tracking-[0.3em] text-slate-300/70">
            <span>原始素材</span>
            <span>拖拽平移 · 滚轮缩放</span>
          </div>
          <div
            class="relative mt-4 flex h-full w-full items-center justify-center overflow-hidden rounded-2xl border border-white/15 bg-slate-900/40 cursor-move"
            @mousedown="startDrag"
            @mousemove="onDrag"
            @mouseup="endDrag"
            @mouseleave="endDrag"
            @wheel.prevent="onWheel"
          >
            <img
              v-if="previewItem.file_type === 'image'"
              :src="previewItem.original_file"
              :style="{
                transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
                transition: isDragging ? 'none' : 'transform 0.1s',
                transformOrigin: 'center center'
              }"
              class="max-h-full max-w-full select-none object-contain"
              alt="原始素材"
              draggable="false"
            />
            <video
              v-else
              :src="previewItem.original_file"
              controls
              class="max-h-full max-w-full rounded-2xl"
            ></video>
          </div>
        </div>

        <div
          v-if="previewMode === 'result' || previewMode === 'both'"
          class="relative flex h-full flex-col items-center"
        >
          <div class="flex w-full items-center justify-between text-xs uppercase tracking-[0.3em] text-slate-300/70">
            <span>识别结果</span>
            <span>拖拽平移 · 滚轮缩放</span>
          </div>
          <div
            class="relative mt-4 flex h-full w-full items-center justify-center overflow-hidden rounded-2xl border border-white/15 bg-slate-900/40 cursor-move"
            @mousedown="startDrag"
            @mousemove="onDrag"
            @mouseup="endDrag"
            @mouseleave="endDrag"
            @wheel.prevent="onWheel"
          >
            <img
              v-if="previewItem.file_type === 'image'"
              :src="previewItem.result_file"
              :style="{
                transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
                transition: isDragging ? 'none' : 'transform 0.1s',
                transformOrigin: 'center center'
              }"
              class="max-h-full max-w-full select-none object-contain"
              alt="识别结果"
              draggable="false"
            />
            <video
              v-else
              :src="previewItem.result_file"
              controls
              class="max-h-full max-w-full rounded-2xl"
            ></video>
          </div>
        </div>
      </div>
    </div>
  </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useDetectionStore } from '../stores/detection'

const authStore = useAuthStore()
const detectionStore = useDetectionStore()

// 预览相关状态
const previewItem = ref(null)
const previewMode = ref('both') // 'original', 'result', 'both'
const scale = ref(1)
const position = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// 批量选择相关状态
const batchMode = ref(false)
const selectedIds = ref([])

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleDelete = async (id) => {
  if (confirm('确定要删除这条记录吗？')) {
    await detectionStore.deleteHistory(id)
  }
}

// 打开预览
const openPreview = (item, mode) => {
  previewItem.value = item
  previewMode.value = mode
  resetZoom()
}

// 关闭预览
const closePreview = () => {
  previewItem.value = null
  resetZoom()
}

// 放大
const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.2, 5)
}

// 缩小
const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.2, 0.5)
}

// 重置缩放
const resetZoom = () => {
  scale.value = 1
  position.value = { x: 0, y: 0 }
}

// 鼠标滚轮缩放
const onWheel = (event) => {
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  scale.value = Math.max(0.5, Math.min(5, scale.value + delta))
}

// 开始拖动
const startDrag = (event) => {
  isDragging.value = true
  dragStart.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y
  }
}

// 拖动中
const onDrag = (event) => {
  if (!isDragging.value) return
  position.value = {
    x: event.clientX - dragStart.value.x,
    y: event.clientY - dragStart.value.y
  }
}

// 结束拖动
const endDrag = () => {
  isDragging.value = false
}

// 批量选择相关计算属性
const isAllSelected = computed(() => {
  return detectionStore.detectionHistory.length > 0 && 
         selectedIds.value.length === detectionStore.detectionHistory.length
})

// 进入批量模式
const enterBatchMode = () => {
  batchMode.value = true
  selectedIds.value = []
}

// 退出批量模式
const exitBatchMode = () => {
  batchMode.value = false
  selectedIds.value = []
}

// 切换单个选项
const toggleSelect = (id) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

// 全选/取消全选
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = detectionStore.detectionHistory.map(item => item.id)
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) return
  
  const confirmMessage = `确定要删除这 ${selectedIds.value.length} 条记录吗？此操作不可恢复！`
  if (!confirm(confirmMessage)) return
  
  try {
    // 逐个删除选中的记录
    for (const id of selectedIds.value) {
      await detectionStore.deleteHistory(id)
    }
    
    // 清空选中列表
    selectedIds.value = []
    // 退出批量模式
    batchMode.value = false
  } catch (error) {
    alert('批量删除失败，请重试')
    console.error('批量删除错误:', error)
  }
}

onMounted(() => {
  detectionStore.loadHistory()
})
</script>
