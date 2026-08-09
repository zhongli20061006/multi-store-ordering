import { http } from './http'

export interface LoginPayload {
  username: string
  password: string
}

export async function login(payload: LoginPayload) {
  return http.post('/auth/login', payload) as Promise<{
    access_token: string
    must_change_password: boolean
  }>
}

export async function getMe() {
  return http.get('/auth/me') as Promise<{
    id: number
    username: string
    display_name: string
    must_change_password: boolean
  }>
}

export async function changePassword(old_password: string, new_password: string) {
  return http.post('/auth/change-password', { old_password, new_password }) as Promise<{ changed: boolean }>
}
