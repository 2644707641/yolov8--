import { beforeEach, describe, it, expect, vi } from 'vitest'
import { mount, RouterLinkStub, flushPromises } from '@vue/test-utils'
import History from '../History.vue'

const authStoreMock = {
  user: { email: 'demo@local.test' },
  logout: vi.fn()
}

const detectionStoreMock = {
  detectionHistory: [],
  historyLoading: false,
  historyError: '',
  lastHistorySyncAt: 0,
  loadHistory: vi.fn().mockResolvedValue([]),
  deleteHistory: vi.fn().mockResolvedValue({ success: true })
}

vi.mock('../../stores/auth', () => ({
  useAuthStore: () => authStoreMock
}))

vi.mock('../../stores/detection', () => ({
  useDetectionStore: () => detectionStoreMock
}))

describe('History', () => {
  beforeEach(() => {
    detectionStoreMock.detectionHistory = []
    detectionStoreMock.historyLoading = false
    detectionStoreMock.historyError = ''
    detectionStoreMock.lastHistorySyncAt = 0
    detectionStoreMock.loadHistory = vi.fn().mockResolvedValue([])
    detectionStoreMock.deleteHistory = vi.fn().mockResolvedValue({ success: true })
  })

  it('展示历史记录中心标题', () => {
    const wrapper = mount(History, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    expect(wrapper.get('[data-testid="history-title"]').text()).toContain('历史记录中心')
  })

  it('加载中显示转圈动画', async () => {
    let resolveLoad
    const pending = new Promise(resolve => {
      resolveLoad = resolve
    })
    detectionStoreMock.historyLoading = true
    detectionStoreMock.loadHistory = vi.fn().mockReturnValue(pending)

    const wrapper = mount(History, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    await flushPromises()

    expect(wrapper.find('[data-testid="history-loading"]').exists()).toBe(true)

    detectionStoreMock.historyLoading = false
    resolveLoad()
    wrapper.unmount()
  })

  it('加载完成后隐藏转圈动画', async () => {
    detectionStoreMock.loadHistory = vi.fn().mockResolvedValue([])

    const wrapper = mount(History, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    await flushPromises()

    expect(wrapper.find('[data-testid="history-loading"]').exists()).toBe(false)
  })

  it('点击刷新按钮时强制重新拉取数据库最新历史记录', async () => {
    detectionStoreMock.loadHistory = vi.fn().mockResolvedValue([])

    const wrapper = mount(History, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    await flushPromises()
    detectionStoreMock.loadHistory.mockClear()

    await wrapper.get('[data-testid="history-refresh"]').trigger('click')

    expect(detectionStoreMock.loadHistory).toHaveBeenCalledTimes(1)
    expect(detectionStoreMock.loadHistory).toHaveBeenCalledWith({ force: true })
  })

  it('存在同步错误时展示统一错误提示', async () => {
    detectionStoreMock.historyError = '历史记录同步失败'

    const wrapper = mount(History, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    await flushPromises()

    expect(wrapper.get('[data-testid="history-error"]').text()).toContain('历史记录同步失败')
    detectionStoreMock.historyError = ''
  })
})
