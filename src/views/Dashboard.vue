<template>
  <div class="relative min-h-screen overflow-hidden">
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
              智能停车位识别控制台
            </h1>
          </div>
          <div class="flex items-center gap-4">
            <div class="hidden text-right text-[11px] uppercase tracking-[0.32em] text-slate-400/80 md:flex md:flex-col">
              <span class="text-[11px] text-slate-300/80">当前账户</span>
              <span class="text-sm font-medium text-white">{{ authStore.user?.email }}</span>
            </div>
            <router-link
              to="/history"
              class="btn-secondary text-sm"
            >
              历史记录
            </router-link>
            <button @click="authStore.logout" class="btn-ghost text-sm">
              退出登录
            </button>
          </div>
        </div>
      </nav>

    <!-- 主要内容 -->
    <div class="flex flex-1 flex-col overflow-hidden lg:flex-row">
      <!-- 左侧导航栏 -->
      <div class="border-b border-white/10 bg-white/5 px-6 py-8 backdrop-blur-xl lg:w-80 lg:border-b-0 lg:border-r">
        <div class="space-y-6">
          <div>
            <p class="section-title">流程</p>
            <h2 class="mt-3 text-lg font-semibold text-white">四步完成识别</h2>
            <p class="mt-2 text-sm text-slate-300/80">
              从模型到结果，全链路智能协同。
            </p>
          </div>
          <div class="space-y-3">
          <!-- 导航项 1 -->
          <button
            @click="currentStep = 1"
            :class="[
              'group w-full rounded-2xl border border-white/10 px-5 py-4 text-left transition-all duration-300',
              currentStep === 1 
                ? 'bg-gradient-to-r from-primary-500/80 to-primary-400/70 text-white shadow-[0_18px_35px_rgba(37,99,235,0.45)]'
                : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20'
            ]"
          >
            <div class="flex items-center gap-4">
              <span
                class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-sm font-semibold transition-all duration-300"
                :class="currentStep === 1 ? 'bg-white/25 text-white shadow-[0_0_18px_rgba(255,255,255,0.35)]' : 'bg-white/10 text-slate-300'"
              >
                01
              </span>
              <div class="flex-1">
                <span class="text-base font-semibold leading-tight">上传模型权重</span>
                <p class="mt-1 text-xs text-slate-300/70">导入 YOLOv8 自定义权重文件</p>
              </div>
              <svg v-if="detectionStore.modelUploaded" class="h-5 w-5 text-emerald-400 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </button>

          <!-- 导航项 2 -->
          <button
            @click="currentStep = 2"
            :class="[
              'group w-full rounded-2xl border border-white/10 px-5 py-4 text-left transition-all duration-300',
              currentStep === 2 
                ? 'bg-gradient-to-r from-accent-500/70 via-primary-500/70 to-primary-500/60 text-white shadow-[0_18px_35px_rgba(168,85,247,0.45)]'
                : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20'
            ]"
          >
            <div class="flex items-center gap-4">
              <span
                class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-sm font-semibold transition-all duration-300"
                :class="currentStep === 2 ? 'bg-white/25 text-white shadow-[0_0_18px_rgba(255,255,255,0.35)]' : 'bg-white/10 text-slate-300'"
              >
                02
              </span>
              <div class="flex-1">
                <span class="text-base font-semibold leading-tight">上传文件</span>
                <p class="mt-1 text-xs text-slate-300/70">支持图片与视频两种输入形态</p>
              </div>
              <svg v-if="selectedFile" class="h-5 w-5 text-emerald-400 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </button>

          <!-- 导航项 3 -->
          <button
            @click="currentStep = 3"
            :class="[
              'group w-full rounded-2xl border border-white/10 px-5 py-4 text-left transition-all duration-300',
              currentStep === 3 
                ? 'bg-gradient-to-r from-slate-600/70 to-slate-500/70 text-white shadow-[0_18px_35px_rgba(30,64,175,0.45)]'
                : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20'
            ]"
          >
            <div class="flex items-center gap-4">
              <span
                class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-sm font-semibold transition-all duration-300"
                :class="currentStep === 3 ? 'bg-white/25 text-white shadow-[0_0_18px_rgba(255,255,255,0.35)]' : 'bg-white/10 text-slate-300'"
              >
                03
              </span>
              <div class="flex-1">
                <span class="text-base font-semibold leading-tight">调整参数</span>
                <p class="mt-1 text-xs text-slate-300/70">灵活调节分辨率与阈值，平衡精度与速度</p>
              </div>
            </div>
          </button>

          <!-- 导航项 4 -->
          <button
            @click="currentStep = 4"
            :class="[
              'group w-full rounded-2xl border border-white/10 px-5 py-4 text-left transition-all duration-300',
              currentStep === 4 
                ? 'bg-gradient-to-r from-emerald-500/70 via-primary-500/70 to-primary-500/60 text-white shadow-[0_18px_35px_rgba(16,185,129,0.45)]'
                : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20'
            ]"
          >
            <div class="flex items-center gap-4">
              <span
                class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-sm font-semibold transition-all duration-300"
                :class="currentStep === 4 ? 'bg-white/25 text-white shadow-[0_0_18px_rgba(255,255,255,0.35)]' : 'bg-white/10 text-slate-300'"
              >
                04
              </span>
              <div class="flex-1">
                <span class="text-base font-semibold leading-tight">识别结果</span>
                <p class="mt-1 text-xs text-slate-300/70">查看原始输入与 AI 推断成果对比</p>
              </div>
              <svg v-if="detectionStore.currentResult" class="h-5 w-5 text-emerald-400 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </button>
          </div>

          <!-- 快速操作提示 -->
          <div class="mt-8 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-md">
            <div class="flex items-start gap-3">
              <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-500/20 text-primary-200">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-sm font-semibold text-white">提示</h3>
                <p class="mt-1 text-xs text-slate-300/80">按照步骤依次操作，完成后会显示绿色勾选标记。</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧主展示区域 -->
      <div class="flex-1 overflow-y-auto px-6 py-10 lg:px-12">
        <div class="mx-auto w-full max-w-6xl space-y-10">
          
          <!-- 步骤1：上传模型权重 -->
          <div v-if="currentStep === 1" class="card">
            <div class="relative mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p class="section-title">Step 01</p>
                <h2 class="mt-3 text-2xl font-semibold text-white">上传模型权重</h2>
                <p class="mt-2 text-sm text-slate-300/80">
                  上传你的 YOLOv8 模型文件（支持 .pt / .pth），系统会自动完成版本校验与安全存储。
                </p>
              </div>
              <button
                v-if="detectionStore.modelUploaded"
                class="btn-secondary self-start sm:self-auto"
                @click="currentStep = 2"
              >
                继续下一步
              </button>
            </div>

            <div
              @dragover.prevent
              @drop.prevent="handleModelDrop"
              class="group relative rounded-3xl border-2 border-dashed border-white/15 bg-white/5 p-12 text-center transition-all duration-300 hover:border-primary-400/70 hover:bg-white/10"
              @click="modelInput?.click()"
            >
              <input
                ref="modelInput"
                type="file"
                accept=".pt,.pth"
                @change="handleModelSelect"
                class="hidden"
              />
              <div v-if="isUploadingModel" class="flex flex-col items-center gap-3 text-primary-200">
                <div class="h-14 w-14 animate-spin rounded-full border-2 border-primary-500/40 border-t-transparent"></div>
                <p class="text-sm">正在上传模型...</p>
              </div>
              <div v-else-if="!detectionStore.modelUploaded && !selectedModelName" class="space-y-4 text-slate-300/85">
                <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-primary-200">
                  <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6H16a5 5 0 011 9.9m-4-2.9l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                </div>
                <p class="text-lg font-medium text-white/90">点击或拖动模型文件到此处</p>
                <p class="text-sm text-slate-400/80">支持格式：.pt、.pth</p>
              </div>
              <div v-else-if="detectionStore.modelUploaded" class="space-y-2 text-emerald-200">
                <svg class="mx-auto h-12 w-12 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <p class="text-base font-semibold text-white">模型已上传完成</p>
                <p class="text-sm text-emerald-200/80">{{ detectionStore.modelFile?.name || selectedModelName }}</p>
              </div>
              <div v-else class="space-y-3 text-amber-100">
                <svg class="mx-auto h-12 w-12 text-amber-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M5.1 19h13.8c1.54 0 2.5-1.66 1.73-3L13.73 4a2 2 0 00-3.46 0L3.37 16c-.77 1.34.19 3 1.73 3z"></path>
                </svg>
                <p class="text-sm font-medium text-white/90">模型已选择，等待上传至后端</p>
                <p class="text-xs text-slate-300/70">{{ selectedModelName }}</p>
                <button @click.stop="retryUpload" class="text-xs font-semibold text-amber-200/90 underline underline-offset-4 hover:text-amber-100">
                  重新上传
                </button>
              </div>
            </div>

            <div v-if="detectionStore.modelUploaded" class="mt-8 flex flex-col gap-4 rounded-2xl border border-emerald-400/30 bg-emerald-500/10 p-5 sm:flex-row sm:items-center sm:justify-between">
              <div class="flex items-center gap-3 text-emerald-100">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="text-sm">模型已就绪，可以继续上传待识别文件。</p>
              </div>
              <button @click="currentStep = 2" class="btn-primary text-sm">
                下一步
              </button>
            </div>

            <div v-else-if="selectedModelName && !isUploadingModel" class="mt-8 rounded-2xl border border-amber-400/30 bg-amber-500/10 p-4 text-sm text-amber-100">
              <p>
                模型文件 <span class="font-medium">{{ selectedModelName }}</span> 已选择，点击上方区域上传至后端。
              </p>
            </div>

            <div v-if="uploadError" class="mt-6 rounded-2xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-100">
              <div class="flex items-start gap-3">
                <svg class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div class="flex-1 space-y-2">
                  <p class="font-medium">上传失败</p>
                  <p>{{ uploadError }}</p>
                  <p class="text-xs text-red-200/80">请确认后端服务已启动（端口 8000）。</p>
                </div>
                <button @click="uploadError = null" class="text-red-200 hover:text-red-100">
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <!-- 步骤2：上传文件 -->
          <div v-if="currentStep === 2" class="card">
            <div class="relative mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p class="section-title">Step 02</p>
                <h2 class="mt-3 text-2xl font-semibold text-white">选择识别素材</h2>
                <p class="mt-2 text-sm text-slate-300/80">
                  支持上传停车场图片或监控视频，系统会根据文件类型自动优化检测流程。
                </p>
              </div>
              <span
                v-if="selectedFile"
                class="pill self-start sm:self-auto"
              >
                已选择 {{ selectedFile.name }}
              </span>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <button
                @click="fileType = 'image'"
                :class="[
                  'group relative overflow-hidden rounded-2xl border border-white/10 px-6 py-5 text-left transition-all duration-300',
                  fileType === 'image'
                    ? 'bg-gradient-to-r from-primary-500/80 to-primary-400/70 text-white shadow-[0_18px_35px_rgba(37,99,235,0.45)]'
                    : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20'
                ]"
              >
                <div class="flex items-center gap-4">
                  <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm font-semibold tracking-wide uppercase">图片</p>
                    <p class="mt-1 text-xs text-slate-300/70">JPG · PNG · BMP</p>
                  </div>
                </div>
                <span
                  v-if="fileType === 'image'"
                  class="absolute right-5 top-5 text-xs font-medium uppercase tracking-widest text-white/80"
                >
                  当前
                </span>
              </button>

              <button
                @click="fileType = 'video'"
                :class="[
                  'group relative overflow-hidden rounded-2xl border border-white/10 px-6 py-5 text-left transition-all duration-300',
                  fileType === 'video'
                    ? 'bg-gradient-to-r from-accent-500/70 via-primary-500/70 to-primary-500/60 text-white shadow-[0_18px_35px_rgba(168,85,247,0.45)]'
                    : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20'
                ]"
              >
                <div class="flex items-center gap-4">
                  <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm font-semibold tracking-wide uppercase">视频</p>
                    <p class="mt-1 text-xs text-slate-300/70">MP4 · AVI · MOV</p>
                  </div>
                </div>
                <span
                  v-if="fileType === 'video'"
                  class="absolute right-5 top-5 text-xs font-medium uppercase tracking-widest text-white/80"
                >
                  当前
                </span>
              </button>
            </div>

            <div
              class="group relative mt-8 flex flex-col items-center justify-center rounded-3xl border-2 border-dashed border-white/15 bg-white/5 p-12 text-center transition-all duration-300 hover:border-primary-400/70 hover:bg-white/10"
              @click="fileInput?.click()"
              @dragover.prevent
              @drop.prevent="handleFileDrop"
            >
              <input
                ref="fileInput"
                type="file"
                class="hidden"
                :accept="fileType === 'image' ? 'image/*' : 'video/*'"
                @change="handleFileSelect"
              />
              <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-primary-200">
                <svg
                  v-if="fileType === 'image'"
                  class="h-8 w-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 7a4 4 0 014-4h10a4 4 0 014 4v10a4 4 0 01-4 4H7a4 4 0 01-4-4V7z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8.5 11.5l2.25 2.25 3.75-3.75L19 14" />
                </svg>
                <svg
                  v-else
                  class="h-8 w-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6a2 2 0 012-2h8.382a2 2 0 011.414.586l3.618 3.618A2 2 0 0116.828 10H6a2 2 0 01-2-2V6z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 16l4-3 4 3-4 3-4-3z" />
                </svg>
              </div>
              <p class="mt-6 text-lg font-semibold text-white/90">
                拖拽或点击上传 {{ fileType === 'image' ? '图片' : '视频' }} 文件
              </p>
              <p class="mt-2 text-sm text-slate-400/80">
                支持单文件上传，最大 1GB。拖拽至此区域即可快速导入。
              </p>
              <span class="mt-4 text-xs text-slate-400/60">
                小贴士：同名文件会覆盖上一版本，请提前备份。
              </span>
            </div>

            <div
              v-if="selectedFile"
              class="mt-8 flex flex-col gap-4 rounded-2xl border border-primary-500/30 bg-primary-500/10 p-5 sm:flex-row sm:items-center sm:justify-between"
            >
              <div class="flex items-start gap-4">
                <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-500/25 text-white">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-semibold text-white/90 break-all">{{ selectedFile.name }}</p>
                  <p class="mt-1 text-xs text-primary-100/80">
                    {{ formatFileSize(selectedFile.size) }} · {{ fileType === 'image' ? '图像素材' : '视频素材' }}
                  </p>
                </div>
              </div>
              <div class="flex flex-wrap items-center gap-3">
                <button type="button" class="btn-secondary text-sm" @click.stop="fileInput?.click()">
                  重新选择
                </button>
                <button type="button" class="btn-ghost text-sm" @click="clearSelectedFile">
                  清除
                </button>
                <button type="button" class="btn-primary text-sm" @click="currentStep = 3">
                  前往参数调优
                </button>
              </div>
            </div>

            <div v-else class="mt-6 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300/70">
              <svg class="h-4 w-4 flex-shrink-0 text-slate-300/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16h-1v-4h-1m1-4h.01" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>
                暂未选择文件，请上传一份停车场图片或视频开启识别流程。
              </span>
            </div>
          </div>
          <!-- 步骤3：调整参数 -->
          <div v-if="currentStep === 3" class="card">
            <div class="relative mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p class="section-title">Step 03</p>
                <h2 class="mt-3 text-2xl font-semibold text-white">智能调参</h2>
                <p class="mt-2 text-sm text-slate-300/80">
                  根据场景灵活调整检测参数，平衡识别精度与运行效率。数值实时作用于推理引擎。
                </p>
              </div>
              <div class="flex flex-col items-start gap-2 text-xs text-slate-300/70 sm:items-end">
                <span class="pill">实时生效</span>
                <p>YOLOv8 · 高置信度筛选 · 多目标追踪</p>
              </div>
            </div>

            <div class="space-y-6">
              <div class="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div class="flex items-baseline justify-between">
                  <h3 class="text-sm font-semibold text-white/90">输入尺寸</h3>
                  <span class="text-lg font-semibold text-primary-200">{{ Number(detectionStore.detectionParams.imgSize) }} px</span>
                </div>
                <p class="mt-1 text-xs text-slate-400/80">尺寸越大检测越精细，但推理耗时越长。</p>
                <input
                  v-model="detectionStore.detectionParams.imgSize"
                  type="range"
                  min="160"
                  max="1920"
                  step="32"
                  class="ui-range mt-5"
                />
                <div class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-slate-400/60">
                  <span>160 · 极速</span>
                  <span>640 · 均衡</span>
                  <span>1920 · 极致</span>
                </div>
              </div>

              <div class="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div class="flex items-baseline justify-between">
                  <h3 class="text-sm font-semibold text-white/90">置信度阈值</h3>
                  <span class="text-lg font-semibold text-primary-200">{{ Number(detectionStore.detectionParams.confidence).toFixed(2) }}</span>
                </div>
                <p class="mt-1 text-xs text-slate-400/80">数值越高越严格，可显著降低误检。</p>
                <input
                  v-model="detectionStore.detectionParams.confidence"
                  type="range"
                  min="0.01"
                  max="0.99"
                  step="0.01"
                  class="ui-range mt-5"
                />
                <div class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-slate-400/60">
                  <span>0.01 · 召回</span>
                  <span>0.50 · 均衡</span>
                  <span>0.99 · 精准</span>
                </div>
              </div>

              <div class="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div class="flex items-baseline justify-between">
                  <h3 class="text-sm font-semibold text-white/90">IOU 阈值</h3>
                  <span class="text-lg font-semibold text-primary-200">{{ Number(detectionStore.detectionParams.iouThreshold).toFixed(2) }}</span>
                </div>
                <p class="mt-1 text-xs text-slate-400/80">控制候选框合并策略，优化重叠目标的识别体验。</p>
                <input
                  v-model="detectionStore.detectionParams.iouThreshold"
                  type="range"
                  min="0.05"
                  max="0.95"
                  step="0.01"
                  class="ui-range mt-5"
                />
                <div class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-slate-400/60">
                  <span>0.05 · 更少</span>
                  <span>0.60 · 平衡</span>
                  <span>0.95 · 更多</span>
                </div>
              </div>

              <div class="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div class="flex items-baseline justify-between">
                  <h3 class="text-sm font-semibold text-white/90">最大检测数量</h3>
                  <span class="text-lg font-semibold text-primary-200">{{ Number(detectionStore.detectionParams.maxDetections) }}</span>
                </div>
                <p class="mt-1 text-xs text-slate-400/80">限制单张图像的目标上限，控制渲染开销。</p>
                <input
                  v-model="detectionStore.detectionParams.maxDetections"
                  type="range"
                  min="10"
                  max="2000"
                  step="10"
                  class="ui-range mt-5"
                />
                <div class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-slate-400/60">
                  <span>10 · 精准</span>
                  <span>300 · 推荐</span>
                  <span>2000 · 全量</span>
                </div>
              </div>

              <div
                v-if="fileType === 'video'"
                class="rounded-2xl border border-accent-500/25 bg-accent-500/10 p-6"
              >
                <div class="flex items-baseline justify-between">
                  <h3 class="text-sm font-semibold text-white/90">视频抽帧间隔</h3>
                  <span class="text-lg font-semibold text-accent-200">{{ detectionStore.detectionParams.frameSkip }}</span>
                </div>
                <p class="mt-1 text-xs text-accent-100/80">抽帧越大越节能，抽帧越小越平滑。</p>
                <input
                  v-model="detectionStore.detectionParams.frameSkip"
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  class="ui-range mt-5 accent-accent-400"
                />
                <div class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-accent-100/70">
                  <span>1 · 每帧</span>
                  <span>5 · 均衡</span>
                  <span>10 · 极速</span>
                </div>
              </div>
            </div>

            <div class="mt-10 flex flex-col gap-4 border-t border-white/10 pt-6 text-sm text-slate-300/70 sm:flex-row sm:items-center sm:justify-between">
              <p>参数会自动同步到历史记录，便于后续复现与对比。</p>
              <div class="flex flex-wrap items-center gap-3">
                <button type="button" class="btn-secondary text-sm" @click="currentStep = 2">返回素材选择</button>
                <button
                  type="button"
                  class="btn-primary px-8 text-sm"
                  :disabled="!detectionStore.modelUploaded || !selectedFile || detectionStore.isProcessing"
                  @click="runDetection"
                >
                  {{ detectionStore.isProcessing ? '处理中…' : '开始识别 🚀' }}
                </button>
              </div>
            </div>
          </div>
          <!-- 步骤4：识别结果 -->
          <div v-if="currentStep === 4">
            <div v-if="detectionStore.isProcessing" class="card">
              <div class="flex flex-col items-center justify-center gap-6 py-20 text-center">
                <div class="relative">
                  <div class="h-24 w-24 rounded-full border border-white/10 bg-white/5"></div>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <div class="h-20 w-20 rounded-full border-2 border-primary-500/20"></div>
                  </div>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <div class="h-16 w-16 animate-spin rounded-full border-b-4 border-primary-500"></div>
                  </div>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <svg class="h-7 w-7 text-primary-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>
                <div>
                  <h3 class="text-xl font-semibold text-white">AI 正在分析素材</h3>
                  <p class="mt-2 text-sm text-slate-300/75">使用 YOLOv8 模型推理，并应用预设的最优参数组合。</p>
                </div>
                <div class="flex items-center gap-2 text-[11px] uppercase tracking-[0.3em] text-slate-400/60">
                  <span>多目标追踪</span>
                  <span>智能降噪</span>
                  <span>稳定运行</span>
                </div>
              </div>
            </div>

            <div v-else-if="detectionStore.currentResult" class="space-y-8">
              <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p class="section-title">Step 04</p>
                  <h2 class="mt-3 text-3xl font-semibold text-white">识别完成</h2>
                  <p class="mt-2 text-sm text-slate-300/80">以下是本次识别的核心指标与可视化结果。</p>
                </div>
                <div class="flex flex-wrap items-center gap-3">
                  <span class="pill bg-emerald-500/20 text-emerald-200">检测完成</span>
                  <span class="text-xs text-slate-300/70">耗时 {{ (detectionStore.currentResult.processTime || 0).toFixed(2) }}s</span>
                </div>
              </div>

              <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div class="glass-panel p-5 text-center">
                  <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">检测目标</p>
                  <p class="mt-3 text-3xl font-semibold text-primary-200">{{ detectionStore.currentResult.detections?.length || 0 }}</p>
                </div>
                <div class="glass-panel p-5 text-center">
                  <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">置信度</p>
                  <p class="mt-3 text-3xl font-semibold text-primary-200">{{ Number(detectionStore.detectionParams.confidence).toFixed(2) }}</p>
                </div>
                <div class="glass-panel p-5 text-center">
                  <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">输入尺寸</p>
                  <p class="mt-3 text-3xl font-semibold text-primary-200">{{ Number(detectionStore.detectionParams.imgSize) }}</p>
                </div>
                <div class="glass-panel p-5 text-center">
                  <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">推理耗时</p>
                  <p class="mt-3 text-3xl font-semibold text-primary-200">{{ (detectionStore.currentResult.processTime || 0).toFixed(2) }}s</p>
                </div>
              </div>

              <div class="grid gap-6 lg:grid-cols-2">
                <div class="glass-panel group overflow-hidden p-5">
                  <div class="flex items-center justify-between">
                    <h3 class="text-sm font-semibold text-white/90">原始素材</h3>
                    <button type="button" class="btn-ghost text-xs" @click="openPreview('original')">放大查看</button>
                  </div>
                  <div class="relative mt-4 overflow-hidden rounded-2xl border border-white/10">
                    <img
                      v-if="fileType === 'image'"
                      :src="detectionStore.currentResult.originalUrl"
                      @error="handleImageError($event, '原始图片')"
                      class="w-full object-cover"
                      alt="原始素材预览"
                    />
                    <video
                      v-else
                      :src="detectionStore.currentResult.originalUrl"
                      controls
                      class="w-full rounded-2xl"
                    ></video>
                    <div class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                  </div>
                </div>
                <div class="glass-panel group overflow-hidden p-5">
                  <div class="flex items-center justify-between">
                    <h3 class="text-sm font-semibold text-white/90">识别结果</h3>
                    <button type="button" class="btn-ghost text-xs" @click="openPreview('result')">放大查看</button>
                  </div>
                  <div class="relative mt-4 overflow-hidden rounded-2xl border border-white/10">
                    <img
                      v-if="fileType === 'image'"
                      :src="detectionStore.currentResult.resultUrl"
                      @error="handleImageError($event, '结果图片')"
                      class="w-full object-cover"
                      alt="识别结果预览"
                    />
                    <video
                      v-else
                      :src="detectionStore.currentResult.resultUrl"
                      controls
                      class="w-full rounded-2xl"
                    ></video>
                    <div class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/45 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                  </div>
                </div>
              </div>

              <div class="glass-panel p-6">
                <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div class="space-y-2 text-sm text-slate-300/80">
                    <p>素材名称：{{ selectedFile?.name || detectionStore.currentResult.fileName || '未命名素材' }}</p>
                    <p>置信度阈值：{{ Number(detectionStore.detectionParams.confidence).toFixed(2) }} · IOU：{{ Number(detectionStore.detectionParams.iouThreshold).toFixed(2) }}</p>
                    <p v-if="fileType === 'video'">视频抽帧：每 {{ detectionStore.detectionParams.frameSkip }} 帧分析一次</p>
                    <p v-else>图像尺寸：{{ detectionStore.detectionParams.imgSize }} 像素</p>
                  </div>
                  <div class="flex flex-wrap items-center gap-3">
                    <button type="button" class="btn-secondary text-sm" @click="openPreview('both')">对比预览</button>
                    <router-link to="/history" class="btn-ghost text-sm">查看历史记录</router-link>
                    <button type="button" class="btn-primary text-sm" @click="resetAllStates">重新开始</button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="card text-center">
              <div class="py-16">
                <svg class="mx-auto h-16 w-16 text-slate-400/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 class="mt-6 text-lg font-semibold text-white">尚未开始识别</h3>
                <p class="mt-2 text-sm text-slate-300/75">请完成前面三个步骤后，点击“开始识别”按钮。</p>
                <button type="button" class="btn-primary mt-6" @click="currentStep = 1">回到第一步</button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- 图片预览模态框 -->
    <div
      v-if="showPreview && detectionStore.currentResult"
      class="fixed inset-0 z-[70] flex items-center justify-center bg-slate-950/95 backdrop-blur-xl"
      @click="closePreview"
    >
      <div class="absolute top-6 right-8 z-[80] flex items-center gap-4">
        <div class="flex items-center gap-3 rounded-2xl border border-white/15 bg-white/10 px-4 py-2 shadow-[0_12px_35px_rgba(8,15,40,0.45)] backdrop-blur">
          <button
            @click.stop="zoomOut"
            class="text-slate-200 transition-colors hover:text-white"
            title="缩小"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-5.197-5.197M4 10h7m0 0h7m-7 0V3m0 7v7" />
            </svg>
          </button>
          <span class="text-xs font-semibold tracking-[0.28em] text-slate-200 uppercase">{{ Math.round(scale * 100) }}%</span>
          <button
            @click.stop="zoomIn"
            class="text-slate-200 transition-colors hover:text-white"
            title="放大"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 5v14m7-7H5" />
            </svg>
          </button>
          <button
            @click.stop="resetZoom"
            class="ml-1 text-slate-200 transition-colors hover:text-white"
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
            <span>拖拽以平移 · 滚轮缩放</span>
          </div>
          <div
            :class="[
              'relative mt-4 flex h-full w-full items-center justify-center overflow-hidden rounded-2xl border border-white/15 bg-slate-900/40',
              previewMode === 'both' ? 'cursor-move' : 'cursor-move'
            ]"
            @mousedown="startDrag"
            @mousemove="onDrag"
            @mouseup="endDrag"
            @mouseleave="endDrag"
            @wheel.prevent="onWheel"
          >
            <img
              v-if="fileType === 'image'"
              :src="detectionStore.currentResult.originalUrl"
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
              :src="detectionStore.currentResult.originalUrl"
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
            <span>拖拽以平移 · 滚轮缩放</span>
          </div>
          <div
            :class="[
              'relative mt-4 flex h-full w-full items-center justify-center overflow-hidden rounded-2xl border border-white/15 bg-slate-900/40',
              previewMode === 'both' ? 'cursor-move' : 'cursor-move'
            ]"
            @mousedown="startDrag"
            @mousemove="onDrag"
            @mouseup="endDrag"
            @mouseleave="endDrag"
            @wheel.prevent="onWheel"
          >
            <img
              v-if="fileType === 'image'"
              :src="detectionStore.currentResult.resultUrl"
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
              :src="detectionStore.currentResult.resultUrl"
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

const applySelectedFile = (file) => {
  if (!file) return

  const mime = file.type || ''
  if (mime.startsWith('video')) {
    fileType.value = 'video'
  } else if (mime.startsWith('image')) {
    fileType.value = 'image'
  } else {
    alert('暂不支持该文件类型，请选择图片或视频')
    return
  }

  selectedFile.value = file
}

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
  const file = e.target.files?.[0]
  applySelectedFile(file)

  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleFileDrop = (event) => {
  const file = event.dataTransfer?.files?.[0]
  applySelectedFile(file)
}

const clearSelectedFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes === undefined || bytes === null) return '0 B'
  let size = Number(bytes)
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex += 1
  }

  const fixed = unitIndex === 0 ? 0 : unitIndex === 1 ? 1 : 2
  return `${size.toFixed(fixed)} ${units[unitIndex]}`
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
    clearSelectedFile()
    selectedModelName.value = ''
    isUploadingModel.value = false
    uploadError.value = null
    pendingModelFile = null
    fileType.value = 'image'
    
    // 清空文件输入框的value（关键修复 - 解决重新选择文件无反应的问题）
    if (modelInput.value) {
      modelInput.value.value = ''
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
