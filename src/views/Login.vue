<template>
  <div class="min-h-screen bg-black">
    <Transition name="fade" mode="out-in">
      <SplashScreen v-if="showSplash" key="splash" />
      <div
        v-else
        key="login"
        class="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black px-4"
      >
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
              <div class="relative">
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  class="input-field pr-12"
                  placeholder="********"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
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
