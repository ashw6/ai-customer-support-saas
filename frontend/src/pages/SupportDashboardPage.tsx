import { useMemo, useState } from 'react'
import { DashboardLayout, supportNav } from '@/layouts/DashboardLayout'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LazyDashboardCharts } from '@/components/LazyDashboardCharts'
import { StatCardsSkeleton } from '@/components/LoadingState'
import { StatCard } from '@/components/StatCard'
import { TicketListPanel } from '@/components/TicketListPanel'
import { useAuth } from '@/context/AuthContext'
import type { Ticket } from '@/types/api'

export function SupportDashboardPage() {
  const { user } = useAuth()
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(false)

  const assigned = useMemo(
    () => tickets.filter((t) => t.assigned_agent_id === user?.id),
    [tickets, user?.id],
  )
  const escalated = useMemo(() => tickets.filter((t) => t.is_escalated === true), [tickets])
  const highPriority = useMemo(() => tickets.filter((t) => t.priority === 'high'), [tickets])
  const handleData = useMemo(() => setTickets, [])
  const handleLoading = useMemo(() => setLoading, [])

  return (
    <DashboardLayout
      title="Support queue"
      subtitle="Global ticket intelligence for agents"
      navItems={supportNav}
    >
      {loading ? (
        <StatCardsSkeleton count={3} />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard title="Assigned to you" value={assigned.length} hint="From full queue" />
            <StatCard title="Escalated tickets" value={escalated.length} hint="Needs leadership" />
            <StatCard title="High AI priority" value={highPriority.length} hint="Keyword / AI score" />
          </div>
        </>
      )}
      <section className="mt-6">
        <LazyDashboardCharts tickets={tickets} />
      </section>
      <div className="mt-8">
        <ErrorBoundary label="Support ticket list">
          <TicketListPanel
            scope="all"
            title="Support queue"
            description="Filter by status, priority, sentiment, assignee, and search text."
            includeStaffFilters
            onDataChange={handleData}
            onLoadingChange={handleLoading}
          />
        </ErrorBoundary>
      </div>
    </DashboardLayout>
  )
}
