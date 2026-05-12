<template>
  <div class="space-y-8">
    <div
      v-if="workspaceNotice"
      data-testid="workspace-notice"
      class="rounded-2xl border px-4 py-3 text-sm shadow-[0_18px_35px_rgba(8,15,40,0.28)]"
      :class="workspaceNoticeClass"
    >
      <div class="flex items-start gap-3">
        <div class="flex-1">
          <p class="font-medium">{{ workspaceNotice.message }}</p>
        </div>
        <button
          type="button"
          data-testid="workspace-notice-close"
          class="text-current/80 transition hover:text-current"
          @click="clearWorkspaceNotice"
        >
          <svg
            class="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>

    <div
      class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"
    >
      <div>
        <p class="section-title">系统</p>
        <h1
          data-testid="workspace-title"
          class="mt-3 text-2xl font-semibold text-white"
        >
          识别工作台
        </h1>
        <p class="mt-2 text-sm text-slate-300/80">
          统一管理模型、参数与识别流程，面向日常运营的核心工作区。
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <div
          class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-300/80"
        >
          当前账户：<span class="text-slate-100">{{
            authStore.user?.email || "未登录"
          }}</span>
        </div>
        <router-link to="/model-weights" class="btn-secondary text-sm">
          模型管理
        </router-link>
        <router-link to="/history" class="btn-secondary text-sm">
          历史记录
        </router-link>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="flex flex-1 flex-col overflow-hidden lg:flex-row">
      <!-- 左侧导航栏 -->
      <div
        class="border-b border-white/10 bg-white/5 px-6 py-8 backdrop-blur-xl lg:w-80 lg:border-b-0 lg:border-r"
      >
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
                  : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20',
              ]"
            >
              <div class="flex items-center gap-4">
                <span
                  class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-sm font-semibold transition-all duration-300"
                  :class="
                    currentStep === 1
                      ? 'bg-white/25 text-white shadow-[0_0_18px_rgba(255,255,255,0.35)]'
                      : 'bg-white/10 text-slate-300'
                  "
                >
                  01
                </span>
                <div class="flex-1">
                  <span class="text-base font-semibold leading-tight"
                    >选择模型权重</span
                  >
                  <p class="mt-1 text-xs text-slate-300/70">
                    从已有模型权重中选择当前识别使用的模型
                  </p>
                </div>
                <svg
                  v-if="detectionStore.modelUploaded"
                  class="h-5 w-5 text-emerald-400 transition-transform duration-300 group-hover:scale-110"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
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
                  : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20',
              ]"
            >
              <div class="flex items-center gap-4">
                <span
                  class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-sm font-semibold transition-all duration-300"
                  :class="
                    currentStep === 2
                      ? 'bg-white/25 text-white shadow-[0_0_18px_rgba(255,255,255,0.35)]'
                      : 'bg-white/10 text-slate-300'
                  "
                >
                  02
                </span>
                <div class="flex-1">
                  <span class="text-base font-semibold leading-tight"
                    >上传文件</span
                  >
                  <p class="mt-1 text-xs text-slate-300/70">
                    支持图片与视频两种输入形态
                  </p>
                </div>
                <svg
                  v-if="selectedFile"
                  class="h-5 w-5 text-emerald-400 transition-transform duration-300 group-hover:scale-110"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
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
                  : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20',
              ]"
            >
              <div class="flex items-center gap-4">
                <span
                  class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-sm font-semibold transition-all duration-300"
                  :class="
                    currentStep === 3
                      ? 'bg-white/25 text-white shadow-[0_0_18px_rgba(255,255,255,0.35)]'
                      : 'bg-white/10 text-slate-300'
                  "
                >
                  03
                </span>
                <div class="flex-1">
                  <span class="text-base font-semibold leading-tight"
                    >调整参数</span
                  >
                  <p class="mt-1 text-xs text-slate-300/70">
                    灵活调节分辨率与阈值，平衡精度与速度
                  </p>
                </div>
                <svg
                  v-if="isStep3Completed"
                  class="h-5 w-5 text-emerald-400 transition-transform duration-300 group-hover:scale-110"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
              </div>
            </button>

            <!-- 导航项 4 -->
            <button
              @click="currentStep = 4"
              :class="[
                'group w-full rounded-2xl border border-white/10 px-5 py-4 text-left transition-all duration-300',
                currentStep === 4
                  ? 'bg-gradient-to-r from-emerald-500/70 via-primary-500/70 to-primary-500/60 text-white shadow-[0_18px_35px_rgba(16,185,129,0.45)]'
                  : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20',
              ]"
            >
              <div class="flex items-center gap-4">
                <span
                  class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-sm font-semibold transition-all duration-300"
                  :class="
                    currentStep === 4
                      ? 'bg-white/25 text-white shadow-[0_0_18px_rgba(255,255,255,0.35)]'
                      : 'bg-white/10 text-slate-300'
                  "
                >
                  04
                </span>
                <div class="flex-1">
                  <span class="text-base font-semibold leading-tight"
                    >识别结果</span
                  >
                  <p class="mt-1 text-xs text-slate-300/70">
                    查看原始输入与 AI 推断成果对比
                  </p>
                </div>
                <svg
                  v-if="detectionStore.currentResult"
                  class="h-5 w-5 text-emerald-400 transition-transform duration-300 group-hover:scale-110"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
              </div>
            </button>
          </div>

          <!-- 快速操作提示 -->
          <div
            class="mt-8 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-md"
          >
            <div class="flex items-start gap-3">
              <div
                class="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-500/20 text-primary-200"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
              </div>
              <div>
                <h3 class="text-sm font-semibold text-white">提示</h3>
                <p class="mt-1 text-xs text-slate-300/80">
                  按照步骤依次操作，完成后会显示绿色勾选标记。
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧主展示区域 -->
      <div class="flex-1 overflow-y-auto px-6 py-10 lg:px-12">
        <div class="mx-auto w-full max-w-6xl">
          <!-- 步骤切换容器 -->
          <div class="relative" style="min-height: 600px">
            <!-- 步骤1：选择模型权重 -->
            <Transition :name="slideDirection" mode="out-in">
              <div
                v-if="currentStep === 1"
                key="step-1"
                class="card absolute w-full"
              >
                <div
                  class="relative mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"
                >
                  <div>
                    <p class="section-title">Step 01</p>
                    <h2 class="mt-3 text-2xl font-semibold text-white">
                      选择模型权重
                    </h2>
                    <p class="mt-2 text-sm text-slate-300/80">
                      从你的权重库中选择 YOLOv8 模型权重，选中后即可进入下一步上传识别素材。
                    </p>
                  </div>
                </div>
                <!-- 已有权重列表 -->
                <div
                  v-if="loadingWeights && availableWeights.length === 0"
                  class="mt-8 flex items-center justify-center gap-3 py-8 text-slate-400"
                >
                  <div
                    class="h-5 w-5 animate-spin rounded-full border-2 border-white/20 border-t-white"
                  ></div>
                  <span class="text-sm">正在加载权重列表…</span>
                </div>
                <div v-else-if="availableWeights.length > 0" class="mt-8">
                  <div class="mb-4 flex items-center justify-between">
                    <h3 class="text-lg font-semibold text-white">
                      选择已有权重
                    </h3>
                    <button
                      @click="loadUserWeights"
                      :disabled="loadingWeights"
                      class="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300 transition-all hover:bg-white/10"
                    >
                      <svg
                        v-if="!loadingWeights"
                        class="h-3 w-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                        ></path>
                      </svg>
                      <div
                        v-else
                        class="h-3 w-3 animate-spin rounded-full border-2 border-white/20 border-t-white"
                      ></div>
                      刷新
                    </button>
                  </div>

                  <div class="grid gap-3 sm:grid-cols-2">
                    <button
                      v-for="weight in availableWeights"
                      :key="weight.id"
                      @click="selectExistingWeight(weight)"
                      :class="[
                        'group relative rounded-xl border p-4 text-left transition-all duration-300',
                        selectedWeightId === weight.id
                          ? 'border-primary-400/50 bg-gradient-to-r from-primary-500/20 to-primary-400/10 shadow-[0_0_20px_rgba(37,99,235,0.2)]'
                          : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/8',
                      ]"
                    >
                      <div class="flex items-start gap-3">
                        <div
                          class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-white/10"
                        >
                          <svg
                            class="h-5 w-5 text-primary-300"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            ></path>
                          </svg>
                        </div>
                        <div class="flex-1 min-w-0">
                          <div class="flex items-center gap-2">
                            <p
                              class="truncate text-sm font-semibold text-white"
                            >
                              {{ weight.name }}
                            </p>
                            <span
                              v-if="selectedWeightId === weight.id"
                              class="inline-flex items-center gap-1 rounded-full bg-primary-500/20 px-2 py-0.5 text-xs font-medium text-primary-300"
                            >
                              <svg
                                class="h-3 w-3"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                              >
                                <path
                                  fill-rule="evenodd"
                                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                  clip-rule="evenodd"
                                ></path>
                              </svg>
                              当前使用
                            </span>
                          </div>
                          <p
                            v-if="weight.description"
                            class="mt-1 text-xs text-slate-400 truncate"
                          >
                            {{ weight.description }}
                          </p>
                          <div
                            class="mt-2 flex items-center gap-3 text-xs text-slate-500"
                          >
                            <span>{{ formatFileSize(weight.file_size) }}</span>
                            <span>{{
                              new Date(weight.created_at).toLocaleDateString(
                                "zh-CN",
                              )
                            }}</span>
                          </div>
                        </div>
                      </div>
                    </button>
                  </div>

                  <div class="mt-4 text-center">
                    <router-link
                      to="/model-weights"
                      class="inline-flex items-center gap-2 text-sm text-primary-300 hover:text-primary-200"
                    >
                      <span>查看全部权重</span>
                      <svg
                        class="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M9 5l7 7-7 7"
                        ></path>
                      </svg>
                    </router-link>
                  </div>

                  <div
                    v-if="detectionStore.modelUploaded"
                    class="mt-6 flex justify-center"
                  >
                    <button
                      class="btn-secondary inline-flex min-w-[9rem] items-center justify-center whitespace-nowrap"
                      @click="currentStep = 2"
                    >
                      继续下一步
                    </button>
                  </div>
                </div>
                <div
                  v-else
                  class="mt-8 rounded-2xl border border-white/10 bg-white/5 p-6 text-center"
                >
                  <p class="text-sm text-slate-300">
                    当前暂无可用模型权重，请先前往权重管理页添加模型。
                  </p>
                  <router-link
                    to="/model-weights"
                    class="mt-4 inline-flex items-center gap-2 rounded-full border border-primary-300/50 bg-primary-500/15 px-4 py-2 text-xs font-semibold text-primary-200 transition hover:bg-primary-500/25"
                  >
                    去管理模型权重
                  </router-link>
                </div>
              </div>
            </Transition>
            <!-- 步骤2：上传文件 -->
            <Transition :name="slideDirection" mode="out-in">
              <div
                v-if="currentStep === 2"
                key="step-2"
                class="card absolute w-full"
              >
                <div
                  class="relative mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"
                >
                  <div>
                    <p class="section-title">Step 02</p>
                    <h2 class="mt-3 text-2xl font-semibold text-white">
                      选择识别素材
                    </h2>
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
                        : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20',
                    ]"
                  >
                    <div class="flex items-center gap-4">
                      <div
                        class="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10"
                      >
                        <svg
                          class="h-6 w-6"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="1.5"
                            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                      </div>
                      <div>
                        <p
                          class="text-sm font-semibold tracking-wide uppercase"
                        >
                          图片
                        </p>
                        <p class="mt-1 text-xs text-slate-300/70">
                          JPG · PNG · BMP
                        </p>
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
                        : 'bg-white/5 text-slate-200 hover:bg-white/8 hover:border-white/20',
                    ]"
                  >
                    <div class="flex items-center gap-4">
                      <div
                        class="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10"
                      >
                        <svg
                          class="h-6 w-6"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="1.5"
                            d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                          />
                        </svg>
                      </div>
                      <div>
                        <p
                          class="text-sm font-semibold tracking-wide uppercase"
                        >
                          视频
                        </p>
                        <p class="mt-1 text-xs text-slate-300/70">
                          MP4 · AVI · MOV
                        </p>
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
                  <div
                    class="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-primary-200"
                  >
                    <svg
                      v-if="fileType === 'image'"
                      class="h-8 w-8"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.5"
                        d="M3 7a4 4 0 014-4h10a4 4 0 014 4v10a4 4 0 01-4 4H7a4 4 0 01-4-4V7z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.5"
                        d="M8.5 11.5l2.25 2.25 3.75-3.75L19 14"
                      />
                    </svg>
                    <svg
                      v-else
                      class="h-8 w-8"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.5"
                        d="M4 6a2 2 0 012-2h8.382a2 2 0 011.414.586l3.618 3.618A2 2 0 0116.828 10H6a2 2 0 01-2-2V6z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.5"
                        d="M8 16l4-3 4 3-4 3-4-3z"
                      />
                    </svg>
                  </div>
                  <p class="mt-6 text-lg font-semibold text-white/90">
                    拖拽或点击上传
                    {{ fileType === "image" ? "图片" : "视频" }} 文件
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
                  class="mt-8 grid gap-4 rounded-2xl border border-primary-500/30 bg-primary-500/10 p-5 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center"
                >
                  <div class="flex items-start gap-4">
                    <div
                      class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-500/25 text-white flex-shrink-0"
                    >
                      <svg
                        class="h-5 w-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="1.5"
                          d="M4 6h16M4 12h16M4 18h16"
                        />
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <!-- 素材名称编辑 -->
                      <div class="flex items-center gap-2">
                        <input
                          v-if="isEditingFileName"
                          v-model="customFileName"
                          @blur="isEditingFileName = false"
                          @keyup.enter="isEditingFileName = false"
                          class="flex-1 rounded-lg border border-primary-400/50 bg-white/10 px-3 py-1.5 text-sm font-semibold text-white outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-400/30"
                          placeholder="输入素材名称"
                          autofocus
                        />
                        <p
                          v-else
                          class="text-sm font-semibold text-white/90 break-all"
                        >
                          {{ customFileName || selectedFile.name }}
                        </p>
                        <button
                          v-if="!isEditingFileName"
                          @click="isEditingFileName = true"
                          class="flex-shrink-0 p-1.5 text-primary-200 transition hover:text-primary-100"
                          title="编辑名称"
                        >
                          <svg
                            class="h-4 w-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                            />
                          </svg>
                        </button>
                      </div>
                      <p class="mt-1 text-xs text-primary-100/80">
                        {{ formatFileSize(selectedFile.size) }} ·
                        {{ fileType === "image" ? "图像素材" : "视频素材" }} ·
                        原始：{{ selectedFile.name }}
                      </p>
                    </div>
                  </div>
                  <div class="flex flex-wrap items-center gap-3">
                    <button
                      type="button"
                      class="btn-secondary text-sm"
                      @click.stop="fileInput?.click()"
                    >
                      重新选择
                    </button>
                    <button
                      type="button"
                      class="btn-ghost text-sm"
                      @click="clearSelectedFile"
                    >
                      清除
                    </button>
                    <button
                      type="button"
                      class="btn-primary text-sm"
                      @click="currentStep = 3"
                    >
                      前往参数调优
                    </button>
                  </div>
                </div>

                <div
                  v-else
                  class="mt-6 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300/70"
                >
                  <svg
                    class="h-4 w-4 flex-shrink-0 text-slate-300/60"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="1.5"
                      d="M13 16h-1v-4h-1m1-4h.01"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="1.5"
                      d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <span>
                    暂未选择文件，请上传一份停车场图片或视频开启识别流程。
                  </span>
                </div>
              </div>
            </Transition>

            <!-- 步骤3：调整参数 -->
            <Transition :name="slideDirection" mode="out-in">
              <div
                v-if="currentStep === 3"
                key="step-3"
                class="card absolute w-full"
              >
                <div
                  class="relative mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"
                >
                  <div>
                    <p class="section-title">Step 03</p>
                    <h2 class="mt-3 text-2xl font-semibold text-white">
                      智能调参
                    </h2>
                    <p class="mt-2 text-sm text-slate-300/80">
                      根据场景灵活调整检测参数，平衡识别精度与运行效率。数值实时作用于推理引擎。
                    </p>
                  </div>
                  <div
                    class="flex flex-col items-start gap-2 text-xs text-slate-300/70 sm:items-end"
                  >
                    <span class="pill">实时生效</span>
                    <p>YOLOv8 · 高置信度筛选 · 多目标追踪</p>
                  </div>
                </div>

                <div class="space-y-6">
                  <div
                    class="rounded-2xl border border-white/10 bg-white/5 p-6"
                  >
                    <div class="flex items-baseline justify-between">
                      <h3 class="text-sm font-semibold text-white/90">
                        输入尺寸
                      </h3>
                      <span class="text-lg font-semibold text-primary-200"
                        >{{
                          Number(detectionStore.detectionParams.imgSize)
                        }}
                        px</span
                      >
                    </div>
                    <p class="mt-1 text-xs text-slate-400/80">
                      尺寸越大检测越精细，但推理耗时越长。
                    </p>
                    <input
                      v-model="detectionStore.detectionParams.imgSize"
                      type="range"
                      min="160"
                      max="1920"
                      step="32"
                      class="ui-range mt-5"
                    />
                    <div
                      class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-slate-400/60"
                    >
                      <span>160 · 极速</span>
                      <span>640 · 均衡</span>
                      <span>1920 · 极致</span>
                    </div>
                  </div>

                  <div
                    class="rounded-2xl border border-white/10 bg-white/5 p-6"
                  >
                    <div class="flex items-baseline justify-between">
                      <h3 class="text-sm font-semibold text-white/90">
                        置信度阈值
                      </h3>
                      <span class="text-lg font-semibold text-primary-200">{{
                        Number(
                          detectionStore.detectionParams.confidence,
                        ).toFixed(2)
                      }}</span>
                    </div>
                    <p class="mt-1 text-xs text-slate-400/80">
                      数值越高越严格，可显著降低误检。
                    </p>
                    <input
                      v-model="detectionStore.detectionParams.confidence"
                      type="range"
                      min="0.01"
                      max="0.99"
                      step="0.01"
                      class="ui-range mt-5"
                    />
                    <div
                      class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-slate-400/60"
                    >
                      <span>0.01 · 召回</span>
                      <span>0.50 · 均衡</span>
                      <span>0.99 · 精准</span>
                    </div>
                  </div>

                  <div
                    class="rounded-2xl border border-white/10 bg-white/5 p-6"
                  >
                    <div class="flex items-baseline justify-between">
                      <h3 class="text-sm font-semibold text-white/90">
                        IOU 阈值
                      </h3>
                      <span class="text-lg font-semibold text-primary-200">{{
                        Number(
                          detectionStore.detectionParams.iouThreshold,
                        ).toFixed(2)
                      }}</span>
                    </div>
                    <p class="mt-1 text-xs text-slate-400/80">
                      控制候选框合并策略，优化重叠目标的识别体验。
                    </p>
                    <input
                      v-model="detectionStore.detectionParams.iouThreshold"
                      type="range"
                      min="0.05"
                      max="0.95"
                      step="0.01"
                      class="ui-range mt-5"
                    />
                    <div
                      class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-slate-400/60"
                    >
                      <span>0.05 · 更少</span>
                      <span>0.60 · 平衡</span>
                      <span>0.95 · 更多</span>
                    </div>
                  </div>

                  <div
                    class="rounded-2xl border border-white/10 bg-white/5 p-6"
                  >
                    <div class="flex items-baseline justify-between">
                      <h3 class="text-sm font-semibold text-white/90">
                        最大检测数量
                      </h3>
                      <span class="text-lg font-semibold text-primary-200">{{
                        Number(detectionStore.detectionParams.maxDetections)
                      }}</span>
                    </div>
                    <p class="mt-1 text-xs text-slate-400/80">
                      限制单张图像的目标上限，控制渲染开销。
                    </p>
                    <input
                      v-model="detectionStore.detectionParams.maxDetections"
                      type="range"
                      min="10"
                      max="2000"
                      step="10"
                      class="ui-range mt-5"
                    />
                    <div
                      class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-slate-400/60"
                    >
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
                      <h3 class="text-sm font-semibold text-white/90">
                        视频抽帧间隔
                      </h3>
                      <span class="text-lg font-semibold text-accent-200">{{
                        detectionStore.detectionParams.frameSkip
                      }}</span>
                    </div>
                    <p class="mt-1 text-xs text-accent-100/80">
                      抽帧越大越节能，抽帧越小越平滑。
                    </p>
                    <input
                      v-model="detectionStore.detectionParams.frameSkip"
                      type="range"
                      min="1"
                      max="10"
                      step="1"
                      class="ui-range mt-5 accent-accent-400"
                    />
                    <div
                      class="mt-3 flex items-center justify-between text-[11px] uppercase tracking-widest text-accent-100/70"
                    >
                      <span>1 · 每帧</span>
                      <span>5 · 均衡</span>
                      <span>10 · 极速</span>
                    </div>
                  </div>

                  <div
                    v-if="fileType === 'video'"
                    class="rounded-2xl border border-primary-500/25 bg-primary-500/10 p-6"
                  >
                    <div class="flex items-baseline justify-between">
                      <h3 class="text-sm font-semibold text-white/90">
                        视频识别模式
                      </h3>
                      <span class="text-sm font-semibold text-primary-200">
                        {{
                          detectionMode === "realtime" ? "实时识别" : "批量识别"
                        }}
                      </span>
                    </div>
                    <p class="mt-1 text-xs text-primary-100/80">
                      实时模式会边推理边显示结果帧；批量模式保持原来的整段处理后展示。
                    </p>
                    <div class="mt-5 grid gap-3 sm:grid-cols-2">
                      <button
                        type="button"
                        class="rounded-xl border px-4 py-3 text-left text-sm transition-all"
                        :class="
                          detectionMode === 'realtime'
                            ? 'border-primary-400/60 bg-primary-500/20 text-primary-100'
                            : 'border-white/10 bg-white/5 text-slate-300 hover:bg-white/10'
                        "
                        @click="detectionMode = 'realtime'"
                      >
                        <p class="font-semibold">实时识别</p>
                        <p class="mt-1 text-xs opacity-80">
                          边处理边展示当前检测画面
                        </p>
                      </button>
                      <button
                        type="button"
                        class="rounded-xl border px-4 py-3 text-left text-sm transition-all"
                        :class="
                          detectionMode === 'batch'
                            ? 'border-primary-400/60 bg-primary-500/20 text-primary-100'
                            : 'border-white/10 bg-white/5 text-slate-300 hover:bg-white/10'
                        "
                        @click="detectionMode = 'batch'"
                      >
                        <p class="font-semibold">批量识别</p>
                        <p class="mt-1 text-xs opacity-80">
                          处理完成后输出完整结果视频
                        </p>
                      </button>
                    </div>
                  </div>
                </div>

                <div
                  class="mt-10 grid gap-4 border-t border-white/10 pt-6 text-sm text-slate-300/70 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center"
                >
                  <p>参数会自动同步到历史记录，便于后续复现与对比。</p>
                  <div
                    class="flex flex-wrap items-center gap-3 sm:justify-self-end"
                  >
                    <button
                      type="button"
                      class="btn-secondary text-sm"
                      @click="currentStep = 2"
                    >
                      返回素材选择
                    </button>
                    <button
                      type="button"
                      class="btn-primary px-8 text-sm"
                      :disabled="
                        !detectionStore.modelUploaded ||
                        !selectedFile ||
                        detectionStore.isProcessing
                      "
                      @click="runDetection"
                    >
                      {{
                        detectionStore.isProcessing
                          ? "处理中…"
                          : isRealtimeVideo
                            ? "开始实时识别 🚀"
                            : "开始识别 🚀"
                      }}
                    </button>
                  </div>
                </div>
              </div>
            </Transition>
            <!-- 步骤4：识别结果 -->
            <Transition :name="slideDirection" mode="out-in">
              <div
                v-if="currentStep === 4"
                key="step-4"
                class="absolute w-full"
              >
                <div v-if="detectionStore.isProcessing" class="card">
                  <div v-if="isRealtimeVideo" class="space-y-4">
                    <div
                      class="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300/80"
                    >
                      <span
                        >已发送 {{ realtimeState.sentFrames }} /
                        {{ realtimeState.totalFrames }} 帧</span
                      >
                      <span>已处理 {{ realtimeState.processedFrames }} 帧</span>
                      <span
                        >累计检测
                        {{ realtimeState.totalDetections }} 个目标</span
                      >
                      <span
                        >单帧耗时
                        {{
                          (realtimeState.lastInferTime || 0).toFixed(2)
                        }}s</span
                      >
                    </div>
                    <div
                      class="overflow-hidden rounded-xl border border-white/10 bg-slate-900/50"
                    >
                      <img
                        v-if="realtimePreviewUrl"
                        :src="realtimePreviewUrl"
                        class="max-h-[420px] w-full object-contain"
                        alt="实时识别预览"
                      />
                      <div
                        v-else
                        class="flex h-[280px] items-center justify-center text-sm text-slate-400"
                      >
                        正在等待第一帧检测结果...
                      </div>
                    </div>
                    <p v-if="realtimeError" class="text-xs text-rose-300">
                      {{ realtimeError }}
                    </p>
                  </div>
                  <div v-else class="flex flex-col gap-8 py-12 px-2">
                    <!-- 顶部图标 + 标题 -->
                    <div class="flex flex-col items-center gap-4 text-center">
                      <div class="relative">
                        <div
                          class="h-20 w-20 rounded-full border border-white/10 bg-white/5"
                        ></div>
                        <div
                          class="absolute inset-0 flex items-center justify-center"
                        >
                          <div
                            class="h-16 w-16 animate-spin rounded-full border-b-4 border-primary-500"
                          ></div>
                        </div>
                        <div
                          class="absolute inset-0 flex items-center justify-center"
                        >
                          <svg
                            class="h-6 w-6 text-primary-300"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="1.5"
                              d="M13 10V3L4 14h7v7l9-11h-7z"
                            />
                          </svg>
                        </div>
                      </div>
                      <div>
                        <h3 class="text-xl font-semibold text-white">
                          AI 正在分析素材
                        </h3>
                        <p class="mt-1 text-sm text-slate-300/70">
                          {{
                            detectionStore.detectionProgress.message ||
                            "正在初始化..."
                          }}
                        </p>
                      </div>
                    </div>

                    <!-- 进度条区域 -->
                    <div class="space-y-3">
                      <!-- 进度百分比 + 阶段标签 -->
                      <div class="flex items-center justify-between text-xs">
                        <span
                          class="rounded-full px-2.5 py-0.5 font-medium"
                          :class="{
                            'bg-slate-500/20 text-slate-300':
                              detectionStore.detectionProgress.stage ===
                                'prepare' ||
                              detectionStore.detectionProgress.stage ===
                                'start',
                            'bg-primary-500/20 text-primary-200':
                              detectionStore.detectionProgress.stage ===
                                'model_loaded' ||
                              detectionStore.detectionProgress.stage ===
                                'detecting' ||
                              detectionStore.detectionProgress.stage ===
                                'annotating' ||
                              detectionStore.detectionProgress.stage ===
                                'done_annotating',
                            'bg-amber-500/20 text-amber-200':
                              detectionStore.detectionProgress.stage ===
                                'optimizing' ||
                              detectionStore.detectionProgress.stage ===
                                'done_optimizing' ||
                              detectionStore.detectionProgress.stage ===
                                'uploading_original' ||
                              detectionStore.detectionProgress.stage ===
                                'uploading_result' ||
                              detectionStore.detectionProgress.stage ===
                                'saving_local' ||
                              detectionStore.detectionProgress.stage ===
                                'loading_history',
                            'bg-emerald-500/20 text-emerald-200':
                              detectionStore.detectionProgress.stage ===
                              'result',
                          }"
                        >
                          {{
                            {
                              prepare: "准备中",
                              start: "启动中",
                              model_loaded: "模型就绪",
                              detecting: "识别中",
                              annotating: "推理完成",
                              done_annotating: "保存结果",
                              optimizing: "优化视频",
                              done_optimizing: "即将完成",
                              uploading_original: "上传原始文件",
                              uploading_result: "上传结果文件",
                              saving_local: "保存本地记录",
                              loading_history: "同步历史记录",
                              result: "完成",
                            }[detectionStore.detectionProgress.stage] ||
                            "处理中"
                          }}
                        </span>
                        <span class="tabular-nums font-semibold text-white">
                          {{ detectionStore.detectionProgress.percent }}%
                        </span>
                      </div>

                      <!-- 进度条轨道 -->
                      <div
                        class="h-2.5 w-full overflow-hidden rounded-full bg-white/10"
                      >
                        <div
                          class="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-400 transition-all duration-300 ease-out"
                          :style="{
                            width:
                              detectionStore.detectionProgress.percent + '%',
                          }"
                        ></div>
                      </div>

                      <!-- 帧进度（仅视频识别时显示） -->
                      <div
                        v-if="detectionStore.detectionProgress.total > 0"
                        class="flex items-center justify-between text-xs text-slate-400/70"
                      >
                        <span>
                          已处理帧：
                          <span class="tabular-nums text-slate-200">
                            {{ detectionStore.detectionProgress.current }}
                          </span>
                          /
                          <span class="tabular-nums text-slate-200">
                            {{ detectionStore.detectionProgress.total }}
                          </span>
                        </span>
                        <span class="text-slate-400/50">视频逐帧推理中</span>
                      </div>
                    </div>

                    <!-- 底部标签 -->
                    <div
                      class="flex items-center justify-center gap-3 text-[11px] uppercase tracking-[0.3em] text-slate-400/50"
                    >
                      <span>多目标追踪</span>
                      <span>·</span>
                      <span>智能降噪</span>
                      <span>·</span>
                      <span>稳定运行</span>
                    </div>
                  </div>
                </div>

                <div v-else-if="detectionStore.currentResult" class="space-y-8">
                  <div
                    class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"
                  >
                    <div>
                      <p class="section-title">Step 04</p>
                      <h2 class="mt-3 text-3xl font-semibold text-white">
                        {{ isRealtimeResult ? "实时识别完成" : "识别完成" }}
                      </h2>
                      <p class="mt-2 text-sm text-slate-300/80">
                        {{
                          isRealtimeResult
                            ? "以下是实时模式返回的检测快照与统计信息。"
                            : "以下是本次识别的核心指标与可视化结果。"
                        }}
                      </p>
                    </div>
                    <div class="flex flex-wrap items-center gap-3">
                      <span class="pill bg-emerald-500/20 text-emerald-200"
                        >检测完成</span
                      >
                      <span class="text-xs text-slate-300/70"
                        >耗时
                        {{
                          (
                            detectionStore.currentResult.processTime || 0
                          ).toFixed(2)
                        }}s</span
                      >
                    </div>
                  </div>

                  <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <div class="glass-panel p-5 text-center">
                      <p
                        class="text-xs uppercase tracking-[0.3em] text-slate-400/70"
                      >
                        {{ resultCountLabel }}
                      </p>
                      <p class="mt-3 text-3xl font-semibold text-primary-200">
                        {{ resultTargetCount }}
                      </p>
                      <p
                        v-if="resultCountHint"
                        class="mt-2 text-[11px] text-slate-400/80"
                      >
                        {{ resultCountHint }}
                      </p>
                    </div>
                    <div class="glass-panel p-5 text-center">
                      <p
                        class="text-xs uppercase tracking-[0.3em] text-slate-400/70"
                      >
                        置信度
                      </p>
                      <p class="mt-3 text-3xl font-semibold text-primary-200">
                        {{
                          Number(
                            detectionStore.detectionParams.confidence,
                          ).toFixed(2)
                        }}
                      </p>
                    </div>
                    <div class="glass-panel p-5 text-center">
                      <p
                        class="text-xs uppercase tracking-[0.3em] text-slate-400/70"
                      >
                        输入尺寸
                      </p>
                      <p class="mt-3 text-3xl font-semibold text-primary-200">
                        {{ Number(detectionStore.detectionParams.imgSize) }}
                      </p>
                    </div>
                    <div class="glass-panel p-5 text-center">
                      <p
                        class="text-xs uppercase tracking-[0.3em] text-slate-400/70"
                      >
                        推理耗时
                      </p>
                      <p class="mt-3 text-3xl font-semibold text-primary-200">
                        {{
                          (
                            detectionStore.currentResult.processTime || 0
                          ).toFixed(2)
                        }}s
                      </p>
                    </div>
                  </div>

                  <div
                    v-if="resultClassCounts.length > 0"
                    class="glass-panel p-6"
                  >
                    <div class="flex items-center justify-between gap-3">
                      <h3 class="text-sm font-semibold text-white/90">
                        分类计数
                      </h3>
                      <span class="text-xs text-slate-400/80">{{
                        resultClassCountModeLabel
                      }}</span>
                    </div>
                    <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                      <div
                        v-for="item in resultClassCounts"
                        :key="item.className"
                        class="rounded-xl border border-white/10 bg-white/5 px-4 py-3"
                      >
                        <p class="truncate text-sm text-slate-200">
                          {{ item.className }}
                        </p>
                        <p class="mt-1 text-xl font-semibold text-primary-200">
                          {{ item.count }}
                        </p>
                      </div>
                    </div>
                  </div>

                  <!-- 识别结果文字描述 -->
                  <div
                    v-if="detectionStore.currentResult.description"
                    class="glass-panel p-6"
                  >
                    <div class="flex items-start gap-4">
                      <div
                        class="flex-shrink-0 rounded-full bg-primary-500/20 p-3"
                      >
                        <svg
                          class="h-6 w-6 text-primary-300"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                      </div>
                      <div class="flex-1">
                        <h3 class="text-sm font-semibold text-white/90">
                          识别结果概要
                        </h3>
                        <p
                          class="mt-2 text-base leading-relaxed text-slate-300"
                        >
                          {{ detectionStore.currentResult.description }}
                        </p>
                      </div>
                    </div>
                  </div>

                  <!-- AI 智能分析 -->
                  <AiAnalysisPanel
                    v-if="shouldShowAiAnalysis"
                    :analysis="detectionStore.aiAnalysisResult"
                    :loading="detectionStore.aiAnalysisLoading"
                    :retrying="detectionStore.aiRetrying"
                    :cooldown="detectionStore.aiRetryCooldown"
                    :llm-loading="detectionStore.aiAnalysisLoading"
                    @retry="detectionStore.retryAiAnalysis()"
                  />

                  <div class="grid gap-6 lg:grid-cols-2">
                    <div class="glass-panel group overflow-hidden p-5">
                      <div class="flex items-center justify-between">
                        <h3 class="text-sm font-semibold text-white/90">
                          原始素材
                        </h3>
                        <button
                          type="button"
                          class="btn-ghost text-xs"
                          @click="openPreview('original')"
                        >
                          放大查看
                        </button>
                      </div>
                      <div
                        class="relative mt-4 aspect-video overflow-hidden rounded-2xl border border-white/10 bg-slate-900/35"
                      >
                        <img
                          v-if="fileType === 'image'"
                          :src="detectionStore.currentResult.originalUrl"
                          @error="handleImageError($event, '原始图片')"
                          class="absolute inset-0 h-full w-full object-contain"
                          alt="原始素材预览"
                        />
                        <video
                          v-else
                          :src="detectionStore.currentResult.originalUrl"
                          controls
                          class="absolute inset-0 h-full w-full object-cover"
                        ></video>
                        <div
                          class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                        ></div>
                      </div>
                    </div>
                    <div class="glass-panel group overflow-hidden p-5">
                      <div class="flex items-center justify-between">
                        <h3 class="text-sm font-semibold text-white/90">
                          识别结果
                        </h3>
                        <button
                          type="button"
                          class="btn-ghost text-xs"
                          @click="openPreview('result')"
                        >
                          放大查看
                        </button>
                      </div>
                      <div
                        class="relative mt-4 aspect-video overflow-hidden rounded-2xl border border-white/10 bg-slate-900/35"
                      >
                        <img
                          v-if="fileType === 'image' || showRealtimeSnapshot"
                          :src="detectionStore.currentResult.resultUrl"
                          @error="handleImageError($event, '结果图片')"
                          class="absolute inset-0 h-full w-full object-contain"
                          alt="识别结果预览"
                        />
                        <video
                          v-else
                          :src="detectionStore.currentResult.resultUrl"
                          controls
                          class="absolute inset-0 h-full w-full object-cover"
                        ></video>
                        <div
                          class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/45 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div class="glass-panel p-5">
                    <div class="flex flex-col gap-3">
                      <div
                        class="grid gap-2 text-sm text-slate-300/80 sm:grid-cols-2 sm:gap-x-8"
                      >
                        <p>
                          素材名称：{{
                            customFileName ||
                            selectedFile?.name ||
                            detectionStore.currentResult.fileName ||
                            "未命名素材"
                          }}
                        </p>
                        <p>
                          置信度阈值：{{
                            Number(
                              detectionStore.detectionParams.confidence,
                            ).toFixed(2)
                          }}
                          · IOU：{{
                            Number(
                              detectionStore.detectionParams.iouThreshold,
                            ).toFixed(2)
                          }}
                        </p>
                        <p v-if="fileType === 'video'">
                          视频抽帧：每
                          {{ detectionStore.detectionParams.frameSkip }}
                          帧分析一次
                        </p>
                        <p v-if="fileType === 'video'">
                          识别模式：{{
                            isRealtimeResult ? "实时识别" : "批量识别"
                          }}
                        </p>
                        <p v-else>
                          图像尺寸：{{ detectionStore.detectionParams.imgSize }}
                          像素
                        </p>
                      </div>
                      <div
                        class="grid grid-cols-2 gap-3 sm:grid-cols-[repeat(auto-fit,minmax(140px,1fr))]"
                      >
                        <button
                          type="button"
                          class="btn-secondary w-full text-sm"
                          @click="openPreview('both')"
                        >
                          对比预览
                        </button>
                        <a
                          v-if="
                            hasRealtimeResultVideo &&
                            detectionStore.currentResult.resultDownloadUrl
                          "
                          :href="detectionStore.currentResult.resultDownloadUrl"
                          class="btn-secondary w-full text-sm"
                        >
                          导出视频
                        </a>
                        <router-link
                          to="/history"
                          class="btn-secondary w-full text-sm"
                          >查看历史记录</router-link
                        >
                        <button
                          type="button"
                          class="btn-primary w-full text-sm"
                          @click="resetAllStates"
                        >
                          重新开始
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else class="card text-center">
                  <div class="py-16">
                    <svg
                      class="mx-auto h-16 w-16 text-slate-400/60"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.5"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    <h3 class="mt-6 text-lg font-semibold text-white">
                      尚未开始识别
                    </h3>
                    <p class="mt-2 text-sm text-slate-300/75">
                      请完成前面三个步骤后，点击“开始识别”按钮。
                    </p>
                    <button
                      type="button"
                      class="btn-primary mt-6"
                      @click="currentStep = 1"
                    >
                      回到第一步
                    </button>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
          <!-- 结束步骤切换容器 -->
        </div>
      </div>
    </div>

    <!-- 所有弹窗通过 Teleport 传送到 body，避免被父级 stacking context 限制 -->
    <Teleport to="body">
      <!-- 图片预览模态框 -->
      <div
        v-if="showPreview && detectionStore.currentResult"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-slate-950/95 backdrop-blur-xl"
        @click="closePreview"
      >
        <div class="absolute top-6 right-8 z-[80] flex items-center gap-4">
          <div
            class="flex items-center gap-3 rounded-2xl border border-white/15 bg-white/10 px-4 py-2 shadow-[0_12px_35px_rgba(8,15,40,0.45)] backdrop-blur"
          >
            <button
              @click.stop="zoomOut"
              class="text-slate-200 transition-colors hover:text-white"
              title="缩小"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M21 21l-5.197-5.197M4 10h7m0 0h7m-7 0V3m0 7v7"
                />
              </svg>
            </button>
            <span
              class="text-xs font-semibold tracking-[0.28em] text-slate-200 uppercase"
              >{{ Math.round(scale * 100) }}%</span
            >
            <button
              @click.stop="zoomIn"
              class="text-slate-200 transition-colors hover:text-white"
              title="放大"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M12 5v14m7-7H5"
                />
              </svg>
            </button>
            <button
              @click.stop="resetZoom"
              class="ml-1 text-slate-200 transition-colors hover:text-white"
              title="复位"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M12 4V2m0 20v-2m8-8h2M2 12h2m15.071 6.071l1.414 1.414M4.515 4.515l1.414 1.414m0 12.727l-1.414 1.414M19.071 4.929l1.414-1.414"
                />
              </svg>
            </button>
          </div>

          <!-- 视频控制按钮组 -->
          <div
            v-if="
              fileType === 'video' &&
              previewMode === 'both' &&
              !showRealtimeSnapshot
            "
            class="flex items-center gap-2"
          >
            <!-- 同步播放/暂停按钮 -->
            <button
              @click.stop="toggleVideoPlayback"
              class="flex h-10 items-center gap-2 rounded-full border px-4 transition-all"
              :class="
                isVideoPlaying
                  ? 'border-red-400/30 bg-red-500/20 text-red-300 hover:border-red-400/50 hover:bg-red-500/30'
                  : 'border-primary-400/30 bg-primary-500/20 text-primary-300 hover:border-primary-400/50 hover:bg-primary-500/30'
              "
              :title="isVideoPlaying ? '暂停播放' : '同步播放'"
            >
              <svg
                v-if="!isVideoPlaying"
                class="h-5 w-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M8 5v14l11-7z" />
              </svg>
              <svg
                v-else
                class="h-5 w-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
              </svg>
              <span class="text-sm font-medium">{{
                isVideoPlaying ? "暂停" : "同步播放"
              }}</span>
            </button>

            <!-- 回到原点按钮 -->
            <button
              @click.stop="resetVideos"
              class="flex h-10 items-center gap-2 rounded-full border border-slate-400/30 bg-slate-500/20 px-4 text-slate-300 transition-all hover:border-slate-400/50 hover:bg-slate-500/30"
              title="重置到开始位置"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
                />
              </svg>
              <span class="text-sm font-medium">回到原点</span>
            </button>
          </div>

          <button
            @click="closePreview"
            class="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/10 text-slate-200 transition hover:border-white/20 hover:text-white"
            title="关闭"
          >
            <svg
              class="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div
          :class="[
            'relative h-[92vh] w-full max-w-[98vw] rounded-3xl border border-white/10 bg-white/5 px-6 py-6 shadow-[0_35px_120px_rgba(8,15,40,0.55)]',
            previewMode === 'both'
              ? 'grid grid-cols-2 gap-8'
              : 'flex items-center justify-center',
          ]"
          @click.stop
        >
          <div
            v-if="previewMode === 'original' || previewMode === 'both'"
            class="relative flex h-full flex-col items-center"
          >
            <div
              class="flex w-full items-center justify-between text-xs uppercase tracking-[0.3em] text-slate-300/70 mb-2"
            >
              <span>原始素材</span>
              <span v-if="fileType === 'image'">拖拽以平移 · 滚轮缩放</span>
              <span v-else>视频播放</span>
            </div>
            <div
              :class="[
                'relative flex h-full w-full items-center justify-center overflow-hidden rounded-2xl border border-white/15 bg-slate-900/40 p-2',
                fileType === 'image' ? 'cursor-move' : '',
              ]"
              @mousedown="(e) => fileType === 'image' && startDrag(e)"
              @mousemove="(e) => fileType === 'image' && onDrag(e)"
              @mouseup="fileType === 'image' && endDrag()"
              @mouseleave="fileType === 'image' && endDrag()"
              @wheel.prevent="(e) => fileType === 'image' && onWheel(e)"
            >
              <img
                v-if="fileType === 'image'"
                :src="detectionStore.currentResult.originalUrl"
                :style="{
                  transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
                  transition: isDragging ? 'none' : 'transform 0.1s',
                  transformOrigin: 'center center',
                  width: '100%',
                  height: '100%',
                }"
                class="select-none object-contain"
                alt="原始素材"
                draggable="false"
              />
              <video
                v-else
                ref="originalVideoRef"
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
            <div
              class="flex w-full items-center justify-between text-xs uppercase tracking-[0.3em] text-slate-300/70 mb-2"
            >
              <span>识别结果</span>
              <span v-if="fileType === 'image' || showRealtimeSnapshot"
                >拖拽以平移 · 滚轮缩放</span
              >
              <span v-else>视频播放</span>
            </div>
            <div
              :class="[
                'relative flex h-full w-full items-center justify-center overflow-hidden rounded-2xl border border-white/15 bg-slate-900/40 p-2',
                fileType === 'image' || showRealtimeSnapshot
                  ? 'cursor-move'
                  : '',
              ]"
              @mousedown="
                (e) =>
                  (fileType === 'image' || showRealtimeSnapshot) && startDrag(e)
              "
              @mousemove="
                (e) =>
                  (fileType === 'image' || showRealtimeSnapshot) && onDrag(e)
              "
              @mouseup="
                (fileType === 'image' || showRealtimeSnapshot) && endDrag()
              "
              @mouseleave="
                (fileType === 'image' || showRealtimeSnapshot) && endDrag()
              "
              @wheel.prevent="
                (e) =>
                  (fileType === 'image' || showRealtimeSnapshot) && onWheel(e)
              "
            >
              <img
                v-if="fileType === 'image' || showRealtimeSnapshot"
                :src="detectionStore.currentResult.resultUrl"
                :style="{
                  transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
                  transition: isDragging ? 'none' : 'transform 0.1s',
                  transformOrigin: 'center center',
                  width: '100%',
                  height: '100%',
                }"
                class="select-none object-contain"
                alt="识别结果"
                draggable="false"
              />
              <video
                v-else
                ref="resultVideoRef"
                :src="detectionStore.currentResult.resultUrl"
                controls
                class="max-h-full max-w-full rounded-2xl"
              ></video>
            </div>
          </div>
        </div>
      </div>

      <!-- 权重选择加载弹窗 -->
      <div
        v-if="isSelectingWeight"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      >
        <div
          class="relative rounded-3xl border border-white/10 bg-slate-900 p-8 shadow-2xl"
        >
          <div class="flex flex-col items-center gap-4">
            <div
              class="h-16 w-16 animate-spin rounded-full border-4 border-primary-500/20 border-t-primary-400"
            ></div>
            <div class="text-center">
              <h3 class="text-xl font-semibold text-white">正在加载权重</h3>
              <p class="mt-2 text-sm text-slate-400">请稍等，正在准备模型...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 重新开始确认弹窗 -->
      <div
        v-if="showResetDialog"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
        @click.self="cancelReset"
      >
        <div
          class="relative w-full max-w-md rounded-3xl border border-white/10 bg-slate-900 p-8 shadow-2xl"
        >
          <div class="text-center">
            <div
              class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-amber-500/20"
            >
              <svg
                class="h-8 w-8 text-amber-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                ></path>
              </svg>
            </div>

            <h3 class="mt-4 text-xl font-semibold text-white">确认重新开始</h3>
            <p class="mt-2 text-sm text-slate-300">
              这将清空所有当前的识别数据和设置，包括已上传的文件、检测参数和结果。此操作无法撤销。
            </p>
          </div>

          <div class="mt-6 flex gap-3">
            <button
              @click="confirmReset"
              class="flex-1 rounded-xl bg-primary-500 px-4 py-3 text-sm font-medium text-white transition-all hover:bg-primary-600"
            >
              确认重新开始
            </button>
            <button
              @click="cancelReset"
              class="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-white transition-all hover:bg-white/10"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
export default {
  name: "Workspace",
};
</script>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useAuthStore } from "../stores/auth";
import { useDetectionStore } from "../stores/detection";
import { supabase } from "../config/supabase";
import { buildProtectedApiUrl } from "../utils/protected-url";
import { getRealtimeSamplingPlan } from "../utils/realtime-video";
import AiAnalysisPanel from "../components/AiAnalysisPanel.vue";

const authStore = useAuthStore();
const detectionStore = useDetectionStore();
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const currentStep = ref(1);
const previousStep = ref(1);
const slideDirection = ref("slide-left");
const fileType = ref("image");
const selectedFile = ref(null);
const customFileName = ref("");
const isEditingFileName = ref(false);
const showResetDialog = ref(false);

// 视频实时识别相关
const detectionMode = ref("realtime");
const realtimePreviewUrl = ref("");
const realtimeError = ref("");
const realtimeState = ref({
  active: false,
  totalFrames: 0,
  sentFrames: 0,
  processedFrames: 0,
  totalDetections: 0,
  lastInferTime: 0,
});
let realtimeSocket = null;
let stopRealtimeRequested = false;
let originalVideoObjectUrl = null;
const isRealtimeVideo = computed(
  () => fileType.value === "video" && detectionMode.value === "realtime",
);
const isRealtimeResult = computed(
  () => !!detectionStore.currentResult?.realtime,
);
const hasRealtimeResultVideo = computed(
  () => !!detectionStore.currentResult?.resultVideoUrl,
);
const showRealtimeSnapshot = computed(
  () => isRealtimeResult.value && !hasRealtimeResultVideo.value,
);
const isVideoResult = computed(() => fileType.value === "video");
const shouldShowAiAnalysis = computed(() => {
  if (!detectionStore.aiAnalysisResult) return false;
  const resultType = detectionStore.currentResult?.type || fileType.value;
  return resultType !== "video";
});
const isStep3Completed = computed(
  () => detectionStore.isProcessing || !!detectionStore.currentResult,
);

const resultTargetCount = computed(() => {
  const result = detectionStore.currentResult;
  if (!result) return 0;
  if (isVideoResult.value) {
    return (
      result.uniqueTargetCount ??
      result.maxTargetsPerFrame ??
      result.totalDetections ??
      result.detections?.length ??
      0
    );
  }
  return result.totalDetections ?? result.detections?.length ?? 0;
});

const resultCountLabel = computed(() => {
  const result = detectionStore.currentResult;
  if (!result || !isVideoResult.value) return "检测目标";
  return result.countMode === "tracking_unique" ? "去重目标" : "单帧峰值";
});

const resultCountHint = computed(() => {
  const result = detectionStore.currentResult;
  if (!result || !isVideoResult.value) return "";
  const total = result.totalDetections ?? result.detections?.length ?? 0;
  if (result.countMode === "tracking_unique") {
    return `累计检测框 ${total}`;
  }
  return `峰值统计，累计检测框 ${total}`;
});

const resultClassCountModeLabel = computed(() => {
  const result = detectionStore.currentResult;
  if (!result || !isVideoResult.value) return "累计分类计数";
  return result.countMode === "tracking_unique" ? "按跟踪去重" : "按单帧峰值";
});

const resultClassCounts = computed(() => {
  const result = detectionStore.currentResult;
  if (!result) return [];

  const preferred = isVideoResult.value
    ? result.uniqueClassCounts || result.classCounts || {}
    : result.classCounts || {};

  const entries = Object.entries(preferred)
    .map(([className, count]) => ({ className, count: Number(count) || 0 }))
    .filter((item) => item.count > 0)
    .sort((a, b) => b.count - a.count);

  if (entries.length > 0) {
    return entries;
  }

  const fallbackCounts = {};
  for (const det of result.detections || []) {
    const className = det.class || "未知";
    fallbackCounts[className] = (fallbackCounts[className] || 0) + 1;
  }
  return Object.entries(fallbackCounts)
    .map(([className, count]) => ({ className, count }))
    .sort((a, b) => b.count - a.count);
});

// 权重管理相关
const availableWeights = ref([]);
const loadingWeights = ref(false);
const selectedWeightId = ref(null);
const isSelectingWeight = ref(false);
const workspaceNotice = ref(null);

const showWorkspaceNotice = (message, type = "error") => {
  if (!message) return;
  workspaceNotice.value = {
    type,
    message,
  };
};

const clearWorkspaceNotice = () => {
  workspaceNotice.value = null;
};

const workspaceNoticeClass = computed(() => {
  const type = workspaceNotice.value?.type || "info";
  if (type === "warning") {
    return "border-amber-500/40 bg-amber-500/10 text-amber-100";
  }
  if (type === "success") {
    return "border-emerald-500/40 bg-emerald-500/10 text-emerald-100";
  }
  if (type === "info") {
    return "border-primary-500/40 bg-primary-500/10 text-primary-100";
  }
  return "border-red-500/40 bg-red-500/10 text-red-100";
});

const applySelectedFile = (file) => {
  if (!file) return;

  stopRealtimeDetection();
  resetRealtimeState();
  clearWorkspaceNotice();

  const mime = file.type || "";
  if (mime.startsWith("video")) {
    fileType.value = "video";
    detectionMode.value = "realtime";
  } else if (mime.startsWith("image")) {
    fileType.value = "image";
    detectionMode.value = "batch";
  } else {
    showWorkspaceNotice("暂不支持该文件类型，请选择图片或视频", "warning");
    return;
  }

  selectedFile.value = file;
  // 初始化自定义文件名（去除扩展名）
  const nameWithoutExt = file.name.replace(/\.[^/.]+$/, "");
  customFileName.value = nameWithoutExt;
  isEditingFileName.value = false;
};

// 文件输入框的引用
const fileInput = ref(null);

// 预览相关状态
const showPreview = ref(false);
const previewMode = ref("both");
const scale = ref(1);
const position = ref({ x: 0, y: 0 });
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });

// 视频同步播放相关
const originalVideoRef = ref(null);
const resultVideoRef = ref(null);
const isVideoPlaying = ref(false);

const handleFileSelect = (e) => {
  const file = e.target.files?.[0];
  applySelectedFile(file);

  if (fileInput.value) {
    fileInput.value.value = "";
  }
};

const handleFileDrop = (event) => {
  const file = event.dataTransfer?.files?.[0];
  applySelectedFile(file);
};

const clearSelectedFile = () => {
  stopRealtimeDetection();
  resetRealtimeState();
  clearWorkspaceNotice();
  selectedFile.value = null;
  customFileName.value = "";
  isEditingFileName.value = false;
  if (fileInput.value) {
    fileInput.value.value = "";
  }
};

const formatFileSize = (bytes) => {
  if (bytes === undefined || bytes === null) return "0 B";
  let size = Number(bytes);
  const units = ["B", "KB", "MB", "GB", "TB"];
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }

  const fixed = unitIndex === 0 ? 0 : unitIndex === 1 ? 1 : 2;
  return `${size.toFixed(fixed)} ${units[unitIndex]}`;
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const revokeRealtimePreviewUrl = () => {
  if (
    realtimePreviewUrl.value &&
    realtimePreviewUrl.value.startsWith("blob:")
  ) {
    URL.revokeObjectURL(realtimePreviewUrl.value);
  }
};

const updateRealtimePreview = (blob) => {
  revokeRealtimePreviewUrl();
  realtimePreviewUrl.value = URL.createObjectURL(blob);
};

const resetRealtimeState = () => {
  revokeRealtimePreviewUrl();
  realtimePreviewUrl.value = "";
  realtimeError.value = "";
  realtimeState.value = {
    active: false,
    totalFrames: 0,
    sentFrames: 0,
    processedFrames: 0,
    totalDetections: 0,
    lastInferTime: 0,
  };
};

const closeRealtimeSocket = () => {
  if (realtimeSocket) {
    try {
      realtimeSocket.close();
    } catch (error) {
      console.warn("关闭实时连接失败:", error);
    }
    realtimeSocket = null;
  }
};

const stopRealtimeDetection = () => {
  stopRealtimeRequested = true;
  realtimeState.value.active = false;
  closeRealtimeSocket();
};

const waitForSocketOpen = (socket) => {
  return new Promise((resolve, reject) => {
    const onOpen = () => {
      cleanup();
      resolve();
    };
    const onError = () => {
      cleanup();
      reject(new Error("实时连接建立失败"));
    };
    const onClose = () => {
      cleanup();
      reject(new Error("实时连接被关闭"));
    };
    const cleanup = () => {
      socket.removeEventListener("open", onOpen);
      socket.removeEventListener("error", onError);
      socket.removeEventListener("close", onClose);
    };
    socket.addEventListener("open", onOpen);
    socket.addEventListener("error", onError);
    socket.addEventListener("close", onClose);
  });
};

const parseSocketMessage = async (data) => {
  if (typeof data === "string") {
    return JSON.parse(data);
  }

  let arrayBuffer = null;
  if (data instanceof Blob) {
    arrayBuffer = await data.arrayBuffer();
  } else if (data instanceof ArrayBuffer) {
    arrayBuffer = data;
  } else if (ArrayBuffer.isView(data)) {
    arrayBuffer = data.buffer.slice(
      data.byteOffset,
      data.byteOffset + data.byteLength,
    );
  } else {
    throw new Error("未知的 WebSocket 数据格式");
  }

  if (arrayBuffer.byteLength < 4) {
    throw new Error("二进制消息长度不足");
  }

  const view = new DataView(arrayBuffer);
  const metaLength = view.getUint32(0, false);
  if (arrayBuffer.byteLength < 4 + metaLength) {
    throw new Error("二进制消息元数据损坏");
  }

  const metaBytes = new Uint8Array(arrayBuffer, 4, metaLength);
  const meta = JSON.parse(new TextDecoder().decode(metaBytes));
  const imageBytes = new Uint8Array(arrayBuffer, 4 + metaLength);
  const imageBlob = new Blob([imageBytes], { type: "image/jpeg" });
  return {
    ...meta,
    imageBlob,
  };
};

const waitForSocketPacket = (socket, timeoutMs = 120000) => {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      cleanup();
      reject(new Error("实时识别响应超时"));
    }, timeoutMs);

    const onMessage = async (event) => {
      cleanup();
      try {
        const parsed = await parseSocketMessage(event.data);
        resolve(parsed);
      } catch (error) {
        reject(new Error("实时识别响应解析失败"));
      }
    };
    const onError = () => {
      cleanup();
      reject(new Error("实时识别连接发生错误"));
    };
    const onClose = () => {
      cleanup();
      reject(new Error("实时识别连接已断开"));
    };
    const cleanup = () => {
      clearTimeout(timer);
      socket.removeEventListener("message", onMessage);
      socket.removeEventListener("error", onError);
      socket.removeEventListener("close", onClose);
    };

    socket.addEventListener("message", onMessage);
    socket.addEventListener("error", onError);
    socket.addEventListener("close", onClose);
  });
};

const canvasToJpegBlob = (canvas) => {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new Error("视频帧编码失败"));
          return;
        }
        resolve(blob);
      },
      "image/jpeg",
      0.8,
    );
  });
};

const runRealtimeVideoDetection = async (file) => {
  resetRealtimeState();
  stopRealtimeRequested = false;
  detectionStore.currentResult = null;
  detectionStore.isProcessing = true;
  realtimeState.value.active = true;
  const startedAt = performance.now();

  const {
    data: { session },
  } = await supabase.auth.getSession();
  const token = session?.access_token;
  if (!token) {
    throw new Error("未检测到有效登录会话，请重新登录后重试");
  }

  const apiUrl = new URL(API_URL);
  apiUrl.protocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";
  apiUrl.pathname = "/ws/detect-live";
  apiUrl.search = "";
  apiUrl.searchParams.set("token", token);

  const processingVideoUrl = URL.createObjectURL(file);

  try {
    realtimeSocket = new WebSocket(apiUrl.toString());
    await waitForSocketOpen(realtimeSocket);

    const expectedFps = 25;
    const sampleFps = Math.max(
      2,
      Math.min(
        12,
        Math.round(
          expectedFps /
            Math.max(1, detectionStore.detectionParams.frameSkip || 1),
        ),
      ),
    );

    realtimeSocket.send(
      JSON.stringify({
        type: "start",
        params: detectionStore.detectionParams,
        recording: {
          enabled: true,
          fps: sampleFps,
        },
      }),
    );

    const readyPacket = await waitForSocketPacket(realtimeSocket);
    if (readyPacket.type === "error") {
      throw new Error(readyPacket.detail || "实时识别初始化失败");
    }

    const video = document.createElement("video");
    video.preload = "auto";
    video.muted = true;
    video.playsInline = true;
    video.src = processingVideoUrl;

    await new Promise((resolve, reject) => {
      video.onloadedmetadata = () => resolve();
      video.onerror = () => reject(new Error("视频元数据读取失败"));
    });

    const duration = Number(video.duration);
    if (!Number.isFinite(duration) || duration <= 0) {
      throw new Error("视频时长无效，无法实时识别");
    }

    const canvas = document.createElement("canvas");
    canvas.width = Math.max(2, video.videoWidth);
    canvas.height = Math.max(2, video.videoHeight);
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      throw new Error("无法创建画布上下文");
    }

    // 纯时间戳 seek 方案，完全避免帧重叠和重复
    const { timestamps, totalFrames } = getRealtimeSamplingPlan({
      durationSeconds: duration,
      frameSkip: detectionStore.detectionParams.frameSkip || 1,
      sourceFps: expectedFps,
      fallbackSourceFps: 25,
      minSampleFps: 2,
      maxSampleFps: 12,
    });
    realtimeState.value.totalFrames = totalFrames;

    // 不需要播放视频，只需 seek 到每个时间点并抓帧
    await video.play();
    video.pause(); // 立即暂停，后续通过 seek 移动位置

    const sendFrame = async () => {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const frameBlob = await canvasToJpegBlob(canvas);
      const frameBuffer = await frameBlob.arrayBuffer();
      realtimeSocket.send(frameBuffer);
      realtimeState.value.sentFrames = realtimeState.value.sentFrames + 1;

      const packet = await waitForSocketPacket(realtimeSocket);
      if (packet.type === "error") {
        throw new Error(packet.detail || "实时识别帧处理失败");
      }
      if (packet.type !== "frame") {
        return;
      }

      realtimeState.value.processedFrames =
        packet.processedFrames || realtimeState.value.processedFrames;
      realtimeState.value.totalDetections =
        packet.totalDetections ?? realtimeState.value.totalDetections;
      realtimeState.value.lastInferTime = packet.inferTime || 0;
      if (packet.imageBlob) {
        updateRealtimePreview(packet.imageBlob);
      }
    };

    for (let i = 0; i < timestamps.length; i++) {
      if (stopRealtimeRequested) {
        throw new Error("实时识别已取消");
      }

      const targetTime = timestamps[i];
      video.currentTime = targetTime;
      await new Promise((resolve) => {
        video.onseeked = resolve;
      });

      await sendFrame();
    }

    realtimeSocket.send(JSON.stringify({ type: "end" }));
    const donePacket = await waitForSocketPacket(realtimeSocket);
    if (donePacket.type === "error") {
      throw new Error(donePacket.detail || "实时识别结束失败");
    }

    if (originalVideoObjectUrl) {
      URL.revokeObjectURL(originalVideoObjectUrl);
    }
    originalVideoObjectUrl = URL.createObjectURL(file);
    const protectedResultUrl = donePacket.resultUrl
      ? await buildProtectedApiUrl(donePacket.resultUrl, token)
      : "";
    const protectedDownloadUrl = donePacket.downloadUrl
      ? await buildProtectedApiUrl(donePacket.downloadUrl, token)
      : "";

    detectionStore.currentResult = {
      success: true,
      realtime: true,
      originalUrl: originalVideoObjectUrl,
      resultUrl: protectedResultUrl || realtimePreviewUrl.value,
      resultVideoUrl: protectedResultUrl,
      resultDownloadUrl: protectedDownloadUrl,
      detections: [],
      totalDetections:
        donePacket.totalDetections || realtimeState.value.totalDetections,
      uniqueTargetCount: donePacket.uniqueTargetCount ?? 0,
      classCounts: donePacket.classCounts || {},
      uniqueClassCounts: donePacket.classCounts || {},
      countMode: donePacket.countMode || "frame_peak",
      maxTargetsPerFrame: donePacket.maxTargetsPerFrame ?? 0,
      description: donePacket.description || "实时识别完成",
      processTime: (performance.now() - startedAt) / 1000,
    };
  } finally {
    realtimeState.value.active = false;
    detectionStore.isProcessing = false;
    closeRealtimeSocket();
    URL.revokeObjectURL(processingVideoUrl);
  }
};

const runDetection = async () => {
  if (!selectedFile.value) return;

  realtimeError.value = "";
  clearWorkspaceNotice();
  currentStep.value = 4; // 跳转到结果页面

  try {
    if (isRealtimeVideo.value) {
      await runRealtimeVideoDetection(selectedFile.value);
      return;
    }

    stopRealtimeDetection();
    resetRealtimeState();

    const result = await detectionStore.runDetection(
      selectedFile.value,
      fileType.value,
    );
    if (!result.success) {
      showWorkspaceNotice(`识别失败：${result.error || "请稍后重试"}`, "error");
      currentStep.value = 3; // 识别失败返回参数页面
    }
  } catch (error) {
    realtimeError.value = error.message || "实时识别失败";
    showWorkspaceNotice(`识别失败：${realtimeError.value}`, "error");
    currentStep.value = 3;
  }
};

const handleImageError = (event, type) => {
  console.error(`[ERROR] ${type}加载失败:`, event.target.src);
  console.error("[ERROR] 错误事件:", event);
  showWorkspaceNotice(`${type}加载失败，请检查文件是否仍然可访问`, "warning");
};

// 打开预览
const openPreview = (mode) => {
  showPreview.value = true;
  previewMode.value = mode;
  resetZoom();
};

// 关闭预览
const closePreview = () => {
  showPreview.value = false;
  resetZoom();
  // 暂停所有视频
  if (originalVideoRef.value) originalVideoRef.value.pause();
  if (resultVideoRef.value) resultVideoRef.value.pause();
  isVideoPlaying.value = false;
};

// 视频同步播放/暂停
const toggleVideoPlayback = () => {
  if (fileType.value !== "video") return;

  const videos = [];
  if (previewMode.value === "both" || previewMode.value === "original") {
    if (originalVideoRef.value) videos.push(originalVideoRef.value);
  }
  if (previewMode.value === "both" || previewMode.value === "result") {
    if (resultVideoRef.value) videos.push(resultVideoRef.value);
  }

  if (videos.length === 0) return;

  if (isVideoPlaying.value) {
    // 暂停所有视频
    videos.forEach((video) => video.pause());
    isVideoPlaying.value = false;
  } else {
    // 同步播放所有视频
    // 1. 如果所有视频都已播放完毕，从头开始
    // 2. 如果视频位置不同步，同步到第一个视频的位置
    // 3. 否则从当前位置继续播放
    const allEnded = videos.every((video) => video.ended);

    if (allEnded) {
      // 所有视频都播放完了，从头开始
      videos.forEach((video) => {
        video.currentTime = 0;
        video.play();
      });
    } else if (videos.length > 1) {
      // 多个视频时，同步到第一个视频的位置
      const syncTime = videos[0].currentTime;
      videos.forEach((video) => {
        video.currentTime = syncTime;
        video.play();
      });
    } else {
      // 单个视频，直接播放
      videos[0].play();
    }

    isVideoPlaying.value = true;
  }
};

// 重置视频到开始位置（暂停状态）
const resetVideos = () => {
  if (fileType.value !== "video") return;

  const videos = [];
  if (previewMode.value === "both" || previewMode.value === "original") {
    if (originalVideoRef.value) videos.push(originalVideoRef.value);
  }
  if (previewMode.value === "both" || previewMode.value === "result") {
    if (resultVideoRef.value) videos.push(resultVideoRef.value);
  }

  // 重置所有视频到开始位置并暂停
  videos.forEach((video) => {
    video.pause();
    video.currentTime = 0;
  });

  isVideoPlaying.value = false;
};

// 放大
const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.2, 5);
};

// 缩小
const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.2, 0.5);
};

// 重置缩放
const resetZoom = () => {
  scale.value = 1;
  position.value = { x: 0, y: 0 };
};

// 鼠标滚轮缩放
const onWheel = (event) => {
  const delta = event.deltaY > 0 ? -0.1 : 0.1;
  scale.value = Math.max(0.5, Math.min(5, scale.value + delta));
};

// 开始拖动
const startDrag = (event) => {
  isDragging.value = true;
  dragStart.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y,
  };
};

// 拖动中
const onDrag = (event) => {
  if (!isDragging.value) return;
  position.value = {
    x: event.clientX - dragStart.value.x,
    y: event.clientY - dragStart.value.y,
  };
};

// 结束拖动
const endDrag = () => {
  isDragging.value = false;
};

// 重新开始 - 显示确认弹窗
const resetAllStates = () => {
  showResetDialog.value = true;
};

// 确认重新开始
const confirmReset = () => {
  showResetDialog.value = false;
  stopRealtimeDetection();
  resetRealtimeState();
  clearWorkspaceNotice();

  // 重置本地状态
  clearSelectedFile();
  selectedWeightId.value = null;
  fileType.value = "image";
  detectionMode.value = "batch";

  // 重置store中的状态
  detectionStore.modelFile = null;
  detectionStore.modelUploaded = false;
  detectionStore.currentResult = null;
  if (originalVideoObjectUrl) {
    URL.revokeObjectURL(originalVideoObjectUrl);
    originalVideoObjectUrl = null;
  }
  detectionStore.detectionParams = {
    imgSize: 640,
    confidence: 0.5,
    iouThreshold: 0.6,
    maxDetections: 300,
    frameSkip: 1,
  };

  // 重置预览状态
  showPreview.value = false;
  resetZoom();

  // 重新加载权重列表
  loadUserWeights();

  // 返回到步骤1
  currentStep.value = 1;

  console.log("[INFO] 已重置所有状态，返回到步骤1");
};

// 取消重新开始
const cancelReset = () => {
  showResetDialog.value = false;
};

// 加载用户的权重列表
const loadUserWeights = async () => {
  loadingWeights.value = true;
  // 先清空旧数据，防止显示上一个用户的权重
  availableWeights.value = [];
  try {
    const token = (await supabase.auth.getSession()).data.session?.access_token;
    if (!token) return;

    const response = await fetch(`${API_URL}/api/model-weights`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      availableWeights.value = data.weights || [];

      // 不自动选择权重，用户需要主动点击选择
    }
  } catch (error) {
    console.error("加载权重列表失败:", error);
  } finally {
    loadingWeights.value = false;
  }
};

// 选择已有权重
const selectExistingWeight = async (weight) => {
  isSelectingWeight.value = true;
  clearWorkspaceNotice();
  try {
    const token = (await supabase.auth.getSession()).data.session?.access_token;
    if (!token) {
      showWorkspaceNotice("未登录，请重新登录", "error");
      return;
    }

    // 激活选中的权重
    const response = await fetch(
      `${API_URL}/api/model-weights/${weight.id}/activate`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    if (response.ok) {
      // 更新本地状态
      selectedWeightId.value = weight.id;
      detectionStore.modelUploaded = true;

      // 重新加载权重列表
      await loadUserWeights();
    } else {
      const errorData = await response.json();
      throw new Error(errorData.detail || "激活权重失败");
    }
  } catch (error) {
    console.error("选择权重失败:", error);
    showWorkspaceNotice(`选择权重失败：${error.message}`, "error");
  } finally {
    isSelectingWeight.value = false;
  }
};

// 监听步骤变化，设置滑动方向
watch(currentStep, (newStep, oldStep) => {
  previousStep.value = oldStep;
  // 向前切换（步骤增大）使用 slide-left，向后切换（步骤减小）使用 slide-right
  slideDirection.value = newStep > oldStep ? "slide-left" : "slide-right";
});

// 监听用户变化，自动重新加载权重列表
watch(
  () => authStore.user,
  (newUser, oldUser) => {
    if (newUser?.id !== oldUser?.id) {
      console.log("👤 用户已切换，清空Dashboard旧权重列表");
      availableWeights.value = [];
      if (newUser) {
        loadUserWeights();
      }
    }
  },
);

watch(fileType, (newType) => {
  if (newType === "video") {
    detectionMode.value = "realtime";
    return;
  }
  detectionMode.value = "batch";
});

onMounted(() => {
  detectionStore.loadHistory();
  loadUserWeights();
});

onBeforeUnmount(() => {
  stopRealtimeDetection();
  if (originalVideoObjectUrl) {
    URL.revokeObjectURL(originalVideoObjectUrl);
    originalVideoObjectUrl = null;
  }
});
</script>

<style scoped>
/* 向前切换动画（步骤增大，如1→2→3→4）：旧内容向上滑出，新内容从下方滑入 */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateY(80px);
}

.slide-left-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.slide-left-leave-from {
  opacity: 1;
  transform: translateY(0);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateY(-80px);
}

/* 向后切换动画（步骤减小，如4→3→2→1）：旧内容向下滑出，新内容从上方滑入 */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateY(-80px);
}

.slide-right-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.slide-right-leave-from {
  opacity: 1;
  transform: translateY(0);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateY(80px);
}

/* 确保绝对定位的元素不影响布局 */
.card.absolute {
  position: absolute;
  top: 0;
  left: 0;
}
</style>
