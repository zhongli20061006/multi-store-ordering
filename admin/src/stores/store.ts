import { defineStore } from 'pinia'

export interface StoreOption {
  id: number
  name: string
}

export const useCurrentStore = defineStore('currentStore', {
  state: () => ({
    id: Number(localStorage.getItem('currentStoreId')) || 0,
    name: localStorage.getItem('currentStoreName') || '',
  }),
  getters: {
    hasStore: (state) => state.id > 0,
  },
  actions: {
    select(store: StoreOption) {
      this.id = store.id
      this.name = store.name
      localStorage.setItem('currentStoreId', String(store.id))
      localStorage.setItem('currentStoreName', store.name)
    },
    clear() {
      this.id = 0
      this.name = ''
      localStorage.removeItem('currentStoreId')
      localStorage.removeItem('currentStoreName')
    },
  },
})
