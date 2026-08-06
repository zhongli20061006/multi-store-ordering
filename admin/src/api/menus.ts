import { http } from './http'

export interface Category {
  id: number
  name: string
  sort_order: number
  is_active: boolean
}

export interface Item {
  id: number
  name: string
  description?: string | null
  price_cents: number
  stock?: number | null
  image_url?: string | null
  category_id?: number | null
  is_active: boolean
  sort_order: number
}

export const menusApi = {
  categories: (storeId: number) => http.get(`/admin/stores/${storeId}/categories`) as Promise<Category[]>,
  createCategory: (storeId: number, payload: Omit<Category, 'id'>) =>
    http.post(`/admin/stores/${storeId}/categories`, payload),
  updateCategory: (storeId: number, id: number, payload: Omit<Category, 'id'>) =>
    http.put(`/admin/stores/${storeId}/categories/${id}`, payload),
  deleteCategory: (storeId: number, id: number) => http.delete(`/admin/stores/${storeId}/categories/${id}`),
  items: (storeId: number) => http.get(`/admin/stores/${storeId}/items`) as Promise<Item[]>,
  createItem: (storeId: number, payload: Omit<Item, 'id'>) => http.post(`/admin/stores/${storeId}/items`, payload),
  updateItem: (storeId: number, id: number, payload: Partial<Item>) => http.put(`/admin/stores/${storeId}/items/${id}`, payload),
  deleteItem: (storeId: number, id: number) => http.delete(`/admin/stores/${storeId}/items/${id}`),
  uploadItemImage: (storeId: number, itemId: number, file: File) =>
    http.put(`/admin/stores/${storeId}/items/${itemId}/image`, file, { headers: { 'Content-Type': file.type } }) as Promise<Item>,
  clearItemImage: (storeId: number, itemId: number) =>
    http.delete(`/admin/stores/${storeId}/items/${itemId}/image`) as Promise<Item>,
}
