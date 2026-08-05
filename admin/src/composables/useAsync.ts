import { ref } from 'vue'

export function useAsync<T>(fn: () => Promise<T>) {
  const loading = ref(false)
  const error = ref('')

  async function run(): Promise<T | undefined> {
    loading.value = true
    error.value = ''
    try {
      return await fn()
    } catch (e: unknown) {
      const detail = (e as { response?: { data?: { message?: string } } })?.response?.data?.message
      error.value = detail || '加载失败'
      return undefined
    } finally {
      loading.value = false
    }
  }

  return { loading, error, run }
}
