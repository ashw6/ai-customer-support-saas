import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, CalendarDays, UserRound } from 'lucide-react'
import { Badge, priorityTone, sentimentTone, statusTone } from '@/components/Badge'
import { EmptyState } from '@/components/EmptyState'
import { DetailSkeleton } from '@/components/LoadingState'
import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import {
  adminNav,
  customerNav,
  DashboardLayout,
  supportNav,
  type NavItem,
} from '@/layouts/DashboardLayout'
import { dashboardPathForRole } from '@/lib/paths'
import { parseApiError } from '@/services/api'
import { fetchTicketById } from '@/services/tickets.service'
import type { Ticket } from '@/types/api'

function formatDate(value: string | null | undefined) {
  if (!value) return 'N/A'
  return new Date(value).toLocaleString()
}

function navForRole(role: string | undefined): NavItem[] {
  if (role === 'admin') return adminNav
  if (role === 'support_agent') return supportNav
  return customerNav
}

function DetailItem({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-xs font-medium uppercase text-muted-foreground">{label}</p>
      <div className="mt-2 text-sm font-medium text-foreground">{value}</div>
    </div>
  )
}

export function TicketDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const toast = useToast()
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const ticketId = Number(id)
  const backPath = user ? dashboardPathForRole(user.role) : '/'
  const navItems = useMemo(() => navForRole(user?.role), [user?.role])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError('')
      try {
        if (!Number.isInteger(ticketId) || ticketId < 1) {
          throw new Error('Ticket id is invalid')
        }
        const data = await fetchTicketById(ticketId)
        if (!cancelled) setTicket(data)
      } catch (e) {
        const message = parseApiError(e)
        if (!cancelled) {
          setError(message)
          toast.error('Could not load ticket', message)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [ticketId, toast])

  return (
    <DashboardLayout title="Ticket detail" subtitle="Support request overview" navItems={navItems}>
      <Link
        to={backPath}
        className="mb-5 inline-flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm font-medium text-muted-foreground shadow-sm hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to dashboard
      </Link>

      {loading ? <DetailSkeleton /> : null}

      {!loading && error ? (
        <EmptyState title="Ticket unavailable" description={error} />
      ) : null}

      {!loading && !error && ticket ? (
        <div className="space-y-6">
          <section className="rounded-lg border border-border bg-card p-5 shadow-sm sm:p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="min-w-0">
                <p className="font-mono text-xs text-muted-foreground">Ticket #{ticket.id}</p>
                <h2 className="mt-2 text-2xl font-semibold tracking-tight">{ticket.title}</h2>
                <div className="mt-4 flex flex-wrap gap-2">
                  <Badge tone={statusTone(ticket.status)}>{ticket.status.replaceAll('_', ' ')}</Badge>
                  <Badge tone={priorityTone(ticket.priority)}>{ticket.priority}</Badge>
                  {ticket.sentiment ? (
                    <Badge tone={sentimentTone(ticket.sentiment)}>{ticket.sentiment}</Badge>
                  ) : null}
                </div>
              </div>
              <div className="flex flex-col gap-2 text-sm text-muted-foreground sm:flex-row lg:flex-col">
                <span className="inline-flex items-center gap-2">
                  <CalendarDays className="h-4 w-4" />
                  {formatDate(ticket.created_at)}
                </span>
                <span className="inline-flex items-center gap-2">
                  <UserRound className="h-4 w-4" />
                  {ticket.assigned_agent_id ? `Agent #${ticket.assigned_agent_id}` : 'Unassigned'}
                </span>
              </div>
            </div>
            <p className="mt-6 whitespace-pre-wrap text-sm leading-6 text-muted-foreground">
              {ticket.description}
            </p>
          </section>

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <DetailItem label="Status" value={<Badge tone={statusTone(ticket.status)}>{ticket.status.replaceAll('_', ' ')}</Badge>} />
            <DetailItem label="Priority" value={<Badge tone={priorityTone(ticket.priority)}>{ticket.priority}</Badge>} />
            <DetailItem label="Urgency score" value={ticket.urgency_score ?? 'N/A'} />
            <DetailItem label="Assigned agent" value={ticket.assigned_agent_id ? `Agent #${ticket.assigned_agent_id}` : 'Unassigned'} />
            <DetailItem label="Sentiment" value={ticket.sentiment ? <Badge tone={sentimentTone(ticket.sentiment)}>{ticket.sentiment}</Badge> : 'N/A'} />
            <DetailItem label="Category" value={ticket.category ?? 'N/A'} />
            <DetailItem label="SLA tag" value={ticket.sla_tag ?? 'N/A'} />
            <DetailItem label="Created" value={formatDate(ticket.created_at)} />
          </section>
        </div>
      ) : null}
    </DashboardLayout>
  )
}
