<template>
  <div class="relative min-h-screen overflow-hidden bg-slate-950">
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -top-32 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-primary-500/25 blur-3xl"></div>
      <div class="absolute top-1/3 -left-24 h-[420px] w-[420px] rounded-full bg-accent-500/20 blur-3xl"></div>
      <div class="absolute bottom-0 right-0 h-[360px] w-[360px] rounded-full bg-primary-900/25 blur-3xl"></div>
    </div>
    <Transition name="fade" mode="out-in">
      <SplashScreen v-if="showSplash" key="splash" />
      <div
        v-else
        key="login"
        class="relative z-10 flex min-h-screen items-center justify-center px-6 py-12"
      >
        <div class="mx-auto flex w-full max-w-6xl flex-col gap-12 lg:flex-row lg:items-center">
          <div class="hidden w-full lg:block lg:w-1/2">
            <span class="pill">YOLOv8 Vision</span>
            <h2 class="mt-6 text-4xl font-semibold text-white lg:text-5xl">
              智能识别每一个泊位，让停车运营
              <span class="text-gradient">更高效</span>
            </h2>
            <p class="mt-6 max-w-lg text-sm text-slate-300/75">
              登录后即可管理模型、上传素材并实时获得 AI 推理结果。所有识别历史都会自动保存，支持一键追溯与导出。
            </p>
            <div class="mt-10 grid grid-cols-2 gap-4 text-sm text-slate-300/70">
              <div class="glass-panel p-4">
                <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">AI 推理</p>
                <p class="mt-2 text-lg font-semibold text-white">毫秒级响应</p>
              </div>
              <div class="glass-panel p-4">
                <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">全流程安全</p>
                <p class="mt-2 text-lg font-semibold text-white">端到端加密</p>
              </div>
            </div>
          </div>
          <div class="w-full lg:w-[420px]">
            <div class="card p-10">
              <div class="text-center">
                <span class="pill">欢迎回来</span>
                <h1 class="mt-5 text-3xl font-semibold text-white">登录智能停车识别平台</h1>
                <p class="mt-3 text-sm text-slate-300/75">使用注册邮箱和密码继续</p>
              </div>
              <form @submit.prevent="handleLogin" class="mt-10 space-y-6">
                <div class="space-y-2">
                  <label class="text-sm font-medium text-slate-200">邮箱</label>
                  <input
                    v-model="email"
                    type="email"
                    required
                    autocomplete="email"
                    class="input-field"
                    placeholder="your@email.com"
                  />
                </div>
                <div class="space-y-2">
                  <label class="text-sm font-medium text-slate-200">密码</label>
                  <div class="relative">
                    <input
                      v-model="password"
                      :type="showPassword ? 'text' : 'password'"
                      required
                      autocomplete="current-password"
                      class="input-field pr-12"
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      class="absolute inset-y-0 right-3 flex items-center text-slate-400 transition hover:text-white"
                      :aria-label="showPassword ? '隐藏密码' : '显示密码'"
                      :title="showPassword ? '隐藏密码' : '显示密码'"
                      @click="togglePasswordVisibility"
                    >
                      <svg
                        v-if="!showPassword"
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-5 w-5"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path d="M1.5 12S5 5.25 12 5.25 22.5 12 22.5 12 19 18.75 12 18.75 1.5 12 1.5 12Z" />
                        <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" />
                      </svg>
                      <svg
                        v-else
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-5 w-5"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path d="M3 3l18 18" />
                        <path d="M10.6 10.65a3 3 0 0 0 2.75 2.75" />
                        <path d="M6.1 6.56A10.82 10.82 0 0 0 1.5 12s3.5 6.75 10.5 6.75a10.46 10.46 0 0 0 4.3-.9" />
                        <path d="M17.9 17.44A10.79 10.79 0 0 0 22.5 12s-3.5-6.75-10.5-6.75a10.46 10.46 0 0 0-4.3.9" />
                      </svg>
                    </button>
                  </div>
                </div>
                <div
                  v-if="authStore.error"
                  class="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-100"
                >
                  {{ authStore.error }}
                </div>
                <button
                  type="submit"
                  :disabled="authStore.loading"
                  class="w-full btn-primary"
                >
                  {{ authStore.loading ? '登录中…' : '登录' }}
                </button>
              </form>
              <div class="mt-8 text-center text-sm text-slate-300/75">
                还没有账户？
                <router-link
                  to="/register"
                  class="text-primary-200 transition hover:text-primary-100"
                >
                  立即注册
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>


<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import SplashScreen from '../components/SplashScreen.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showSplash = ref(true)
const showPassword = ref(false)
let splashTimeoutId = 0

onMounted(() => {
  splashTimeoutId = window.setTimeout(() => {
    showSplash.value = false
  }, 2000)
})

onBeforeUnmount(() => {
  window.clearTimeout(splashTimeoutId)
})

const handleLogin = async () => {
  await authStore.login(email.value, password.value)
}

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.6s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
