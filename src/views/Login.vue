<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700 px-4">
    <div class="card max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">YOLOv8 智能识别停车位系统</h1>
        <p class="text-gray-600">登录您的账户</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
          <input
            v-model="email"
            type="email"
            required
            class="input-field"
            placeholder="your@email.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
          <input
            v-model="password"
            type="password"
            required
            class="input-field"
            placeholder="••••••••"
          />
        </div>

        <div v-if="authStore.error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ authStore.error }}</p>
        </div>

        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full btn-primary"
        >
          {{ authStore.loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          还没有账户？
          <router-link to="/register" class="text-primary-600 hover:text-primary-700 font-medium">
            立即注册
          </router-link>
        </p>
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

const handleLogin = async () => {
  await authStore.login(email.value, password.value)
}
</script>
