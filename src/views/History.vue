<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <div class="flex items-center space-x-4">
            <router-link to="/dashboard" class="text-gray-600 hover:text-gray-900">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
            </router-link>
            <h1 class="text-xl font-bold text-gray-900">识别历史记录</h1>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-sm text-gray-600">{{ authStore.user?.email }}</div>
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
              class="text-sm text-primary-600 hover:text-primary-700 font-medium"
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
                <span class="text-sm text-gray-700">全选</span>
              </label>
              <span class="text-sm text-gray-600">已选中 {{ selectedIds.length }} 条</span>
              <button
                @click="exitBatchMode"
                class="text-sm text-gray-600 hover:text-gray-800"
              >
                取消
              </button>
              <button
                v-if="selectedIds.length > 0"
                @click="handleBatchDelete"
                class="px-3 py-1 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
              >
                删除所选 ({{ selectedIds.length }})
              </button>
            </div>
          </div>
          <button @click="detectionStore.loadHistory()" class="btn-secondary text-sm">
            刷新
          </button>
        </div>

        <div v-if="detectionStore.detectionHistory.length === 0" class="text-center py-12 text-gray-400">
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
              'relative border rounded-lg overflow-hidden hover:shadow-lg transition-all',
              selectedIds.includes(item.id) ? 'border-primary-500 border-2 shadow-lg' : 'border-gray-200'
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
            <div class="grid grid-cols-2 gap-1 bg-gray-100 p-2">
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
                  <span class="px-2 py-0.5 text-xs font-medium rounded bg-gray-800 bg-opacity-70 text-white">
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
                  <span class="px-2 py-0.5 text-xs font-medium rounded bg-blue-500 text-white">
                    结果
                  </span>
                </div>
              </div>
            </div>

            <div class="absolute top-4 right-4 z-10">
              <span
                :class="['px-2 py-1 text-xs font-medium rounded shadow-lg', item.file_type === 'image' ? 'bg-blue-500 text-white' : 'bg-purple-500 text-white']"
              >
                {{ item.file_type === 'image' ? '图片' : '视频' }}
              </span>
            </div>

            <div class="p-4">
              <div class="flex justify-between items-start mb-3">
                <div>
                  <p class="text-sm font-medium text-gray-900">
                    检测到 {{ item.detections?.length || 0 }} 个物体
                  </p>
                  <p class="text-xs text-gray-500 mt-1">
                    {{ formatDate(item.created_at) }}
                  </p>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-2 text-xs text-gray-600 mb-3">
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
      class="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center"
      @click="closePreview"
    >
      <div class="absolute top-4 right-4 flex items-center space-x-4 z-10">
        <!-- 缩放控制 -->
        <div class="flex items-center space-x-2 bg-white bg-opacity-10 rounded-lg px-3 py-2">
          <button
            @click.stop="zoomOut"
            class="text-white hover:text-gray-300 transition-colors"
            title="缩小"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"></path>
            </svg>
          </button>
          <span class="text-white text-sm font-medium">{{ Math.round(scale * 100) }}%</span>
          <button
            @click.stop="zoomIn"
            class="text-white hover:text-gray-300 transition-colors"
            title="放大"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
            </svg>
          </button>
          <button
            @click.stop="resetZoom"
            class="text-white hover:text-gray-300 transition-colors ml-2"
            title="重置"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
        </div>
        
        <!-- 关闭按钮 -->
        <button
          @click="closePreview"
          class="text-white hover:text-gray-300 transition-colors"
        >
          <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <div
        class="w-full h-full flex items-center justify-center p-8"
        :class="previewMode === 'both' ? 'grid grid-cols-2 gap-4' : ''"
        @click.stop
      >
        <!-- 原始图片 -->
        <div
          v-if="previewMode === 'original' || previewMode === 'both'"
          class="relative h-full flex flex-col items-center justify-center"
        >
          <h3 class="text-white text-lg font-semibold mb-4">原始图片</h3>
          <div
            :class="[
              'relative cursor-move w-full h-full flex items-center justify-center',
              previewMode === 'both' ? 'overflow-hidden' : ''
            ]"
            @mousedown="startDrag"
            @mousemove="onDrag"
            @mouseup="endDrag"
            @mouseleave="endDrag"
            @wheel.prevent="onWheel"
          >
            <img
              :src="previewItem.original_file"
              :style="{
                transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
                transition: isDragging ? 'none' : 'transform 0.1s',
                transformOrigin: 'center center'
              }"
              class="max-w-full max-h-[80vh] object-contain select-none"
              alt="原始图片"
              draggable="false"
            />
          </div>
        </div>

        <!-- 结果图片 -->
        <div
          v-if="previewMode === 'result' || previewMode === 'both'"
          class="relative h-full flex flex-col items-center justify-center"
        >
          <h3 class="text-white text-lg font-semibold mb-4">检测结果</h3>
          <div
            :class="[
              'relative cursor-move w-full h-full flex items-center justify-center',
              previewMode === 'both' ? 'overflow-hidden' : ''
            ]"
            @mousedown="startDrag"
            @mousemove="onDrag"
            @mouseup="endDrag"
            @mouseleave="endDrag"
            @wheel.prevent="onWheel"
          >
            <img
              :src="previewItem.result_file"
              :style="{
                transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
                transition: isDragging ? 'none' : 'transform 0.1s',
                transformOrigin: 'center center'
              }"
              class="max-w-full max-h-[80vh] object-contain select-none"
              alt="检测结果"
              draggable="false"
            />
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
