import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { installLocalStorageMock } from '@/test/localStorageMock'
import { useCurrentStore } from '../store'

describe('current store', () => {
  beforeEach(() => {
    installLocalStorageMock()
    setActivePinia(createPinia())
  })

  it('persists selected store', () => {
    const store = useCurrentStore()
    store.select({ id: 1, name: '中山路店' })
    expect(store.hasStore).toBe(true)
    expect(localStorage.getItem('currentStoreId')).toBe('1')
  })

  it('clears on logout', () => {
    const store = useCurrentStore()
    store.select({ id: 1, name: '中山路店' })
    store.clear()
    expect(store.hasStore).toBe(false)
  })
})
