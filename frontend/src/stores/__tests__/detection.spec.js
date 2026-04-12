import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const getUserMock = vi.fn()
const getSessionMock = vi.fn()
const axiosGetMock = vi.fn()
const axiosDeleteMock = vi.fn()
const fetchMock = vi.fn()

global.fetch = fetchMock

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
})
