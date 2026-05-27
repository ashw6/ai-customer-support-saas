import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { User, UserRole } from '@/types/api'
import { AUTH_EXPIRED_EVENT, getStoredToken } from '@/services/api'
import {
  clearAuthStorage,
  fetchCurrentUser,
  getStoredUser,
  login as loginRequest,
  register as registerRequest,
} from '@/services/auth.service'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string, role?: UserRole) => Promise<User>
  register: (payload: {
    name: string
    email: string
    password: string
    role?: UserRole
  }) => Promise<User>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => getStoredUser())
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = getStoredToken()
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const me = await fetchCurrentUser()
      setUser(me)
    } catch {
      clearAuthStorage()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refreshUser()
  }, [refreshUser])

  useEffect(() => {
    const handleAuthExpired = () => {
      clearAuthStorage()
      setUser(null)
    }
    window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
  }, [])

  const login = useCallback(async (email: string, password: string, role?: UserRole) => {
    const data = await loginRequest(email, password, role)
    setUser(data.user)
    return data.user
  }, [])

  const register = useCallback(
    async (payload: {
      name: string
      email: string
      password: string
      role?: UserRole
    }) => {
      const data = await registerRequest({
        name: payload.name,
        email: payload.email,
        password: payload.password,
        role: payload.role,
      })
      setUser(data.user)
      return data.user
    },
    [],
  )

  const logout = useCallback(() => {
    clearAuthStorage()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, loading, login, register, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
