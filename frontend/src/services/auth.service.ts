import type { AuthResponse, PasswordResetResponse, User } from '@/types/api'
import { api, setStoredToken, setStoredRefreshToken } from './api'

const USER_KEY = 'user'

export function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as User
  } catch {
    return null
  }
}

export function setStoredUser(user: User | null): void {
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
  else localStorage.removeItem(USER_KEY)
}

export function clearAuthStorage(): void {
  setStoredToken(null)
  setStoredRefreshToken(null)
  setStoredUser(null)
}

export async function login(email: string, password: string, role?: string): Promise<AuthResponse> {
  const payload: { email: string; password: string; role?: string } = { email, password }
  if (role) {
    payload.role = role
  }
  const { data } = await api.post<AuthResponse>('/auth/login', payload)
  setStoredToken(data.access_token)
  if (data.refresh_token) {
    setStoredRefreshToken(data.refresh_token)
  }
  setStoredUser(data.user)
  return data
}

export async function register(payload: {
  name: string
  email: string
  password: string
  role?: string
}): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/auth/register', payload)
  setStoredToken(data.access_token)
  if (data.refresh_token) {
    setStoredRefreshToken(data.refresh_token)
  }
  setStoredUser(data.user)
  return data
}

export async function requestPasswordReset(email: string): Promise<PasswordResetResponse> {
  const { data } = await api.post<PasswordResetResponse>('/auth/forgot-password', { email })
  return data
}

export async function resetPassword(token: string, password: string): Promise<string> {
  const { data } = await api.post<{ message: string }>('/auth/reset-password', { token, password })
  return data.message
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await api.get<User>('/auth/me')
  setStoredUser(data)
  return data
}

export async function refreshToken(refreshToken: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken })
  setStoredToken(data.access_token)
  if (data.refresh_token) {
    setStoredRefreshToken(data.refresh_token)
  }
  setStoredUser(data.user)
  return data
}
