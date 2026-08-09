import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
    mustChangePassword: localStorage.getItem('must_change_password') === '1',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    setToken(token: string, username: string) {
      this.token = token
      this.username = username
      this.mustChangePassword = false
      localStorage.setItem('token', token)
      localStorage.setItem('username', username)
      localStorage.removeItem('must_change_password')
    },
    setLogin(token: string, username: string, mustChangePassword: boolean) {
      this.token = token
      this.username = username
      this.mustChangePassword = mustChangePassword
      localStorage.setItem('token', token)
      localStorage.setItem('username', username)
      localStorage.setItem('must_change_password', mustChangePassword ? '1' : '0')
    },
    passwordChanged() {
      this.mustChangePassword = false
      localStorage.setItem('must_change_password', '0')
    },
    logout() {
      this.token = ''
      this.username = ''
      this.mustChangePassword = false
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('must_change_password')
    },
  },
})
