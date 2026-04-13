<template>
  <div class="space-y-8">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="section-title">系统概览</p>
        <h1 data-testid="overview-title" class="mt-3 text-2xl font-semibold text-white">系统概览</h1>
        <p class="mt-2 text-sm text-slate-300/80">
          关键指标、模型状态与服务健康度统一展示。
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <span class="pill">运行中</span>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
      <div v-for="stat in stats" :key="stat.label" class="card">
        <p class="text-xs uppercase tracking-[0.3em] text-slate-400/70">{{ stat.label }}</p>
        <div class="mt-4 flex items-end justify-between">
          <p class="text-3xl font-semibold text-white">{{ stat.value }}</p>
          <span
            class="rounded-full px-3 py-1 text-xs font-medium"
            :class="stat.deltaType === 'up' ? 'bg-emerald-500/20 text-emerald-200' : 'bg-amber-500/20 text-amber-200'"
          >
            {{ stat.delta }}
          </span>
        </div>
        <p class="mt-3 text-xs text-slate-400">{{ stat.hint }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6 xl:grid-cols-3">
      <div class="card xl:col-span-2">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-white">识别任务趋势</h2>
          <span class="text-xs text-slate-400">最近7天</span>
        </div>

        <div v-if="activityLoading" class="mt-6 grid gap-4 md:grid-cols-2">
          <div v-for="i in 4" :key="`loading-${i}`" class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div class="h-6 w-1/2 animate-pulse rounded bg-white/10"></div>
            <div class="mt-3 h-4 w-11/12 animate-pulse rounded bg-white/10"></div>
            <div class="mt-2 h-4 w-3/4 animate-pulse rounded bg-white/10"></div>
            <div class="mt-4 h-4 w-1/3 animate-pulse rounded bg-white/10"></div>
          </div>
        </div>

        <div v-else class="mt-6 grid gap-4 md:grid-cols-2">
          <div
            v-for="item in activity"
            :key="item.key"
            class="rounded-2xl border border-white/10 bg-white/5 p-4"
          >
            <p class="text-sm font-medium text-white">{{ item.title }}</p>
            <p class="mt-2 text-xs text-slate-300/80">{{ item.desc }}</p>
            <div class="mt-4 flex items-center justify-between text-xs text-slate-400">
              <span>{{ item.time }}</span>
              <span class="text-primary-200">{{ item.status }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="text-lg font-semibold text-white">系统健康度</h2>
        <div class="mt-6 space-y-4">
          <div v-for="health in healthItems" :key="health.label" class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-200">{{ health.label }}</span>
              <span class="text-slate-400">{{ health.value }}</span>
            </div>
            <div class="h-2 rounded-full bg-white/10">
              <div
                class="h-2 rounded-full"
                :class="health.color"
                :style="{ width: health.percent }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { supabase } from "../config/supabase";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const REFRESH_INTERVAL_MS = 5000;

const stats = ref([
  {
    label: "今日识别次数",
    value: "0",
    delta: "+0",
    deltaType: "up",
    hint: "今日累计检测任务",
  },
  {
    label: "平均推理耗时",
    value: "0.00s",
    delta: "实时",
    deltaType: "up",
    hint: "基于成功检测任务实时统计",
  },
  {
    label: "活跃模型",
    value: "0",
    delta: "实时",
    deltaType: "up",
    hint: "当前已激活模型数量",
  },
  {
    label: "实时在线流",
    value: "0",
    delta: "实时",
    deltaType: "up",
    hint: "当前实时检测在线流数量",
  },
]);

const activity = ref([
  {
    key: "empty",
    title: "暂无识别记录",
    desc: "最近7天还没有新的检测任务",
    time: "--",
    status: "等待中",
  },
]);

const activityLoading = ref(true);
const isFirstActivityLoad = ref(true);
const isRefreshing = ref(false);

const healthItems = ref([
  { label: "GPU 利用率", value: "0%", percent: "0%", color: "bg-primary-500" },
  { label: "内存占用", value: "0GB", percent: "0%", color: "bg-emerald-500" },
  { label: "成功率", value: "100%", percent: "100%", color: "bg-cyan-500" },
]);

const clampPercent = (num) => {
  const parsed = Number(num);
  if (!Number.isFinite(parsed)) return 0;
  return Math.max(0, Math.min(100, parsed));
};

const toRelativeTime = (isoValue) => {
  const date = new Date(isoValue);
  const ts = date.getTime();
  if (!Number.isFinite(ts)) return "未知时间";

  const diffSec = Math.max(0, Math.floor((Date.now() - ts) / 1000));
  if (diffSec < 60) return "刚刚";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}分钟前`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}小时前`;
  if (diffSec < 172800) return "昨天";
  if (diffSec < 604800) return `${Math.floor(diffSec / 86400)}天前`;

  return date.toLocaleDateString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const buildTodayDelta = (todayCount, yesterdayCount) => {
  const today = Number(todayCount) || 0;
  const yesterday = Number(yesterdayCount) || 0;
  const diff = today - yesterday;
  const sign = diff >= 0 ? "+" : "";
  return {
    text: `${sign}${diff}`,
    type: diff >= 0 ? "up" : "down",
  };
};

const toActivityItems = (items) => {
  const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;

  const recentItems = (Array.isArray(items) ? items : [])
    .filter((item) => {
      const ts = new Date(item?.created_at).getTime();
      return Number.isFinite(ts) && ts >= weekAgo;
    })
    .slice(0, 4);

  if (recentItems.length === 0) {
    return [
      {
        key: "empty",
        title: "暂无识别记录",
        desc: "最近7天还没有新的检测任务",
        time: "--",
        status: "等待中",
      },
    ];
  }

  return recentItems.map((item, index) => {
    const detections = Array.isArray(item?.detections) ? item.detections : [];
    const avgConfidence = detections.length
      ? detections.reduce((sum, det) => sum + (Number(det?.confidence) || 0), 0) /
        detections.length
      : 0;

    const typeLabel = item?.file_type === "video" ? "视频" : "图片";
    const shortId = String(item?.id || "").slice(0, 8) || String(index + 1);

    const detailParts = [
      `检测目标 ${detections.length} 个`,
      `平均置信度 ${(avgConfidence * 100).toFixed(1)}%`,
    ];

    if (item?.params?.imgSize) {
      detailParts.push(`输入尺寸 ${item.params.imgSize}`);
    }

    return {
      key: item?.id || `record-${index}`,
      title: `${typeLabel}任务 ${shortId}`,
      desc: detailParts.join("，"),
      time: toRelativeTime(item?.created_at),
      status: detections.length > 0 ? "已识别" : "无目标",
    };
  });
};

async function fetchSystemStatus() {
  try {
    const response = await fetch(`${API_URL}/api/system/status`);
    const data = await response.json();
    if (!data.success || !data.data) return;

    const d = data.data;
    const gpuPercent = clampPercent(d.gpu_utilization);
    const memoryPercent = clampPercent(d.memory_percent);
    const successPercent = clampPercent(d.success_rate);

    healthItems.value = [
      {
        label: "GPU 利用率",
        value: `${gpuPercent.toFixed(0)}%`,
        percent: `${gpuPercent.toFixed(0)}%`,
        color: "bg-primary-500",
      },
      {
        label: "内存占用",
        value: `${Number(d.memory_used || 0).toFixed(1)}GB`,
        percent: `${memoryPercent.toFixed(0)}%`,
        color: "bg-emerald-500",
      },
      {
        label: "成功率",
        value: `${successPercent.toFixed(0)}%`,
        percent: `${successPercent.toFixed(0)}%`,
        color: "bg-cyan-500",
      },
    ];
  } catch (error) {
    console.error("获取系统状态失败:", error);
  }
}

async function fetchOverviewStats() {
  try {
    const { data } = await supabase.auth.getSession();
    const token = data?.session?.access_token;
    if (!token) return;

    const response = await fetch(`${API_URL}/api/system/overview`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const body = await response.json();
    if (!body.success || !body.data) return;

    const d = body.data;
    const todayDelta = buildTodayDelta(d.today_detection_count, d.yesterday_detection_count);

    stats.value = [
      {
        label: "今日识别次数",
        value: `${d.today_detection_count}`,
        delta: todayDelta.text,
        deltaType: todayDelta.type,
        hint: "今日累计检测任务",
      },
      {
        label: "平均推理耗时",
        value: `${Number(d.avg_inference_time || 0).toFixed(2)}s`,
        delta: "实时",
        deltaType: "up",
        hint: "基于成功检测任务实时统计",
      },
      {
        label: "活跃模型",
        value: `${d.active_model_count}`,
        delta: "实时",
        deltaType: "up",
        hint: "当前已激活模型数量",
      },
      {
        label: "实时在线流",
        value: `${d.online_stream_count}`,
        delta: "实时",
        deltaType: "up",
        hint: "当前实时检测在线流数量",
      },
    ];
  } catch (error) {
    console.error("获取概览统计失败:", error);
  }
}

async function fetchOverviewActivity({ showLoading = false } = {}) {
  if (showLoading) {
    activityLoading.value = true;
  }
  try {
    const { data } = await supabase.auth.getSession();
    const token = data?.session?.access_token;
    if (!token) {
      activity.value = toActivityItems([]);
      return;
    }

    const response = await fetch(`${API_URL}/api/history`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const body = await response.json();
    activity.value = toActivityItems(body?.items);
  } catch (error) {
    console.error("获取识别任务趋势失败:", error);
    activity.value = toActivityItems([]);
  } finally {
    if (showLoading) {
      activityLoading.value = false;
    }
    if (isFirstActivityLoad.value) {
      isFirstActivityLoad.value = false;
    }
  }
}

async function refreshOverviewData() {
  if (isRefreshing.value) {
    return;
  }
  isRefreshing.value = true;
  try {
    await Promise.all([
      fetchSystemStatus(),
      fetchOverviewStats(),
      fetchOverviewActivity({ showLoading: isFirstActivityLoad.value }),
    ]);
  } finally {
    isRefreshing.value = false;
  }
}

let statusTimer = null;

onMounted(() => {
  refreshOverviewData();
  statusTimer = setInterval(refreshOverviewData, REFRESH_INTERVAL_MS);
});

onBeforeUnmount(() => {
  if (statusTimer) {
    clearInterval(statusTimer);
    statusTimer = null;
  }
});
</script>
