import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import type { UserRole } from '@/types/api'
import { useAuth } from '@/context/AuthContext'
import { dashboardPathForRole } from '@/lib/paths'
import { SessionSkeleton } from '@/components/LoadingState'

interface ProtectedRouteProps {
  children: ReactNode
  roles?: UserRole[]
}

export function ProtectedRoute({ children, roles }: ProtectedRouteProps) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <SessionSkeleton />
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (roles && roles.length > 0 && !roles.includes(user.role)) {
    return <Navigate to={dashboardPathForRole(user.role)} replace />
  }

  return <>{children}</>
}
