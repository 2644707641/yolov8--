<template>
  <div class="glass-panel p-6">
    <div class="flex items-start gap-4">
      <div class="flex-shrink-0 rounded-full bg-accent-500/20 p-3">
        <svg
          class="h-6 w-6 text-accent-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <h3 class="text-sm font-semibold text-white/90">AI 智能分析</h3>

        <!-- 加载态 -->
        <div v-if="loading" class="mt-4 space-y-3">
          <div class="grid gap-2" style="grid-template-columns: repeat(3, 1fr)">
            <div
              v-for="i in 9"
              :key="i"
              class="h-16 animate-pulse rounded-xl bg-white/5"
            />
          </div>
          <div class="h-4 w-3/4 animate-pulse rounded bg-white/5" />
        </div>

        <!-- 有分析结果 -->
        <template v-else-if="analysis">
          <!-- 启发式结果：九宫格热力图 -->
          <div
            v-if="analysis.spatial"
            class="mt-4 space-y-4"
          >
            <div
              class="grid gap-2"
              style="grid-template-columns: repeat(3, 1fr)"
            >
              <div
                v-for="zone in analysis.spatial.zones"
                :key="zone.label"
                class="relative rounded-xl border p-3 text-center transition-colors"
                :class="
                  zone.isBest
                    ? 'border-emerald-500/40 bg-emerald-500/10'
                    : zone.isRecommended && zone.total > 0
                      ? 'border-cyan-500/30 bg-cyan-500/[0.06]'
                      : zone.total === 0
                        ? 'border-white/5 bg-white/[0.02] opacity-40'
                        : 'border-white/10 bg-white/5'
                "
              >
                <!-- 推荐标签 -->
                <span
                  v-if="zone.recommendation"
                  class="absolute -top-2 right-1 rounded-md px-1.5 py-0.5 text-[10px] font-medium leading-none"
                  :class="
                    zone.recommendation === '强烈推荐'
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : zone.recommendation === '推荐'
                        ? 'bg-cyan-500/20 text-cyan-300'
                        : zone.recommendation === '已满'
                          ? 'bg-red-500/15 text-red-400'
                          : 'bg-white/10 text-slate-400'
                  "
                >{{ zone.recommendation }}</span>

                <p
                  class="text-xs"
                  :class="zone.total === 0 ? 'text-slate-600' : 'text-slate-400'"
                >
                  {{ zone.label }}
                </p>
                <p
                  class="mt-1 text-lg font-semibold"
                  :class="
                    zone.isBest
                      ? 'text-emerald-300'
                      : zone.total === 0
                        ? 'text-slate-600'
                        : zone.empty === 0 && zone.occupied > 0
                          ? 'text-red-400'
                          : 'text-white'
                  "
                >
                  {{ zone.empty }}
                  <span
                    class="text-xs font-normal"
                    :class="zone.total === 0 ? 'text-slate-600' : 'text-slate-400'"
                  >空</span>
                </p>
                <p
                  class="text-[11px]"
                  :class="zone.total === 0 ? 'text-slate-700' : 'text-slate-500'"
                >
                  {{ zone.occupied }} 占
                </p>
                <!-- 空闲率 -->
                <p
                  v-if="zone.total > 0"
                  class="mt-1 text-[11px] font-medium"
                  :class="
                    zone.vacancyRate >= 0.7
                      ? 'text-emerald-400'
                      : zone.vacancyRate >= 0.4
                        ? 'text-cyan-400'
                        : zone.vacancyRate > 0
                          ? 'text-amber-400'
                          : 'text-red-400'
                  "
                >
                  {{ Math.round(zone.vacancyRate * 100) }}% 空闲
                </p>
              </div>
            </div>

            <!-- 启发式摘要 -->
            <div class="rounded-xl border border-white/10 bg-slate-950/30 p-4">
              <p class="text-sm text-slate-300">
                {{ analysis.spatial.summary }}
              </p>
              <div
                class="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500"
              >
                <span>空车位 {{ analysis.spatial.totalEmpty }}</span>
                <span>占用车位 {{ analysis.spatial.totalOccupied }}</span>
                <span v-if="analysis.spatial.recommendedZones?.length">
                  推荐区域 {{ analysis.spatial.recommendedZones.join('、') }}
                </span>
              </div>
            </div>
          </div>

          <!-- LLM 加载中 -->
          <div
            v-if="llmLoading && (!analysis.llm || !analysis.llm.success)"
            class="mt-4 rounded-xl border border-accent-500/20 bg-accent-500/[0.03] p-4"
          >
            <div class="flex items-center gap-3">
              <div class="h-4 w-4 animate-spin rounded-full border-2 border-accent-400 border-t-transparent" />
              <span class="text-xs text-accent-300">AI 正在生成建议...</span>
            </div>
          </div>

          <!-- LLM 成功 -->
          <div
            v-if="analysis.llm && analysis.llm.success"
            class="mt-4 rounded-xl border border-accent-500/30 bg-accent-500/5 p-4"
          >
            <div class="mb-2 flex items-center gap-2 text-xs text-accent-300">
              <span>AI 建议</span>
            </div>
            <p class="whitespace-pre-line break-words text-sm leading-relaxed text-slate-200">
              {{ analysis.llm.suggestion }}
            </p>
          </div>

          <!-- LLM 失败 -->
          <div
            v-if="analysis.llm && !analysis.llm.success"
            class="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1">
                <p class="text-xs font-medium text-amber-200">AI 深度分析不可用</p>
                <p class="mt-1 text-xs text-amber-100/70">
                  {{ analysis.llm.error }}
                </p>
              </div>
              <button
                class="flex-shrink-0 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-200 transition-colors hover:bg-amber-500/20 disabled:cursor-not-allowed disabled:opacity-40"
                :disabled="retrying || cooldown"
                @click="$emit('retry')"
              >
                {{ retrying ? "重试中..." : cooldown ? "稍后重试" : "重试" }}
              </button>
            </div>
          </div>

          <!-- LLM 未配置（服务端未启用） -->
          <div
            v-if="analysis.llm === null && analysis.spatial && !llmLoading"
            class="mt-4 rounded-xl border border-dashed border-white/10 bg-white/[0.02] p-3"
          >
            <p class="text-xs text-slate-500">
              AI 深度分析服务暂未启用，当前展示为基础空间分析结果
            </p>
          </div>
        </template>

        <!-- 无分析结果 -->
        <p v-else class="mt-1 text-xs text-slate-400">
          暂无分析数据
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  analysis: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  retrying: {
    type: Boolean,
    default: false,
  },
  cooldown: {
    type: Boolean,
    default: false,
  },
  llmLoading: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["retry"]);
</script>
