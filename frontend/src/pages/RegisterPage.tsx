import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { SessionSkeleton } from '@/components/LoadingState'
import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import { parseApiError } from '@/services/api'
import { dashboardPathForRole } from '@/lib/paths'
import type { UserRole } from '@/types/api'

export function RegisterPage() {
  const { register, user, loading } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [selectedRole, setSelectedRole] = useState<UserRole>('customer')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!loading && user) {
      navigate(dashboardPathForRole(user.role), { replace: true })
    }
  }, [loading, user, navigate])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (password !== confirm) {
      setError('Passwords do not match')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const u = await register({ name, email, password, role: selectedRole })
      toast.success('Account created', `Welcome, ${u.name}.`)
      navigate(dashboardPathForRole(u.role), { replace: true })
    } catch (err) {
      const message = parseApiError(err)
      setError(message)
      toast.error('Registration failed', message)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <SessionSkeleton />
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 px-4 py-10">
      <div className="w-full max-w-md space-y-8 rounded-lg border border-border bg-card p-6 shadow-xl sm:p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight">Create your account</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Already registered?{' '}
            <Link to="/login" className="font-medium text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </div>
        <div className="flex gap-2 rounded-lg border border-border bg-muted/20 p-1">
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
            <label htmlFor="name" className="text-sm font-medium">
              Full name
            </label>
            <input
              id="name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
          <div>
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
          <div>
            <label htmlFor="password" className="text-sm font-medium">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
          <div>
            <label htmlFor="confirm" className="text-sm font-medium">
              Confirm password
            </label>
            <input
              id="confirm"
              type="password"
              required
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
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
            {submitting ? 'Creating...' : 'Create account'}
          </button>
        </form>
      </div>
    </div>
  )
}
