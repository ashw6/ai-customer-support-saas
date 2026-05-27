import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { SessionSkeleton } from '@/components/LoadingState'
import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import { parseApiError } from '@/services/api'
import { dashboardPathForRole } from '@/lib/paths'
import type { UserRole } from '@/types/api'

export function LoginPage() {
  const { login, user, loading } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!loading && user) {
      navigate(dashboardPathForRole(user.role), { replace: true })
    }
  }, [loading, user, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      const u = await login(email, password, selectedRole ?? undefined)
      toast.success('Signed in', `Welcome back, ${u.name}.`)
      navigate(dashboardPathForRole(u.role), { replace: true })
    } catch (err) {
      const message = parseApiError(err)
      setError(message)
      toast.error('Sign in failed', message)
    } finally {
      setSubmitting(false)
    }
  }

  const fillDemo = (demoEmail: string, demoPassword: string, role: UserRole) => {
    setEmail(demoEmail)
    setPassword(demoPassword)
    setSelectedRole(role)
    setError('')
  }

  if (loading) {
    return <SessionSkeleton />
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 px-4 py-10">
      <div className="w-full max-w-md space-y-8 rounded-lg border border-border bg-card p-6 shadow-xl sm:p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Sign in to the AI Customer Support console.{' '}
            <Link to="/register" className="font-medium text-primary hover:underline">
              Create account
            </Link>
          </p>
        </div>
        
        {/* Role Selection Tabs */}
        <div className="flex gap-2 rounded-lg border border-border p-1 bg-muted/20">
          <button
            type="button"
            onClick={() => setSelectedRole('customer')}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition ${
              selectedRole === 'customer'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted'
            }`}
          >
            Customer
          </button>
          <button
            type="button"
            onClick={() => setSelectedRole('admin')}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition ${
              selectedRole === 'admin'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted'
            }`}
          >
            Admin
          </button>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
          <div>
            <div className="flex items-center justify-between gap-3">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <Link to="/forgot-password" className="text-sm font-medium text-primary hover:underline">
                Forgot password?
              </Link>
            </div>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
          {error ? (
            <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </div>
          ) : null}
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-primary py-2.5 text-sm font-medium text-primary-foreground transition hover:bg-primary/90 disabled:opacity-50"
          >
            {submitting ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
        <div className="rounded-lg border border-border bg-muted/40 p-3">
          <p className="text-xs font-medium uppercase text-muted-foreground">Demo logins</p>
          <div className="mt-3 grid gap-2">
            <button
              type="button"
              onClick={() => fillDemo('customer@example.com', 'Customer123', 'customer')}
              className="rounded-lg border border-border bg-background px-3 py-2 text-left text-sm hover:bg-muted"
            >
              Customer / Client
              <span className="block text-xs text-muted-foreground">customer@example.com</span>
            </button>
            <button
              type="button"
              onClick={() => fillDemo('owner@example.com', 'Owner12345', 'admin')}
              className="rounded-lg border border-border bg-background px-3 py-2 text-left text-sm hover:bg-muted"
            >
              Company Owner
              <span className="block text-xs text-muted-foreground">owner@example.com</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
