import { lazy, Suspense, type ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { useAuth } from '@/context/AuthContext'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage'
import { ResetPasswordPage } from '@/pages/ResetPasswordPage'
import { dashboardPathForRole } from '@/lib/paths'
import { LoadingState, SessionSkeleton } from '@/components/LoadingState'

const CustomerDashboardPage = lazy(() =>
  import('@/pages/CustomerDashboardPage').then((module) => ({ default: module.CustomerDashboardPage })),
)
const SupportDashboardPage = lazy(() =>
  import('@/pages/SupportDashboardPage').then((module) => ({ default: module.SupportDashboardPage })),
)
const AdminDashboardPage = lazy(() =>
  import('@/pages/AdminDashboardPage').then((module) => ({ default: module.AdminDashboardPage })),
)
const TicketDetailPage = lazy(() =>
  import('@/pages/TicketDetailPage').then((module) => ({ default: module.TicketDetailPage })),
)
const ChatPage = lazy(() =>
  import('@/pages/ChatPage').then((module) => ({ default: module.ChatPage })),
)
const DocumentsPage = lazy(() =>
  import('@/pages/DocumentsPage').then((module) => ({ default: module.DocumentsPage })),
)

function RouteBoundary({ children, label }: { children: ReactNode; label: string }) {
  return (
    <ErrorBoundary label={label}>
      <Suspense fallback={<LoadingState label="Loading page..." className="min-h-[50vh]" />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  )
}

function HomeRedirect() {
  const { user, loading } = useAuth()
  if (loading) {
    return <SessionSkeleton />
  }
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={dashboardPathForRole(user.role)} replace />
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route
        path="/customer/dashboard"
        element={
          <ProtectedRoute roles={['customer']}>
            <RouteBoundary label="Customer dashboard">
              <CustomerDashboardPage />
            </RouteBoundary>
          </ProtectedRoute>
        }
      />
      <Route
        path="/support/dashboard"
        element={
          <ProtectedRoute roles={['support_agent']}>
            <RouteBoundary label="Support dashboard">
              <SupportDashboardPage />
            </RouteBoundary>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute roles={['admin']}>
            <RouteBoundary label="Admin dashboard">
              <AdminDashboardPage />
            </RouteBoundary>
          </ProtectedRoute>
        }
      />
      <Route
        path="/tickets/:id"
        element={
          <ProtectedRoute>
            <RouteBoundary label="Ticket detail">
              <TicketDetailPage />
            </RouteBoundary>
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <RouteBoundary label="AI chat">
              <ChatPage />
            </RouteBoundary>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/documents"
        element={
          <ProtectedRoute roles={['admin', 'support_agent']}>
            <RouteBoundary label="AI documents">
              <DocumentsPage />
            </RouteBoundary>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
