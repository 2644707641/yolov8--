import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '../config/supabase'
import axios from 'axios'
import { buildProtectedApiUrl } from '../utils/protected-url'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const SETTINGS_STORAGE_KEY = 'yolov8.settings.v1'
const HISTORY_CACHE_TTL_MS = 60 * 1000

const defaultDetectionParams = {
  imgSize: 640,
  confidence: 0.5,
  iouThreshold: 0.6,
  maxDetections: 300,
  frameSkip: 1
}

const defaultRealtimePrefs = {
  recordEnabled: true,
  recordFps: 8,
  recordDurationSeconds: 0
}

const getStorage = () => {
  if (typeof window === 'undefined') return null
  return window.localStorage || null
}

const loadLocalSettings = () => {
  const storage = getStorage()
  if (!storage) return {}
  try {
    return JSON.parse(storage.getItem(SETTINGS_STORAGE_KEY) || '{}')
  } catch (error) {
    console.warn('读取本地设置失败，已忽略:', error)
    return {}
  }
}

const saveLocalSettings = (payload) => {
  const storage = getStorage()
  if (!storage) return
  storage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(payload))
}

const clearLocalSettings = () => {
  const storage = getStorage()
  if (!storage) return
  storage.removeItem(SETTINGS_STORAGE_KEY)
}

const normalizeDefaults = (raw) => ({
  imgSize: Math.max(320, Number(raw.imgSize || 640)),
  confidence: Math.min(1, Math.max(0, Number(raw.confidence || 0.5))),
  iouThreshold: Math.min(1, Math.max(0, Number(raw.iouThreshold || 0.6))),
  maxDetections: Math.max(1, Number(raw.maxDetections || 1)),
  frameSkip: Math.max(1, Number(raw.frameSkip || 1))
})

const normalizeRealtimePrefs = (raw) => ({
  recordEnabled: Boolean(raw.recordEnabled),
  recordFps: Math.max(1, Number(raw.recordFps || 8)),
  recordDurationSeconds: Math.max(0, Number(raw.recordDurationSeconds || 0))
})

export const useDetectionStore = defineStore('detection', () => {
  const localSettings = loadLocalSettings()
  const modelFile = ref(null)
  const modelUploaded = ref(false)
  const requestError = ref('')
  const detectionParams = ref(
    normalizeDefaults({ ...defaultDetectionParams, ...(localSettings.defaults || {}) })
  )
  const realtimePrefs = ref(
    normalizeRealtimePrefs({ ...defaultRealtimePrefs, ...(localSettings.realtime || {}) })
  )
  const isProcessing = ref(false)
  const detectionHistory = ref([])
  const currentResult = ref(null)
  const historyLoading = ref(false)
  const historyError = ref('')
  const lastHistorySyncAt = ref(0)
  const historyCacheUserId = ref(null)
  const historyCacheFetchedAt = ref(0)
  const historyLoaded = ref(false)

  const updateHistoryState = (userId, items, fetchedAt = Date.now()) => {
    detectionHistory.value = Array.isArray(items) ? items : []
    historyCacheUserId.value = userId || null
    historyCacheFetchedAt.value = fetchedAt
    historyLoaded.value = Boolean(userId)
    lastHistorySyncAt.value = fetchedAt
  }

  const resetHistoryState = () => {
    detectionHistory.value = []
    historyCacheUserId.value = null
    historyCacheFetchedAt.value = 0
    historyLoaded.value = false
    lastHistorySyncAt.value = 0
  }

  const hasFreshHistoryMemoryCache = (userId) => {
    if (!historyLoaded.value || historyCacheUserId.value !== userId) {
      return false
    }
    return Date.now() - historyCacheFetchedAt.value <= HISTORY_CACHE_TTL_MS
  }

  const persistSettings = () => {
    saveLocalSettings({
      defaults: detectionParams.value,
      realtime: realtimePrefs.value
    })
  }

  const updateDefaults = (next = {}) => {
    detectionParams.value = normalizeDefaults({ ...detectionParams.value, ...next })
    persistSettings()
  }

  const updateRealtimePrefs = (next = {}) => {
    realtimePrefs.value = normalizeRealtimePrefs({ ...realtimePrefs.value, ...next })
    persistSettings()
  }

  // 上传模型文件到后端
  const getAuthHeader = async () => {
    const { data: { session }, error } = await supabase.auth.getSession()
    if (error || !session?.access_token) {
      throw new Error('未检测到有效的登录会话，请重新登录后重试')
    }
    return `Bearer ${session.access_token}`
  }

  const uploadModel = async (file, name = null, description = null) => {
    try {
      isProcessing.value = true
      requestError.value = ''
      const formData = new FormData()
      formData.append('model', file)
      if (name) {
        formData.append('name', name)
      }
      if (description) {
        formData.append('description', description)
      }
      
      const authHeader = await getAuthHeader()
      
      const response = await axios.post(`${API_URL}/api/upload-model`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': authHeader
        }
      })
      
      modelFile.value = file
      modelUploaded.value = true
      
      return { success: true, data: response.data }
    } catch (error) {
      console.error('上传模型失败:', error)
      
      // 提取详细错误信息
      let errorMessage = '上传失败'
      if (error.response) {
        // 后端返回的错误
        errorMessage = error.response.data?.detail || error.response.data?.message || `HTTP ${error.response.status} 错误`
        console.error('后端错误详情:', error.response.data)
      } else if (error.request) {
        // 请求已发送但没有收到响应
        errorMessage = '无法连接到后端服务，请确保后端已启动在端口8000'
      } else {
        // 请求配置错误
        errorMessage = error.message
      }
      requestError.value = errorMessage
      
      return { success: false, error: errorMessage }
    } finally {
      isProcessing.value = false
    }
  }

  // 执行检测
  const runDetection = async (file, type = 'image') => {
    try {
      isProcessing.value = true
      requestError.value = ''
      const formData = new FormData()
      formData.append('file', file)
      formData.append('type', type)
      formData.append('params', JSON.stringify(detectionParams.value))
      
      const authHeader = await getAuthHeader()
      
      const response = await axios.post(`${API_URL}/api/detect`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': authHeader
        }
      })
      
      const result = response.data
      console.log('[DEBUG] 后端返回的结果:', result)
      
      // 使用后端返回的URL（优先使用Supabase URL，如果没有则使用本地API URL）
      const originalUrl = result.originalUrlSupabase || URL.createObjectURL(file)
      const resultUrl = result.resultUrlSupabase || await buildProtectedApiUrl(result.resultUrl)
      
      console.log('[DEBUG] 原始图片URL:', originalUrl)
      console.log('[DEBUG] 结果URL:', resultUrl)
      
      // 设置当前结果
      currentResult.value = {
        ...result,
        originalUrl: originalUrl,
        resultUrl: resultUrl,
        isSupabase: !!result.originalUrlSupabase // 标记是否来自Supabase
      }
      
      console.log('[DEBUG] 当前结果设置为:', currentResult.value)
      
      // 重新加载历史记录
      await loadHistory({ force: true })
      
      return { success: true, data: currentResult.value }
    } catch (error) {
      console.error('检测失败:', error)
      currentResult.value = null
      
      // 提取详细错误信息
      let errorMessage = '检测失败'
      if (error.response) {
        errorMessage = error.response.data?.detail || error.response.data?.message || `HTTP ${error.response.status} 错误`
        console.error('后端错误详情:', error.response.data)
      } else if (error.request) {
        errorMessage = '无法连接到后端服务，请确保后端已启动在端口8000'
      } else {
        errorMessage = error.message
      }
      requestError.value = errorMessage
      
      return { success: false, error: errorMessage }
    } finally {
      isProcessing.value = false
    }
  }

  // 加载历史记录
  const loadHistory = async ({ force = false } = {}) => {
    historyLoading.value = true
    historyError.value = ''
    try {
      const { data: { user } } = await supabase.auth.getUser()
      const userId = user?.id

      if (!userId) {
        resetHistoryState()
        return []
      }

      if (!force && hasFreshHistoryMemoryCache(userId)) {
        lastHistorySyncAt.value = historyCacheFetchedAt.value
        return detectionHistory.value
      }

      if (historyCacheUserId.value && historyCacheUserId.value !== userId) {
        resetHistoryState()
      }

      const authHeader = await getAuthHeader()
      const response = await axios.get(`${API_URL}/api/history`, {
        headers: {
          Authorization: authHeader
        }
      })

      const items = Array.isArray(response.data?.items) ? response.data.items : []
      const fetchedAt = Date.now()
      updateHistoryState(userId, items, fetchedAt)
      return detectionHistory.value
    } catch (error) {
      console.error('加载历史记录失败:', error)
      historyError.value = error?.message || '历史记录加载失败'
      return detectionHistory.value
    } finally {
      historyLoading.value = false
    }
  }

  // 删除历史记录
  const deleteHistory = async (id) => {
    try {
      requestError.value = ''
      const authHeader = await getAuthHeader()
      await axios.delete(`${API_URL}/api/history/${id}`, {
        headers: {
          Authorization: authHeader
        }
      })

      const nextHistory = detectionHistory.value.filter(item => item.id !== id)
      detectionHistory.value = nextHistory
      if (historyCacheUserId.value) {
        historyCacheFetchedAt.value = Date.now()
      }

      return { success: true }
    } catch (error) {
      console.error('删除失败:', error)
      const errorMessage = error?.response?.data?.detail || error.message || '删除失败'
      requestError.value = errorMessage
      return { success: false, error: errorMessage }
    }
  }

  // 清理缓存（退出登录时使用）
  const clearCache = () => {
    modelFile.value = null
    modelUploaded.value = false
    resetHistoryState()
    currentResult.value = null
    requestError.value = ''
    historyLoading.value = false
    historyError.value = ''
    // 重置参数到默认值
    detectionParams.value = { ...defaultDetectionParams }
    realtimePrefs.value = { ...defaultRealtimePrefs }
    clearLocalSettings()
    console.log('✅ 已清理用户检测缓存')
  }

  return {
    modelFile,
    modelUploaded,
    requestError,
    detectionParams,
    realtimePrefs,
    isProcessing,
    detectionHistory,
    currentResult,
    historyLoading,
    historyError,
    lastHistorySyncAt,
    updateDefaults,
    updateRealtimePrefs,
    uploadModel,
    runDetection,
    loadHistory,
    deleteHistory,
    clearCache
  }
})
