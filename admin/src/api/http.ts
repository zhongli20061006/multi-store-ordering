import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  timeout: 10000,
})

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) config.headers.Authorization = `Bearer ${auth.token}`
  return config
})

http.interceptors.response.use(
  (resp) => resp.data.data,
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.message || '请求失败'
    if (status === 401) {
      useAuthStore().logout()
      window.location.href = '/login'
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  },
)
