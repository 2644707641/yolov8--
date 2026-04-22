<template>
  <div class="space-y-8">
    <div
      class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"
    >
      <div>
        <p class="section-title">实时监控</p>
        <h1
          data-testid="realtime-title"
          class="mt-3 text-2xl font-semibold text-white"
        >
          实时监控
        </h1>
        <p class="mt-2 text-sm text-slate-300/80">
          接入实时视频流，观察车位占用变化与识别结果。
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <button
          data-testid="realtime-connect"
          class="btn-secondary text-sm"
          :disabled="isConnecting"
          @click="isConnected ? disconnectRealtime() : connectRealtime()"
        >
          {{
            isConnecting ? "连接中…" : isConnected ? "关闭实时流" : "连接实时流"
          }}
        </button>
        <button
          class="btn-primary text-sm"
          :disabled="!isConnected || isRunning"
          @click="startDetection"
        >
          {{ isRunning ? "识别中…" : "开启识别" }}
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

    <div
      v-if="errorMessage"
      class="rounded-2xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-100"
    >
      {{ errorMessage }}
    </div>

    <div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(280px,0.9fr)]">
      <div class="rounded-3xl border border-white/10 bg-white/[0.04] p-5">
        <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
          视频源
        </p>
        <div class="mt-4 grid gap-3 sm:grid-cols-2">
          <label
            class="flex cursor-pointer items-center gap-3 rounded-2xl border border-white/10 bg-slate-950/30 px-4 py-3 text-sm text-slate-200"
          >
            <input
              v-model="sourceMode"
              type="radio"
              value="camera"
              name="realtime-source"
            />
            本机摄像头
          </label>
          <label
            class="flex cursor-pointer items-center gap-3 rounded-2xl border border-white/10 bg-slate-950/30 px-4 py-3 text-sm text-slate-200"
          >
            <input
              v-model="sourceMode"
              data-testid="realtime-source-network"
              type="radio"
              value="network"
              name="realtime-source"
            />
            无线手机流
          </label>
        </div>
      </div>

      <div class="rounded-3xl border border-white/10 bg-white/[0.04] p-5">
        <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
          无线流地址
        </p>
        <input
          v-model.trim="networkStreamUrl"
          data-testid="realtime-network-url"
          type="text"
          class="mt-4 w-full rounded-2xl border border-white/10 bg-slate-950/30 px-4 py-3 text-sm text-white outline-none transition focus:border-primary-400/60"
          placeholder="rtsp://192.168.1.8:8554/live 或 http://192.168.1.8:8080/video"
        />
        <p class="mt-2 text-xs text-slate-400">
          适用于手机投屏 App 输出的 RTSP 或 MJPEG/HTTP(S)
          地址。使用本机摄像头时可留空。
        </p>
      </div>
    </div>

    <div class="space-y-6">
      <!-- 实时画面预览（全宽，置于摘要上方） -->
      <div
        class="card card--no-glow card--no-blur"
        data-testid="realtime-preview-card"
      >
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-white">实时画面预览</h2>
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-400">{{ statusLabel }}</span>
            <button
              class="flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300 transition hover:bg-white/10 hover:text-white"
              title="全屏放大对比"
              @click="showCompareModal = true"
            >
              <svg
                class="h-3.5 w-3.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
                />
              </svg>
              全屏对比
            </button>
          </div>
        </div>
        <p class="mt-2 text-xs text-slate-500">滚轮缩放 · 拖拽平移</p>
        <div class="mt-4 grid gap-4 lg:grid-cols-2">
          <!-- 左面板：原始输入 -->
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p
              class="mb-3 text-xs font-medium uppercase tracking-[0.25em] text-slate-400/80"
            >
              {{ sourceLabel }}
            </p>
            <div
              :ref="
                (el) => {
                  leftPZ.containerRef.value = el;
                }
              "
              class="relative h-72 overflow-hidden rounded-2xl border border-dashed border-white/15 bg-slate-900/40"
              :class="leftPZ.cursorClass.value"
              @mousedown="leftPZ.onMousedown"
              @mousemove="leftPZ.onMousemove"
              @mouseup="leftPZ.stopDrag"
              @mouseleave="leftPZ.stopDrag"
            >
              <!-- 缩放倍率角标 -->
              <transition name="fade-badge">
                <span
                  v-if="leftPZ.zoomLabel.value"
                  class="pointer-events-none absolute right-2 top-2 z-10 rounded-md bg-black/60 px-1.5 py-0.5 text-xs tabular-nums text-white/80 backdrop-blur-sm"
                >
                  {{ leftPZ.zoomLabel.value }}
                </span>
              </transition>
              <!-- 可变换内容层 -->
              <div class="h-full w-full" :style="leftPZ.transformStyle.value">
                <video
                  v-if="isCameraSource"
                  ref="videoRef"
                  class="h-full w-full object-cover -scale-x-100"
                  autoplay
                  muted
                  playsinline
                ></video>
                <img
                  v-else-if="previewUrl"
                  data-testid="realtime-network-preview"
                  :src="previewUrl"
                  class="h-full w-full object-cover"
                  alt="无线流预览"
                />
                <div
                  v-else
                  class="flex h-full w-full items-center justify-center px-6 text-center"
                >
                  <p class="text-sm text-slate-400">
                    连接后将在此显示无线流实时画面
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- 右面板：识别输出 -->
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p
              class="mb-3 text-xs font-medium uppercase tracking-[0.25em] text-slate-400/80"
            >
              识别输出
            </p>
            <div
              :ref="
                (el) => {
                  rightPZ.containerRef.value = el;
                }
              "
              class="relative h-72 overflow-hidden rounded-2xl border border-dashed border-white/15 bg-slate-900/40"
              :class="rightPZ.cursorClass.value"
              @mousedown="rightPZ.onMousedown"
              @mousemove="rightPZ.onMousemove"
              @mouseup="rightPZ.stopDrag"
              @mouseleave="rightPZ.stopDrag"
            >
              <transition name="fade-badge">
                <span
                  v-if="rightPZ.zoomLabel.value"
                  class="pointer-events-none absolute right-2 top-2 z-10 rounded-md bg-black/60 px-1.5 py-0.5 text-xs tabular-nums text-white/80 backdrop-blur-sm"
                >
                  {{ rightPZ.zoomLabel.value }}
                </span>
              </transition>
              <div class="h-full w-full" :style="rightPZ.transformStyle.value">
                <img
                  v-if="previewUrl"
                  :src="previewUrl"
                  class="h-full w-full object-cover"
                  alt="识别结果"
                />
                <span
                  v-else
                  class="flex h-full w-full items-center justify-center text-sm text-slate-400"
                >
                  等待识别结果
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 全屏放大对比模态框 -->
      <Teleport to="body">
        <Transition name="modal-fade">
          <div
            v-if="showCompareModal"
            class="fixed inset-0 z-[200] flex flex-col bg-black/95 backdrop-blur-sm"
            @click.self="showCompareModal = false"
          >
            <!-- 弹窗顶栏 -->
            <div
              class="flex shrink-0 items-center justify-between border-b border-white/10 px-6 py-4"
            >
              <div class="flex items-center gap-3">
                <svg
                  class="h-5 w-5 text-primary-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.5"
                    d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
                  />
                </svg>
                <h3 class="text-lg font-semibold text-white">放大对比</h3>
                <span
                  class="rounded-full bg-slate-700/50 px-2 py-0.5 text-xs text-slate-400"
                >
                  {{ statusLabel }}
                </span>
              </div>
              <div class="flex items-center gap-3">
                <span class="hidden text-xs text-slate-500 sm:inline">
                  滚轮缩放 · 拖拽平移 · 双面板独立操作
                </span>
                <button
                  class="flex h-8 w-8 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-300 transition hover:bg-white/10 hover:text-white"
                  title="关闭 (ESC)"
                  @click="showCompareModal = false"
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

            <!-- 对比面板区域 -->
            <div class="flex min-h-0 flex-1 gap-4 p-6">
              <!-- 左侧：原始输入 -->
              <div
                class="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03]"
              >
                <div class="shrink-0 border-b border-white/10 px-4 py-2.5">
                  <p
                    class="text-xs font-medium uppercase tracking-[0.25em] text-slate-400/80"
                  >
                    {{ sourceLabel }}
                  </p>
                </div>
                <div
                  :ref="
                    (el) => {
                      modalLeftPZ.containerRef.value = el;
                    }
                  "
                  class="relative min-h-0 flex-1 overflow-hidden bg-slate-950/60"
                  :class="modalLeftPZ.cursorClass.value"
                  @mousedown="modalLeftPZ.onMousedown"
                  @mousemove="modalLeftPZ.onMousemove"
                  @mouseup="modalLeftPZ.stopDrag"
                  @mouseleave="modalLeftPZ.stopDrag"
                >
                  <transition name="fade-badge">
                    <span
                      v-if="modalLeftPZ.zoomLabel.value"
                      class="pointer-events-none absolute right-2 top-2 z-10 rounded-md bg-black/60 px-1.5 py-0.5 text-xs tabular-nums text-white/80 backdrop-blur-sm"
                    >
                      {{ modalLeftPZ.zoomLabel.value }}
                    </span>
                  </transition>
                  <div
                    class="h-full w-full"
                    :style="modalLeftPZ.transformStyle.value"
                  >
                    <video
                      v-if="isCameraSource"
                      ref="modalVideoRef"
                      class="h-full w-full object-cover -scale-x-100"
                      autoplay
                      muted
                      playsinline
                    ></video>
                    <img
                      v-else-if="previewUrl"
                      :src="previewUrl"
                      class="h-full w-full object-cover"
                      alt="无线流预览"
                    />
                    <div
                      v-else
                      class="flex h-full w-full flex-col items-center justify-center gap-3 text-slate-500"
                    >
                      <svg
                        class="h-10 w-10 opacity-40"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="1.5"
                          d="M15 10l4.553-2.069A1 1 0 0121 8.869v6.262a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z"
                        />
                      </svg>
                      <p class="text-sm">等待视频源连接…</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 右侧：识别输出 -->
              <div
                class="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03]"
              >
                <div class="shrink-0 border-b border-white/10 px-4 py-2.5">
                  <p
                    class="text-xs font-medium uppercase tracking-[0.25em] text-slate-400/80"
                  >
                    识别输出
                  </p>
                </div>
                <div
                  :ref="
                    (el) => {
                      modalRightPZ.containerRef.value = el;
                    }
                  "
                  class="relative min-h-0 flex-1 overflow-hidden bg-slate-950/60"
                  :class="modalRightPZ.cursorClass.value"
                  @mousedown="modalRightPZ.onMousedown"
                  @mousemove="modalRightPZ.onMousemove"
                  @mouseup="modalRightPZ.stopDrag"
                  @mouseleave="modalRightPZ.stopDrag"
                >
                  <transition name="fade-badge">
                    <span
                      v-if="modalRightPZ.zoomLabel.value"
                      class="pointer-events-none absolute right-2 top-2 z-10 rounded-md bg-black/60 px-1.5 py-0.5 text-xs tabular-nums text-white/80 backdrop-blur-sm"
                    >
                      {{ modalRightPZ.zoomLabel.value }}
                    </span>
                  </transition>
                  <div
                    class="h-full w-full"
                    :style="modalRightPZ.transformStyle.value"
                  >
                    <img
                      v-if="previewUrl"
                      :src="previewUrl"
                      class="h-full w-full object-cover"
                      alt="识别结果"
                    />
                    <div
                      v-else
                      class="flex h-full w-full flex-col items-center justify-center gap-3 text-slate-500"
                    >
                      <svg
                        class="h-10 w-10 opacity-40"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="1.5"
                          d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                        />
                      </svg>
                      <p class="text-sm">等待识别结果…</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 底部提示栏 -->
            <div
              class="shrink-0 border-t border-white/10 px-6 py-3 text-center"
            >
              <p class="text-xs text-slate-500">
                按
                <kbd
                  class="rounded border border-white/20 bg-white/10 px-1.5 py-0.5 text-slate-300"
                  >ESC</kbd
                >
                或点击空白处关闭 &nbsp;·&nbsp; 双面板可独立滚轮缩放与拖拽平移
              </p>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- 识别摘要（全宽，横向统计卡片） -->
      <div
        class="card card--no-glow card--no-blur"
        data-testid="realtime-summary-card"
      >
        <h2 class="text-xl font-semibold text-white">识别摘要</h2>
        <div
          class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7"
        >
          <div
            class="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-center"
          >
            <p class="text-xs text-slate-400/80">当前帧耗时</p>
            <p class="mt-2 text-xl font-semibold text-white">
              {{ metrics.inferTime.toFixed(2) }}s
            </p>
          </div>
          <div
            class="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-center"
          >
            <p class="text-xs text-slate-400/80">当前检测数</p>
            <p class="mt-2 text-xl font-semibold text-white">
              {{ metrics.detectionCount }}
            </p>
          </div>
          <div
            class="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-center"
          >
            <p class="text-xs text-slate-400/80">累计检测数</p>
            <p class="mt-2 text-xl font-semibold text-white">
              {{ metrics.totalDetections }}
            </p>
          </div>
          <div
            class="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-center"
          >
            <p class="text-xs text-slate-400/80">估计目标</p>
            <p class="mt-2 text-xl font-semibold text-emerald-300">
              {{ metrics.uniqueTargetCount }}
            </p>
          </div>
          <div
            class="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-center"
          >
            <p class="text-xs text-slate-400/80">处理帧数</p>
            <p class="mt-2 text-xl font-semibold text-white">
              {{ metrics.processedFrames }}
            </p>
          </div>
          <div
            class="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-center"
          >
            <p class="text-xs text-slate-400/80">平均置信度</p>
            <p
              class="mt-2 text-xl font-semibold"
              :class="
                metrics.avgConfidence >= 0.8
                  ? 'text-emerald-300'
                  : metrics.avgConfidence >= 0.5
                    ? 'text-amber-300'
                    : 'text-white'
              "
            >
              {{
                metrics.avgConfidence > 0
                  ? (metrics.avgConfidence * 100).toFixed(1) + "%"
                  : "—"
              }}
            </p>
          </div>
          <div
            class="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-center"
          >
            <p class="text-xs text-slate-400/80">错帧率</p>
            <p
              class="mt-2 text-xl font-semibold"
              :class="
                metrics.frameErrors === 0
                  ? 'text-white'
                  : metrics.frameErrors <= 3
                    ? 'text-amber-300'
                    : 'text-red-400'
              "
            >
              {{ dropRate }}
            </p>
          </div>
        </div>
        <!-- 推理置信度阈值 -->
        <div class="mt-5 space-y-2 border-t border-white/10 pt-5">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-sm text-slate-300/80">推理置信度阈值</span>
              <span
                v-if="isRunning"
                class="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[11px] font-medium text-emerald-400"
                >实时生效</span
              >
              <span
                v-else
                class="rounded-full bg-slate-500/20 px-2 py-0.5 text-[11px] text-slate-400"
                >下次生效</span
              >
            </div>
            <span
              class="text-base font-semibold tabular-nums"
              :class="
                displayConfidence >= 0.8
                  ? 'text-emerald-300'
                  : displayConfidence >= 0.5
                    ? 'text-amber-300'
                    : 'text-red-400'
              "
              >{{ (displayConfidence * 100).toFixed(0) }}%</span
            >
          </div>
          <input
            v-model.number="displayConfidence"
            type="range"
            min="0.05"
            max="0.95"
            step="0.05"
            class="w-full cursor-pointer accent-indigo-400"
          />
          <div class="flex justify-between text-[10px] text-slate-500">
            <span>5% 低</span>
            <span>50%</span>
            <span>高 95%</span>
          </div>
        </div>

        <!-- 录制设置 -->
        <div
          class="mt-4 flex flex-wrap items-center gap-x-8 gap-y-3 border-t border-white/10 pt-4"
        >
          <label
            class="flex cursor-pointer items-center gap-2 text-sm text-slate-300/80"
          >
            <input v-model="recordEnabled" type="checkbox" class="h-4 w-4" />
            录制结果视频
          </label>
          <label class="flex items-center gap-2 text-sm text-slate-300/80">
            录制帧率
            <input
              v-model.number="recordFps"
              data-testid="realtime-fps"
              type="number"
              min="1"
              step="1"
              class="w-20 rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-right text-sm text-white"
            />
          </label>
          <label class="flex items-center gap-2 text-sm text-slate-300/80">
            录制时长（秒）
            <input
              v-model.number="recordDurationSeconds"
              data-testid="realtime-duration"
              type="number"
              min="0"
              step="1"
              class="w-20 rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-right text-sm text-white"
            />
          </label>
          <p class="text-xs text-slate-500">填写 0 表示不限时。</p>
        </div>
        <a
          v-if="downloadUrl"
          :href="downloadUrl"
          class="mt-5 inline-flex w-full items-center justify-center rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-100 transition hover:bg-white/10"
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
          <div
            class="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary-500/15 text-primary-200"
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
                d="M4 12h16M12 4v16"
              ></path>
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
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import { supabase } from "../config/supabase";
import { useDetectionStore } from "../stores/detection";
import {
  createLatestFrameScheduler,
  getRealtimeCaptureSize,
} from "../utils/realtime-frame";
import { buildProtectedApiUrl } from "../utils/protected-url";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const detectionStore = useDetectionStore();
const LIVE_PREVIEW_RENDER_INTERVAL_MS = 100;
const LIVE_CAPTURE_INTERVAL_MS = 33;

// ── usePanZoom：鼠标滚轮缩放 + 拖拽平移 ──────────────────────────────
function usePanZoom(options = {}) {
  const containerRef = ref(null);
  const zoom = ref(1);
  const tx = ref(0);
  const ty = ref(0);
  const isDragging = ref(false);
  let _sx = 0,
    _sy = 0,
    _stx = 0,
    _sty = 0;

  const clamp = () => {
    if (!containerRef.value) return;
    if (zoom.value <= 1) {
      tx.value = 0;
      ty.value = 0;
      return;
    }
    const W = containerRef.value.clientWidth;
    const H = containerRef.value.clientHeight;
    tx.value = Math.max(W * (1 - zoom.value), Math.min(0, tx.value));
    ty.value = Math.max(H * (1 - zoom.value), Math.min(0, ty.value));
  };

  const getPanRatio = () => {
    if (!containerRef.value || zoom.value <= 1) {
      return { x: 0, y: 0 };
    }
    const W = containerRef.value.clientWidth;
    const H = containerRef.value.clientHeight;
    const maxOffsetX = Math.max(0, W * (zoom.value - 1));
    const maxOffsetY = Math.max(0, H * (zoom.value - 1));
    return {
      x: maxOffsetX > 0 ? Math.max(0, Math.min(1, -tx.value / maxOffsetX)) : 0,
      y: maxOffsetY > 0 ? Math.max(0, Math.min(1, -ty.value / maxOffsetY)) : 0,
    };
  };

  const applyPanRatio = (ratio = null, { sync = true } = {}) => {
    if (!containerRef.value || zoom.value <= 1) {
      tx.value = 0;
      ty.value = 0;
      if (sync) {
        options.onPanChange?.({ ratio: { x: 0, y: 0 } });
      }
      return;
    }

    const nextRatioX = Math.max(0, Math.min(1, Number(ratio?.x) || 0));
    const nextRatioY = Math.max(0, Math.min(1, Number(ratio?.y) || 0));
    const W = containerRef.value.clientWidth;
    const H = containerRef.value.clientHeight;
    const maxOffsetX = Math.max(0, W * (zoom.value - 1));
    const maxOffsetY = Math.max(0, H * (zoom.value - 1));

    tx.value = -maxOffsetX * nextRatioX;
    ty.value = -maxOffsetY * nextRatioY;
    clamp();

    if (sync) {
      options.onPanChange?.({ ratio: getPanRatio() });
    }
  };

  const applyZoom = (nextZoom, anchor = null, { sync = true } = {}) => {
    const boundedZoom = Math.max(1, Math.min(8, nextZoom));
    if (boundedZoom === zoom.value) return;

    if (containerRef.value) {
      const rect = containerRef.value.getBoundingClientRect();
      const cx = rect.width * (anchor?.x ?? 0.5);
      const cy = rect.height * (anchor?.y ?? 0.5);
      const ratio = boundedZoom / zoom.value;
      tx.value = cx * (1 - ratio) + tx.value * ratio;
      ty.value = cy * (1 - ratio) + ty.value * ratio;
    }

    zoom.value = boundedZoom;
    clamp();

    if (sync) {
      options.onZoomChange?.({ zoom: boundedZoom, anchor });
    }
  };

  const _onWheel = (e) => {
    e.preventDefault();
    if (!containerRef.value) return;
    const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    const rect = containerRef.value.getBoundingClientRect();
    applyZoom(zoom.value * factor, {
      x: Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height)),
    });
  };

  // containerRef 变化时自动注册/注销 wheel 监听（passive:false 才能 preventDefault）
  watch(containerRef, (el, oldEl) => {
    oldEl?.removeEventListener("wheel", _onWheel);
    el?.addEventListener("wheel", _onWheel, { passive: false });
  });

  onBeforeUnmount(() => {
    containerRef.value?.removeEventListener("wheel", _onWheel);
  });

  const onMousedown = (e) => {
    if (zoom.value <= 1) return;
    e.preventDefault();
    isDragging.value = true;
    _sx = e.clientX;
    _sy = e.clientY;
    _stx = tx.value;
    _sty = ty.value;
  };

  const onMousemove = (e) => {
    if (!isDragging.value) return;
    tx.value = _stx + (e.clientX - _sx);
    ty.value = _sty + (e.clientY - _sy);
    clamp();
    options.onPanChange?.({ ratio: getPanRatio() });
  };

  const stopDrag = () => {
    isDragging.value = false;
  };

  const reset = () => {
    zoom.value = 1;
    tx.value = 0;
    ty.value = 0;
    isDragging.value = false;
  };

  const transformStyle = computed(() => ({
    transform: `translate(${tx.value}px, ${ty.value}px) scale(${zoom.value})`,
    transformOrigin: "0 0",
    userSelect: "none",
    willChange: "transform",
  }));

  const cursorClass = computed(() => {
    if (isDragging.value) return "cursor-grabbing";
    if (zoom.value > 1) return "cursor-grab";
    return "cursor-zoom-in";
  });

  const zoomLabel = computed(() =>
    zoom.value > 1.02 ? zoom.value.toFixed(1) + "x" : null,
  );

  return {
    containerRef,
    applyPanRatio,
    applyZoom,
    zoom,
    transformStyle,
    cursorClass,
    zoomLabel,
    isDragging,
    onMousedown,
    onMousemove,
    stopDrag,
    reset,
  };
}

const leftPZ = usePanZoom();
const rightPZ = usePanZoom();
const modalLeftPZ = usePanZoom({
  onZoomChange: ({ zoom, anchor }) => {
    modalRightPZ.applyZoom(zoom, anchor, { sync: false });
  },
  onPanChange: ({ ratio }) => {
    modalRightPZ.applyPanRatio(ratio, { sync: false });
  },
});
const modalRightPZ = usePanZoom({
  onZoomChange: ({ zoom, anchor }) => {
    modalLeftPZ.applyZoom(zoom, anchor, { sync: false });
  },
  onPanChange: ({ ratio }) => {
    modalLeftPZ.applyPanRatio(ratio, { sync: false });
  },
});
// ─────────────────────────────────────────────────────────────────────

const videoRef = ref(null);
const modalVideoRef = ref(null);
const showCompareModal = ref(false);
const previewUrl = ref("");
const errorMessage = ref("");
const connectionState = ref("idle");
const recordEnabled = computed({
  get: () => detectionStore.realtimePrefs.recordEnabled,
  set: (value) => detectionStore.updateRealtimePrefs({ recordEnabled: value }),
});
const recordFps = computed({
  get: () => detectionStore.realtimePrefs.recordFps,
  set: (value) => detectionStore.updateRealtimePrefs({ recordFps: value }),
});
const recordDurationSeconds = computed({
  get: () => detectionStore.realtimePrefs.recordDurationSeconds,
  set: (value) =>
    detectionStore.updateRealtimePrefs({ recordDurationSeconds: value }),
});
const activeSourceMode = ref(null);
const activeNetworkUrl = ref(null);

const sourceMode = computed({
  get: () => activeSourceMode.value ?? detectionStore.realtimePrefs.sourceMode,
  set: (value) => {
    activeSourceMode.value = value;
  },
});
const networkStreamUrl = computed({
  get: () => activeNetworkUrl.value ?? detectionStore.realtimePrefs.networkStreamUrl,
  set: (value) => {
    activeNetworkUrl.value = value;
  },
});

watch(
  () => detectionStore.realtimePrefs.sourceMode,
  () => {
    activeSourceMode.value = null;
    activeNetworkUrl.value = null;
  },
);

// 推理置信度阈值：读写 detectionStore，变化时实时推送给后端
const displayConfidence = computed({
  get: () => detectionStore.detectionParams.confidence,
  set: (value) => {
    detectionStore.updateDefaults({ confidence: value });
  },
});

const downloadUrl = ref("");
const pendingStart = ref(false);

const createEmptyMetrics = () => ({
  processedFrames: 0,
  detectionCount: 0,
  inferTime: 0,
  totalDetections: 0,
  uniqueTargetCount: 0,
  avgConfidence: 0,
  frameErrors: 0,
});
const metrics = ref(createEmptyMetrics());

const dropRate = computed(() => {
  const total = metrics.value.processedFrames + metrics.value.frameErrors;
  if (total === 0) return "—";
  return ((metrics.value.frameErrors / total) * 100).toFixed(1) + "%";
});

const isConnecting = computed(() => connectionState.value === "connecting");
const isConnected = computed(() =>
  ["ready", "running"].includes(connectionState.value),
);
const isRunning = computed(() => connectionState.value === "running");
const isCameraSource = computed(() => sourceMode.value !== "network");
const sourceLabel = computed(() =>
  isCameraSource.value ? "原始输入" : "无线流输入",
);
const statusLabel = computed(() => {
  if (connectionState.value === "connecting") return "正在连接";
  if (connectionState.value === "ready") return "连接就绪";
  if (connectionState.value === "running") return "识别中";
  return "等待连接";
});

const events = ref([
  {
    title: "等待视频源",
    desc: "尚未检测到实时推流，请先配置摄像头或无线手机流。",
    time: "刚刚",
  },
  {
    title: "推理引擎待命",
    desc: "模型加载完成后会自动开始识别。",
    time: "2 分钟前",
  },
  {
    title: "系统监控已启用",
    desc: "实时状态同步中，准备记录事件。",
    time: "5 分钟前",
  },
]);

let socket = null;
let stream = null;
let captureTimer = null;
let captureCanvas = null;
let lastPreviewUrl = "";
let recordTimer = null;
let isDisposed = false;
let sendingFrame = false;
let awaitingFrameResult = false;
let pendingFrameRequest = false;
let frameRenderScheduler = null;
const socketHandlers = {
  open: null,
  message: null,
  close: null,
  error: null,
};

const buildWsUrl = (token) => {
  if (API_URL.startsWith("https://")) {
    return (
      API_URL.replace("https://", "wss://") + `/ws/detect-live?token=${token}`
    );
  }
  if (API_URL.startsWith("http://")) {
    return (
      API_URL.replace("http://", "ws://") + `/ws/detect-live?token=${token}`
    );
  }
  return `ws://${API_URL}/ws/detect-live?token=${token}`;
};

const getAuthToken = async () => {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error("未登录或会话已失效");
  }
  return session.access_token;
};

const startCamera = async () => {
  if (stream) return;
  stream = await navigator.mediaDevices.getUserMedia({
    video: true,
    audio: false,
  });
  if (videoRef.value) {
    videoRef.value.srcObject = stream;
    await videoRef.value.play();
  }
};

const stopCamera = () => {
  if (!stream) return;
  stream.getTracks().forEach((track) => track.stop());
  if (videoRef.value) {
    videoRef.value.srcObject = null;
  }
  stream = null;
};

const detachSocketListeners = () => {
  if (!socket) return;
  if (socketHandlers.open)
    socket.removeEventListener("open", socketHandlers.open);
  if (socketHandlers.message)
    socket.removeEventListener("message", socketHandlers.message);
  if (socketHandlers.close)
    socket.removeEventListener("close", socketHandlers.close);
  if (socketHandlers.error)
    socket.removeEventListener("error", socketHandlers.error);
  socketHandlers.open = null;
  socketHandlers.message = null;
  socketHandlers.close = null;
  socketHandlers.error = null;
};

const resetRealtimeView = () => {
  stopCapture();
  clearRecordTimer();
  stopCamera();
  frameRenderScheduler?.dispose();
  frameRenderScheduler = null;
  if (lastPreviewUrl) {
    URL.revokeObjectURL(lastPreviewUrl);
    lastPreviewUrl = "";
  }
  previewUrl.value = "";
  Object.assign(metrics.value, createEmptyMetrics());
  connectionState.value = "idle";
};

const closeSocketConnection = () => {
  if (!socket) return;
  detachSocketListeners();
  try {
    socket.close();
  } catch (error) {
    console.warn("关闭实时连接失败:", error);
  }
  socket = null;
};

const disconnectRealtime = () => {
  pendingStart.value = false;
  closeSocketConnection();
  resetRealtimeView();
};

const cleanupRealtime = () => {
  if (isDisposed) return;
  isDisposed = true;
  disconnectRealtime();
};

const connectRealtime = async () => {
  if (isConnecting.value || isConnected.value) return;
  errorMessage.value = "";
  connectionState.value = "connecting";
  downloadUrl.value = "";

  try {
    if (isCameraSource.value) {
      await startCamera();
    } else {
      stopCamera();
      if (!networkStreamUrl.value) {
        throw new Error("请输入无线手机流地址");
      }
    }
    const token = await getAuthToken();
    const wsUrl = buildWsUrl(token);
    socket = new WebSocket(wsUrl);
    socket.binaryType = "arraybuffer";

    socketHandlers.open = () => {
      if (isDisposed) return;
      if (!isCameraSource.value) {
        pendingStart.value = false;
        startDetection();
        return;
      }
      connectionState.value = "ready";
      if (pendingStart.value) {
        pendingStart.value = false;
        startDetection();
      }
    };

    socketHandlers.message = (event) => {
      if (isDisposed) return;
      handleSocketMessage(event);
    };

    socketHandlers.close = () => {
      if (isDisposed) return;
      disconnectRealtime();
    };

    socketHandlers.error = () => {
      if (isDisposed) return;
      errorMessage.value = "实时连接失败，请检查服务状态";
      disconnectRealtime();
      connectionState.value = "error";
    };

    socket.addEventListener("open", socketHandlers.open);
    socket.addEventListener("message", socketHandlers.message);
    socket.addEventListener("close", socketHandlers.close);
    socket.addEventListener("error", socketHandlers.error);
  } catch (error) {
    errorMessage.value = error.message || "无法启动摄像头";
    connectionState.value = "error";
  }
};

const startDetection = async () => {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    pendingStart.value = true;
    await connectRealtime();
    return;
  }

  connectionState.value = "running";
  Object.assign(metrics.value, createEmptyMetrics());
  frameRenderScheduler?.dispose();
  frameRenderScheduler = createLatestFrameScheduler({
    commit: ({ blob, meta }) => {
      const nextPreviewUrl = URL.createObjectURL(blob);
      if (lastPreviewUrl) {
        URL.revokeObjectURL(lastPreviewUrl);
      }
      lastPreviewUrl = nextPreviewUrl;
      previewUrl.value = nextPreviewUrl;
      Object.assign(metrics.value, {
        processedFrames: meta.processedFrames || 0,
        detectionCount: meta.detectionCount || 0,
        inferTime: meta.inferTime || 0,
        totalDetections: meta.totalDetections || 0,
        uniqueTargetCount: meta.uniqueTargetCount || 0,
        avgConfidence: meta.avgConfidence || 0,
        frameErrors: meta.frameErrors || 0,
      });
      connectionState.value = "running";
    },
    minIntervalMs: LIVE_PREVIEW_RENDER_INTERVAL_MS,
  });

  socket.send(
    JSON.stringify({
      type: "start",
      params: detectionStore.detectionParams,
      source: isCameraSource.value
        ? { type: "camera" }
        : {
            type: "network",
            url: networkStreamUrl.value,
          },
      recording: {
        enabled: recordEnabled.value,
        fps: recordFps.value,
        durationSeconds: Number(recordDurationSeconds.value) || 0,
      },
    }),
  );

  if (isCameraSource.value) {
    startCapture();
  }
  scheduleRecordStop();
};

const stopDetection = () => {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  clearRecordTimer();
  socket.send(JSON.stringify({ type: "end" }));
  stopCapture();
};

// 实时将置信度阈值变更推送给后端
const sendConfidenceUpdate = (value) => {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({ type: "setConf", confidence: value }));
};

// 监听置信度变化：连接中则实时生效，否则下次识别时自动带入
watch(displayConfidence, (value) => {
  sendConfidenceUpdate(value);
});

const flushPendingFrame = () => {
  if (!pendingFrameRequest) return;
  if (sendingFrame || awaitingFrameResult) return;
  pendingFrameRequest = false;
  void sendFrame();
};

const requestFrameCapture = () => {
  if (isDisposed || !isCameraSource.value || !isRunning.value) return;
  pendingFrameRequest = true;
  flushPendingFrame();
};

const startCapture = () => {
  if (captureTimer) return;
  sendingFrame = false;
  awaitingFrameResult = false;
  pendingFrameRequest = false;
  captureCanvas = captureCanvas || document.createElement("canvas");
  captureTimer = window.setInterval(requestFrameCapture, LIVE_CAPTURE_INTERVAL_MS);
  requestFrameCapture();
};

const stopCapture = () => {
  if (captureTimer) {
    window.clearInterval(captureTimer);
    captureTimer = null;
  }
  pendingFrameRequest = false;
  sendingFrame = false;
  awaitingFrameResult = false;
};

const scheduleRecordStop = () => {
  clearRecordTimer();
  const seconds = Number(recordDurationSeconds.value);
  if (!Number.isFinite(seconds) || seconds <= 0) return;
  recordTimer = window.setTimeout(() => {
    recordTimer = null;
    stopDetection();
  }, seconds * 1000);
};

const clearRecordTimer = () => {
  if (recordTimer) {
    window.clearTimeout(recordTimer);
    recordTimer = null;
  }
};

const getCaptureInterval = () => {
  return LIVE_CAPTURE_INTERVAL_MS;
};

const sendFrame = async () => {
  if (isDisposed) return;
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  if (!isRunning.value || !isCameraSource.value) return;
  if (sendingFrame || awaitingFrameResult) return;
  const videoEl = videoRef.value;
  if (!videoEl || videoEl.readyState < 2) return;

  sendingFrame = true;
  try {
    const { width, height } = getRealtimeCaptureSize({
      width: videoEl.videoWidth || 640,
      height: videoEl.videoHeight || 360,
      targetLongEdge: detectionStore.detectionParams.imgSize,
    });
    captureCanvas.width = width;
    captureCanvas.height = height;

    const context = captureCanvas.getContext("2d");
    if (!context) return;
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = "high";
    // flip camera frame horizontally before upload
    context.save();
    context.clearRect(0, 0, width, height);
    context.translate(width, 0);
    context.scale(-1, 1);
    context.drawImage(videoEl, 0, 0, width, height);
    context.restore();

    const blob = await new Promise((resolve) =>
      captureCanvas.toBlob(resolve, "image/jpeg", 0.8),
    );

    if (!blob) return;
    const buffer = await blob.arrayBuffer();
    if (isDisposed || !socket || socket.readyState !== WebSocket.OPEN) return;
    socket.send(buffer);
    sendingFrame = false;
    awaitingFrameResult = true;
  } catch (error) {
    if (!isDisposed) {
      console.warn("发送实时帧失败:", error);
    }
    sendingFrame = false;
    awaitingFrameResult = false;
  }
};

const handleSocketMessage = async (event) => {
  if (isDisposed) return;
  try {
    if (typeof event.data === "string") {
      const payload = JSON.parse(event.data);
      if (payload.type === "ready") {
        if (connectionState.value !== "running") {
          connectionState.value = "ready";
        }
        return;
      }
      if (payload.type === "error") {
        awaitingFrameResult = false;
        errorMessage.value = payload.detail || "实时识别出错";
        connectionState.value = "error";
        return;
      }
      if (payload.type === "done") {
        frameRenderScheduler?.flush();
        connectionState.value = "ready";
        if (payload.downloadUrl) {
          downloadUrl.value = await buildProtectedApiUrl(payload.downloadUrl);
        }
        return;
      }
    }

    const buffer =
      event.data instanceof Blob ? await event.data.arrayBuffer() : event.data;
    if (!(buffer instanceof ArrayBuffer)) return;
    awaitingFrameResult = false;
    flushPendingFrame();
    if (buffer.byteLength < 4) return;

    const view = new DataView(buffer);
    const metaLength = view.getUint32(0);
    if (buffer.byteLength < 4 + metaLength) return;

    const metaBytes = new Uint8Array(buffer, 4, metaLength);
    const metaText = new TextDecoder("utf-8").decode(metaBytes);
    const meta = JSON.parse(metaText);
    const imageBytes = new Uint8Array(buffer, 4 + metaLength);

    frameRenderScheduler?.enqueue({
      blob: new Blob([imageBytes], { type: "image/jpeg" }),
      meta,
    });
  } catch (error) {
    console.warn("实时消息解析失败:", error);
  }
};

// 全屏对比弹窗：打开时将摄像头流接入 modalVideoRef
watch(showCompareModal, async (visible) => {
  if (visible) {
    modalLeftPZ.reset();
    modalRightPZ.reset();
    if (isCameraSource.value && stream) {
      await nextTick();
      if (modalVideoRef.value) {
        modalVideoRef.value.srcObject = stream;
        try {
          await modalVideoRef.value.play();
        } catch (_) {}
      }
    }
  }
});

const handleGlobalKeydown = (e) => {
  if (e.key === "Escape" && showCompareModal.value) {
    showCompareModal.value = false;
  }
};

onMounted(() => {
  document.addEventListener("keydown", handleGlobalKeydown);
  activeSourceMode.value = null;
  activeNetworkUrl.value = null;
  detectionStore.initRealtimeFromBackend();
});

onBeforeUnmount(() => {
  document.removeEventListener("keydown", handleGlobalKeydown);
  cleanupRealtime();
});
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.fade-badge-enter-active,
.fade-badge-leave-active {
  transition: opacity 0.15s ease;
}
.fade-badge-enter-from,
.fade-badge-leave-to {
  opacity: 0;
}
</style>
