import { useEffect, useState } from 'react'
import { EmptyState } from '@/components/EmptyState'
import { SkeletonBlock } from '@/components/LoadingState'
import { StatCard } from '@/components/StatCard'
import { useToast } from '@/context/ToastContext'
import { parseApiError } from '@/services/api'
import { fetchLeadAnalytics, fetchLeads } from '@/services/leads.service'
import type { Lead, LeadAnalytics } from '@/types/api'

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

export function LeadAnalyticsSection() {
  const toast = useToast()
  const [analytics, setAnalytics] = useState<LeadAnalytics | null>(null)
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      try {
        const [nextAnalytics, leadsPageData] = await Promise.all([fetchLeadAnalytics(), fetchLeads()])
        if (!cancelled) {
          setAnalytics(nextAnalytics)
          setLeads(leadsPageData.items)
        }
      } catch (error) {
        if (!cancelled) toast.error('Could not load leads', parseApiError(error))
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [toast])

  if (loading) {
    return (
      <section className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="rounded-lg border border-border bg-card p-5 shadow-sm">
              <SkeletonBlock className="h-4 w-24" />
              <SkeletonBlock className="mt-4 h-8 w-14" />
            </div>
          ))}
        </div>
        <SkeletonBlock className="h-48 w-full" />
      </section>
    )
  }

  return (
    <section className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Captured leads" value={analytics?.total ?? 0} hint="All-time chat lead forms" />
        <StatCard title="Today" value={analytics?.today ?? 0} hint="Captured since midnight" />
        <StatCard title="Follow-ups sent" value={analytics?.followups_sent ?? 0} hint="Resend success count" />
        <StatCard title="Email rate" value={`${analytics?.conversion_rate ?? 0}%`} hint="Follow-up delivery ratio" />
      </div>

      <div className="rounded-lg border border-border bg-card shadow-sm">
        <div className="border-b border-border px-5 py-4">
          <h3 className="text-sm font-semibold">Recent leads</h3>
        </div>
        {leads.length === 0 ? (
          <div className="p-5">
            <EmptyState title="No leads yet" description="Sales interest captured in chat will appear here." />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border text-sm">
              <thead className="bg-muted/40 text-left text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-5 py-3 font-semibold">Lead</th>
                  <th className="px-5 py-3 font-semibold">Phone</th>
                  <th className="px-5 py-3 font-semibold">Keyword</th>
                  <th className="px-5 py-3 font-semibold">Follow-up</th>
                  <th className="px-5 py-3 font-semibold">Captured</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {leads.slice(0, 8).map((lead) => (
                  <tr key={lead.id}>
                    <td className="px-5 py-4">
                      <p className="font-medium text-foreground">{lead.name}</p>
                      <p className="text-xs text-muted-foreground">{lead.email}</p>
                    </td>
                    <td className="px-5 py-4 text-muted-foreground">{lead.phone}</td>
                    <td className="px-5 py-4 text-muted-foreground">{lead.matched_keyword ?? 'chat'}</td>
                    <td className="px-5 py-4">
                      <span className="rounded-full bg-muted px-2 py-1 text-xs text-muted-foreground">
                        {lead.followup_sent ? 'Sent' : 'Pending'}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-muted-foreground">{formatDate(lead.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}
