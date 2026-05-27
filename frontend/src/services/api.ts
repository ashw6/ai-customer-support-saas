import axios, { type AxiosError, type AxiosRequestConfig } from 'axios'

const configuredBaseURL = import.meta.env.VITE_API_URL
const baseURL = (configuredBaseURL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')
const parsedTimeout = Number(import.meta.env.VITE_API_TIMEOUT_MS ?? 90000)
const REQUEST_TIMEOUT_MS = Number.isFinite(parsedTimeout) && parsedTimeout > 0 ? parsedTimeout : 90000

if (import.meta.env.PROD && !configuredBaseURL) {
  throw new Error('VITE_API_URL must be set for production builds.')
}

export const api = axios.create({
  baseURL,
  timeout: REQUEST_TIMEOUT_MS,
  headers: { 'Content-Type': 'application/json' },
})

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
export const AUTH_EXPIRED_EVENT = 'auth:expired'

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function getStoredRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setStoredToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export function setStoredRefreshToken(token: string | null): void {
  if (token) localStorage.setItem(REFRESH_TOKEN_KEY, token)
  else localStorage.removeItem(REFRESH_TOKEN_KEY)
}

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function isRetryable(error: AxiosError) {
  const status = error.response?.status
  return !status || status === 408 || status === 429 || status >= 500
}

api.interceptors.response.use(undefined, async (error: AxiosError) => {
  if (error.response?.status === 401) {
    const refreshToken = getStoredRefreshToken()
    if (refreshToken) {
      try {
        const { refreshToken: refreshFn } = await import('./auth.service')
        const response = await refreshFn(refreshToken)
        // Retry the original request with new token
        if (error.config) {
          error.config.headers.Authorization = `Bearer ${response.access_token}`
          return api(error.config)
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and dispatch expired event
        setStoredToken(null)
        setStoredRefreshToken(null)
        window.dispatchEvent(new CustomEvent(AUTH_EXPIRED_EVENT))
        return Promise.reject(error)
      }
    } else {
      // No refresh token, clear access token and dispatch expired event
      setStoredToken(null)
      window.dispatchEvent(new CustomEvent(AUTH_EXPIRED_EVENT))
    }
  }

  const config = error.config as (AxiosRequestConfig & { _retryCount?: number }) | undefined
  if (!config || config.method?.toLowerCase() !== 'get' || !isRetryable(error)) {
    return Promise.reject(error)
  }

  config._retryCount = config._retryCount ?? 0
  if (config._retryCount >= 2) {
    return Promise.reject(error)
  }

  const retryCount = config._retryCount + 1
  config._retryCount = retryCount
  await new Promise((resolve) => window.setTimeout(resolve, retryCount * 350))
  return api(config)
})

export function parseApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const ax = error as AxiosError<{ detail?: string | { msg: string }[]; message?: string }>
    if (ax.code === 'ECONNABORTED') return 'The request timed out. Please try again.'
    if (!ax.response) return 'Could not reach the server. Check your connection and try again.'
    const message = ax.response.data?.message
    if (typeof message === 'string' && message.trim()) return message
    const detail = ax.response.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((d) => ('msg' in d ? d.msg : JSON.stringify(d))).join(', ')
    }
    if (ax.response?.status === 401) return 'Session expired. Please sign in again.'
    if (ax.response?.status === 403) return 'You do not have access to this resource.'
  }
  if (error instanceof Error) return error.message
  return 'Something went wrong'
}
