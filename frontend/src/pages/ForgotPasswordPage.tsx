import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Mail } from 'lucide-react'
import { useToast } from '@/context/ToastContext'
import { parseApiError } from '@/services/api'
import { requestPasswordReset } from '@/services/auth.service'

export function ForgotPasswordPage() {
  const toast = useToast()
  const [email, setEmail] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')
  const [resetUrl, setResetUrl] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setMessage('')
    setResetUrl('')
    setError('')
    try {
      const response = await requestPasswordReset(email)
      setMessage(response.message)
      if (response.dev_reset_url) {
        setResetUrl(response.dev_reset_url)
      }
      if (response.email_sent) {
        toast.success('Check your email', response.message)
      } else if (response.dev_reset_url) {
        toast.success('Reset link created', 'Use the local reset link shown on this page.')
      } else {
        toast.success('Request received', response.message)
      }
    } catch (err) {
      const nextError = parseApiError(err)
      setError(nextError)
      toast.error('Reset request failed', nextError)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 px-4 py-10">
      <div className="w-full max-w-md space-y-8 rounded-lg border border-border bg-card p-6 shadow-xl sm:p-8">
        <div className="text-center">
          <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Mail className="h-5 w-5" />
          </div>
          <h1 className="mt-4 text-2xl font-bold tracking-tight">Reset your password</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter your account email and we will send a reset link.
          </p>
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
              onChange={(event) => setEmail(event.target.value)}
              className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>

          {message ? (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
              {message}
              {resetUrl ? (
                <a
                  href={resetUrl}
                  className="mt-2 block break-all font-medium text-primary underline"
                >
                  Open local reset link
                </a>
              ) : null}
            </div>
          ) : null}
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
            {submitting ? 'Sending...' : 'Send reset link'}
          </button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          Remembered it?{' '}
          <Link to="/login" className="font-medium text-primary hover:underline">
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
