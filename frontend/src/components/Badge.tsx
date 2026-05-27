import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import type { TicketPriority, TicketStatus } from '@/types/api'

type BadgeTone = 'default' | 'success' | 'warning' | 'danger' | 'neutral'

interface BadgeProps {
  children: ReactNode
  tone?: BadgeTone
  className?: string
}

const toneClasses: Record<BadgeTone, string> = {
  default: 'border-slate-200 bg-slate-100 text-slate-700',
  success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  warning: 'border-amber-200 bg-amber-50 text-amber-700',
  danger: 'border-rose-200 bg-rose-50 text-rose-700',
  neutral: 'border-zinc-200 bg-zinc-50 text-zinc-700',
}

export function Badge({ children, tone = 'default', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium capitalize leading-none',
        toneClasses[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}

export function statusTone(status: TicketStatus): BadgeTone {
  if (status === 'resolved' || status === 'closed') return 'success'
  if (status === 'in_progress') return 'warning'
  return 'default'
}

export function priorityTone(priority: TicketPriority): BadgeTone {
  if (priority === 'high') return 'danger'
  if (priority === 'medium') return 'warning'
  return 'success'
}

export function sentimentTone(sentiment?: string | null): BadgeTone {
  if (sentiment === 'positive') return 'success'
  if (sentiment === 'negative') return 'danger'
  if (sentiment === 'neutral') return 'neutral'
  return 'default'
}
