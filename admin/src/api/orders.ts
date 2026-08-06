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

export const ordersApi = {
  list: (params: { store_id?: number; order_status?: string; keyword?: string }) =>
    http.get('/admin/orders', { params }) as Promise<Order[]>,
  detail: (id: number) => http.get(`/admin/orders/${id}`) as Promise<OrderDetail>,
  updateStatus: (id: number, order_status: string) => http.patch(`/admin/orders/${id}/status`, { order_status }),
  cancel: (id: number, cancel_reason: 'merchant_cancel_not_made' | 'merchant_cancel_made') =>
    http.post(`/admin/orders/${id}/cancel`, { cancel_reason }),
  markPaid: (id: number) => http.patch(`/admin/orders/${id}/payment`, { payment_status: 'paid' }),
}
