<template>
  <div class="space-y-8">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="section-title">系统概览</p>
        <h1 data-testid="overview-title" class="mt-3 text-2xl font-semibold text-white">系统概览</h1>
        <p class="mt-2 text-sm text-slate-300/80">
          关键指标、模型状态与服务健康度统一在此集中展示。
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
          <span class="text-xs text-slate-400">最近 7 天</span>
        </div>
        <div class="mt-6 grid gap-4 md:grid-cols-2">
          <div
            v-for="item in activity"
            :key="item.title"
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
        <button class="mt-6 w-full btn-secondary text-sm">
          查看完整状态
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { supabase } from '../config/supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const stats = ref([
  {
    label: '今日识别次数',
    value: '0',
    delta: '0',
    deltaType: 'up',
    hint: '今日累计检测任务'
  },
  {
    label: '平均推理耗时',
    value: '0.00s',
    delta: '实时',
    deltaType: 'up',
    hint: '基于成功检测任务实时统计'
  },
  {
    label: '活跃模型',
    value: '0',
    delta: '实时',
    deltaType: 'up',
    hint: '当前已激活模型数量'
  },
  {
    label: '实时在线流',
    value: '0',
    delta: '实时',
    deltaType: 'up',
    hint: '当前实时检测在线流数量'
  }
])

const activity = ref([
  {
    title: '停车场 A 区域',
    desc: '已完成 32 次识别任务，最高并发 3 路视频流',
    time: '2 小时前',
    status: '稳定运行'
  },
  {
    title: '地库入口',
    desc: '最新模型权重已同步，识别准确率 96%',
    time: '4 小时前',
    status: '已更新'
  },
  {
    title: 'VIP 车位区',
    desc: '检测阈值已调整为 0.55，输出更平稳',
    time: '昨天',
    status: '策略生效'
  },
  {
    title: '云端备份',
    desc: '历史记录已归档 1,240 条，自动清理 30 天前数据',
    time: '昨天',
    status: '自动完成'
  }
])

const healthItems = ref([
  { label: 'GPU 利用率', value: '0%', percent: '0%', color: 'bg-primary-500' },
  { label: '内存占用', value: '0GB', percent: '0%', color: 'bg-emerald-500' },
  { label: '成功率', value: '100%', percent: '100%', color: 'bg-cyan-500' }
])

async function fetchSystemStatus() {
  try {
    const response = await fetch(`${API_URL}/api/system/status`)
    const data = await response.json()
    if (data.success && data.data) {
      const d = data.data
      healthItems.value = [
        { label: 'GPU 利用率', value: `${d.gpu_utilization}%`, percent: `${d.gpu_utilization}%`, color: 'bg-primary-500' },
        { label: '内存占用', value: `${d.memory_used}GB`, percent: `${d.memory_percent}%`, color: 'bg-emerald-500' },
        { label: '成功率', value: `${d.success_rate}%`, percent: `${d.success_rate}%`, color: 'bg-cyan-500' }
      ]
    }
  } catch (error) {
    console.error('获取系统状态失败:', error)
  }
}

function buildTodayDelta(todayCount, yesterdayCount) {
  const today = Number(todayCount) || 0
  const yesterday = Number(yesterdayCount) || 0
  const diff = today - yesterday
  const sign = diff >= 0 ? '+' : ''
  return {
    text: `${sign}${diff}`,
    type: diff >= 0 ? 'up' : 'down'
  }
}

async function fetchOverviewStats() {
  try {
    const { data } = await supabase.auth.getSession()
    const token = data?.session?.access_token
    if (!token) return

    const response = await fetch(`${API_URL}/api/system/overview`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    const body = await response.json()
    if (!body.success || !body.data) return

    const d = body.data
    const todayDelta = buildTodayDelta(d.today_detection_count, d.yesterday_detection_count)
    stats.value = [
      {
        label: '今日识别次数',
        value: `${d.today_detection_count}`,
        delta: todayDelta.text,
        deltaType: todayDelta.type,
        hint: '今日累计检测任务'
      },
      {
        label: '平均推理耗时',
        value: `${Number(d.avg_inference_time || 0).toFixed(2)}s`,
        delta: '实时',
        deltaType: 'up',
        hint: '基于成功检测任务实时统计'
      },
      {
        label: '活跃模型',
        value: `${d.active_model_count}`,
        delta: '实时',
        deltaType: 'up',
        hint: '当前已激活模型数量'
      },
      {
        label: '实时在线流',
        value: `${d.online_stream_count}`,
        delta: '实时',
        deltaType: 'up',
        hint: '当前实时检测在线流数量'
      }
    ]
  } catch (error) {
    console.error('获取概览统计失败:', error)
  }
}

async function refreshOverviewData() {
  await Promise.all([fetchSystemStatus(), fetchOverviewStats()])
}

let statusTimer = null

onMounted(() => {
  refreshOverviewData()
  statusTimer = setInterval(refreshOverviewData, 5000)
})

onBeforeUnmount(() => {
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
})
</script>
