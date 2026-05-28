import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '../auth'

const getSessionMock = vi.fn()
const onAuthStateChangeMock = vi.fn()
const signInWithPasswordMock = vi.fn()
const signUpMock = vi.fn()
const signOutMock = vi.fn()
const routerPushMock = vi.fn()

vi.mock('../../config/supabase', () => ({
  supabase: {
    auth: {
      getSession: (...args) => getSessionMock(...args),
      onAuthStateChange: (...args) => onAuthStateChangeMock(...args),
      signInWithPassword: (...args) => signInWithPasswordMock(...args),
      signUp: (...args) => signUpMock(...args),
      signOut: (...args) => signOutMock(...args)
    }
  }
}))

vi.mock('../../router', () => ({
  default: {
    push: (...args) => routerPushMock(...args)
  }
}))

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    getSessionMock.mockResolvedValue({ data: { session: null }, error: null })
    onAuthStateChangeMock.mockReturnValue({
      data: { subscription: { unsubscribe: vi.fn() } }
    })
    signUpMock.mockResolvedValue({ data: {}, error: null })
    signOutMock.mockResolvedValue({})
  })

  it('登录成功后立即写入返回的用户，避免等待认证事件回填', async () => {
    const user = { id: 'user-1', email: 'demo@local.test' }
    signInWithPasswordMock.mockResolvedValue({
      data: {
        user,
        session: { access_token: 'token-1' }
      },
      error: null
    })
    const authStore = useAuthStore()

    const result = await authStore.login('demo@local.test', 'password123')

    expect(result.success).toBe(true)
    expect(authStore.user).toEqual(user)
    expect(authStore.loading).toBe(false)
  })
})
