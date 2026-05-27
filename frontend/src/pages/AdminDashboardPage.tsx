import { useEffect, useMemo, useState } from 'react'
import { DashboardLayout, adminNav } from '@/layouts/DashboardLayout'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LazyDashboardCharts } from '@/components/LazyDashboardCharts'
import { LeadAnalyticsSection } from '@/components/LeadAnalyticsSection'
import { StatCardsSkeleton } from '@/components/LoadingState'
import { StatCard } from '@/components/StatCard'
import { TicketListPanel } from '@/components/TicketListPanel'
import { fetchAllUsers } from '@/services/tickets.service'
import type { Ticket, User } from '@/types/api'

export function AdminDashboardPage() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchAllUsers().then(setUsers).catch(console.error)
  }, [])

  const uniqueCustomers = useMemo(() => users.length, [users])
  const escalated = useMemo(() => tickets.filter((t) => t.is_escalated === true).length, [tickets])
  const openTickets = useMemo(
    () => tickets.filter((t) => t.status === 'open' || t.status === 'in_progress').length,
    [tickets],
  )
  const handleData = useMemo(() => setTickets, [])
  const handleLoading = useMemo(() => setLoading, [])

  return (
    <DashboardLayout
      title="Admin overview"
      subtitle="Operations snapshot across users and tickets"
      navItems={adminNav}
    >
      {loading ? (
        <StatCardsSkeleton count={4} />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Unique customers"
              value={uniqueCustomers}
              hint="Total registered users in the system"
            />
            <StatCard title="Total tickets" value={tickets.length} hint="All statuses" />
            <StatCard title="Escalated" value={escalated} hint="AI / keyword escalation" />
            <StatCard title="Open pipeline" value={openTickets} hint="Open + in progress" />
          </div>
          <section className="mt-6">
            <LazyDashboardCharts tickets={tickets} />
          </section>
          <section className="mt-6">
            <LeadAnalyticsSection />
          </section>
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
              <h3 className="text-sm font-semibold">Analytics</h3>
              <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                <li>
                  High priority share:{' '}
                  <span className="font-medium text-foreground">
                    {tickets.length
                      ? Math.round(
                          (tickets.filter((t) => t.priority === 'high').length / tickets.length) *
                            100,
                        )
                      : 0}
                    %
                  </span>
                </li>
                <li>
                  Negative sentiment share:{' '}
                  <span className="font-medium text-foreground">
                    {tickets.length
                      ? Math.round(
                          (tickets.filter((t) => t.sentiment === 'negative').length / tickets.length) *
                            100,
                        )
                      : 0}
                    %
                  </span>
                </li>
              </ul>
            </div>
            <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
              <h3 className="text-sm font-semibold">Recent activity</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Latest ticket movement (newest first). Connect audit webhooks later for richer
                timelines.
              </p>
            </div>
          </div>
        </>
      )}
      <div className="mt-8">
        <ErrorBoundary label="Admin ticket list">
          <TicketListPanel
            scope="all"
            title="Latest tickets"
            description="Operational ticket view with backend-backed pagination and filters."
            includeStaffFilters
            onDataChange={handleData}
            onLoadingChange={handleLoading}
          />
        </ErrorBoundary>
      </div>
    </DashboardLayout>
  )
}
