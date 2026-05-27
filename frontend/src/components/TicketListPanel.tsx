import { RotateCcw, Search } from 'lucide-react'
import { useEffect } from 'react'
import { EmptyState } from '@/components/EmptyState'
import { TicketTable, TicketTableSkeleton } from '@/components/TicketTable'
import { useTicketList } from '@/hooks/useTicketList'
import { useToast } from '@/context/ToastContext'
import { cn } from '@/lib/utils'
import type { Ticket, TicketPriority, TicketSortOption, TicketStatus } from '@/types/api'

interface TicketListPanelProps {
  scope: 'my' | 'all'
  title: string
  description?: string
  includeStaffFilters?: boolean
  onDataChange?: (tickets: Ticket[]) => void
  onLoadingChange?: (loading: boolean) => void
}

const statusOptions: TicketStatus[] = ['open', 'in_progress', 'resolved', 'closed']
const priorityOptions: TicketPriority[] = ['low', 'medium', 'high']
const sentimentOptions = ['positive', 'neutral', 'negative']
const sortOptions: { value: TicketSortOption; label: string }[] = [
  { value: 'newest', label: 'Newest' },
  { value: 'oldest', label: 'Oldest' },
  { value: 'priority', label: 'Priority' },
  { value: 'status', label: 'Status' },
]

function OptionLabel({ value }: { value: string }) {
  return <>{value.replaceAll('_', ' ')}</>
}

export function TicketListPanel({
  scope,
  title,
  description,
  includeStaffFilters = false,
  onDataChange,
  onLoadingChange,
}: TicketListPanelProps) {
  const toast = useToast()
  const {
    query,
    searchDraft,
    setSearchDraft,
    page,
    loading,
    error,
    updateQuery,
    resetFilters,
  } = useTicketList(scope, includeStaffFilters)

  useEffect(() => {
    onDataChange?.(page.items)
  }, [onDataChange, page.items])

  useEffect(() => {
    onLoadingChange?.(loading)
  }, [loading, onLoadingChange])

  useEffect(() => {
    if (error) toast.error('Ticket list failed', error)
  }, [error, toast])

  const canPrev = page.page > 1
  const canNext = page.pages > page.page

  return (
    <section className="rounded-lg border border-border bg-card p-4 shadow-sm sm:p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold">{title}</h2>
          {description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}
        </div>
        <div className="text-sm text-muted-foreground">
          {page.total} {page.total === 1 ? 'ticket' : 'tickets'}
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-6">
        <label className="relative md:col-span-2">
          <span className="sr-only">Search tickets</span>
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            value={searchDraft}
            onChange={(event) => setSearchDraft(event.target.value)}
            placeholder="Search title or description"
            className="h-10 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </label>

        <select
          aria-label="Filter by status"
          value={query.status ?? ''}
          onChange={(event) => updateQuery({ status: event.target.value as TicketStatus, page: 1 })}
          className="h-10 rounded-lg border border-input bg-background px-3 text-sm capitalize outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <option value="">All statuses</option>
          {statusOptions.map((status) => (
            <option key={status} value={status}>
              <OptionLabel value={status} />
            </option>
          ))}
        </select>

        <select
          aria-label="Filter by priority"
          value={query.priority ?? ''}
          onChange={(event) => updateQuery({ priority: event.target.value as TicketPriority, page: 1 })}
          className="h-10 rounded-lg border border-input bg-background px-3 text-sm capitalize outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <option value="">All priorities</option>
          {priorityOptions.map((priority) => (
            <option key={priority} value={priority}>
              {priority}
            </option>
          ))}
        </select>

        <select
          aria-label="Filter by sentiment"
          value={query.sentiment ?? ''}
          onChange={(event) => updateQuery({ sentiment: event.target.value, page: 1 })}
          className="h-10 rounded-lg border border-input bg-background px-3 text-sm capitalize outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <option value="">All sentiment</option>
          {sentimentOptions.map((sentiment) => (
            <option key={sentiment} value={sentiment}>
              {sentiment}
            </option>
          ))}
        </select>

        <select
          aria-label="Sort tickets"
          value={query.sort ?? 'newest'}
          onChange={(event) => updateQuery({ sort: event.target.value as TicketSortOption, page: 1 })}
          className="h-10 rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        {includeStaffFilters ? (
          <input
            aria-label="Filter by assigned support agent"
            type="number"
            min={1}
            value={query.assigned_agent_id ?? ''}
            onChange={(event) =>
              updateQuery({
                assigned_agent_id: event.target.value ? Number(event.target.value) : '',
                page: 1,
              })
            }
            placeholder="Agent ID"
            className="h-10 rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        ) : null}
      </div>

      <div className="mt-3 flex justify-end">
        <button
          type="button"
          onClick={resetFilters}
          className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <RotateCcw className="h-4 w-4" />
          Reset
        </button>
      </div>

      <div className={cn('mt-4', loading ? 'opacity-80' : '')} aria-busy={loading}>
        {loading ? <TicketTableSkeleton /> : null}
        {!loading && error ? <EmptyState title="Could not load tickets" description={error} /> : null}
        {!loading && !error ? (
          <TicketTable
            tickets={page.items}
            emptyMessage={searchDraft ? 'No tickets match your search.' : 'No tickets found.'}
          />
        ) : null}
      </div>

      <div className="mt-4 flex flex-col gap-3 border-t border-border pt-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-muted-foreground">
          Page {page.pages === 0 ? 0 : page.page} of {page.pages}
        </p>
        <div className="flex items-center gap-2">
          <select
            aria-label="Rows per page"
            value={query.limit ?? 10}
            onChange={(event) => updateQuery({ limit: Number(event.target.value), page: 1 })}
            className="h-9 rounded-lg border border-input bg-background px-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {[10, 25, 50, 100].map((limit) => (
              <option key={limit} value={limit}>
                {limit} / page
              </option>
            ))}
          </select>
          <button
            type="button"
            disabled={!canPrev || loading}
            onClick={() => updateQuery({ page: Math.max(1, page.page - 1) })}
            className="rounded-lg border border-border px-3 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            Previous
          </button>
          <button
            type="button"
            disabled={!canNext || loading}
            onClick={() => updateQuery({ page: page.page + 1 })}
            className="rounded-lg border border-border bg-primary px-3 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            Next
          </button>
        </div>
      </div>
    </section>
  )
}
