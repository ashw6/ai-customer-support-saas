import { Link } from 'react-router-dom'
import { Badge, priorityTone, sentimentTone, statusTone } from '@/components/Badge'
import { EmptyState } from '@/components/EmptyState'
import { SkeletonBlock } from '@/components/LoadingState'
import type { Ticket } from '@/types/api'

interface TicketTableProps {
  tickets: Ticket[]
  emptyMessage?: string
}

export function TicketTable({ tickets, emptyMessage = 'No tickets yet.' }: TicketTableProps) {
  if (tickets.length === 0) {
    return (
      <EmptyState title={emptyMessage} description="New support requests will show up here." />
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-card shadow-sm">
      <table className="min-w-full divide-y divide-border text-sm">
        <caption className="sr-only">Support tickets</caption>
        <thead className="bg-muted/50">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">ID</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Title</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Priority</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground hidden md:table-cell">
              Category
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground hidden lg:table-cell">
              Sentiment
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground hidden lg:table-cell">
              Created
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {tickets.map((t) => (
            <tr key={t.id} className="hover:bg-muted/40">
              <td className="whitespace-nowrap px-4 py-3 font-mono text-xs text-muted-foreground">
                #{t.id}
              </td>
              <td className="max-w-[240px] px-4 py-3 font-medium text-foreground">
                <Link
                  to={`/tickets/${t.id}`}
                  className="block truncate rounded-sm hover:text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  {t.title}
                </Link>
              </td>
              <td className="whitespace-nowrap px-4 py-3">
                <Badge tone={statusTone(t.status)}>{t.status.replaceAll('_', ' ')}</Badge>
              </td>
              <td className="whitespace-nowrap px-4 py-3">
                <Badge tone={priorityTone(t.priority)}>{t.priority}</Badge>
              </td>
              <td className="hidden whitespace-nowrap px-4 py-3 md:table-cell">
                {t.category ?? 'N/A'}
              </td>
              <td className="hidden whitespace-nowrap px-4 py-3 lg:table-cell">
                {t.sentiment ? <Badge tone={sentimentTone(t.sentiment)}>{t.sentiment}</Badge> : 'N/A'}
              </td>
              <td className="hidden whitespace-nowrap px-4 py-3 text-muted-foreground lg:table-cell">
                {new Date(t.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function TicketTableSkeleton() {
  return (
    <div className="rounded-lg border border-border bg-card p-4 shadow-sm" aria-label="Loading tickets">
      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="grid grid-cols-6 gap-3">
            <SkeletonBlock className="h-5" />
            <SkeletonBlock className="col-span-2 h-5" />
            <SkeletonBlock className="h-5" />
            <SkeletonBlock className="h-5" />
            <SkeletonBlock className="h-5" />
          </div>
        ))}
      </div>
    </div>
  )
}
