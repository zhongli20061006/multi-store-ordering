import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { installLocalStorageMock } from '@/test/localStorageMock'
import { useAuthStore } from '../auth'

describe('auth store', () => {
  beforeEach(() => {
    installLocalStorageMock()
    setActivePinia(createPinia())
  })

  it('stores token after login', () => {
    const store = useAuthStore()
    expect(store.isLoggedIn).toBe(false)
    store.setToken('abc', 'admin1')
    expect(store.isLoggedIn).toBe(true)
    expect(localStorage.getItem('token')).toBe('abc')
  })

  it('clears token on logout', () => {
    const store = useAuthStore()
    store.setToken('abc', 'admin1')
    store.logout()
    expect(store.isLoggedIn).toBe(false)
    expect(localStorage.getItem('token')).toBeNull()
  })
})
