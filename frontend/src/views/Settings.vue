<template>
  <div class="space-y-8">
    <div
      class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"
    >
      <div>
        <p class="section-title">系统设置</p>
        <h1
          data-testid="settings-title"
          class="mt-3 text-2xl font-semibold text-white"
        >
          系统设置
        </h1>
        <p class="mt-2 text-sm text-slate-300/80">
          管理账号信息、默认推理参数与存储策略。
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button
          class="btn-secondary text-sm"
          :disabled="loading || saving || cleaning"
          @click="loadSettings"
        >
          {{ loading ? "加载中…" : "重新加载" }}
        </button>
      </div>
    </div>

    <div
      v-if="error"
      class="rounded-2xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-100"
    >
      {{ error }}
    </div>
    <div
      v-if="success"
      class="rounded-2xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100"
    >
      配置已保存：推理参数与本地清理策略已同步到后端，实时偏好保存在本地浏览器。
    </div>

    <div
      data-testid="settings-overview-strip"
      class="grid gap-3 rounded-3xl border border-white/10 bg-white/[0.04] p-4 shadow-[0_18px_45px_rgba(6,11,30,0.22)] sm:grid-cols-2 xl:grid-cols-4"
    >
      <div class="rounded-2xl border border-white/10 bg-slate-950/35 px-4 py-3">
        <p class="text-[11px] uppercase tracking-[0.28em] text-slate-400/70">
          账号
        </p>
        <p class="mt-2 truncate text-sm font-medium text-white">
          {{ userEmail }}
        </p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-slate-950/35 px-4 py-3">
        <p class="text-[11px] uppercase tracking-[0.28em] text-slate-400/70">
          系统版本
        </p>
        <p class="mt-2 text-sm font-medium text-white">
          v{{ systemInfo.apiVersion }}
        </p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-slate-950/35 px-4 py-3">
        <p class="text-[11px] uppercase tracking-[0.28em] text-slate-400/70">
          默认模型
        </p>
        <p class="mt-2 truncate text-sm font-medium text-white">
          {{ systemInfo.defaultModelName }}
        </p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-slate-950/35 px-4 py-3">
        <p class="text-[11px] uppercase tracking-[0.28em] text-slate-400/70">
          同步范围
        </p>
        <p class="mt-2 text-sm font-medium text-white">后端参数 + 本地偏好</p>
      </div>
    </div>

    <div data-testid="settings-priority-stack" class="space-y-6">
      <div data-testid="settings-section-defaults" class="card">
        <div
          class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between"
        >
          <div>
            <h2 class="text-lg font-semibold text-white">默认推理参数</h2>
            <p class="mt-2 text-sm text-slate-300/80">
              用于新任务的默认检测配置，优先保证稳定性和资源利用率。
            </p>
          </div>
          <span class="text-xs text-slate-400">应用于新任务</span>
        </div>
        <div
          class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-[repeat(2,minmax(0,1fr))_220px]"
        >
          <label class="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              置信度
            </p>
            <input
              data-testid="setting-confidence"
              v-model.number="defaults.confidence"
              type="number"
              min="0"
              max="1"
              step="0.01"
              class="input-field mt-4"
            />
            <p class="mt-2 text-xs text-slate-400">低于阈值将被过滤</p>
          </label>
          <label class="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              IOU 阈值
            </p>
            <input
              data-testid="setting-iou"
              v-model.number="defaults.iouThreshold"
              type="number"
              min="0"
              max="1"
              step="0.01"
              class="input-field mt-4"
            />
            <p class="mt-2 text-xs text-slate-400">控制重复框合并</p>
          </label>
          <label
            class="rounded-2xl border border-white/10 bg-white/5 p-5 xl:row-span-2"
          >
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              帧间隔
            </p>
            <input
              data-testid="setting-frame-skip"
              v-model.number="defaults.frameSkip"
              type="number"
              min="1"
              step="1"
              class="input-field mt-4"
            />
            <p class="mt-2 text-xs text-slate-400">视频模式采样频率</p>
          </label>
          <label class="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              输入尺寸
            </p>
            <input
              data-testid="setting-img-size"
              v-model.number="defaults.imgSize"
              type="number"
              min="320"
              step="32"
              class="input-field mt-4"
            />
            <p class="mt-2 text-xs text-slate-400">默认推理分辨率</p>
          </label>
          <label class="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              最大目标数
            </p>
            <input
              data-testid="setting-max-detections"
              v-model.number="defaults.maxDetections"
              type="number"
              min="1"
              step="10"
              class="input-field mt-4"
            />
            <p class="mt-2 text-xs text-slate-400">单帧最多检测框</p>
          </label>
        </div>
      </div>

      <div data-testid="settings-section-storage" class="card">
        <div
          class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"
        >
          <div>
            <h2 class="text-lg font-semibold text-white">存储策略</h2>
            <p class="mt-2 text-sm text-slate-300/80">
              集中管理本地留存、备份和清理策略，避免历史数据持续膨胀。
            </p>
          </div>
          <button
            data-testid="settings-run-cleanup"
            class="btn-secondary text-sm"
            :disabled="loading || saving || cleaning"
            @click="runCleanupNow"
          >
            {{ cleaning ? "清理中…" : "立即清理一次" }}
          </button>
        </div>

        <div
          class="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]"
        >
          <div
            data-testid="settings-storage-config-card"
            class="rounded-2xl border border-white/10 bg-white/5 p-5"
          >
            <div class="grid gap-3 sm:grid-cols-2">
              <div
                class="rounded-2xl border border-white/10 bg-slate-950/30 p-4"
              >
                <p
                  class="text-xs uppercase tracking-[0.28em] text-slate-400/70"
                >
                  存储模式
                </p>
                <p class="mt-3 text-sm font-medium text-white">
                  {{ storageModeLabel }}
                </p>
              </div>
              <div
                class="rounded-2xl border border-white/10 bg-slate-950/30 p-4"
              >
                <p
                  class="text-xs uppercase tracking-[0.28em] text-slate-400/70"
                >
                  历史保留
                </p>
                <p class="mt-3 text-sm font-medium text-white">
                  {{ storagePolicy.retentionDays }} 天
                </p>
              </div>
              <div
                class="rounded-2xl border border-white/10 bg-slate-950/30 p-4"
              >
                <p
                  class="text-xs uppercase tracking-[0.28em] text-slate-400/70"
                >
                  备份频率
                </p>
                <p class="mt-3 text-sm font-medium text-white">
                  每天 {{ storagePolicy.backupTime }}
                </p>
              </div>
              <div
                class="rounded-2xl border border-white/10 bg-slate-950/30 p-4"
              >
                <p
                  class="text-xs uppercase tracking-[0.28em] text-slate-400/70"
                >
                  存储区域
                </p>
                <p class="mt-3 text-sm font-medium text-white">
                  {{ storagePolicy.region }}
                </p>
              </div>
            </div>

            <div
              class="mt-4 rounded-2xl border border-white/10 bg-slate-950/30 p-4"
            >
              <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">
                默认模型
              </p>
              <p class="mt-3 text-sm font-medium text-white">
                {{ systemInfo.defaultModelName }}
              </p>
            </div>

            <div
              class="mt-4 rounded-2xl border border-white/10 bg-slate-950/30 p-4"
            >
              <label
                class="flex items-center justify-between text-sm text-slate-300/80"
              >
                <span>本地自动清理</span>
                <input
                  data-testid="setting-local-cleanup-enabled"
                  v-model="storagePolicy.localCleanup.enabled"
                  :disabled="loading || saving"
                  type="checkbox"
                  class="h-4 w-4"
                />
              </label>
              <p class="mt-2 text-xs text-slate-400">
                关闭后将停止自动裁剪本地历史与孤立文件。
              </p>
            </div>

            <div class="mt-4 grid gap-4 sm:grid-cols-2">
              <div
                class="rounded-2xl border border-white/10 bg-slate-950/30 p-4"
              >
                <p class="text-sm text-white">本地保留天数</p>
                <p class="mt-2 text-xs text-slate-400">
                  超过这个天数的本地历史会被清理。
                </p>
                <div class="mt-4 flex items-center gap-2">
                  <input
                    data-testid="setting-local-cleanup-retention-days"
                    v-model.number="storagePolicy.localCleanup.retentionDays"
                    :disabled="loading || saving"
                    type="number"
                    min="1"
                    step="1"
                    class="input-field text-right"
                  />
                  <span class="text-sm text-white">天</span>
                </div>
              </div>
              <div
                class="rounded-2xl border border-white/10 bg-slate-950/30 p-4"
              >
                <p class="text-sm text-white">最大历史记录数</p>
                <p class="mt-2 text-xs text-slate-400">
                  超过上限后会优先裁剪较旧记录。
                </p>
                <div class="mt-4 flex items-center gap-2">
                  <input
                    data-testid="setting-local-cleanup-max-records"
                    v-model.number="storagePolicy.localCleanup.maxRecords"
                    :disabled="loading || saving"
                    type="number"
                    min="1"
                    step="1"
                    class="input-field text-right"
                  />
                  <span class="text-sm text-white">条</span>
                </div>
              </div>
            </div>

            <p class="mt-4 text-xs text-slate-500">
              当前状态：{{ localCleanupEnabledLabel }}，保留
              {{ storagePolicy.localCleanup.retentionDays }} 天，最多
              {{ storagePolicy.localCleanup.maxRecords }} 条。
            </p>
          </div>

          <div
            data-testid="settings-storage-status-card"
            class="rounded-2xl border border-white/10 bg-white/5 p-5"
          >
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="text-sm text-white">当前本地占用</p>
                <p class="mt-2 text-xs text-slate-400">
                  用于判断当前策略是否需要收紧。
                </p>
              </div>
              <div class="text-right">
                <p class="text-xs text-slate-400">总占用</p>
                <p class="mt-2 text-sm text-white">
                  {{ formatBytes(storagePolicy.localStats.totalBytes) }}
                </p>
              </div>
            </div>
            <div class="mt-4 space-y-3 text-sm text-slate-300/80">
              <div class="flex items-center justify-between gap-4">
                <span
                  >历史记录
                  {{ storagePolicy.localStats.historyRecordCount }} 条</span
                >
                <span class="text-white"
                  >归档记录
                  {{ storagePolicy.localStats.archiveRecordCount }} 条</span
                >
              </div>
              <div class="flex items-center justify-between gap-4">
                <span
                  >上传目录
                  {{ storagePolicy.localStats.uploadsFileCount }} 个文件</span
                >
                <span class="text-white">{{
                  formatBytes(storagePolicy.localStats.uploadsBytes)
                }}</span>
              </div>
              <div class="flex items-center justify-between gap-4">
                <span
                  >结果目录
                  {{ storagePolicy.localStats.resultsFileCount }} 个文件</span
                >
                <span class="text-white">{{
                  formatBytes(storagePolicy.localStats.resultsBytes)
                }}</span>
              </div>
              <div class="flex items-center justify-between gap-4">
                <span>上次清理</span>
                <span class="text-white">{{ lastCleanupAtLabel }}</span>
              </div>
            </div>

            <div
              v-if="cleanupMessage"
              class="mt-4 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-xs text-emerald-100"
            >
              {{ cleanupMessage }}
            </div>
          </div>
        </div>
      </div>

      <div data-testid="settings-section-realtime" class="card">
        <div
          class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between"
        >
          <div>
            <h2 class="text-lg font-semibold text-white">实时识别偏好</h2>
            <p class="mt-2 text-sm text-slate-300/80">
              这里的选项只影响实时监控页面，保存后会写入本地浏览器。
            </p>
          </div>
          <span class="text-xs text-slate-400">应用于实时监控</span>
        </div>
        <div class="mt-6 grid gap-4 md:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              录制开关
            </p>
            <label
              class="mt-4 flex items-center justify-between text-sm text-slate-300/80"
            >
              默认开启录制
              <input
                v-model="realtimePrefs.recordEnabled"
                type="checkbox"
                class="h-4 w-4"
              />
            </label>
            <p class="mt-2 text-xs text-slate-400">
              实时监控默认是否录制结果视频
            </p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              录制帧率
            </p>
            <input
              v-model.number="realtimePrefs.recordFps"
              type="number"
              min="1"
              step="1"
              class="input-field mt-4"
            />
            <p class="mt-2 text-xs text-slate-400">建议 4-12 帧以平衡性能</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              默认时长
            </p>
            <input
              v-model.number="realtimePrefs.recordDurationSeconds"
              type="number"
              min="0"
              step="1"
              class="input-field mt-4"
            />
            <p class="mt-2 text-xs text-slate-400">填写 0 表示不限时</p>
          </div>
        </div>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              默认视频源
            </p>
            <select v-model="realtimePrefs.sourceMode" class="input-field mt-4">
              <option value="camera">本机摄像头</option>
              <option value="network">无线手机流</option>
            </select>
            <p class="mt-2 text-xs text-slate-400">
              无线手机流适用于 RTSP 或 MJPEG/HTTP(S) 地址
            </p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">
              无线流地址
            </p>
            <input
              v-model.trim="realtimePrefs.networkStreamUrl"
              type="text"
              class="input-field mt-4"
              placeholder="rtsp://192.168.1.8:8554/live"
            />
            <p class="mt-2 text-xs text-slate-400">
              仅在默认视频源为无线手机流时生效
            </p>
          </div>
        </div>
      </div>

      <div data-testid="settings-section-system" class="card">
        <div
          class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between"
        >
          <div>
            <h2 class="text-lg font-semibold text-white">系统限制</h2>
            <p class="mt-2 text-sm text-slate-300/80">
              这一部分主要用于查看系统边界和同步规则，不建议频繁改动。
            </p>
          </div>
          <span class="text-xs text-slate-400">只读信息</span>
        </div>
        <div class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">
              最大上传
            </p>
            <p class="mt-3 text-sm font-medium text-white">
              {{ systemInfo.maxUploadSizeMb }} MB
            </p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">
              最大并发
            </p>
            <p class="mt-3 text-sm font-medium text-white">
              {{ systemInfo.maxConcurrentDetections ?? "未暴露" }}
            </p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">
              系统版本
            </p>
            <p class="mt-3 text-sm font-medium text-white">
              v{{ systemInfo.apiVersion }}
            </p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">
              接口名称
            </p>
            <p class="mt-3 text-sm font-medium text-white">
              {{ systemInfo.apiTitle }}
            </p>
          </div>
        </div>
        <div
          class="mt-4 rounded-2xl border border-dashed border-white/10 bg-slate-950/30 p-4 text-sm text-slate-300/80"
        >
          <p class="font-medium text-white">同步说明</p>
          <p class="mt-2 text-xs text-slate-400">
            默认推理参数与本地清理策略同步到后端，实时识别偏好仅保存在当前浏览器。
          </p>
        </div>
      </div>
    </div>

    <div
      data-testid="settings-bottom-actions"
      class="sticky bottom-0 z-20 -mx-6 border-t border-white/10 bg-slate-950/88 px-6 py-4 backdrop-blur-xl lg:-mx-10 lg:px-10"
    >
      <div
        class="mx-auto flex max-w-7xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <div class="text-sm text-slate-300/80">
          <p class="font-medium text-white">配置修改后需要手动保存</p>
          <p class="mt-1 text-xs text-slate-400">
            默认推理参数与本地清理策略会同步到后端，实时识别偏好保存在当前浏览器。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <button
            class="btn-secondary text-sm"
            :disabled="loading || saving || cleaning"
            @click="loadSettings"
          >
            {{ loading ? "加载中…" : "放弃修改并重载" }}
          </button>
          <button
            data-testid="settings-save"
            class="btn-primary text-sm"
            :disabled="loading || saving || cleaning"
            @click="saveSettings"
          >
            {{ saving ? "保存中…" : "保存配置" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useAuthStore } from "../stores/auth";
import { useDetectionStore } from "../stores/detection";
import { supabase } from "../config/supabase";

const authStore = useAuthStore();
const detectionStore = useDetectionStore();
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const defaults = ref({
  imgSize: 640,
  confidence: 0.5,
  iouThreshold: 0.6,
  maxDetections: 300,
  frameSkip: 1,
});

const systemInfo = ref({
  apiTitle: "YOLOv8 Detection API",
  apiVersion: "1.1.0",
  defaultModelName: "默认停车位检测模型",
  maxUploadSizeMb: 200,
  maxConcurrentDetections: null,
});

const storagePolicy = ref({
  retentionDays: 30,
  region: "CN-East-1",
  backupTime: "02:00",
  mode: "local",
  localCleanup: {
    enabled: true,
    retentionDays: 30,
    maxRecords: 500,
    lastRunAt: null,
    lastSummary: null,
  },
  localStats: {
    historyRecordCount: 0,
    archiveRecordCount: 0,
    uploadsFileCount: 0,
    uploadsBytes: 0,
    resultsFileCount: 0,
    resultsBytes: 0,
    totalBytes: 0,
    lastCleanupAt: null,
  },
});

const realtimePrefs = ref({
  recordEnabled: true,
  recordFps: 8,
  recordDurationSeconds: 0,
  sourceMode: "camera",
  networkStreamUrl: "",
});

const loading = ref(false);
const saving = ref(false);
const cleaning = ref(false);
const error = ref("");
const success = ref(false);
const cleanupMessage = ref("");

const userEmail = computed(() => authStore.user?.email || "未登录");
const storageModeLabel = computed(() =>
  storagePolicy.value.mode === "supabase" ? "云端模式" : "本地模式",
);
const localCleanupEnabledLabel = computed(() =>
  storagePolicy.value.localCleanup.enabled ? "已启用" : "未启用",
);
const lastCleanupAtLabel = computed(() =>
  storagePolicy.value.localStats.lastCleanupAt
    ? formatDateTime(storagePolicy.value.localStats.lastCleanupAt)
    : "尚未执行",
);

const getAuthToken = async () => {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error("未登录或会话已失效");
  }
  return session.access_token;
};

const normalizeDefaults = () => {
  defaults.value = {
    ...defaults.value,
    frameSkip: Math.max(1, Number(defaults.value.frameSkip || 1)),
    maxDetections: Math.max(1, Number(defaults.value.maxDetections || 1)),
  };
};

const normalizeRealtimePrefs = () => {
  realtimePrefs.value = {
    ...realtimePrefs.value,
    recordEnabled: Boolean(realtimePrefs.value.recordEnabled),
    recordFps: Math.max(1, Number(realtimePrefs.value.recordFps || 8)),
    recordDurationSeconds: Math.max(
      0,
      Number(realtimePrefs.value.recordDurationSeconds || 0),
    ),
    sourceMode:
      realtimePrefs.value.sourceMode === "network" ? "network" : "camera",
    networkStreamUrl: String(realtimePrefs.value.networkStreamUrl || "").trim(),
  };
};

const normalizeStoragePolicy = () => {
  storagePolicy.value = {
    ...storagePolicy.value,
    localCleanup: {
      ...storagePolicy.value.localCleanup,
      enabled: Boolean(storagePolicy.value.localCleanup.enabled),
      retentionDays: Math.max(
        1,
        Number(storagePolicy.value.localCleanup.retentionDays || 1),
      ),
      maxRecords: Math.max(
        1,
        Number(storagePolicy.value.localCleanup.maxRecords || 1),
      ),
      lastRunAt: storagePolicy.value.localCleanup.lastRunAt || null,
      lastSummary: storagePolicy.value.localCleanup.lastSummary || null,
    },
    localStats: {
      ...storagePolicy.value.localStats,
      historyRecordCount: Math.max(
        0,
        Number(storagePolicy.value.localStats.historyRecordCount || 0),
      ),
      archiveRecordCount: Math.max(
        0,
        Number(storagePolicy.value.localStats.archiveRecordCount || 0),
      ),
      uploadsFileCount: Math.max(
        0,
        Number(storagePolicy.value.localStats.uploadsFileCount || 0),
      ),
      uploadsBytes: Math.max(
        0,
        Number(storagePolicy.value.localStats.uploadsBytes || 0),
      ),
      resultsFileCount: Math.max(
        0,
        Number(storagePolicy.value.localStats.resultsFileCount || 0),
      ),
      resultsBytes: Math.max(
        0,
        Number(storagePolicy.value.localStats.resultsBytes || 0),
      ),
      totalBytes: Math.max(
        0,
        Number(storagePolicy.value.localStats.totalBytes || 0),
      ),
      lastCleanupAt: storagePolicy.value.localStats.lastCleanupAt || null,
    },
  };
};

const mergeStoragePolicy = (incomingStorage = {}) => {
  storagePolicy.value = {
    ...storagePolicy.value,
    ...incomingStorage,
    localCleanup: {
      ...storagePolicy.value.localCleanup,
      ...(incomingStorage.localCleanup || {}),
    },
    localStats: {
      ...storagePolicy.value.localStats,
      ...(incomingStorage.localStats || {}),
    },
  };
  normalizeStoragePolicy();
};

const formatBytes = (value) => {
  const bytes = Math.max(0, Number(value || 0));
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const formatDateTime = (value) => {
  if (!value) {
    return "尚未执行";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", {
    hour12: false,
  });
};

const syncLocalFromStore = () => {
  defaults.value = {
    ...defaults.value,
    ...detectionStore.detectionParams,
  };
  realtimePrefs.value = {
    ...realtimePrefs.value,
    ...detectionStore.realtimePrefs,
  };
};

const persistLocalSettings = () => {
  detectionStore.updateDefaults(defaults.value);
  detectionStore.updateRealtimePrefs(realtimePrefs.value);
};

const loadSettings = async () => {
  loading.value = true;
  error.value = "";
  success.value = false;
  cleanupMessage.value = "";
  syncLocalFromStore();
  try {
    const token = await getAuthToken();
    const response = await fetch(`${API_URL}/api/settings`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("无法获取系统设置");
    }

    const data = await response.json();
    const settings = data.settings || {};

    if (settings.defaults) {
      defaults.value = {
        ...defaults.value,
        ...settings.defaults,
      };
    }

    if (settings.system) {
      systemInfo.value = {
        ...systemInfo.value,
        ...settings.system,
      };
    }

    if (settings.storage) {
      mergeStoragePolicy(settings.storage);
    }

    normalizeDefaults();
    persistLocalSettings();
  } catch (err) {
    error.value = err.message || "加载设置失败";
  } finally {
    loading.value = false;
  }
};

const saveSettings = async () => {
  saving.value = true;
  error.value = "";
  success.value = false;
  cleanupMessage.value = "";
  try {
    normalizeDefaults();
    normalizeRealtimePrefs();
    normalizeStoragePolicy();
    persistLocalSettings();
    const token = await getAuthToken();
    const response = await fetch(`${API_URL}/api/settings`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        defaults: defaults.value,
        storage: {
          localCleanup: {
            enabled: storagePolicy.value.localCleanup.enabled,
            retentionDays: storagePolicy.value.localCleanup.retentionDays,
            maxRecords: storagePolicy.value.localCleanup.maxRecords,
          },
        },
      }),
    });

    if (!response.ok) {
      throw new Error("保存设置失败");
    }

    const data = await response.json();
    const settings = data.settings || {};
    if (settings.defaults) {
      defaults.value = {
        ...defaults.value,
        ...settings.defaults,
      };
    }
    if (settings.storage) {
      mergeStoragePolicy(settings.storage);
    }
    if (settings.system) {
      systemInfo.value = {
        ...systemInfo.value,
        ...settings.system,
      };
    }
    success.value = true;
  } catch (err) {
    error.value = `${err.message || "保存设置失败"}（实时偏好已保存在本地浏览器）`;
  } finally {
    saving.value = false;
  }
};

const runCleanupNow = async () => {
  cleaning.value = true;
  error.value = "";
  success.value = false;
  cleanupMessage.value = "";
  try {
    const token = await getAuthToken();
    const response = await fetch(`${API_URL}/api/settings/storage/cleanup`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("执行本地清理失败");
    }

    const data = await response.json();
    const settings = data.settings || {};
    if (settings.storage) {
      mergeStoragePolicy(settings.storage);
    }
    if (data.cleanup) {
      cleanupMessage.value = `本地清理已完成：移除 ${data.cleanup.removedRecords} 条历史、${data.cleanup.removedFiles} 个文件。`;
    }
  } catch (err) {
    error.value = err.message || "执行本地清理失败";
  } finally {
    cleaning.value = false;
  }
};

onMounted(() => {
  loadSettings();
});
</script>
