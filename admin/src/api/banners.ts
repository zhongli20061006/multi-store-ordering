import { http } from './http'

export interface Banner {
  id: number
  store_id: number
  image_url: string
  sort_order: number
  is_active: boolean
}

export const bannersApi = {
  list: (storeId: number) => http.get(`/admin/stores/${storeId}/banners`) as Promise<Banner[]>,
  create: (storeId: number, file: File) =>
    http.post(`/admin/stores/${storeId}/banners`, file, { headers: { 'Content-Type': file.type } }) as Promise<Banner>,
  update: (storeId: number, id: number, payload: Partial<Pick<Banner, 'sort_order' | 'is_active'>>) =>
    http.put(`/admin/stores/${storeId}/banners/${id}`, payload) as Promise<Banner>,
  remove: (storeId: number, id: number) => http.delete(`/admin/stores/${storeId}/banners/${id}`),
}
