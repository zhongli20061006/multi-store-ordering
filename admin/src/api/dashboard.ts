import { http } from './http'

export interface DashboardRow {
  date: string
  order_count: number
  revenue_cents: number
}

export interface DashboardData {
  daily: DashboardRow[]
  today: { order_count: number; pending: number; completed: number; revenue_cents: number }
}

export const dashboardApi = {
  get: (storeId: number) => http.get(`/admin/stores/${storeId}/dashboard`) as Promise<DashboardData>,
}
