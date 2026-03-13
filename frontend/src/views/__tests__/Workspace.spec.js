import { beforeEach, describe, it, expect, vi } from 'vitest'
import { mount, RouterLinkStub, flushPromises } from '@vue/test-utils'
import Dashboard from '../Dashboard.vue'

const authStoreMock = {
  user: { email: 'demo@local.test' },
  logout: vi.fn()
}

const detectionStoreMock = {
  modelFile: null,
  modelUploaded: false,
  detectionParams: {
    imgSize: 640,
    confidence: 0.5,
    iouThreshold: 0.6,
    maxDetections: 300,
    frameSkip: 1
  },
  isProcessing: false,
  detectionHistory: [],
  currentResult: null,
  uploadModel: vi.fn().mockResolvedValue({ success: true }),
  runDetection: vi.fn().mockResolvedValue({ success: true }),
  loadHistory: vi.fn().mockResolvedValue([])
}

vi.mock('../../stores/auth', () => ({
  useAuthStore: () => authStoreMock
}))

vi.mock('../../stores/detection', () => ({
  useDetectionStore: () => detectionStoreMock
}))

vi.mock('../../config/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } })
    }
  }
}))

describe('Workspace', () => {
  beforeEach(() => {
    detectionStoreMock.modelFile = null
    detectionStoreMock.modelUploaded = false
    detectionStoreMock.isProcessing = false
    detectionStoreMock.currentResult = null
    detectionStoreMock.uploadModel = vi.fn().mockResolvedValue({ success: true })
    detectionStoreMock.runDetection = vi.fn().mockResolvedValue({ success: true })
    detectionStoreMock.loadHistory = vi.fn().mockResolvedValue([])
  })

  it('展示识别工作台标题', () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    expect(wrapper.get('[data-testid="workspace-title"]').text()).toContain('识别工作台')
  })

  it('不支持的文件类型改为页内提示而不是浏览器弹窗', async () => {
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})
    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    const uploadStepButton = wrapper.findAll('button').find(button => button.text().includes('上传文件'))
    await uploadStepButton.trigger('click')

    const invalidFile = new File(['demo'], 'demo.txt', { type: 'text/plain' })
    const fileInput = wrapper.get('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [invalidFile],
      configurable: true
    })
    await fileInput.trigger('change')

    expect(alertSpy).not.toHaveBeenCalled()
    expect(wrapper.get('[data-testid="workspace-notice"]').text()).toContain('暂不支持该文件类型')

    alertSpy.mockRestore()
  })

  it('识别失败时显示页内错误提示并返回参数步骤', async () => {
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})
    detectionStoreMock.modelUploaded = true
    detectionStoreMock.runDetection = vi.fn().mockResolvedValue({
      success: false,
      error: '后端识别失败'
    })

    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub
        }
      }
    })

    const uploadStepButton = wrapper.findAll('button').find(button => button.text().includes('上传文件'))
    await uploadStepButton.trigger('click')

    const imageFile = new File(['demo'], 'demo.jpg', { type: 'image/jpeg' })
    const fileInput = wrapper.get('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [imageFile],
      configurable: true
    })
    await fileInput.trigger('change')

    const nextButton = wrapper.findAll('button').find(button => button.text().includes('前往参数调优'))
    await nextButton.trigger('click')

    const runButton = wrapper.findAll('button').find(button => button.text().includes('开始识别'))
    await runButton.trigger('click')
    await flushPromises()

    expect(alertSpy).not.toHaveBeenCalled()
    expect(detectionStoreMock.runDetection).toHaveBeenCalled()
    expect(wrapper.get('[data-testid="workspace-notice"]').text()).toContain('后端识别失败')
    expect(wrapper.text()).toContain('智能调参')

    alertSpy.mockRestore()
  })
})
