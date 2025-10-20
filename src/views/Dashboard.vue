<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">YOLOv8 智能识别停车位系统</h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link
              to="/history"
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              历史记录
            </router-link>
            <div class="text-sm text-gray-600">{{ authStore.user?.email }}</div>
            <button @click="authStore.logout" class="btn-secondary text-sm">
              退出登录
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <div class="flex h-[calc(100vh-4rem)]">
      <!-- 左侧导航栏 -->
      <div class="w-80 bg-white border-r border-gray-200 overflow-y-auto">
        <div class="p-4">
          <h2 class="text-lg font-semibold text-gray-800 mb-4">操作步骤</h2>
          <div class="space-y-2">
          <!-- 导航项 1 -->
          <button
            @click="currentStep = 1"
            :class="[
              'w-full text-left px-4 py-3 rounded-lg transition-all',
              currentStep === 1 
                ? 'bg-primary-600 text-white shadow-md' 
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            ]"
          >
            <div class="flex items-center">
              <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" :class="currentStep === 1 ? 'bg-white text-primary-600' : 'bg-gray-200 text-gray-600'">1</span>
              <span class="ml-3 font-medium">上传模型权重</span>
              <svg v-if="detectionStore.modelUploaded" class="ml-auto h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </button>

          <!-- 导航项 2 -->
          <button
            @click="currentStep = 2"
            :class="[
              'w-full text-left px-4 py-3 rounded-lg transition-all',
              currentStep === 2 
                ? 'bg-primary-600 text-white shadow-md' 
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            ]"
          >
            <div class="flex items-center">
              <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" :class="currentStep === 2 ? 'bg-white text-primary-600' : 'bg-gray-200 text-gray-600'">2</span>
              <span class="ml-3 font-medium">上传文件</span>
              <svg v-if="selectedFile" class="ml-auto h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </button>

          <!-- 导航项 3 -->
          <button
            @click="currentStep = 3"
            :class="[
              'w-full text-left px-4 py-3 rounded-lg transition-all',
              currentStep === 3 
                ? 'bg-primary-600 text-white shadow-md' 
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            ]"
          >
            <div class="flex items-center">
              <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" :class="currentStep === 3 ? 'bg-white text-primary-600' : 'bg-gray-200 text-gray-600'">3</span>
              <span class="ml-3 font-medium">调整参数</span>
            </div>
          </button>

          <!-- 导航项 4 -->
          <button
            @click="currentStep = 4"
            :class="[
              'w-full text-left px-4 py-3 rounded-lg transition-all',
              currentStep === 4 
                ? 'bg-primary-600 text-white shadow-md' 
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            ]"
          >
            <div class="flex items-center">
              <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" :class="currentStep === 4 ? 'bg-white text-primary-600' : 'bg-gray-200 text-gray-600'">4</span>
              <span class="ml-3 font-medium">识别结果</span>
              <svg v-if="detectionStore.currentResult" class="ml-auto h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </button>
          </div>

          <!-- 快速操作提示 -->
          <div class="mt-6 p-4 bg-blue-50 rounded-lg">
            <div class="flex items-start">
              <svg class="h-5 w-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-blue-900">提示</h3>
                <p class="mt-1 text-xs text-blue-700">按照步骤依次操作，完成后会显示绿色勾选标记</p>
              </div>
            </div>
          </div>

          <!-- 隐藏的原有卡片内容，保留功能 -->
          <div class="hidden">
          <!-- 模型上传（隐藏但保留功能） -->
          <div class="card">
            <h2 class="text-lg font-semibold mb-4">上传模型权重</h2>
            <div class="space-y-4">
              <div
                @dragover.prevent
                @drop.prevent="handleModelDrop"
                class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-500 transition-colors cursor-pointer"
                @click="modelInput?.click()"
              >
                <input
                  ref="modelInput"
                  type="file"
                  accept=".pt,.pth"
                  @change="handleModelSelect"
                  class="hidden"
                />
                <!-- 上传中状态 -->
                <div v-if="isUploadingModel" class="text-primary-600">
                  <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
                  <p class="mt-2 text-sm">正在上传模型...</p>
                </div>
                <!-- 未上传状态 -->
                <div v-else-if="!detectionStore.modelUploaded && !selectedModelName">
                  <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                  <p class="mt-2 text-sm text-gray-600">拖拽或点击上传模型文件 (.pt, .pth)</p>
                </div>
                <!-- 已上传成功状态 -->
                <div v-else-if="detectionStore.modelUploaded" class="text-green-600">
                  <svg class="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <p class="mt-2 text-sm font-medium">模型已上传</p>
                  <p class="text-xs text-gray-600">{{ detectionStore.modelFile?.name || selectedModelName }}</p>
                </div>
                <!-- 已选择但未成功上传状态 -->
                <div v-else class="text-yellow-600">
                  <svg class="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                  </svg>
                  <p class="mt-2 text-sm font-medium">模型已选择（等待上传到后端）</p>
                  <p class="text-xs text-gray-600">{{ selectedModelName }}</p>
                  <button @click.stop="retryUpload" class="mt-2 text-xs text-primary-600 hover:text-primary-700 underline">
                    重新上传
                  </button>
                </div>
              </div>
              
              <!-- 错误提示 -->
              <div v-if="uploadError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
                <div class="flex items-start">
                  <svg class="h-5 w-5 text-red-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <div class="flex-1">
                    <p class="text-sm text-red-800 font-medium">上传失败</p>
                    <p class="text-xs text-red-600 mt-1">{{ uploadError }}</p>
                    <p class="text-xs text-red-600 mt-1">请确保后端服务已启动（端口8000）</p>
                  </div>
                  <button @click="uploadError = null" class="text-red-600 hover:text-red-800">
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 文件上传（隐藏但保留功能） -->
          <div class="card">
            <input
              ref="fileInput"
              type="file"
              :accept="fileType === 'image' ? 'image/*' : 'video/*'"
              @change="handleFileSelect"
              class="hidden"
            />
          </div>
          </div>
        </div>
      </div>

      <!-- 右侧主展示区域 -->
      <div class="flex-1 overflow-y-auto bg-gradient-to-br from-gray-50 to-gray-100">
        <div class="max-w-5xl mx-auto p-8">
          
          <!-- 步骤1：上传模型权重 -->
          <div v-if="currentStep === 1" class="card shadow-lg">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">上传模型权重</h2>
            <p class="text-sm text-gray-500 mb-6">上传你的 YOLOv8 模型文件（.pt 或 .pth 格式）</p>
            
            <div
              @dragover.prevent
              @drop.prevent="handleModelDrop"
              class="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-primary-500 transition-colors cursor-pointer bg-gray-50"
              @click="modelInput?.click()"
            >
              <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              <p class="mt-4 text-lg font-medium text-gray-700">点击或拖动模型文件到此处</p>
              <p class="mt-2 text-sm text-gray-500">支持格式：.pt, .pth</p>
            </div>
            
            <div v-if="uploadStatus === 'uploading'" class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="flex items-center">
                <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
                <p class="ml-3 text-sm text-blue-900">正在上传模型...</p>
              </div>
            </div>
            
            <div v-if="detectionStore.modelUploaded" class="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <p class="ml-3 text-sm text-green-900 font-medium">模型上传成功！</p>
                </div>
                <button @click="currentStep = 2" class="btn-primary text-sm">
                  下一步 →
                </button>
              </div>
            </div>
            
            <div v-if="uploadError" class="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div class="flex items-center justify-between">
                <p class="text-sm text-red-900">{{ uploadError }}</p>
                <button @click="uploadError = null" class="text-red-600 hover:text-red-800">
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- 步骤2：上传文件 -->
          <div v-if="currentStep === 2" class="card shadow-lg">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">上传文件</h2>
            <p class="text-sm text-gray-500 mb-6">选择需要进行目标检测的图片或视频文件</p>
            
            <div class="grid grid-cols-2 gap-4 mb-6">
              <button
                @click="fileType = 'image'"
                :class="[
                  'px-6 py-4 rounded-lg border-2 transition-all text-left',
                  fileType === 'image' 
                    ? 'border-primary-600 bg-primary-50' 
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <div class="flex items-center">
                  <div :class="[
                    'flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center',
                    fileType === 'image' ? 'bg-primary-100' : 'bg-gray-100'
                  ]">
                    <svg class="h-6 w-6" :class="fileType === 'image' ? 'text-primary-600' : 'text-gray-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                  </div>
                  <div class="ml-4">
                    <h3 class="font-semibold" :class="fileType === 'image' ? 'text-primary-900' : 'text-gray-900'">图片</h3>
                    <p class="text-xs text-gray-500 mt-1">JPG, PNG, BMP 等</p>
                  </div>
                </div>
              </button>
              
              <button
                @click="fileType = 'video'"
                :class="[
                  'px-6 py-4 rounded-lg border-2 transition-all text-left',
                  fileType === 'video' 
                    ? 'border-primary-600 bg-primary-50' 
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <div class="flex items-center">
                  <div :class="[
                    'flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center',
                    fileType === 'video' ? 'bg-primary-100' : 'bg-gray-100'
                  ]">
                    <svg class="h-6 w-6" :class="fileType === 'video' ? 'text-primary-600' : 'text-gray-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                  </div>
                  <div class="ml-4">
                    <h3 class="font-semibold" :class="fileType === 'video' ? 'text-primary-900' : 'text-gray-900'">视频</h3>
                    <p class="text-xs text-gray-500 mt-1">MP4, AVI, MOV 等</p>
                  </div>
                </div>
              </button>
            </div>
            
            <div 
              @click="fileInput?.click()"
              class="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-primary-500 transition-colors cursor-pointer bg-gray-50"
            >
              <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              <p class="mt-4 text-lg font-medium text-gray-700">点击选择{{ fileType === 'image' ? '图片' : '视频' }}文件</p>
              <p class="mt-2 text-sm text-gray-500">或拖动文件到此处</p>
            </div>
            
            <div v-if="selectedFile" class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <svg class="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <div class="ml-3">
                    <p class="text-sm text-blue-900 font-medium">已选择文件</p>
                    <p class="text-xs text-blue-700 mt-1">{{ selectedFile.name }}</p>
                  </div>
                </div>
                <button @click="currentStep = 3" class="btn-primary text-sm">
                  下一步 →
                </button>
              </div>
            </div>
          </div>
          
          <!-- 步骤3：调整参数 -->
          <div v-if="currentStep === 3" class="card shadow-lg">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">调整参数</h2>
            <p class="text-sm text-gray-500 mb-8">根据需要调整检测参数，优化识别结果</p>
            
            <div class="space-y-6">
              <!-- 图片大小 -->
              <div class="bg-gray-50 p-6 rounded-lg">
                <label class="block text-sm font-semibold text-gray-800 mb-3">
                  图片大小: <span class="text-primary-600">{{ detectionStore.detectionParams.imgSize }}px</span>
                </label>
                <input
                  v-model="detectionStore.detectionParams.imgSize"
                  type="range"
                  min="160"
                  max="1920"
                  step="32"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div class="flex justify-between text-xs text-gray-400 mt-1">
                  <span>160px (超快)</span>
                  <span>640px (平衡)</span>
                  <span>1920px (高精度)</span>
                </div>
                <p class="text-xs text-gray-500 mt-2">
                  💡 较大的尺寸可以检测更小的物体，但处理速度较慢
                </p>
              </div>

              <!-- 置信度阈值 -->
              <div class="bg-gray-50 p-6 rounded-lg">
                <label class="block text-sm font-semibold text-gray-800 mb-3">
                  置信度阈值: <span class="text-primary-600">{{ detectionStore.detectionParams.confidence }}</span>
                </label>
                <input
                  v-model="detectionStore.detectionParams.confidence"
                  type="range"
                  min="0.01"
                  max="0.99"
                  step="0.01"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div class="flex justify-between text-xs text-gray-400 mt-1">
                  <span>0.01 (宽松)</span>
                  <span>0.50 (平衡)</span>
                  <span>0.99 (严格)</span>
                </div>
                <p class="text-xs text-gray-500 mt-2">
                  💡 较高的阈值会减少误检，但可能漏检一些物体
                </p>
              </div>

              <!-- IOU阈值 -->
              <div class="bg-gray-50 p-6 rounded-lg">
                <label class="block text-sm font-semibold text-gray-800 mb-3">
                  IOU阈值: <span class="text-primary-600">{{ detectionStore.detectionParams.iouThreshold }}</span>
                </label>
                <input
                  v-model="detectionStore.detectionParams.iouThreshold"
                  type="range"
                  min="0.05"
                  max="0.95"
                  step="0.01"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div class="flex justify-between text-xs text-gray-400 mt-1">
                  <span>0.05 (去除更多)</span>
                  <span>0.60 (平衡)</span>
                  <span>0.95 (保留更多)</span>
                </div>
                <p class="text-xs text-gray-500 mt-2">
                  💡 较高的阈值会保留更多重叠的检测框
                </p>
              </div>

              <!-- 最大检测数 -->
              <div class="bg-gray-50 p-6 rounded-lg">
                <label class="block text-sm font-semibold text-gray-800 mb-3">
                  最大检测数: <span class="text-primary-600">{{ detectionStore.detectionParams.maxDetections }}</span>
                </label>
                <input
                  v-model="detectionStore.detectionParams.maxDetections"
                  type="range"
                  min="10"
                  max="2000"
                  step="10"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div class="flex justify-between text-xs text-gray-400 mt-1">
                  <span>10 (最少)</span>
                  <span>300 (推荐)</span>
                  <span>2000 (最多)</span>
                </div>
                <p class="text-xs text-gray-500 mt-2">
                  💡 限制单张图片中检测的最大物体数量
                </p>
              </div>

              <!-- 视频帧间隔 (仅视频) -->
              <div v-if="fileType === 'video'" class="bg-blue-50 p-6 rounded-lg border-2 border-blue-200">
                <label class="block text-sm font-semibold text-gray-800 mb-3">
                  视频帧间隔: <span class="text-primary-600">{{ detectionStore.detectionParams.frameSkip }}</span>
                  <span class="ml-2 text-xs font-normal text-blue-600">(视频专用)</span>
                </label>
                <input
                  v-model="detectionStore.detectionParams.frameSkip"
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  class="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
                />
                <div class="flex justify-between text-xs text-gray-400 mt-1">
                  <span>1 (每帧)</span>
                  <span>3</span>
                  <span>5</span>
                  <span>10 (最快)</span>
                </div>
                <p class="text-xs text-blue-700 mt-2">
                  💡 <strong>1=最流畅</strong> (每帧检测，慢) | <strong>5=平衡</strong> | <strong>10=最快</strong> (跳帧多，可能跳跃)
                </p>
              </div>
            </div>
            
            <!-- 开始识别按钮 -->
            <div class="mt-8 flex justify-end space-x-3">
              <button @click="currentStep = 2" class="btn-secondary">
                ← 上一步
              </button>
              <button
                @click="runDetection"
                :disabled="!detectionStore.modelUploaded || !selectedFile || detectionStore.isProcessing"
                class="btn-primary px-8"
              >
                {{ detectionStore.isProcessing ? '处理中...' : '开始识别 🚀' }}
              </button>
            </div>
          </div>
          
          <!-- 步骤4：识别结果 -->
          <div v-if="currentStep === 4">

            <!-- 处理中状态 -->
            <div v-if="detectionStore.isProcessing" class="card shadow-lg">
            <div class="flex items-center justify-center py-32">
              <div class="text-center">
                <div class="relative">
                  <div class="animate-spin rounded-full h-20 w-20 border-b-4 border-primary-600 mx-auto"></div>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <svg class="h-8 w-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                  </div>
                </div>
                <p class="mt-8 text-xl font-semibold text-gray-900">AI 正在分析中</p>
                <p class="mt-2 text-sm text-gray-500">使用 YOLOv8 深度学习模型进行目标检测...</p>
                <div class="mt-6 flex items-center justify-center space-x-1">
                  <div class="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                  <div class="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                  <div class="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                </div>
              </div>
            </div>
          </div>

            <!-- 识别结果主展示区 -->
            <div v-if="detectionStore.currentResult && !detectionStore.isProcessing" class="space-y-6">
            <!-- 标题 -->
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-2xl font-bold text-gray-900">识别结果</h2>
                <p class="text-sm text-gray-500 mt-1">检测完成，以下是详细结果</p>
              </div>
              <div class="flex items-center space-x-2">
                <span class="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full flex items-center">
                  <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  检测完成
                </span>
              </div>
            </div>
            
            <!-- 统计卡片 -->
            <div class="grid grid-cols-4 gap-4">
              <div class="card text-center">
                <div class="text-3xl font-bold text-primary-600">{{ detectionStore.currentResult.detections?.length || 0 }}</div>
                <div class="text-sm text-gray-600 mt-1">检测物体</div>
              </div>
              <div class="card text-center">
                <div class="text-3xl font-bold text-blue-600">{{ detectionStore.detectionParams.confidence }}</div>
                <div class="text-sm text-gray-600 mt-1">置信度阈值</div>
              </div>
              <div class="card text-center">
                <div class="text-3xl font-bold text-purple-600">{{ detectionStore.detectionParams.imgSize }}</div>
                <div class="text-sm text-gray-600 mt-1">图片尺寸</div>
              </div>
              <div class="card text-center">
                <div class="text-3xl font-bold text-green-600">{{ (detectionStore.currentResult.processTime || 0).toFixed(2) }}s</div>
                <div class="text-sm text-gray-600 mt-1">处理时间</div>
              </div>
            </div>

            <!-- 对比图片展示 -->
            <div class="card shadow-lg">
              <h3 class="text-lg font-semibold mb-4">对比展示</h3>
              <div class="grid grid-cols-2 gap-6">
                <div>
                  <div class="flex items-center justify-between mb-3">
                    <h4 class="text-sm font-medium text-gray-700">原始文件</h4>
                    <span class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">Original</span>
                  </div>
                  <div class="relative group cursor-pointer" @click="openPreview('original')">
                    <img 
                      v-if="fileType === 'image'" 
                      :src="detectionStore.currentResult.originalUrl" 
                      @error="handleImageError($event, '原始图片')"
                      class="w-full rounded-lg border" 
                      alt="原始图片"
                    />
                    <video v-else :src="detectionStore.currentResult.originalUrl" controls class="w-full rounded-lg border"></video>
                    <div v-if="fileType === 'image'" class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all rounded-lg flex items-center justify-center">
                      <span class="text-white opacity-0 group-hover:opacity-100 text-sm font-medium">点击预览</span>
                    </div>
                  </div>
                </div>
                <div>
                  <div class="flex items-center justify-between mb-3">
                    <h4 class="text-sm font-medium text-gray-700">识别结果</h4>
                    <span class="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded">Detected</span>
                  </div>
                  <div class="relative group cursor-pointer" @click="openPreview('result')">
                    <img 
                      v-if="fileType === 'image'" 
                      :src="detectionStore.currentResult.resultUrl" 
                      @error="handleImageError($event, '结果图片')"
                      class="w-full rounded-lg border" 
                      alt="识别结果"
                    />
                    <video v-else :src="detectionStore.currentResult.resultUrl" controls class="w-full rounded-lg border"></video>
                    <div v-if="fileType === 'image'" class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all rounded-lg flex items-center justify-center">
                      <span class="text-white opacity-0 group-hover:opacity-100 text-sm font-medium">点击预览</span>
                    </div>
                  </div>
                </div>
              </div>
              <!-- 操作按钮 -->
              <div v-if="fileType === 'image'" class="flex justify-center space-x-3 pt-4 border-t">
                <button
                  @click="openPreview('original')"
                  class="btn-secondary"
                >
                  <svg class="h-4 w-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                  查看原图
                </button>
                <button
                  @click="openPreview('result')"
                  class="btn-secondary"
                >
                  <svg class="h-4 w-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                  查看结果
                </button>
                <button
                  @click="openPreview('both')"
                  class="btn-primary"
                >
                  <svg class="h-4 w-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5z"></path>
                  </svg>
                  对比预览
                </button>
              </div>

              <!-- 重新开始按钮 -->
              <div class="flex justify-center pt-6 border-t mt-6">
                <button
                  @click="resetAllStates"
                  class="px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold rounded-lg hover:from-green-600 hover:to-green-700 transition-all shadow-md hover:shadow-lg transform hover:scale-105 flex items-center space-x-2"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                  <span>重新开始</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- 无结果提示 -->
          <div v-if="!detectionStore.currentResult && !detectionStore.isProcessing" class="card shadow-lg">
            <div class="text-center py-20">
              <svg class="mx-auto h-20 w-20 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <h3 class="mt-4 text-lg font-medium text-gray-900">暂无识别结果</h3>
              <p class="mt-2 text-sm text-gray-500">请先完成前面的步骤并点击“开始识别”按钮</p>
              <button @click="currentStep = 1" class="mt-6 btn-primary">返回第一步</button>
            </div>
          </div>
          </div>
          <!-- 结束步骤4 -->
          
        </div>
      </div>
    </div>

    <!-- 图片预览模态框 -->
    <div
      v-if="showPreview && detectionStore.currentResult"
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
              :src="detectionStore.currentResult.originalUrl"
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
              :src="detectionStore.currentResult.resultUrl"
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useDetectionStore } from '../stores/detection'

const authStore = useAuthStore()
const detectionStore = useDetectionStore()

const currentStep = ref(1)
const fileType = ref('image')
const selectedFile = ref(null)
const selectedModelName = ref('')
const isUploadingModel = ref(false)
const uploadError = ref(null)
let pendingModelFile = null

// 文件输入框的引用
const modelInput = ref(null)
const fileInput = ref(null)

// 预览相关状态
const showPreview = ref(false)
const previewMode = ref('both')
const scale = ref(1)
const position = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

const handleModelDrop = async (e) => {
  const file = e.dataTransfer.files[0]
  if (file && (file.name.endsWith('.pt') || file.name.endsWith('.pth'))) {
    await uploadModelFile(file)
  }
}

const handleModelSelect = async (e) => {
  const file = e.target.files[0]
  if (file) {
    await uploadModelFile(file)
  }
}

const uploadModelFile = async (file) => {
  selectedModelName.value = file.name
  pendingModelFile = file
  isUploadingModel.value = true
  uploadError.value = null
  
  try {
    const result = await detectionStore.uploadModel(file)
    if (!result.success) {
      uploadError.value = result.error || '上传失败，请检查网络连接'
    }
  } catch (error) {
    uploadError.value = error.message || '上传失败，请确保后端服务已启动'
    console.error('模型上传错误:', error)
  } finally {
    isUploadingModel.value = false
  }
}

const retryUpload = async () => {
  if (pendingModelFile) {
    await uploadModelFile(pendingModelFile)
  }
}

const handleFileSelect = (e) => {
  selectedFile.value = e.target.files[0]
}

const runDetection = async () => {
  if (selectedFile.value) {
    currentStep.value = 4  // 跳转到结果页面
    const result = await detectionStore.runDetection(selectedFile.value, fileType.value)
    if (!result.success) {
      alert('识别失败: ' + result.error)
      currentStep.value = 3  // 识别失败返回参数页面
    }
  }
}

const handleImageError = (event, type) => {
  console.error(`[ERROR] ${type}加载失败:`, event.target.src)
  console.error('[ERROR] 错误事件:', event)
  alert(`${type}加载失败，请查看控制台`)
}

// 打开预览
const openPreview = (mode) => {
  showPreview.value = true
  previewMode.value = mode
  resetZoom()
}

// 关闭预览
const closePreview = () => {
  showPreview.value = false
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

// 重新开始 - 重置所有状态
const resetAllStates = () => {
  // 确认对话框
  if (confirm('确定要重新开始吗？这将清空所有当前的识别数据和设置。')) {
    // 重置本地状态
    selectedFile.value = null
    selectedModelName.value = ''
    isUploadingModel.value = false
    uploadError.value = null
    pendingModelFile = null
    fileType.value = 'image'
    
    // 清空文件输入框的value（关键修复 - 解决重新选择文件无反应的问题）
    if (modelInput.value) {
      modelInput.value.value = ''
    }
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    
    // 重置store中的状态
    detectionStore.modelFile = null
    detectionStore.modelUploaded = false
    detectionStore.currentResult = null
    detectionStore.detectionParams = {
      imgSize: 640,
      confidence: 0.5,
      iouThreshold: 0.6,
      maxDetections: 300
    }
    
    // 重置预览状态
    showPreview.value = false
    resetZoom()
    
    // 返回到步骤1
    currentStep.value = 1
    
    console.log('[INFO] 已重置所有状态，返回到步骤1')
  }
}

onMounted(() => {
  detectionStore.loadHistory()
})
</script>
