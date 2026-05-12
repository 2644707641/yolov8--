import { describe, it, expect, vi } from 'vitest'
import { mount, RouterLinkStub, flushPromises } from '@vue/test-utils'
import { Transition } from 'vue'
import ModelWeights from '../ModelWeights.vue'

const authStoreMock = {
  user: { email: 'demo@local.test' },
  logout: vi.fn()
}

vi.mock('../../stores/auth', () => ({
  useAuthStore: () => authStoreMock
}))

vi.mock('../../config/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: { access_token: 'test-token' } } })
    }
  }
}))

describe('ModelWeights', () => {
  it('展示模型与权重标题', () => {
    const wrapper = mount(ModelWeights, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    expect(wrapper.get('[data-testid="model-weights-title"]').text()).toContain('模型与权重')
  })

  it('卸载时会中止权重加载请求', async () => {
    const originalAbortController = global.AbortController
    const abortSpy = vi.fn()
    class MockAbortController {
      constructor() {
        this.signal = { aborted: false }
      }
      abort() {
        this.signal.aborted = true
        abortSpy()
      }
    }
    global.AbortController = MockAbortController

    const originalFetch = global.fetch
    global.fetch = vi.fn(() => new Promise(() => {}))

    const wrapper = mount(ModelWeights, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    await flushPromises()
    expect(global.fetch).toHaveBeenCalled()

    wrapper.unmount()
    expect(abortSpy).toHaveBeenCalled()

    global.fetch = originalFetch
    global.AbortController = originalAbortController
  })

  it('在过渡动画中不会产生多根节点警告', () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const Wrapper = {
      components: { ModelWeights, Transition },
      template: '<Transition><ModelWeights /></Transition>'
    }

    mount(Wrapper, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          Transition: false
        }
      }
    })

    const warned = warnSpy.mock.calls.some(call =>
      String(call[0]).includes('non-element root node')
    )
    warnSpy.mockRestore()

    expect(warned).toBe(false)
  })

  it('加载权重成功时不输出调试日志', async () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    const originalFetch = global.fetch
    global.fetch = vi.fn(() => Promise.resolve({
      ok: true,
      json: async () => ({ weights: [] })
    }))

    const wrapper = mount(ModelWeights, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    await flushPromises()

    expect(logSpy).not.toHaveBeenCalled()

    logSpy.mockRestore()
    global.fetch = originalFetch
    wrapper.unmount()
  })

  it('卸载时清理上传成功的定时器', async () => {
    vi.useFakeTimers()
    const setTimeoutSpy = vi.spyOn(window, 'setTimeout')
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout')

    const originalFetch = global.fetch
    global.fetch = vi.fn((url, options) => {
      if (String(url).includes('/api/upload-model')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ success: true, weight: { id: 'w1' } })
        })
      }

      if (String(url).includes('/api/model-weights')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ weights: [] })
        })
      }

      return Promise.resolve({
        ok: true,
        json: async () => ({})
      })
    })

    const wrapper = mount(ModelWeights, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          Teleport: true
        }
      }
    })

    const fileInput = wrapper.get('input[type="file"]')
    const file = new File(['mock'], 'model.pt', { type: 'application/octet-stream' })
    Object.defineProperty(fileInput.element, 'files', {
      value: [file]
    })
    await fileInput.trigger('change')
    await flushPromises()

    const confirmButton = wrapper.findAll('button')
      .find(button => button.text().includes('确认上传'))
    await confirmButton.trigger('click')
    await flushPromises()

    expect(setTimeoutSpy).toHaveBeenCalled()

    wrapper.unmount()
    expect(clearTimeoutSpy).toHaveBeenCalled()

    setTimeoutSpy.mockRestore()
    clearTimeoutSpy.mockRestore()
    global.fetch = originalFetch
    vi.useRealTimers()
  })
})
