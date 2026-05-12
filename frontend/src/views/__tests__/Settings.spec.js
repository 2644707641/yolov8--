import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Settings from '../Settings.vue'

const authStoreMock = {
  user: { email: 'demo@local.test' }
}

const detectionStoreMock = {
  detectionParams: {
    imgSize: 640,
    confidence: 0.5,
    iouThreshold: 0.6,
    maxDetections: 300,
    frameSkip: 1
  },
  realtimePrefs: {
    recordEnabled: true,
    recordFps: 8,
    recordDurationSeconds: 0
  },
  updateDefaults: vi.fn(),
  updateRealtimePrefs: vi.fn()
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
      getSession: vi.fn().mockResolvedValue({
        data: { session: { access_token: 'test-token' } }
      })
    }
  }
}))

describe('Settings', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('加载后端设置并渲染默认参数', async () => {
    const responsePayload = {
      success: true,
      settings: {
        defaults: {
          imgSize: 640,
          confidence: 0.77,
          iouThreshold: 0.55,
          maxDetections: 240,
          frameSkip: 2
        },
        system: {
          apiTitle: 'YOLOv8 Detection API',
          apiVersion: '1.1.0',
          defaultModelName: '默认停车位检测模型',
          maxUploadSizeMb: 200
        },
        storage: {
          retentionDays: 30,
          region: 'CN-East-1',
          backupTime: '02:00',
          mode: 'local',
          localCleanup: {
            enabled: true,
            retentionDays: 30,
            maxRecords: 500
          },
          localStats: {
            historyRecordCount: 2,
            archiveRecordCount: 1,
            uploadsFileCount: 3,
            uploadsBytes: 13,
            resultsFileCount: 2,
            resultsBytes: 19,
            totalBytes: 32,
            lastCleanupAt: null
          }
        }
      }
    }

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => responsePayload
    })

    const wrapper = mount(Settings)

    await flushPromises()

    expect(global.fetch).toHaveBeenCalled()
    expect(wrapper.get('[data-testid="setting-confidence"]').element.value).toBe('0.77')
    expect(wrapper.get('[data-testid="setting-iou"]').element.value).toBe('0.55')
    expect(wrapper.get('[data-testid="setting-img-size"]').element.value).toBe('640')
    expect(wrapper.get('[data-testid="setting-max-detections"]').element.value).toBe('240')
    expect(wrapper.get('[data-testid="setting-frame-skip"]').element.value).toBe('2')
    expect(wrapper.text()).toContain('存储模式')
    expect(wrapper.text()).toContain('本地模式')
    expect(wrapper.text()).toContain('本地自动清理')
    expect(wrapper.text()).toContain('已启用')
    expect(wrapper.text()).toContain('本地保留天数')
    expect(wrapper.text()).toContain('30 天')
    expect(wrapper.text()).toContain('最大历史记录数')
    expect(wrapper.text()).toContain('500 条')
    expect(wrapper.text()).toContain('当前本地占用')
    expect(wrapper.text()).toContain('历史记录 2 条')
    expect(wrapper.text()).toContain('归档记录 1 条')
    expect(wrapper.text()).toContain('上传目录')
    expect(wrapper.text()).toContain('结果目录')
    expect(wrapper.text()).toContain('总占用')
    expect(wrapper.text()).toContain('尚未执行')
  })

  it('按照优先级将四个设置区块纵向排列并弱化概览区', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        settings: {}
      })
    })

    const wrapper = mount(Settings)
    await flushPromises()

    const overviewStrip = wrapper.get('[data-testid="settings-overview-strip"]')
    const stack = wrapper.get('[data-testid="settings-priority-stack"]')
    const sections = stack.findAll('[data-testid^="settings-section-"]')

    expect(overviewStrip.classes()).toContain('grid')
    expect(stack.classes()).toContain('space-y-6')
    expect(sections).toHaveLength(4)
    expect(sections[0].attributes('data-testid')).toBe('settings-section-defaults')
    expect(sections[1].attributes('data-testid')).toBe('settings-section-storage')
    expect(sections[2].attributes('data-testid')).toBe('settings-section-realtime')
    expect(sections[3].attributes('data-testid')).toBe('settings-section-system')
    expect(wrapper.find('[data-testid="settings-storage-config-card"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="settings-storage-status-card"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="settings-bottom-actions"]').exists()).toBe(true)
  })

  it('保存时提交本地清理策略配置', async () => {
    const loadPayload = {
      success: true,
      settings: {
        defaults: {
          imgSize: 640,
          confidence: 0.77,
          iouThreshold: 0.55,
          maxDetections: 240,
          frameSkip: 2
        },
        system: {
          apiTitle: 'YOLOv8 Detection API',
          apiVersion: '1.1.0',
          defaultModelName: '默认停车位检测模型',
          maxUploadSizeMb: 200
        },
        storage: {
          retentionDays: 30,
          region: 'CN-East-1',
          backupTime: '02:00',
          mode: 'local',
          localCleanup: {
            enabled: true,
            retentionDays: 30,
            maxRecords: 500
          },
          localStats: {
            historyRecordCount: 2,
            archiveRecordCount: 1,
            uploadsFileCount: 3,
            uploadsBytes: 13,
            resultsFileCount: 2,
            resultsBytes: 19,
            totalBytes: 32,
            lastCleanupAt: null
          }
        }
      }
    }

    const savePayload = {
      success: true,
      settings: {
        ...loadPayload.settings,
        storage: {
          ...loadPayload.settings.storage,
          localCleanup: {
            enabled: false,
            retentionDays: 14,
            maxRecords: 120
          },
          localStats: {
            historyRecordCount: 2,
            archiveRecordCount: 1,
            uploadsFileCount: 3,
            uploadsBytes: 13,
            resultsFileCount: 2,
            resultsBytes: 19,
            totalBytes: 32,
            lastCleanupAt: null
          }
        }
      }
    }

    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => loadPayload
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => savePayload
      })
    global.fetch = fetchMock

    const wrapper = mount(Settings)
    await flushPromises()

    await wrapper.get('[data-testid="setting-local-cleanup-enabled"]').setValue(false)
    await wrapper.get('[data-testid="setting-local-cleanup-retention-days"]').setValue('14')
    await wrapper.get('[data-testid="setting-local-cleanup-max-records"]').setValue('120')
    await wrapper.get('[data-testid="settings-save"]').trigger('click')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledTimes(2)
    const [, saveRequest] = fetchMock.mock.calls[1]
    const savedBody = JSON.parse(saveRequest.body)
    expect(savedBody.defaults).toEqual({
      imgSize: 640,
      confidence: 0.77,
      iouThreshold: 0.55,
      maxDetections: 240,
      frameSkip: 2
    })
    expect(savedBody.storage).toEqual({
      localCleanup: {
        enabled: false,
        retentionDays: 14,
        maxRecords: 120
      }
    })
    expect(savedBody.realtime).toEqual({
      recordEnabled: true,
      recordFps: 8,
      recordDurationSeconds: 0,
      sourceMode: 'camera',
      networkStreamUrl: ''
    })
    expect(wrapper.text()).toContain('未启用')
    expect(wrapper.text()).toContain('14 天')
    expect(wrapper.text()).toContain('120 条')
  })

  it('可以立即执行一次本地清理并刷新占用统计', async () => {
    const loadPayload = {
      success: true,
      settings: {
        defaults: {
          imgSize: 640,
          confidence: 0.77,
          iouThreshold: 0.55,
          maxDetections: 240,
          frameSkip: 2
        },
        system: {
          apiTitle: 'YOLOv8 Detection API',
          apiVersion: '1.1.0',
          defaultModelName: '默认停车位检测模型',
          maxUploadSizeMb: 200
        },
        storage: {
          retentionDays: 30,
          region: 'CN-East-1',
          backupTime: '02:00',
          mode: 'local',
          localCleanup: {
            enabled: true,
            retentionDays: 30,
            maxRecords: 500
          },
          localStats: {
            historyRecordCount: 2,
            archiveRecordCount: 1,
            uploadsFileCount: 3,
            uploadsBytes: 13,
            resultsFileCount: 2,
            resultsBytes: 19,
            totalBytes: 32,
            lastCleanupAt: null
          }
        }
      }
    }

    const cleanupPayload = {
      success: true,
      cleanup: {
        removedRecords: 1,
        removedArchives: 0,
        removedFiles: 4
      },
      settings: {
        ...loadPayload.settings,
        storage: {
          ...loadPayload.settings.storage,
          localStats: {
            historyRecordCount: 1,
            archiveRecordCount: 1,
            uploadsFileCount: 1,
            uploadsBytes: 4,
            resultsFileCount: 1,
            resultsBytes: 8,
            totalBytes: 12,
            lastCleanupAt: '2026-03-13T10:00:00+00:00'
          }
        }
      }
    }

    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => loadPayload
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => cleanupPayload
      })
    global.fetch = fetchMock

    const wrapper = mount(Settings)
    await flushPromises()

    await wrapper.get('[data-testid="settings-run-cleanup"]').trigger('click')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock.mock.calls[1][0]).toContain('/api/settings/storage/cleanup')
    expect(fetchMock.mock.calls[1][1].method).toBe('POST')
    expect(wrapper.text()).toContain('本地清理已完成')
    expect(wrapper.text()).toContain('历史记录 1 条')
    expect(wrapper.text()).toContain('上传目录 1 个文件')
    expect(wrapper.text()).toContain('总占用')
    expect(wrapper.text()).not.toContain('尚未执行')
  })
})
