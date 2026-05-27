import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { LockKeyhole } from 'lucide-react'
import { useToast } from '@/context/ToastContext'
import { parseApiError } from '@/services/api'
import { resetPassword } from '@/services/auth.service'

const validatePassword = (password: string): string | null => {
  if (password.length < 8) {
    return 'Password must be at least 8 characters long'
  }
  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter'
  }
  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter'
  }
  if (!/\d/.test(password)) {
    return 'Password must contain at least one number'
  }
  return null
}

export function ResetPasswordPage() {
  const toast = useToast()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const token = params.get('token') ?? ''
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (password !== confirm) {
      setError('Passwords do not match')
      return
    }
    const passwordError = validatePassword(password)
    if (passwordError) {
      setError(passwordError)
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const message = await resetPassword(token, password)
      toast.success('Password reset', message)
      navigate('/login', { replace: true })
    } catch (err) {
      const nextError = parseApiError(err)
      setError(nextError)
      toast.error('Reset failed', nextError)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 px-4 py-10">
      <div className="w-full max-w-md space-y-8 rounded-lg border border-border bg-card p-6 shadow-xl sm:p-8">
        <div className="text-center">
          <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <LockKeyhole className="h-5 w-5" />
          </div>
          <h1 className="mt-4 text-2xl font-bold tracking-tight">Choose a new password</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Use at least 8 characters with uppercase, lowercase, and a number.
          </p>
        </div>

        {!token ? (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            This reset link is missing a token. Request a new password reset email.
          </div>
        ) : (
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="password" className="text-sm font-medium">
                New password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
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
                autoComplete="new-password"
                required
                value={confirm}
                onChange={(event) => setConfirm(event.target.value)}
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
              {submitting ? 'Resetting...' : 'Reset password'}
            </button>
          </form>
        )}

        <p className="text-center text-sm text-muted-foreground">
          Need a fresh link?{' '}
          <Link to="/forgot-password" className="font-medium text-primary hover:underline">
            Request reset email
          </Link>
        </p>
      </div>
    </div>
  )
}
