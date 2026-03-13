import { describe, it, expect } from 'vitest'
import { routes } from '../index'

describe('路由结构', () => {
  it('包含系统布局与核心页面', () => {
    const appShellRoute = routes.find(route => route.path === '/')
    expect(appShellRoute).toBeTruthy()
    expect(appShellRoute.children?.length).toBeGreaterThan(0)

    const redirectChild = appShellRoute.children.find(child => child.path === '')
    expect(redirectChild?.redirect).toBe('/overview')

    const childPaths = appShellRoute.children.map(child => child.path)
    expect(childPaths).toContain('overview')
    expect(childPaths).toContain('workspace')
    expect(childPaths).toContain('history')
    expect(childPaths).toContain('model-weights')
    expect(childPaths).toContain('realtime')
    expect(childPaths).toContain('settings')
  })
})
