import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const getUserMock = vi.fn()
const getSessionMock = vi.fn()
const axiosGetMock = vi.fn()
const axiosDeleteMock = vi.fn()
const fetchMock = vi.fn()

global.fetch = fetchMock

const createDeferred = () => {
  let resolve
  let reject
  const promise = new Promise((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

vi.mock('../../config/supabase', () => ({
  supabase: {
    auth: {
      getUser: (...args) => getUserMock(...args),
      getSession: (...args) => getSessionMock(...args)
    }
  }
}))

vi.mock('axios', () => ({
  default: {
    get: (...args) => axiosGetMock(...args),
    delete: (...args) => axiosDeleteMock(...args)
  }
}))

describe('detection store history cache', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-03-12T12:00:00Z'))
    window.localStorage.clear()
    setActivePinia(createPinia())
    getUserMock.mockResolvedValue({ data: { user: { id: 'user-1' } } })
    getSessionMock.mockResolvedValue({
      data: {
        session: {
          access_token: 'token-1'
        }
      },
      error: null
    })
    axiosGetMock.mockResolvedValue({
      data: {
        items: [{ id: 'history-1', file_type: 'image', created_at: '2026-03-12T11:59:00Z' }]
      }
    })
    axiosDeleteMock.mockResolvedValue({ data: { success: true } })
    fetchMock.mockReset()
  })

  it('缓存有效期内重复加载历史记录时不重复请求后端接口', async () => {
    const { useDetectionStore } = await import('../detection')
    const store = useDetectionStore()

    await store.loadHistory()
    await store.loadHistory()

    expect(axiosGetMock).toHaveBeenCalledTimes(1)
    expect(store.detectionHistory).toHaveLength(1)
  })

  it('刷新页面后历史记录缓存失效并重新请求后端接口', async () => {
    const { useDetectionStore } = await import('../detection')
    const store = useDetectionStore()

    await store.loadHistory()
    expect(axiosGetMock).toHaveBeenCalledTimes(1)

    setActivePinia(createPinia())
    const nextStore = useDetectionStore()
    await nextStore.loadHistory()

    expect(axiosGetMock).toHaveBeenCalledTimes(2)
    expect(nextStore.detectionHistory[0]?.id).toBe('history-1')
  })

  it('删除历史记录时调用后端接口并同步更新本地缓存', async () => {
    const { useDetectionStore } = await import('../detection')
    const store = useDetectionStore()

    await store.loadHistory()
    const result = await store.deleteHistory('history-1')

    expect(result).toEqual({ success: true })
    expect(axiosDeleteMock).toHaveBeenCalledTimes(1)
    expect(store.detectionHistory).toEqual([])
  })

  it('历史记录加载失败时暴露统一错误状态并结束加载态', async () => {
    axiosGetMock.mockRejectedValueOnce(new Error('network down'))
    const { useDetectionStore } = await import('../detection')
    const store = useDetectionStore()

    const result = await store.loadHistory()

    expect(result).toEqual([])
    expect(store.historyLoading).toBe(false)
    expect(store.historyError).toContain('network down')
    expect(store.lastHistorySyncAt).toBe(0)
  })

  it('历史记录加载成功后记录最近同步时间并清空错误', async () => {
    const { useDetectionStore } = await import('../detection')
    const store = useDetectionStore()

    await store.loadHistory()

    expect(store.historyLoading).toBe(false)
    expect(store.historyError).toBe('')
    expect(store.lastHistorySyncAt).toBeGreaterThan(0)
  })

  it('识别成功后即使 URL 鉴权拼接失败也不应回退为失败', async () => {
    const { useDetectionStore } = await import('../detection')
    const store = useDetectionStore()
    const ssePayload = [
      'data: {"stage":"uploading","percent":20,"message":"uploading"}\n\n',
      'data: {"stage":"result","data":{"resultUrl":"/api/results/demo.jpg","originalUrlSupabase":"https://storage.example.com/original.jpg","resultUrlSupabase":null,"detections":[]}}\n\n'
    ].join('')
    const encodedPayload = new TextEncoder().encode(ssePayload)
    let sent = false

    fetchMock.mockResolvedValueOnce({
      ok: true,
      body: {
        getReader() {
          return {
            async read() {
              if (sent) {
                return { done: true, value: undefined }
              }
              sent = true
              return { done: false, value: encodedPayload }
            }
          }
        }
      }
    })

    getSessionMock
      .mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'token-1'
          }
        },
        error: null
      })
      .mockResolvedValueOnce({
        data: {
          session: null
        },
        error: null
      })

    const result = await store.runDetection(
      new File(['demo'], 'demo.jpg', { type: 'image/jpeg' }),
      'image'
    )

    expect(result.success).toBe(true)
    expect(store.currentResult?.resultUrl).toContain('/api/results/demo.jpg')
    expect(store.requestError).toBe('')
  })

  it('后端返回 JSON 结果时应直接识别成功并写入当前结果', async () => {
    const { useDetectionStore } = await import('../detection')
    const store = useDetectionStore()

    fetchMock.mockResolvedValueOnce({
      ok: true,
      headers: {
        get: () => 'application/json; charset=utf-8'
      },
      async json() {
        return {
          success: true,
          resultUrl: '/api/results/json-result.jpg',
          originalUrlSupabase: null,
          resultUrlSupabase: null,
          detections: [],
          description: 'json payload'
        }
      }
    })

    const result = await store.runDetection(
      new File(['demo'], 'demo.jpg', { type: 'image/jpeg' }),
      'image'
    )

    expect(result.success).toBe(true)
    expect(store.currentResult?.description).toBe('json payload')
    expect(store.currentResult?.resultUrl).toContain('/api/results/json-result.jpg')
    expect(store.requestError).toBe('')
  })

  it('当启发式结果为空时也应接收并展示异步 LLM 结果', async () => {
    vi.useRealTimers()
    const { useDetectionStore } = await import('../detection')
    const store = useDetectionStore()

    fetchMock.mockImplementation(async (url) => {
      if (String(url).includes('/api/detect')) {
        return {
          ok: true,
          headers: { get: () => 'application/json; charset=utf-8' },
          async json() {
            return {
              success: true,
              resultUrl: '/api/results/no-spatial.jpg',
              originalUrlSupabase: 'https://storage.example.com/original.jpg',
              resultUrlSupabase: null,
              detections: [{ class: 'demo-none-spatial', bbox: [0, 0, 10, 10], confidence: 0.9 }],
              aiAnalysis: null
            }
          }
        }
      }
      if (String(url).includes('/api/ai/analyze-llm')) {
        return {
          ok: true,
          async json() {
            return {
              success: true,
              spatial: null,
              llm: {
                success: true,
                suggestion: '建议前往左侧',
                model: 'demo-model'
              }
            }
          }
        }
      }
      throw new Error(`unexpected fetch url: ${url}`)
    })

    const result = await store.runDetection(
      new File(['demo'], 'demo.jpg', { type: 'image/jpeg' }),
      'image'
    )

    await Promise.resolve()
    await Promise.resolve()

    expect(result.success).toBe(true)
    expect(store.aiAnalysisResult).not.toBeNull()
    expect(store.aiAnalysisResult?.llm?.success).toBe(true)
    expect(store.aiAnalysisResult?.llm?.suggestion).toContain('左侧')
  })

  it('连续两次检测时旧的异步 LLM 回包不应覆盖最新结果', async () => {
    vi.useRealTimers()
    const { useDetectionStore } = await import('../detection')
    const store = useDetectionStore()

    const firstLlmDeferred = createDeferred()
    let detectIndex = 0

    fetchMock.mockImplementation(async (url, options = {}) => {
      const target = String(url)
      if (target.includes('/api/detect')) {
        detectIndex += 1
        const marker = detectIndex === 1 ? 'first-marker' : 'second-marker'
        const summary = detectIndex === 1 ? 'first spatial' : 'second spatial'
        return {
          ok: true,
          headers: { get: () => 'application/json; charset=utf-8' },
          async json() {
            return {
              success: true,
              resultUrl: `/api/results/${marker}.jpg`,
              originalUrlSupabase: 'https://storage.example.com/original.jpg',
              resultUrlSupabase: null,
              detections: [{ class: marker, bbox: [0, 0, 10, 10], confidence: 0.9 }],
              aiAnalysis: {
                spatial: {
                  summary,
                  zones: [],
                  totalEmpty: 1,
                  totalOccupied: 0
                },
                llm: null
              }
            }
          }
        }
      }

      if (target.includes('/api/ai/analyze-llm')) {
        const body = JSON.parse(options.body || '{}')
        const marker = body?.detections?.[0]?.class
        if (marker === 'first-marker') {
          return firstLlmDeferred.promise
        }
        if (marker === 'second-marker') {
          return {
            ok: true,
            async json() {
              return {
                success: true,
                llm: {
                  success: true,
                  suggestion: 'second suggestion',
                  model: 'demo-model'
                }
              }
            }
          }
        }
      }
      throw new Error(`unexpected fetch url: ${url}`)
    })

    await store.runDetection(new File(['one'], 'one.jpg', { type: 'image/jpeg' }), 'image')
    await store.runDetection(new File(['two'], 'two.jpg', { type: 'image/jpeg' }), 'image')

    await Promise.resolve()
    await Promise.resolve()
    expect(store.aiAnalysisResult?.llm?.suggestion).toBe('second suggestion')

    firstLlmDeferred.resolve({
      ok: true,
      async json() {
        return {
          success: true,
          llm: {
            success: true,
            suggestion: 'first late suggestion',
            model: 'demo-model'
          }
        }
      }
    })

    await Promise.resolve()
    await Promise.resolve()

    expect(store.aiAnalysisResult?.llm?.suggestion).toBe('second suggestion')
    expect(store.aiAnalysisResult?.spatial?.summary).toBe('second spatial')
  })
})
