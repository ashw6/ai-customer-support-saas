import { useEffect, useState, type FormEvent } from 'react'
import { Loader2, Mail, Phone, UserRound, X } from 'lucide-react'
import { useToast } from '@/context/ToastContext'
import { parseApiError } from '@/services/api'
import { createLead } from '@/services/leads.service'
import type { Lead, User } from '@/types/api'

interface LeadCaptureModalProps {
  open: boolean
  matchedKeyword?: string | null
  sourceMessage?: string | null
  user?: User | null
  onClose: () => void
  onCreated?: (lead: Lead) => void
}

export function LeadCaptureModal({
  open,
  matchedKeyword,
  sourceMessage,
  user,
  onClose,
  onCreated,
}: LeadCaptureModalProps) {
  const toast = useToast()
  const [name, setName] = useState(user?.name ?? '')
  const [email, setEmail] = useState(user?.email ?? '')
  const [phone, setPhone] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!open) return
    setName(user?.name ?? '')
    setEmail(user?.email ?? '')
    setPhone('')
  }, [open, user?.email, user?.name])

  if (!open) return null

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!name.trim() || !email.trim() || !phone.trim()) return

    setSubmitting(true)
    try {
      const lead = await createLead({
        name: name.trim(),
        email: email.trim(),
        phone: phone.trim(),
        source: 'chat',
        matched_keyword: matchedKeyword,
        source_message: sourceMessage,
      })
      toast.success('Thanks, we will follow up', 'Your details were sent to the sales team.')
      onCreated?.(lead)
      onClose()
    } catch (error) {
      toast.error('Could not save lead', parseApiError(error))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[90] flex items-end justify-center bg-black/45 px-4 py-4 sm:items-center">
      <div className="w-full max-w-md rounded-lg border border-border bg-background shadow-xl">
        <div className="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
          <div>
            <h2 className="text-base font-semibold">Talk to sales</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Share your details and we will send a quick follow-up.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground disabled:opacity-50"
            aria-label="Close lead form"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 p-5">
          <label className="block text-sm">
            <span className="font-medium">Name</span>
            <span className="mt-1 flex items-center gap-2 rounded-lg border border-input bg-background px-3 py-2 focus-within:ring-2 focus-within:ring-ring">
              <UserRound className="h-4 w-4 text-muted-foreground" />
              <input
                value={name}
                onChange={(event) => setName(event.target.value)}
                disabled={submitting}
                className="min-w-0 flex-1 bg-transparent outline-none"
                autoComplete="name"
                required
              />
            </span>
          </label>

          <label className="block text-sm">
            <span className="font-medium">Email</span>
            <span className="mt-1 flex items-center gap-2 rounded-lg border border-input bg-background px-3 py-2 focus-within:ring-2 focus-within:ring-ring">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                disabled={submitting}
                className="min-w-0 flex-1 bg-transparent outline-none"
                autoComplete="email"
                required
              />
            </span>
          </label>

          <label className="block text-sm">
            <span className="font-medium">Phone</span>
            <span className="mt-1 flex items-center gap-2 rounded-lg border border-input bg-background px-3 py-2 focus-within:ring-2 focus-within:ring-ring">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <input
                type="tel"
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                disabled={submitting}
                className="min-w-0 flex-1 bg-transparent outline-none"
                autoComplete="tel"
                required
              />
            </span>
          </label>

          <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
            >
              Not now
            </button>
            <button
              type="submit"
              disabled={submitting || !name.trim() || !email.trim() || !phone.trim()}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mail className="h-4 w-4" />}
              Send details
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
