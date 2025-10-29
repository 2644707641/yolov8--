<template>
  <div class="relative min-h-screen overflow-hidden">
    <!-- 背景 -->
    <div class="absolute inset-0">
      <div class="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-black"></div>
      <div class="absolute inset-0 bg-grid opacity-10"></div>
      <div class="absolute -top-28 -left-32 h-96 w-96 rounded-full bg-primary-500/30 blur-3xl"></div>
      <div class="absolute top-1/3 right-[-120px] h-[420px] w-[420px] rounded-full bg-accent-500/20 blur-3xl"></div>
    </div>

    <div class="relative z-10 flex min-h-screen flex-col">
      <!-- 导航栏 -->
      <nav class="sticky top-0 z-20 border-b border-white/10 bg-white/5 backdrop-blur-xl">
        <div class="mx-auto flex h-20 w-full max-w-7xl items-center justify-between px-6">
          <div>
            <span class="pill">YOLOv8 Suite</span>
            <h1 class="mt-2 text-2xl font-semibold leading-tight text-gradient">
              模型权重管理
            </h1>
          </div>
          <div class="flex items-center gap-4">
            <router-link to="/dashboard" class="btn-secondary text-sm">
              返回控制台
            </router-link>
            <router-link to="/history" class="btn-secondary text-sm">
              历史记录
            </router-link>
            <button @click="authStore.logout" class="btn-ghost text-sm">
              退出登录
            </button>
          </div>
        </div>
      </nav>

      <!-- 主要内容 -->
      <div class="flex-1 overflow-y-auto px-6 py-10 lg:px-12">
        <div class="mx-auto w-full max-w-6xl space-y-8">
          
          <!-- 上传新权重 -->
          <div class="card">
            <div class="mb-6">
              <h2 class="text-2xl font-semibold text-white">上传新权重</h2>
              <p class="mt-2 text-sm text-slate-300/80">
                上传您的 YOLOv8 模型权重文件，支持 .pt 和 .pth 格式
              </p>
            </div>

            <div class="space-y-4">
              <!-- 文件上传区域 -->
              <div
                @drop.prevent="handleFileDrop"
                @dragover.prevent
                @dragenter.prevent
                class="group relative cursor-pointer rounded-2xl border-2 border-dashed border-white/20 bg-white/5 p-8 text-center transition-all duration-300 hover:border-primary-400/50 hover:bg-white/8"
                @click="$refs.fileInput.click()"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept=".pt,.pth"
                  class="hidden"
                  @change="handleFileSelect"
                />
                
                <div v-if="!uploadingFile" class="space-y-4">
                  <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-500/20 text-primary-300 transition-transform duration-300 group-hover:scale-110">
                    <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                    </svg>
                  </div>
                  <div>
                    <p class="text-base font-medium text-white">点击上传或拖放文件</p>
                    <p class="mt-1 text-sm text-slate-400">支持 .pt 和 .pth 格式，最大 200MB</p>
                  </div>
                </div>

                <div v-else class="space-y-4">
                  <div class="mx-auto h-16 w-16">
                    <div class="h-16 w-16 animate-spin rounded-full border-4 border-primary-500/20 border-t-primary-400"></div>
                  </div>
                  <p class="text-base font-medium text-white">正在上传...</p>
                </div>
              </div>
            </div>

            <!-- 上传错误提示 -->
            <div v-if="uploadError" class="mt-4 rounded-xl border border-red-500/20 bg-red-500/10 p-4">
              <div class="flex items-start gap-3">
                <svg class="h-5 w-5 flex-shrink-0 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div class="flex-1">
                  <p class="text-sm font-medium text-red-300">上传失败</p>
                  <p class="mt-1 text-xs text-red-200/80">{{ uploadError }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 已有权重列表 -->
          <div class="card">
            <div class="mb-6 flex items-end justify-between">
              <div>
                <h2 class="text-2xl font-semibold text-white">我的权重列表</h2>
                <p class="mt-2 text-sm text-slate-300/80">
                  管理您上传的所有模型权重，切换或删除
                </p>
              </div>
              <button
                @click="loadWeights"
                :disabled="loading"
                class="btn-secondary text-sm"
              >
                <svg v-if="!loading" class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <div v-else class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white"></div>
                刷新
              </button>
            </div>

            <!-- 加载中 -->
            <div v-if="loading && weights.length === 0" class="flex items-center justify-center py-12">
              <div class="text-center">
                <div class="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-primary-500/20 border-t-primary-400"></div>
                <p class="mt-4 text-sm text-slate-400">加载中...</p>
              </div>
            </div>

            <!-- 无权重 -->
            <div v-else-if="weights.length === 0" class="rounded-2xl border border-white/10 bg-white/5 p-12 text-center">
              <div class="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-slate-700/30 text-slate-400">
                <svg class="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                </svg>
              </div>
              <h3 class="mt-4 text-lg font-semibold text-white">暂无权重文件</h3>
              <p class="mt-2 text-sm text-slate-400">上传您的第一个模型权重开始使用</p>
            </div>

            <!-- 权重列表 -->
            <div v-else class="space-y-4">
              <div
                v-for="weight in weights"
                :key="weight.id"
                class="group relative overflow-hidden rounded-2xl border transition-all duration-300"
                :class="weight.is_active 
                  ? 'border-primary-400/50 bg-gradient-to-r from-primary-500/20 to-primary-400/10 shadow-[0_0_30px_rgba(37,99,235,0.25)]' 
                  : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/8'"
              >
                <div class="p-6">
                  <div class="flex items-start justify-between gap-4">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-3 flex-wrap">
                        <h3 class="text-lg font-semibold text-white truncate">{{ weight.name }}</h3>
                        <span
                          v-if="weight.is_default"
                          class="inline-flex items-center gap-1 rounded-full bg-amber-500/20 px-3 py-1 text-xs font-medium text-amber-300"
                        >
                          <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                          </svg>
                          系统默认
                        </span>
                        <span
                          v-if="weight.is_active"
                          class="inline-flex items-center gap-1 rounded-full bg-primary-500/20 px-3 py-1 text-xs font-medium text-primary-300"
                        >
                          <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                          </svg>
                          当前使用
                        </span>
                      </div>
                      
                      <p v-if="weight.description" class="mt-2 text-sm text-slate-300/80">
                        {{ weight.description }}
                      </p>
                      
                      <div class="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-400">
                        <span v-if="!weight.is_default" class="flex items-center gap-1">
                          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                          </svg>
                          {{ formatFileSize(weight.file_size) }}
                        </span>
                        <span v-if="!weight.is_default" class="flex items-center gap-1">
                          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                          </svg>
                          {{ formatDate(weight.created_at) }}
                        </span>
                        <span v-else class="flex items-center gap-1">
                          <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                          </svg>
                          所有用户可用
                        </span>
                      </div>
                    </div>

                    <div class="flex items-center gap-2">
                      <button
                        v-if="!weight.is_active"
                        @click="activateWeight(weight.id)"
                        :disabled="activating === weight.id"
                        class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white transition-all hover:border-primary-400/50 hover:bg-primary-500/20 disabled:opacity-50"
                      >
                        <div v-if="activating === weight.id" class="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white"></div>
                        <span v-else>使用</span>
                      </button>
                      
                      <button
                        v-if="!weight.is_default"
                        @click="confirmDelete(weight)"
                        :disabled="deleting === weight.id"
                        class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-red-300 transition-all hover:border-red-400/50 hover:bg-red-500/20 disabled:opacity-50"
                      >
                        <div v-if="deleting === weight.id" class="h-4 w-4 animate-spin rounded-full border-2 border-red-300/20 border-t-red-300"></div>
                        <span v-else>删除</span>
                      </button>
                      <span
                        v-else
                        class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-400"
                      >
                        系统权重
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 权重上传确认弹窗 -->
    <div
      v-if="showWeightDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      @click.self="cancelUploadWeight"
    >
      <div class="relative w-full max-w-md rounded-3xl border border-white/10 bg-slate-900 p-8 shadow-2xl">
        <h3 class="text-xl font-semibold text-white">上传权重文件</h3>
        <p class="mt-2 text-sm text-slate-300">
          文件：<span class="font-medium text-primary-300">{{ pendingWeightFile?.name }}</span>
        </p>
        
        <div class="mt-6 space-y-4">
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-300">
              权重名称（可选）
            </label>
            <input
              v-model="weightName"
              type="text"
              placeholder="留空则使用文件名"
              class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-slate-400 transition-all focus:border-primary-400/50 focus:bg-white/8 focus:outline-none"
            />
            <p class="mt-1 text-xs text-slate-400">如果留空，将使用原文件名：{{ pendingWeightFile?.name }}</p>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-300">
              权重描述（可选）
            </label>
            <input
              v-model="weightDescription"
              type="text"
              placeholder="例如：训练于2024年数据集，精度95%"
              class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-slate-400 transition-all focus:border-primary-400/50 focus:bg-white/8 focus:outline-none"
            />
          </div>
        </div>
        
        <div class="mt-6 flex gap-3">
          <button
            @click="cancelUploadWeight"
            class="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-white transition-all hover:bg-white/10"
          >
            取消
          </button>
          <button
            @click="confirmUploadWeight"
            class="flex-1 rounded-xl bg-primary-500 px-4 py-3 text-sm font-medium text-white transition-all hover:bg-primary-600"
          >
            确认上传
          </button>
        </div>
      </div>
    </div>

    <!-- 权重上传中/完成弹窗 -->
    <div
      v-if="uploadingFile || uploadSuccess"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    >
      <div class="relative rounded-3xl border border-white/10 bg-slate-900 p-8 shadow-2xl">
        <div class="flex flex-col items-center gap-4">
          <!-- 上传中 -->
          <div v-if="uploadingFile && !uploadSuccess" class="h-16 w-16 animate-spin rounded-full border-4 border-primary-500/20 border-t-primary-400"></div>
          <!-- 上传成功 -->
          <div v-else class="flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20">
            <svg class="h-10 w-10 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          
          <div class="text-center">
            <h3 class="text-xl font-semibold text-white">
              {{ uploadSuccess ? '权重加载完成' : '权重正在上传中' }}
            </h3>
            <p class="mt-2 text-sm text-slate-400">
              {{ uploadSuccess ? '权重已成功上传到云端存储' : '请稍等，正在上传到云端存储...' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div
      v-if="deleteConfirmWeight"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      @click.self="deleteConfirmWeight = null"
    >
      <div class="relative w-full max-w-md rounded-3xl border border-white/10 bg-slate-900 p-8 shadow-2xl">
        <h3 class="text-xl font-semibold text-white">确认删除</h3>
        <p class="mt-4 text-sm text-slate-300">
          确定要删除权重 <span class="font-medium text-primary-300">{{ deleteConfirmWeight.name }}</span> 吗？此操作无法撤销。
        </p>
        
        <div class="mt-6 flex gap-3">
          <button
            @click="deleteConfirmWeight = null"
            class="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-white transition-all hover:bg-white/10"
          >
            取消
          </button>
          <button
            @click="deleteWeight(deleteConfirmWeight.id)"
            class="flex-1 rounded-xl bg-red-500 px-4 py-3 text-sm font-medium text-white transition-all hover:bg-red-600"
          >
            确认删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { supabase } from '../config/supabase'

const authStore = useAuthStore()

const weights = ref([])
const loading = ref(false)
const uploadingFile = ref(false)
const uploadSuccess = ref(false)
const uploadError = ref(null)
const weightName = ref('')
const weightDescription = ref('')
const showWeightDialog = ref(false)
const pendingWeightFile = ref(null)
const activating = ref(null)
const deleting = ref(null)
const deleteConfirmWeight = ref(null)

// 加载权重列表
const loadWeights = async () => {
  loading.value = true
  try {
    const token = (await supabase.auth.getSession()).data.session?.access_token
    if (!token) {
      throw new Error('未登录')
    }

    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/model-weights`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('加载权重列表失败')
    }

    const data = await response.json()
    console.log('📦 API返回的权重数据:', data)
    console.log('📊 权重列表数量:', data.weights?.length || 0)
    weights.value = data.weights || []
    console.log('✅ 已加载到界面的权重数量:', weights.value.length)
  } catch (error) {
    console.error('加载权重列表失败:', error)
    uploadError.value = error.message
  } finally {
    loading.value = false
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    showWeightConfirmDialog(file)
  }
}

// 处理文件拖放
const handleFileDrop = (event) => {
  const file = event.dataTransfer?.files?.[0]
  if (file && (file.name.endsWith('.pt') || file.name.endsWith('.pth'))) {
    showWeightConfirmDialog(file)
  }
}

// 显示权重确认弹窗
const showWeightConfirmDialog = (file) => {
  pendingWeightFile.value = file
  showWeightDialog.value = true
  // 重置输入框
  weightName.value = ''
  weightDescription.value = ''
}

// 取消上传
const cancelUploadWeight = () => {
  showWeightDialog.value = false
  pendingWeightFile.value = null
  weightName.value = ''
  weightDescription.value = ''
}

// 确认上传权重
const confirmUploadWeight = async () => {
  if (!pendingWeightFile.value) return
  
  // 关闭确认弹窗，显示加载弹窗
  showWeightDialog.value = false
  
  await uploadWeight(pendingWeightFile.value)
  
  pendingWeightFile.value = null
}

// 上传权重
const uploadWeight = async (file) => {
  uploadingFile.value = true
  uploadSuccess.value = false
  uploadError.value = null

  try {
    const token = (await supabase.auth.getSession()).data.session?.access_token
    if (!token) {
      throw new Error('未登录')
    }

    const formData = new FormData()
    formData.append('model', file)
    if (weightName.value) {
      formData.append('name', weightName.value)
    }
    if (weightDescription.value) {
      formData.append('description', weightDescription.value)
    }

    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/upload-model`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '上传失败')
    }

    const data = await response.json()
    console.log('📤 上传响应数据:', data)
    if (data.success) {
      console.log('✅ 权重上传成功，权重信息:', data.weight)
      
      // 显示成功状态
      uploadingFile.value = false
      uploadSuccess.value = true
      
      // 2秒后自动关闭弹窗
      setTimeout(() => {
        uploadSuccess.value = false
      }, 2000)
      
      // 重置表单
      weightName.value = ''
      weightDescription.value = ''
      // 重新加载列表
      await loadWeights()
    } else {
      // 如果上传失败，重新显示确认弹窗
      pendingWeightFile.value = file
      showWeightDialog.value = true
    }
  } catch (error) {
    console.error('上传权重失败:', error)
    uploadError.value = error.message
    uploadingFile.value = false
    uploadSuccess.value = false
  }
}

// 激活权重
const activateWeight = async (weightId) => {
  activating.value = weightId
  try {
    const token = (await supabase.auth.getSession()).data.session?.access_token
    if (!token) {
      throw new Error('未登录')
    }

    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/model-weights/${weightId}/activate`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '激活失败')
    }

    const data = await response.json()
    console.log('✅ 权重激活成功:', data.message)
    
    // 重新加载列表
    await loadWeights()
  } catch (error) {
    console.error('激活权重失败:', error)
    alert('选择权重失败: ' + error.message)
  } finally {
    activating.value = null
  }
}

// 确认删除
const confirmDelete = (weight) => {
  deleteConfirmWeight.value = weight
}

// 删除权重
const deleteWeight = async (weightId) => {
  deleting.value = weightId
  try {
    const token = (await supabase.auth.getSession()).data.session?.access_token
    if (!token) {
      throw new Error('未登录')
    }

    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/model-weights/${weightId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '删除失败')
    }

    console.log('✅ 权重删除成功')
    
    // 关闭确认对话框
    deleteConfirmWeight.value = null
    // 重新加载列表
    await loadWeights()
  } catch (error) {
    console.error('删除权重失败:', error)
    alert('删除失败: ' + error.message)
  } finally {
    deleting.value = null
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadWeights()
})
</script>

<style scoped>
.bg-grid {
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: rgb(148 163 184);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 9999px;
  backdrop-filter: blur(8px);
}

.text-gradient {
  background: linear-gradient(to right, #ffffff, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card {
  border-radius: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  padding: 2rem;
  backdrop-filter: blur(12px);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-ghost {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgb(226 232 240);
  background: transparent;
  border-radius: 0.75rem;
  transition: all 0.2s;
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.05);
}
</style>
