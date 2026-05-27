import { useMemo, useState } from 'react'
import { DashboardLayout, customerNav } from '@/layouts/DashboardLayout'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LazyDashboardCharts } from '@/components/LazyDashboardCharts'
import { StatCardsSkeleton } from '@/components/LoadingState'
import { StatCard } from '@/components/StatCard'
import { TicketListPanel } from '@/components/TicketListPanel'
import type { Ticket } from '@/types/api'

function isOpen(t: Ticket) {
  return t.status === 'open' || t.status === 'in_progress'
}

function isResolved(t: Ticket) {
  return t.status === 'resolved' || t.status === 'closed'
}

export function CustomerDashboardPage() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(false)

  const total = tickets.length
  const openCount = tickets.filter(isOpen).length
  const resolvedCount = tickets.filter(isResolved).length
  const handleData = useMemo(() => setTickets, [])
  const handleLoading = useMemo(() => setLoading, [])

  return (
    <DashboardLayout
      title="Customer workspace"
      subtitle="Your support tickets and AI insights"
      navItems={customerNav}
    >
      {loading ? (
        <StatCardsSkeleton count={3} />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard title="Total tickets" value={total} hint="All time" />
            <StatCard title="Open tickets" value={openCount} hint="Needs attention" />
            <StatCard title="Resolved" value={resolvedCount} hint="Closed loop" />
          </div>
        </>
      )}
      <section className="mt-6">
        <LazyDashboardCharts tickets={tickets} />
      </section>
      <div className="mt-8">
        <ErrorBoundary label="Customer ticket list">
          <TicketListPanel
            scope="my"
            title="Recent tickets"
            description="Search, filter, sort, and page through your support requests."
            onDataChange={handleData}
            onLoadingChange={handleLoading}
          />
        </ErrorBoundary>
      </div>
    </DashboardLayout>
  )
}
