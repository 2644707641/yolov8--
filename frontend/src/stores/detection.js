import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '../config/supabase'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useDetectionStore = defineStore('detection', () => {
  const modelFile = ref(null)
  const modelUploaded = ref(false)
  const detectionParams = ref({
    imgSize: 640,
    confidence: 0.5,
    iouThreshold: 0.6,
    maxDetections: 300,
    frameSkip: 1  // 视频帧间隔，1=每帧检测（最流畅）
  })
  const isProcessing = ref(false)
  const detectionHistory = ref([])
  const currentResult = ref(null)

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
      
      return { success: false, error: errorMessage }
    } finally {
      isProcessing.value = false
    }
  }

  // 执行检测
  const runDetection = async (file, type = 'image') => {
    try {
      isProcessing.value = true
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
      const resultUrl = result.resultUrlSupabase || `${API_URL}${result.resultUrl}`
      
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
      await loadHistory()
      
      return { success: true, data: currentResult.value }
    } catch (error) {
      console.error('检测失败:', error)
      
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
      
      return { success: false, error: errorMessage }
    } finally {
      isProcessing.value = false
    }
  }

  // 加载历史记录
  const loadHistory = async () => {
    // 先清空旧数据，防止显示上一个用户的历史记录
    detectionHistory.value = []
    try {
      const { data: { user } } = await supabase.auth.getUser()
      
      const { data, error } = await supabase
        .from('detection_history')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
      
      if (error) throw error
      
      detectionHistory.value = data
    } catch (error) {
      console.error('加载历史记录失败:', error)
    }
  }

  // 删除历史记录
  const deleteHistory = async (id) => {
    try {
      const { error } = await supabase
        .from('detection_history')
        .delete()
        .eq('id', id)
      
      if (error) throw error
      
      await loadHistory()
      return { success: true }
    } catch (error) {
      console.error('删除失败:', error)
      return { success: false, error: error.message }
    }
  }

  // 清理缓存（退出登录时使用）
  const clearCache = () => {
    modelFile.value = null
    modelUploaded.value = false
    detectionHistory.value = []
    currentResult.value = null
    // 重置参数到默认值
    detectionParams.value = {
      imgSize: 640,
      confidence: 0.5,
      iouThreshold: 0.6,
      maxDetections: 300,
      frameSkip: 1
    }
    console.log('✅ 已清理用户检测缓存')
  }

  return {
    modelFile,
    modelUploaded,
    detectionParams,
    isProcessing,
    detectionHistory,
    currentResult,
    uploadModel,
    runDetection,
    loadHistory,
    deleteHistory,
    clearCache
  }
})
