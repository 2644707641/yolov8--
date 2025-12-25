<template>
  <div class="relative min-h-screen overflow-hidden bg-slate-950">
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -top-20 right-1/3 h-[360px] w-[360px] rounded-full bg-primary-500/25 blur-3xl"></div>
      <div class="absolute top-1/2 -left-32 h-[420px] w-[420px] -translate-y-1/2 rounded-full bg-accent-500/20 blur-3xl"></div>
      <div class="absolute bottom-[-160px] left-1/2 h-[400px] w-[400px] -translate-x-1/2 rounded-full bg-primary-900/25 blur-3xl"></div>
    </div>
    <div class="relative z-10 flex min-h-screen items-center justify-center px-6 py-12">
      <div class="mx-auto grid w-full max-w-5xl gap-12 lg:grid-cols-[1fr_420px]">
        <div class="space-y-6 text-slate-300/80">
          <span class="pill">极速上手</span>
          <h2 class="text-4xl font-semibold text-white">三步完成注册，立即体验 AI 停车识别</h2>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="glass-panel p-5">
              <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">模型中心</p>
              <p class="mt-2 text-lg font-semibold text-white">自定义模型热更新</p>
            </div>
            <div class="glass-panel p-5">
              <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">素材管理</p>
              <p class="mt-2 text-lg font-semibold text-white">拖拽上传极速检测</p>
            </div>
            <div class="glass-panel p-5">
              <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">历史沉淀</p>
              <p class="mt-2 text-lg font-semibold text-white">推理结果自动归档</p>
            </div>
            <div class="glass-panel p-5">
              <p class="text-xs uppercase tracking-[0.28em] text-slate-400/70">安全合规</p>
              <p class="mt-2 text-lg font-semibold text-white">全链路加密与权限控制</p>
            </div>
          </div>
        </div>
        <div class="card p-10">
          <div class="text-center">
            <span class="pill">注册账户</span>
            <h1 class="mt-5 text-3xl font-semibold text-white">开启智能停车识别</h1>
            <p class="mt-3 text-sm text-slate-300/75">填写信息后即可体验 YOLOv8 识别与可视化看板。</p>
          </div>
          <form @submit.prevent="handleRegister" class="mt-10 space-y-6">
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
              <input
                v-model="password"
                type="password"
                required
                minlength="6"
                autocomplete="new-password"
                class="input-field"
                placeholder="至少 6 位字符"
              />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-200">确认密码</label>
              <input
                v-model="confirmPassword"
                type="password"
                required
                autocomplete="new-password"
                class="input-field"
                placeholder="再次输入密码"
              />
            </div>
            <div
              v-if="error"
              class="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-100"
            >
              {{ error }}
            </div>
            <div
              v-if="success"
              class="rounded-xl border border-emerald-500/35 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100"
            >
              注册成功！请查收邮箱完成验证。
            </div>
            <button
              type="submit"
              :disabled="authStore.loading"
              class="w-full btn-primary"
            >
              {{ authStore.loading ? '注册中…' : '注册' }}
            </button>
          </form>
          <div class="mt-8 text-center text-sm text-slate-300/75">
            已有账户？
            <router-link
              to="/login"
              class="text-primary-200 transition hover:text-primary-100"
            >
              立即登录
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const success = ref(false)

const handleRegister = async () => {
  error.value = ''
  success.value = false
  
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  const result = await authStore.register(email.value, password.value)
  
  if (result.success) {
    success.value = true
    email.value = ''
    password.value = ''
    confirmPassword.value = ''
  } else {
    error.value = result.error
  }
}
</script>
