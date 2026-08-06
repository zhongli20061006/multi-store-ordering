import { http } from './http'

export interface Store {
  id: number
  name: string
  address: string
  phone: string
  latitude: number | null
  longitude: number | null
  status: 'open' | 'closed'
  sort_order: number
  open_time: string | null
  close_time: string | null
}

export const storesApi = {
  listMine: () => http.get('/admin/stores') as Promise<Store[]>,
  create: (payload: Omit<Store, 'id' | 'status'>) => http.post('/admin/stores', payload),
  update: (id: number, payload: Partial<Store>) => http.put(`/admin/stores/${id}`, payload),
  setStatus: (id: number, status: Store['status']) => http.patch(`/admin/stores/${id}/status`, { status }),
  remove: (id: number) => http.delete(`/admin/stores/${id}`),
}
