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

  it('flags must change password on login with default seed', () => {
    const store = useAuthStore()
    store.setLogin('abc', 'admin1', true)
    expect(store.isLoggedIn).toBe(true)
    expect(store.mustChangePassword).toBe(true)
    expect(localStorage.getItem('must_change_password')).toBe('1')
  })

  it('clears must change password after password changed', () => {
    const store = useAuthStore()
    store.setLogin('abc', 'admin1', true)
    store.passwordChanged()
    expect(store.mustChangePassword).toBe(false)
    expect(localStorage.getItem('must_change_password')).toBe('0')
  })

  it('setToken resets must change password', () => {
    const store = useAuthStore()
    store.setLogin('abc', 'admin1', true)
    store.setToken('abc2', 'admin1')
    expect(store.mustChangePassword).toBe(false)
    expect(localStorage.getItem('must_change_password')).toBeNull()
  })
})
