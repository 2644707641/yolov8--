import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '../../stores/auth'
import AppShell from '../AppShell.vue'

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    useRoute: () => ({
      path: '/overview',
      meta: { title: '系统概览' }
    })
  }
})

vi.mock('../../config/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
      onAuthStateChange: vi.fn().mockReturnValue({
        data: { subscription: { unsubscribe: vi.fn() } }
      }),
      signOut: vi.fn().mockResolvedValue({})
    }
  }
}))

describe('AppShell', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const authStore = useAuthStore()
    authStore.user = { email: 'demo@local.test' }
  })

  it('渲染系统主导航入口', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    expect(wrapper.get('[data-testid="nav-overview"]').text()).toContain('系统概览')
    expect(wrapper.get('[data-testid="nav-workspace"]').text()).toContain('识别工作台')
    expect(wrapper.get('[data-testid="nav-history"]').text()).toContain('历史记录')
    expect(wrapper.get('[data-testid="nav-models"]').text()).toContain('模型管理')
    expect(wrapper.get('[data-testid="nav-realtime"]').text()).toContain('实时监控')
    expect(wrapper.get('[data-testid="nav-settings"]').text()).toContain('系统设置')
  })

  it('导航入口包含图标', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    const navIds = [
      'nav-overview',
      'nav-workspace',
      'nav-history',
      'nav-models',
      'nav-realtime',
      'nav-settings'
    ]

    navIds.forEach((id) => {
      expect(wrapper.find(`[data-testid="${id}"] svg`).exists()).toBe(true)
    })
  })

  it('图标为装饰用途时设置无障碍属性', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    const navIds = [
      'nav-overview',
      'nav-workspace',
      'nav-history',
      'nav-models',
      'nav-realtime',
      'nav-settings'
    ]

    navIds.forEach((id) => {
      const icon = wrapper.find(`[data-testid="${id}"] svg`)
      expect(icon.attributes('aria-hidden')).toBe('true')
      expect(icon.attributes('focusable')).toBe('false')
    })
  })

  it('收缩后文字进入逐字淡出动画并显示提示标签', async () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    await wrapper.get('[data-testid="nav-collapse"]').trigger('click')

    const label = wrapper.get('[data-testid="nav-overview-label"]')
    expect(label.classes()).toContain('max-w-0')
    expect(label.classes()).toContain('nav-label')
    const letters = wrapper.findAll('[data-testid="nav-overview-letter"]')
    expect(letters).toHaveLength(4)
    expect(letters[0].classes()).toContain('opacity-0')
    expect(letters[0].classes()).toContain('-translate-y-1')
    expect(letters[0].classes()).toContain('duration-500')
    expect(letters[0].classes()).toContain('ease-[cubic-bezier(0.22,1,0.36,1)]')
    expect(letters[0].attributes('style')).toContain('transition-delay: 0ms')
    expect(letters[1].attributes('style')).toContain('transition-delay: 40ms')
    expect(wrapper.find('[data-testid="nav-overview-tooltip"]').exists()).toBe(true)
  })

  it('收缩后侧边栏保持舒适宽度', async () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    await wrapper.get('[data-testid="nav-collapse"]').trigger('click')

    expect(wrapper.get('aside').classes()).toContain('w-28')
    expect(wrapper.get('aside').classes()).toContain('duration-500')
    expect(wrapper.get('aside').classes()).toContain('ease-[cubic-bezier(0.22,1,0.36,1)]')
  })

  it('收缩时头部保持单行布局', async () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    await wrapper.get('[data-testid="nav-collapse"]').trigger('click')

    const headerRow = wrapper.get('[data-testid="nav-header"]')
    expect(headerRow.classes()).toContain('justify-between')
    expect(headerRow.classes()).not.toContain('flex-col')
  })

  it('展开时品牌标题容器保持完整高度', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    const brand = wrapper.get('[data-testid="nav-brand"]')
    expect(brand.classes()).toContain('max-h-[72px]')
    expect(brand.classes()).toContain('opacity-100')
  })

  it('收缩时品牌标题容器高度收起', async () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    await wrapper.get('[data-testid="nav-collapse"]').trigger('click')

    const brand = wrapper.get('[data-testid="nav-brand"]')
    expect(brand.classes()).toContain('max-h-0')
    expect(brand.classes()).toContain('opacity-0')
  })

  it('侧边栏标题支持逐字动画', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    const letters = wrapper.findAll('[data-testid="nav-title-letter"]')
    expect(letters).toHaveLength(7)
    expect(letters[0].classes()).toContain('opacity-100')
    expect(letters[0].classes()).toContain('translate-y-0')
    expect(letters[0].classes()).toContain('duration-500')
    expect(letters[0].classes()).toContain('ease-[cubic-bezier(0.22,1,0.36,1)]')
    expect(letters[0].attributes('style')).toContain('transition-delay: 0ms')
    expect(letters[1].attributes('style')).toContain('transition-delay: 40ms')
  })

  it('收缩时标题逐字淡出', async () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    await wrapper.get('[data-testid="nav-collapse"]').trigger('click')

    const letters = wrapper.findAll('[data-testid="nav-title-letter"]')
    expect(letters[0].classes()).toContain('opacity-0')
    expect(letters[0].classes()).toContain('-translate-y-1')
  })

  it('收缩后图标保持舒适尺寸', async () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    await wrapper.get('[data-testid="nav-collapse"]').trigger('click')

    const iconWrap = wrapper.get('[data-testid="nav-overview"] span.flex')
    expect(iconWrap.classes()).toContain('h-10')
    expect(iconWrap.classes()).toContain('w-10')
  })

  it('展开时文字逐字淡入展开并隐藏提示标签', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    const label = wrapper.get('[data-testid="nav-overview-label"]')
    expect(label.classes()).toContain('max-w-[200px]')
    expect(label.classes()).toContain('nav-label')
    const letters = wrapper.findAll('[data-testid="nav-overview-letter"]')
    expect(letters).toHaveLength(4)
    expect(letters[0].classes()).toContain('opacity-100')
    expect(letters[0].classes()).toContain('translate-y-0')
    expect(letters[0].classes()).toContain('duration-500')
    expect(letters[0].classes()).toContain('ease-[cubic-bezier(0.22,1,0.36,1)]')
    expect(letters[0].attributes('style')).toContain('transition-delay: 0ms')
    expect(letters[1].attributes('style')).toContain('transition-delay: 40ms')
    expect(wrapper.find('[data-testid="nav-overview-tooltip"]').exists()).toBe(false)
  })

  it('将滚动限制在内容区并保持顶部标头固定', () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    expect(wrapper.get('[data-testid="app-shell-root"]').classes()).toContain('h-screen')
    expect(wrapper.get('[data-testid="app-shell-root"]').classes()).toContain('overflow-hidden')
    expect(wrapper.get('[data-testid="app-shell-main-column"]').classes()).toContain('overflow-hidden')
    expect(wrapper.get('[data-testid="app-shell-header"]').classes()).toContain('sticky')
    expect(wrapper.get('[data-testid="app-shell-header"]').classes()).toContain('shrink-0')
    expect(wrapper.get('[data-testid="app-shell-content"]').classes()).toContain('min-h-0')
    expect(wrapper.get('[data-testid="app-shell-content"]').classes()).toContain('overflow-y-auto')
  })

  it('移动侧栏仅在导航内容溢出时滚动且头部保持固定', async () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    })

    await wrapper.get('[data-testid="mobile-nav-toggle"]').trigger('click')

    expect(wrapper.get('[data-testid="mobile-nav-panel"]').classes()).toContain('overflow-hidden')
    expect(wrapper.get('[data-testid="mobile-nav-header"]').classes()).toContain('shrink-0')
    expect(wrapper.get('[data-testid="mobile-nav-scroll"]').classes()).toContain('min-h-0')
    expect(wrapper.get('[data-testid="mobile-nav-scroll"]').classes()).toContain('overflow-y-auto')
  })
})
