<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700 px-4">
    <div class="card max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">创建账户</h1>
        <p class="text-gray-600">开始使用YOLOv8智能识别</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-6">
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
            minlength="6"
            class="input-field"
            placeholder="至少6个字符"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            required
            class="input-field"
            placeholder="再次输入密码"
          />
        </div>

        <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <div v-if="success" class="p-3 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-sm text-green-600">注册成功！请检查您的邮箱以验证账户。</p>
        </div>

        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full btn-primary"
        >
          {{ authStore.loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          已有账户？
          <router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
            立即登录
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
