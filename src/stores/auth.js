import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '../config/supabase'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 初始化认证状态
  const initAuth = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      user.value = session?.user || null

      // 监听认证状态变化
      supabase.auth.onAuthStateChange((event, session) => {
        user.value = session?.user || null
      })
    } catch (err) {
      console.error('初始化认证失败:', err)
    }
  }

  // 注册
  const register = async (email, password) => {
    loading.value = true
    error.value = null
    
    try {
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password
      })
      
      if (signUpError) throw signUpError
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // 登录
  const login = async (email, password) => {
    loading.value = true
    error.value = null
    
    try {
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password
      })
      
      if (signInError) throw signInError
      
      router.push('/dashboard')
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      await supabase.auth.signOut()
      router.push('/login')
    } catch (err) {
      console.error('登出失败:', err)
    }
  }

  return {
    user,
    loading,
    error,
    initAuth,
    register,
    login,
    logout
  }
})
