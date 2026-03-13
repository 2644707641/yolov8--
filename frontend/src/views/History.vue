<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="section-title">历史记录</p>
        <h1 data-testid="history-title" class="mt-3 text-2xl font-semibold text-white">历史记录中心</h1>
        <p class="mt-2 text-sm text-slate-300/80">
          自动归档每一次识别结果，支持筛选、对比与批量管理。
        </p>
      </div>
    <div class="flex items-center gap-3 text-xs text-slate-400/80">
        当前账户：<span class="text-slate-100">{{ authStore.user?.email || '未登录' }}</span>
      </div>
    </div>

    <div
      v-if="historyError"
      data-testid="history-error"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-100"
    >
      {{ historyError }}
    </div>

    <!-- 历史记录列表 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="card">
        <!-- 分类筛选标签 -->
        <div class="mb-6 flex items-center gap-3">
          <button
            @click="setFilterType('all')"
            :class="[
              'rounded-xl px-4 py-2 text-sm font-medium transition-all',
              filterType === 'all'
                ? 'bg-gradient-to-r from-primary-500 to-primary-400 text-white shadow-lg'
                : 'border border-white/10 bg-white/5 text-slate-300 hover:bg-white/10'
            ]"
          >
            全部 ({{ detectionStore.detectionHistory.length }})
          </button>
          <button
            @click="setFilterType('image')"
            :class="[
              'rounded-xl px-4 py-2 text-sm font-medium transition-all',
              filterType === 'image'
                ? 'bg-gradient-to-r from-primary-500 to-primary-400 text-white shadow-lg'
                : 'border border-white/10 bg-white/5 text-slate-300 hover:bg-white/10'
            ]"
          >
            图片 ({{ detectionStore.detectionHistory.filter(h => h.file_type === 'image').length }})
          </button>
          <button
            @click="setFilterType('video')"
            :class="[
              'rounded-xl px-4 py-2 text-sm font-medium transition-all',
              filterType === 'video'
                ? 'bg-gradient-to-r from-accent-500 to-primary-500 text-white shadow-lg'
                : 'border border-white/10 bg-white/5 text-slate-300 hover:bg-white/10'
            ]"
          >
            视频 ({{ detectionStore.detectionHistory.filter(h => h.file_type === 'video').length }})
          </button>
        </div>

        <div class="flex justify-between items-center mb-6">
          <div class="flex items-center space-x-4">
            <h2 class="text-lg font-semibold">当前显示 {{ paginatedHistory.length }} 条 / 共 {{ filteredHistory.length }} 条</h2>
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
          <div v-if="formattedLastSync" class="text-xs text-slate-400/80">
            最近同步：{{ formattedLastSync }}
          </div>
          <button data-testid="history-refresh" @click="loadHistory(true)" class="btn-secondary text-sm">
            刷新
          </button>
        </div>

        <div
          v-if="detectionStore.historyLoading"
          data-testid="history-loading"
          class="flex items-center justify-center py-12 text-slate-300/80"
        >
          <div class="flex flex-col items-center gap-3">
            <div class="h-12 w-12 animate-spin rounded-full border-4 border-primary-500/20 border-t-primary-400"></div>
            <p class="text-sm">加载中...</p>
          </div>
        </div>

        <div v-else-if="filteredHistory.length === 0" class="text-center py-12 text-slate-500/70">
          <svg class="mx-auto h-24 w-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p>{{ filterType === 'all' ? '暂无识别记录' : `暂无${filterType === 'image' ? '图片' : '视频'}记录` }}</p>
        </div>

        <div v-else class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              v-for="item in paginatedHistory"
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

          <!-- 分页控件 -->
          <div v-if="totalPages > 1" class="mt-8 flex items-center justify-center gap-2">
            <!-- 上一页按钮 -->
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              :class="[
                'flex h-10 w-10 items-center justify-center rounded-xl border transition-all',
                currentPage === 1
                  ? 'cursor-not-allowed border-white/5 bg-white/5 text-slate-500'
                  : 'border-white/10 bg-white/5 text-slate-300 hover:border-primary-400/50 hover:bg-primary-500/10 hover:text-primary-300'
              ]"
              title="上一页"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <!-- 页码按钮 -->
            <template v-for="page in totalPages" :key="page">
              <!-- 始终显示第一页 -->
              <button
                v-if="page === 1"
                @click="goToPage(page)"
                :class="[
                  'flex h-10 w-10 items-center justify-center rounded-xl border text-sm font-semibold transition-all',
                  currentPage === page
                    ? 'border-primary-400/50 bg-gradient-to-r from-primary-500 to-primary-400 text-white shadow-lg'
                    : 'border-white/10 bg-white/5 text-slate-300 hover:border-primary-400/50 hover:bg-primary-500/10 hover:text-primary-300'
                ]"
              >
                {{ page }}
              </button>

              <!-- 省略号（前） -->
              <span
                v-else-if="page === 2 && currentPage > 4"
                class="flex h-10 w-10 items-center justify-center text-slate-400"
              >
                ...
              </span>

              <!-- 当前页附近的页码 -->
              <button
                v-else-if="page > 1 && page < totalPages && Math.abs(page - currentPage) <= 2"
                @click="goToPage(page)"
                :class="[
                  'flex h-10 w-10 items-center justify-center rounded-xl border text-sm font-semibold transition-all',
                  currentPage === page
                    ? 'border-primary-400/50 bg-gradient-to-r from-primary-500 to-primary-400 text-white shadow-lg'
                    : 'border-white/10 bg-white/5 text-slate-300 hover:border-primary-400/50 hover:bg-primary-500/10 hover:text-primary-300'
                ]"
              >
                {{ page }}
              </button>

              <!-- 省略号（后） -->
              <span
                v-else-if="page === totalPages - 1 && currentPage < totalPages - 3"
                class="flex h-10 w-10 items-center justify-center text-slate-400"
              >
                ...
              </span>

              <!-- 始终显示最后一页 -->
              <button
                v-else-if="page === totalPages"
                @click="goToPage(page)"
                :class="[
                  'flex h-10 w-10 items-center justify-center rounded-xl border text-sm font-semibold transition-all',
                  currentPage === page
                    ? 'border-primary-400/50 bg-gradient-to-r from-primary-500 to-primary-400 text-white shadow-lg'
                    : 'border-white/10 bg-white/5 text-slate-300 hover:border-primary-400/50 hover:bg-primary-500/10 hover:text-primary-300'
                ]"
              >
                {{ page }}
              </button>
            </template>

            <!-- 下一页按钮 -->
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              :class="[
                'flex h-10 w-10 items-center justify-center rounded-xl border transition-all',
                currentPage === totalPages
                  ? 'cursor-not-allowed border-white/5 bg-white/5 text-slate-500'
                  : 'border-white/10 bg-white/5 text-slate-300 hover:border-primary-400/50 hover:bg-primary-500/10 hover:text-primary-300'
              ]"
              title="下一页"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>

            <!-- 页码信息 -->
            <div class="ml-4 text-sm text-slate-400">
              第 {{ currentPage }} / {{ totalPages }} 页
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
        
        <!-- 视频控制按钮组 -->
        <div v-if="previewItem?.file_type === 'video' && previewMode === 'both'" class="flex items-center gap-2">
          <!-- 同步播放/暂停按钮 -->
          <button
            @click.stop="toggleVideoPlayback"
            class="flex h-10 items-center gap-2 rounded-full border px-4 transition-all"
            :class="isVideoPlaying 
              ? 'border-red-400/30 bg-red-500/20 text-red-300 hover:border-red-400/50 hover:bg-red-500/30' 
              : 'border-primary-400/30 bg-primary-500/20 text-primary-300 hover:border-primary-400/50 hover:bg-primary-500/30'"
            :title="isVideoPlaying ? '暂停播放' : '同步播放'"
          >
            <svg v-if="!isVideoPlaying" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
            <svg v-else class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
            <span class="text-sm font-medium">{{ isVideoPlaying ? '暂停' : '同步播放' }}</span>
          </button>
          
          <!-- 回到原点按钮 -->
          <button
            @click.stop="resetVideos"
            class="flex h-10 items-center gap-2 rounded-full border border-slate-400/30 bg-slate-500/20 px-4 text-slate-300 transition-all hover:border-slate-400/50 hover:bg-slate-500/30"
            title="重置到开始位置"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
            <span class="text-sm font-medium">回到原点</span>
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
            <span v-if="previewItem.file_type === 'image'">拖拽平移 · 滚轮缩放</span>
            <span v-else>视频播放</span>
          </div>
          <div
            :class="[
              'relative mt-4 flex h-full w-full items-center justify-center overflow-hidden rounded-2xl border border-white/15 bg-slate-900/40',
              previewItem.file_type === 'image' ? 'cursor-move' : ''
            ]"
            @mousedown="(e) => previewItem.file_type === 'image' && startDrag(e)"
            @mousemove="(e) => previewItem.file_type === 'image' && onDrag(e)"
            @mouseup="previewItem.file_type === 'image' && endDrag()"
            @mouseleave="previewItem.file_type === 'image' && endDrag()"
            @wheel.prevent="(e) => previewItem.file_type === 'image' && onWheel(e)"
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
              ref="originalVideoRef"
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
            <span v-if="previewItem.file_type === 'image'">拖拽平移 · 滚轮缩放</span>
            <span v-else>视频播放</span>
          </div>
          <div
            :class="[
              'relative mt-4 flex h-full w-full items-center justify-center overflow-hidden rounded-2xl border border-white/15 bg-slate-900/40',
              previewItem.file_type === 'image' ? 'cursor-move' : ''
            ]"
            @mousedown="(e) => previewItem.file_type === 'image' && startDrag(e)"
            @mousemove="(e) => previewItem.file_type === 'image' && onDrag(e)"
            @mouseup="previewItem.file_type === 'image' && endDrag()"
            @mouseleave="previewItem.file_type === 'image' && endDrag()"
            @wheel.prevent="(e) => previewItem.file_type === 'image' && onWheel(e)"
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
              ref="resultVideoRef"
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

<script>
export default {
  name: 'History'
}
</script>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
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

// 视频同步播放相关
const originalVideoRef = ref(null)
const resultVideoRef = ref(null)
const isVideoPlaying = ref(false)

// 批量选择相关状态
const batchMode = ref(false)
const selectedIds = ref([])
const isDisposed = ref(false)

// 分页和筛选相关状态
const currentPage = ref(1)
const pageSize = 9
const filterType = ref('all') // 'all', 'image', 'video'

// 筛选后的历史记录
const filteredHistory = computed(() => {
  if (filterType.value === 'all') {
    return detectionStore.detectionHistory
  }
  return detectionStore.detectionHistory.filter(item => item.file_type === filterType.value)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredHistory.value.length / pageSize)
})

// 当前页的数据
const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredHistory.value.slice(start, end)
})

// 切换筛选类型
const setFilterType = (type) => {
  filterType.value = type
  currentPage.value = 1 // 重置到第一页
}

// 切换页码
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

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
  // 暂停所有视频
  if (originalVideoRef.value) originalVideoRef.value.pause()
  if (resultVideoRef.value) resultVideoRef.value.pause()
  isVideoPlaying.value = false
}

// 视频同步播放/暂停
const toggleVideoPlayback = () => {
  if (!previewItem.value || previewItem.value.file_type !== 'video') return
  
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

// 重置视频到开始位置（暂停状态）
const resetVideos = () => {
  if (!previewItem.value || previewItem.value.file_type !== 'video') return
  
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

// 批量选择相关计算属性（基于当前筛选结果）
const isAllSelected = computed(() => {
  return filteredHistory.value.length > 0 && 
         selectedIds.value.length === filteredHistory.value.length
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

// 全选/取消全选（基于当前筛选结果）
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredHistory.value.map(item => item.id)
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
  loadHistory()
})

const historyError = computed(() => detectionStore.historyError || detectionStore.requestError)
const formattedLastSync = computed(() => {
  if (!detectionStore.lastHistorySyncAt) {
    return ''
  }
  return formatDate(detectionStore.lastHistorySyncAt)
})

onBeforeUnmount(() => {
  isDisposed.value = true
})

const loadHistory = async (force = false) => {
  if (isDisposed.value) {
    return
  }
  await detectionStore.loadHistory({ force })
}
</script>
