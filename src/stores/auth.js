import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '../config/supabase'
import router from '../router'

const defaultErrorMessage = '操作失败，请稍后再试。如问题持续出现，请联系平台管理员。'

const errorRules = [
  { match: 'Invalid login credentials', message: '邮箱或密码不正确，请确认后再试。' },
  { match: 'Email not confirmed', message: '邮箱尚未验证，请前往邮箱完成验证后再试。' },
  { match: 'User already registered', message: '该邮箱已注册，请直接登录或重置密码。' },
  { match: 'Password should be at least 6 characters', message: '密码长度至少需要 6 个字符，请重新设置。' },
  {
    match: 'Unable to validate email address: invalid format',
    message: '邮箱格式不正确，请检查后重新输入。'
  },
  { match: 'Signup requires a valid password', message: '请输入更安全的密码，至少包含 6 个字符。' },
  { includes: 'Failed to fetch', message: '网络连接异常，请检查网络后再次尝试。' },
  { includes: 'Email rate limit exceeded', message: '操作过于频繁，请稍后再试。' }
]

const translateError = (originalMessage) => {
  if (!originalMessage) {
    return defaultErrorMessage
  }

  const normalizedMessage = originalMessage.trim()

  for (const rule of errorRules) {
    if (rule.match && normalizedMessage === rule.match) {
      return rule.message
    }

    if (rule.includes && normalizedMessage.includes(rule.includes)) {
      return rule.message
    }
  }

  return defaultErrorMessage
}

let initializationPromise = null
let authSubscription = null

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const ready = ref(false)

  const initAuth = async () => {
    if (ready.value) {
      return
    }

    if (initializationPromise) {
      return initializationPromise
    }

    initializationPromise = (async () => {
      try {
        const { data, error: sessionError } = await supabase.auth.getSession()

        if (sessionError) {
          throw sessionError
        }

        user.value = data?.session?.user || null

        if (!authSubscription) {
          const { data: subscriptionData } = supabase.auth.onAuthStateChange((_, session) => {
            user.value = session?.user || null
            ready.value = true
          })

          authSubscription = subscriptionData?.subscription || null
        }
      } catch (err) {
        console.error('初始化认证失败:', err)
        error.value = translateError(err.message)
      } finally {
        ready.value = true
      }
    })()

    try {
      await initializationPromise
    } finally {
      initializationPromise = null
    }
  }

  const register = async (email, password) => {
    loading.value = true
    error.value = null

    try {
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password
      })

      if (signUpError) {
        throw signUpError
      }

      return { success: true, data }
    } catch (err) {
      console.error('注册失败:', err)
      const translatedError = translateError(err.message)
      error.value = translatedError
      return { success: false, error: translatedError }
    } finally {
      loading.value = false
    }
  }

  const login = async (email, password) => {
    loading.value = true
    error.value = null

    try {
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (signInError) {
        throw signInError
      }

      router.push('/dashboard')
      return { success: true, data }
    } catch (err) {
      console.error('登录失败:', err)
      const translatedError = translateError(err.message)
      error.value = translatedError
      return { success: false, error: translatedError }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      // 清理detection store中的用户缓存
      const { useDetectionStore } = await import('./detection')
      const detectionStore = useDetectionStore()
      detectionStore.clearCache()
      
      // 执行退出登录
      await supabase.auth.signOut()
      
      console.log('✅ 用户已退出登录，所有缓存已清理')
      router.push('/login')
    } catch (err) {
      console.error('登出失败:', err)
      error.value = translateError(err.message)
    }
  }

  return {
    user,
    loading,
    error,
    ready,
    initAuth,
    register,
    login,
    logout
  }
})
