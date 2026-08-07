import { http } from './http'

export interface AuditLogRow {
  id: number
  order_id: number
  order_no: string
  store_id: number
  store_name: string
  action: string
  actor_type: 'merchant' | 'customer'
  actor_id: number | null
  detail: Record<string, unknown> | null
  created_at: string
}

export interface AuditListData {
  items: AuditLogRow[]
  total: number
}

export const auditApi = {
  list: (params: { store_id?: number; date_from?: string; date_to?: string; page?: number; page_size?: number }) =>
    http.get('/admin/audit-logs', { params }) as Promise<AuditListData>,
  exportCsv: (params: { store_id?: number; date_from?: string; date_to?: string }) =>
    http.get('/admin/audit-logs/export', { params, responseType: 'blob' }) as Promise<Blob>,
}
