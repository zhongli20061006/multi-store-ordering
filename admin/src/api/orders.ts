import { http } from './http'

export interface Order {
  id: number
  order_no: string
  store_id: number
  entry_type: 'preorder' | 'dinein'
  customer_name: string
  customer_phone: string
  item_count: number
  total_cents: number
  order_status: 'pending' | 'accepted' | 'completed' | 'cancelled'
  payment_status: 'unpaid' | 'paid'
  created_at: string
}

export interface OrderItem {
  id: number
  item_name: string
  unit_price_cents: number
  quantity: number
  subtotal_cents: number
}

export interface OrderDetail extends Order {
  remark?: string | null
  items: OrderItem[]
}

export interface OrderListData {
  items: Order[]
  total: number
  stats: { today: number; pending: number; completed: number; revenue_today: number }
}

export interface AuditLog {
  id: number
  action: string
  actor_type: 'merchant' | 'customer'
  actor_id: number | null
  detail: Record<string, unknown> | null
  created_at: string
}

export const ordersApi = {
  list: (params: {
    store_id?: number
    order_status?: string
    keyword?: string
    date_from?: string
    date_to?: string
    page?: number
    page_size?: number
  }) => http.get('/admin/orders', { params }) as Promise<OrderListData>,
  exportCsv: (params: {
    store_id?: number
    order_status?: string
    keyword?: string
    date_from?: string
    date_to?: string
  }) =>
    http.get('/admin/orders/export', { params, responseType: 'blob' }) as Promise<Blob>,
  detail: (id: number) => http.get(`/admin/orders/${id}`) as Promise<OrderDetail>,
  audit: (id: number) => http.get(`/admin/orders/${id}/audit`) as Promise<AuditLog[]>,
  updateStatus: (id: number, order_status: string) => http.patch(`/admin/orders/${id}/status`, { order_status }),
  cancel: (id: number, cancel_reason: 'merchant_cancel_not_made' | 'merchant_cancel_made') =>
    http.post(`/admin/orders/${id}/cancel`, { cancel_reason }),
  markPaid: (id: number) => http.patch(`/admin/orders/${id}/payment`, { payment_status: 'paid' }),
}
