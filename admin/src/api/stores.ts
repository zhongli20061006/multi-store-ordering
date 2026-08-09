import { http } from './http'

export interface Store {
  id: number
  name: string
  address: string
  phone: string
  latitude: number | null
  longitude: number | null
  image_url: string | null
  theme: 'warm' | 'white' | 'night' | 'berry'
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
  uploadImage: (id: number, file: File) =>
    http.post(`/admin/stores/${id}/image`, file, { headers: { 'Content-Type': file.type } }) as Promise<Store>,
  clearImage: (id: number) => http.delete(`/admin/stores/${id}/image`) as Promise<Store>,
  remove: (id: number) => http.delete(`/admin/stores/${id}`),
}
