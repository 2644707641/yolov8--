import { beforeEach, describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { reactive } from 'vue'
import Realtime from '../Realtime.vue'

const detectionStoreMock = {
  detectionParams: {
    imgSize: 640,
    confidence: 0.5,
    iouThreshold: 0.6,
    maxDetections: 300,
    frameSkip: 1
  },
  realtimePrefs: reactive({
    recordEnabled: true,
    recordFps: 8,
    recordDurationSeconds: 0
  }),
  updateRealtimePrefs: vi.fn((next) => {
    Object.assign(detectionStoreMock.realtimePrefs, next)
  }),
  currentResult: null,
  isProcessing: false
}

vi.mock('../../config/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: { session: { access_token: 'ws-token' } }
      })
    }
  }
}))

vi.mock('../../stores/detection', () => ({
  useDetectionStore: () => detectionStoreMock
}))

describe('Realtime', () => {
  beforeEach(() => {
    detectionStoreMock.realtimePrefs.recordEnabled = true
    detectionStoreMock.realtimePrefs.recordFps = 8
    detectionStoreMock.realtimePrefs.recordDurationSeconds = 0
    detectionStoreMock.updateRealtimePrefs.mockClear()
    detectionStoreMock.currentResult = null
    detectionStoreMock.isProcessing = false
  })

  it('点击连接后创建 WebSocket', async () => {
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }]
    }

    const wsInstances = []
    class MockWebSocket {
      constructor(url) {
        this.url = url
        this.readyState = 0
        this.listeners = {}
        wsInstances.push(this)
      }
      send = vi.fn()
      close = vi.fn()
      addEventListener = (event, handler) => {
        this.listeners[event] = this.listeners[event] || []
        this.listeners[event].push(handler)
      }
      removeEventListener = (event, handler) => {
        if (!this.listeners[event]) return
        this.listeners[event] = this.listeners[event].filter(item => item !== handler)
      }
    }

    global.WebSocket = MockWebSocket
    global.navigator.mediaDevices = {
      getUserMedia: vi.fn().mockResolvedValue(mockStream)
    }
    HTMLVideoElement.prototype.play = vi.fn()

    const wrapper = mount(Realtime)

    await wrapper.get('[data-testid="realtime-connect"]').trigger('click')
    await flushPromises()

    expect(wsInstances.length).toBe(1)
    expect(wsInstances[0].url).toContain('/ws/detect-live?token=ws-token')
  })

  it('卸载后释放连接与事件监听', async () => {
    const mockTrackStop = vi.fn()
    const mockStream = {
      getTracks: () => [{ stop: mockTrackStop }]
    }

    const wsInstances = []
    class MockWebSocket {
      constructor(url) {
        this.url = url
        this.readyState = 0
        this.listeners = {}
        wsInstances.push(this)
      }
      send = vi.fn()
      close = vi.fn()
      addEventListener = (event, handler) => {
        this.listeners[event] = this.listeners[event] || []
        this.listeners[event].push(handler)
      }
      removeEventListener = (event, handler) => {
        if (!this.listeners[event]) return
        this.listeners[event] = this.listeners[event].filter(item => item !== handler)
      }
    }

    global.WebSocket = MockWebSocket
    global.navigator.mediaDevices = {
      getUserMedia: vi.fn().mockResolvedValue(mockStream)
    }
    HTMLVideoElement.prototype.play = vi.fn()

    const wrapper = mount(Realtime)
    await wrapper.get('[data-testid="realtime-connect"]').trigger('click')
    await flushPromises()

    const ws = wsInstances[0]
    expect(ws.listeners.message?.length || 0).toBeGreaterThan(0)

    wrapper.unmount()

    expect(ws.close).toHaveBeenCalled()
    expect(ws.listeners.message?.length || 0).toBe(0)
    expect(mockTrackStop).toHaveBeenCalled()
  })

  it('主卡片禁用光晕层', () => {
    const wrapper = mount(Realtime)

    expect(wrapper.get('[data-testid="realtime-preview-card"]').classes())
      .toContain('card--no-glow')
    expect(wrapper.get('[data-testid="realtime-summary-card"]').classes())
      .toContain('card--no-glow')
    expect(wrapper.get('[data-testid="realtime-preview-card"]').classes())
      .toContain('card--no-blur')
    expect(wrapper.get('[data-testid="realtime-summary-card"]').classes())
      .toContain('card--no-blur')
  })

  it('无路由上下文时不触发路由警告', () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    mount(Realtime)

    const warned = warnSpy.mock.calls.some(call =>
      String(call[0]).includes('No active route record') ||
      String(call[0]).includes('onBeforeRouteLeave')
    )

    warnSpy.mockRestore()

    expect(warned).toBe(false)
  })

  it('录制帧率影响采集间隔', async () => {
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }]
    }

    const wsInstances = []
    class MockWebSocket {
      constructor(url) {
        this.url = url
        this.readyState = MockWebSocket.OPEN
        this.listeners = {}
        wsInstances.push(this)
      }
      send = vi.fn()
      close = vi.fn()
      addEventListener = (event, handler) => {
        this.listeners[event] = this.listeners[event] || []
        this.listeners[event].push(handler)
      }
      removeEventListener = (event, handler) => {
        if (!this.listeners[event]) return
        this.listeners[event] = this.listeners[event].filter(item => item !== handler)
      }
    }
    MockWebSocket.OPEN = 1

    global.WebSocket = MockWebSocket
    global.navigator.mediaDevices = {
      getUserMedia: vi.fn().mockResolvedValue(mockStream)
    }
    HTMLVideoElement.prototype.play = vi.fn()

    const setIntervalSpy = vi.spyOn(window, 'setInterval').mockImplementation(() => 1)

    const wrapper = mount(Realtime)
    await wrapper.get('[data-testid="realtime-connect"]').trigger('click')
    await flushPromises()

    const ws = wsInstances[0]
    ws.listeners.open?.forEach(handler => handler())
    await flushPromises()

    const fpsInput = wrapper.find('input[type="number"]')
    await fpsInput.setValue('5')

    const startButton = wrapper.findAll('button')
      .find(button => button.text().includes('开启识别'))
    await startButton.trigger('click')
    await flushPromises()

    expect(setIntervalSpy).toHaveBeenCalled()
    const interval = setIntervalSpy.mock.calls[0][1]
    expect(interval).toBe(200)

    setIntervalSpy.mockRestore()
    wrapper.unmount()
  })

  it('录制时长到期后自动结束识别', async () => {
    vi.useFakeTimers()

    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }]
    }

    const wsInstances = []
    class MockWebSocket {
      constructor(url) {
        this.url = url
        this.readyState = MockWebSocket.OPEN
        this.listeners = {}
        wsInstances.push(this)
      }
      send = vi.fn()
      close = vi.fn()
      addEventListener = (event, handler) => {
        this.listeners[event] = this.listeners[event] || []
        this.listeners[event].push(handler)
      }
      removeEventListener = (event, handler) => {
        if (!this.listeners[event]) return
        this.listeners[event] = this.listeners[event].filter(item => item !== handler)
      }
    }
    MockWebSocket.OPEN = 1

    global.WebSocket = MockWebSocket
    global.navigator.mediaDevices = {
      getUserMedia: vi.fn().mockResolvedValue(mockStream)
    }
    HTMLVideoElement.prototype.play = vi.fn()

    const setTimeoutSpy = vi.spyOn(window, 'setTimeout')

    const wrapper = mount(Realtime)
    await wrapper.get('[data-testid="realtime-connect"]').trigger('click')
    await flushPromises()

    const ws = wsInstances[0]
    ws.listeners.open?.forEach(handler => handler())
    await flushPromises()

    const durationInput = wrapper.get('[data-testid="realtime-duration"]')
    await durationInput.setValue('2')

    const startButton = wrapper.findAll('button')
      .find(button => button.text().includes('开启识别'))
    await startButton.trigger('click')
    await flushPromises()

    expect(setTimeoutSpy).toHaveBeenCalled()
    const delay = setTimeoutSpy.mock.calls[0][1]
    expect(delay).toBe(2000)

    const startPayload = JSON.parse(ws.send.mock.calls[0][0])
    expect(startPayload.recording.durationSeconds).toBe(2)

    vi.advanceTimersByTime(2000)
    const hasEnd = ws.send.mock.calls.some(call => {
      const payload = JSON.parse(call[0])
      return payload.type === 'end'
    })
    expect(hasEnd).toBe(true)

    setTimeoutSpy.mockRestore()
    wrapper.unmount()
    vi.useRealTimers()
  })

  it('帧发送异常不会导致崩溃', async () => {
    const mockTrackStop = vi.fn()
    const mockStream = {
      getTracks: () => [{ stop: mockTrackStop }]
    }

    const wsInstances = []
    class MockWebSocket {
      constructor(url) {
        this.url = url
        this.readyState = MockWebSocket.OPEN
        this.listeners = {}
        this.send = vi.fn()
        this.close = vi.fn()
        wsInstances.push(this)
      }
      addEventListener = (event, handler) => {
        this.listeners[event] = this.listeners[event] || []
        this.listeners[event].push(handler)
      }
      removeEventListener = (event, handler) => {
        if (!this.listeners[event]) return
        this.listeners[event] = this.listeners[event].filter(item => item !== handler)
      }
    }
    MockWebSocket.OPEN = 1

    global.WebSocket = MockWebSocket
    global.navigator.mediaDevices = {
      getUserMedia: vi.fn().mockResolvedValue(mockStream)
    }
    HTMLVideoElement.prototype.play = vi.fn()

    const originalGetContext = HTMLCanvasElement.prototype.getContext
    const originalToBlob = HTMLCanvasElement.prototype.toBlob
    const originalArrayBuffer = Blob.prototype.arrayBuffer

    HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
      drawImage: vi.fn()
    }))
    HTMLCanvasElement.prototype.toBlob = vi.fn((callback) => {
      callback(new Blob([new Uint8Array([1])], { type: 'image/jpeg' }))
    })
    if (!Blob.prototype.arrayBuffer) {
      Blob.prototype.arrayBuffer = vi.fn(async () => new ArrayBuffer(1))
    }

    const intervalCallbacks = []
    const setIntervalSpy = vi.spyOn(window, 'setInterval').mockImplementation((cb) => {
      intervalCallbacks.push(cb)
      return 1
    })
    const clearIntervalSpy = vi.spyOn(window, 'clearInterval').mockImplementation(() => {})

    const wrapper = mount(Realtime)
    await wrapper.get('[data-testid="realtime-connect"]').trigger('click')
    await flushPromises()

    const ws = wsInstances[0]
    ws.send = vi.fn()
      .mockImplementationOnce(() => {})
      .mockImplementationOnce(() => {
        throw new Error('socket closed')
      })

    ws.listeners.open?.forEach(handler => handler())
    await flushPromises()

    const video = wrapper.find('video').element
    Object.defineProperty(video, 'readyState', { value: 2, configurable: true })
    Object.defineProperty(video, 'videoWidth', { value: 640, configurable: true })
    Object.defineProperty(video, 'videoHeight', { value: 360, configurable: true })

    const startButton = wrapper.findAll('button')
      .find(button => button.text().includes('开启识别'))
    await startButton.trigger('click')
    await flushPromises()

    await expect(intervalCallbacks[0]()).resolves.toBeUndefined()

    setIntervalSpy.mockRestore()
    clearIntervalSpy.mockRestore()
    HTMLCanvasElement.prototype.getContext = originalGetContext
    HTMLCanvasElement.prototype.toBlob = originalToBlob
    Blob.prototype.arrayBuffer = originalArrayBuffer
    wrapper.unmount()
  })
})
