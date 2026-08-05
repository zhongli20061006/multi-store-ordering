import { http } from './http'

export interface LoginPayload {
  username: string
  password: string
}

export async function login(payload: LoginPayload) {
  return http.post('/auth/login', payload) as Promise<{ access_token: string }>
}
