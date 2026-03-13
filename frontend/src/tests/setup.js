import { vi } from 'vitest'

if (!global.fetch) {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: async () => ({ weights: [], history: [] })
    })
  )
}

if (!global.ResizeObserver) {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
}

if (!global.IntersectionObserver) {
  global.IntersectionObserver = class IntersectionObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
}

if (!global.URL.createObjectURL) {
  global.URL.createObjectURL = () => 'blob:mock'
}

if (!global.URL.revokeObjectURL) {
  global.URL.revokeObjectURL = () => {}
}

if (!window.matchMedia) {
  window.matchMedia = () => ({
    matches: false,
    media: '',
    onchange: null,
    addEventListener: () => {},
    removeEventListener: () => {},
    addListener: () => {},
    removeListener: () => {},
    dispatchEvent: () => false
  })
}
