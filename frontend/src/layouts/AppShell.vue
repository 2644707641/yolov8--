<template>
  <div data-testid="app-shell-root" class="relative h-screen overflow-hidden bg-slate-950">
    <div class="absolute inset-0">
      <div class="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-black"></div>
      <div class="absolute inset-0 bg-grid opacity-10"></div>
      <div class="absolute -top-24 left-1/4 h-80 w-80 rounded-full bg-primary-500/20 blur-3xl"></div>
      <div class="absolute top-1/2 -right-32 h-[420px] w-[420px] -translate-y-1/2 rounded-full bg-accent-500/20 blur-3xl"></div>
      <div class="absolute bottom-0 left-0 h-[360px] w-[360px] rounded-full bg-primary-900/20 blur-3xl"></div>
    </div>

    <div class="relative z-10 flex h-full overflow-hidden">
      <aside
        class="hidden h-full min-h-0 flex-col overflow-hidden border-r border-white/10 bg-slate-950/70 backdrop-blur-xl transition-[width] duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] lg:flex"
        :class="isCollapsed ? 'w-28' : 'w-72'"
      >
        <div
          data-testid="nav-header"
          class="flex items-center px-4 py-4"
          :class="isCollapsed ? 'justify-between gap-2 px-3' : 'gap-3'"
        >
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary-500/20 text-primary-200">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3l8 4v10l-8 4-8-4V7l8-4z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 7v10"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 9l8 4"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 9l-8 4"></path>
            </svg>
          </div>
          <div
            data-testid="nav-brand"
            class="min-w-0 overflow-hidden transition-[max-width,max-height,opacity,transform] duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"
            :class="isCollapsed ? 'max-w-0 max-h-0 opacity-0 translate-x-2' : 'max-w-[240px] max-h-[72px] opacity-100 translate-x-0'"
          >
            <p class="text-xs uppercase tracking-[0.4em] text-slate-400/80">
              <span
                v-for="(char, index) in brandLetters"
                :key="`brand-${index}`"
                data-testid="nav-brand-letter"
                class="inline-block transition-[opacity,transform] duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"
                :class="isCollapsed ? 'opacity-0 -translate-y-1' : 'opacity-100 translate-y-0'"
                :style="{ transitionDelay: `${index * 30}ms` }"
              >
                {{ char }}
              </span>
            </p>
            <p class="text-lg font-semibold text-white leading-snug">
              <span
                v-for="(char, index) in titleLetters"
                :key="`title-${index}`"
                data-testid="nav-title-letter"
                class="inline-block transition-[opacity,transform] duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"
                :class="isCollapsed ? 'opacity-0 -translate-y-1' : 'opacity-100 translate-y-0'"
                :style="{ transitionDelay: `${index * 40}ms` }"
              >
                {{ char }}
              </span>
            </p>
          </div>
          <button
            data-testid="nav-collapse"
            class="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-300 transition hover:bg-white/10 hover:text-white"
            :class="isCollapsed ? '' : 'ml-auto'"
            @click="toggleCollapse"
          >
            <svg v-if="!isCollapsed" class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 19l-7-7 7-7"></path>
            </svg>
            <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>

        <div
          data-testid="desktop-nav-scroll"
          class="min-h-0 flex-1 overflow-y-auto"
          :class="isCollapsed ? 'px-3 pb-4' : 'px-4'"
        >
          <p v-if="!isCollapsed" class="px-3 text-xs uppercase tracking-[0.4em] text-slate-400/70">系统导航</p>
          <nav class="mt-3 space-y-1.5">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="group relative flex items-center gap-3 rounded-2xl border border-transparent py-2.5 text-sm font-medium transition-all"
              :aria-label="item.label"
              :class="[
                isCollapsed ? 'px-3 justify-center' : 'px-4',
                isActive(item.path)
                  ? 'border-primary-400/40 bg-primary-500/20 text-white shadow-[0_15px_35px_rgba(37,99,235,0.35)]'
                  : 'text-slate-300 hover:border-white/10 hover:bg-white/5'
              ]"
              :data-testid="item.testId"
            >
              <span
                class="flex items-center justify-center rounded-xl transition-all"
                :class="[
                  isCollapsed ? 'h-10 w-10' : 'h-8 w-8',
                  isActive(item.path) ? 'bg-white/15 text-white' : 'bg-white/5 text-slate-300'
                ]"
              >
                <svg
                  :class="isCollapsed ? 'h-5 w-5' : 'h-4 w-4'"
                  fill="none"
                  stroke="currentColor"
                  :viewBox="item.icon.viewBox"
                  aria-hidden="true"
                  focusable="false"
                >
                  <path
                    v-for="(path, index) in item.icon.paths"
                    :key="index"
                    v-bind="path"
                  ></path>
                </svg>
              </span>
              <span
                aria-hidden="true"
                class="nav-label overflow-hidden whitespace-nowrap transition-[max-width] duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"
                :class="[
                  isCollapsed
                    ? 'flex-none max-w-0'
                  : 'flex-1 max-w-[200px]'
                ]"
                :data-testid="`${item.testId}-label`"
              >
                <span
                  v-for="(char, index) in item.letters"
                  :key="`${item.path}-letter-${index}`"
                  :data-testid="`${item.testId}-letter`"
                  class="nav-letter inline-block transition-[opacity,transform] duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"
                  :class="isCollapsed ? 'opacity-0 -translate-y-1' : 'opacity-100 translate-y-0'"
                  :style="{ transitionDelay: `${index * 40}ms` }"
                >
                  {{ char }}
                </span>
              </span>
              <span
                v-if="item.badge && !isCollapsed"
                class="rounded-full bg-white/10 px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-slate-300"
              >
                {{ item.badge }}
              </span>
              <span
                v-if="isCollapsed"
                class="pointer-events-none absolute left-full top-1/2 z-20 -translate-y-1/2 translate-x-2 whitespace-nowrap rounded-xl border border-white/10 bg-slate-900/95 px-3 py-2 text-xs text-white opacity-0 shadow-[0_20px_45px_rgba(8,15,40,0.45)] transition-opacity duration-200 delay-200 group-hover:opacity-100"
                :data-testid="`${item.testId}-tooltip`"
              >
                {{ item.label }}
              </span>
            </router-link>
          </nav>
        </div>

      </aside>

      <div data-testid="app-shell-main-column" class="flex h-full min-h-0 flex-1 flex-col overflow-hidden">
        <header data-testid="app-shell-header" class="sticky top-0 z-30 shrink-0 border-b border-white/10 bg-white/5 backdrop-blur-xl">
          <div class="flex items-center justify-between px-6 py-3 lg:px-10">
            <div class="flex items-center gap-4">
              <button
                data-testid="mobile-nav-toggle"
                class="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-slate-200 lg:hidden"
                @click="toggleMobileNav"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
              </button>
              <div>
                <p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">系统控制台</p>
                <h1 class="text-xl font-semibold text-white">{{ pageTitle }}</h1>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <div class="hidden text-right text-xs text-slate-400/80 md:block">
                <div class="uppercase tracking-[0.3em]">当前账户</div>
                <div class="text-sm font-medium text-white">
                  {{ authStore.user?.email || '未登录' }}
                </div>
              </div>
              <router-link to="/settings" class="btn-secondary text-sm">
                系统设置
              </router-link>
            </div>
          </div>
        </header>

        <main data-testid="app-shell-content" class="min-h-0 flex-1 overflow-y-auto px-6 py-6 lg:px-10">
          <router-view v-slot="{ Component }">
            <Transition name="fade" mode="out-in">
              <component :is="Component" />
            </Transition>
          </router-view>
        </main>
      </div>
    </div>

    <div
      v-if="!isCollapsed"
      class="fixed bottom-0 left-0 z-40 hidden w-72 px-4 pb-4 pt-3 lg:block"
    >
      <div class="rounded-2xl border border-white/10 bg-slate-950/70 p-4 backdrop-blur-xl shadow-[0_18px_45px_rgba(6,11,30,0.35)]">
        <div class="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p class="text-xs uppercase tracking-[0.3em] text-slate-400/80">运行状态</p>
          <div class="mt-3 flex items-center justify-between text-sm">
            <span class="text-slate-300">实时监控</span>
            <span class="text-emerald-300">在线</span>
          </div>
          <div class="mt-1.5 flex items-center justify-between text-sm">
            <span class="text-slate-300">模型版本</span>
            <span class="text-slate-100">YOLOv8</span>
          </div>
        </div>
        <button
          class="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-white/10"
          @click="authStore.logout"
        >
          退出登录
        </button>
      </div>
    </div>

    <Transition name="fade">
      <div
        v-if="mobileNavOpen"
        class="fixed inset-0 z-50 flex lg:hidden"
      >
        <div class="absolute inset-0 bg-black/60" @click="toggleMobileNav"></div>
        <div
          data-testid="mobile-nav-panel"
          class="relative z-10 flex h-full w-72 flex-col overflow-hidden border-r border-white/10 bg-slate-950/95 backdrop-blur-xl"
        >
          <div data-testid="mobile-nav-header" class="flex shrink-0 items-center justify-between px-6 pb-4 pt-6">
            <div>
              <p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">YOLOv8</p>
              <p class="text-lg font-semibold text-white">系统导航</p>
            </div>
            <button class="text-slate-400" @click="toggleMobileNav">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <div data-testid="mobile-nav-scroll" class="min-h-0 flex-1 overflow-y-auto px-6 pb-6">
            <nav class="space-y-2">
              <router-link
                v-for="item in navItems"
                :key="`mobile-${item.path}`"
                :to="item.path"
                class="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200"
                @click="toggleMobileNav"
              >
                <svg
                  class="h-5 w-5 text-slate-300"
                  fill="none"
                  stroke="currentColor"
                  :viewBox="item.icon.viewBox"
                  aria-hidden="true"
                  focusable="false"
                >
                  <path
                    v-for="(path, index) in item.icon.paths"
                    :key="index"
                    v-bind="path"
                  ></path>
                </svg>
                {{ item.label }}
              </router-link>
            </nav>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const mobileNavOpen = ref(false)
const isCollapsed = ref(false)

const pageTitle = computed(() => route.meta?.title || '控制台')

const baseNavItems = [
  {
    label: '系统概览',
    path: '/overview',
    testId: 'nav-overview',
    icon: {
      viewBox: '0 0 24 24',
      paths: [
        { d: 'M4 6h16M4 12h10M4 18h7', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' }
      ]
    }
  },
  {
    label: '识别工作台',
    path: '/workspace',
    testId: 'nav-workspace',
    icon: {
      viewBox: '0 0 24 24',
      paths: [
        { d: 'M4 6h16v12H4z', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' },
        { d: 'M8 10h8M8 14h5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' }
      ]
    }
  },
  {
    label: '历史记录',
    path: '/history',
    testId: 'nav-history',
    icon: {
      viewBox: '0 0 24 24',
      paths: [
        { d: 'M8 7h8M8 11h8M8 15h5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' },
        { d: 'M6 3h8l4 4v14H6z', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' }
      ]
    }
  },
  {
    label: '模型管理',
    path: '/model-weights',
    testId: 'nav-models',
    icon: {
      viewBox: '0 0 24 24',
      paths: [
        { d: 'M4 7l8-4 8 4-8 4-8-4z', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' },
        { d: 'M4 7v10l8 4 8-4V7', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' }
      ]
    }
  },
  {
    label: '实时监控',
    path: '/realtime',
    testId: 'nav-realtime',
    badge: 'LIVE',
    icon: {
      viewBox: '0 0 24 24',
      paths: [
        { d: 'M3 12h4l3 6 4-12 3 6h4', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' }
      ]
    }
  },
  {
    label: '系统设置',
    path: '/settings',
    testId: 'nav-settings',
    icon: {
      viewBox: '0 0 24 24',
      paths: [
        { d: 'M12 6a6 6 0 100 12 6 6 0 000-12z', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' },
        { d: 'M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5' }
      ]
    }
  }
]

const brandLetters = Array.from('YOLOv8')
const titleLetters = Array.from('智能停车控制台')

const navItems = baseNavItems.map((item) => ({
  ...item,
  letters: Array.from(item.label)
}))

const isActive = (path) => {
  if (path === '/overview') {
    return route.path === '/' || route.path === path
  }
  return route.path.startsWith(path)
}

const toggleMobileNav = () => {
  mobileNavOpen.value = !mobileNavOpen.value
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
