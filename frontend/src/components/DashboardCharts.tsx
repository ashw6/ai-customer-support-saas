import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useMemo, useState, type ReactNode } from 'react'
import { EmptyState } from '@/components/EmptyState'
import type { Ticket, TicketPriority, TicketStatus } from '@/types/api'

interface DashboardChartsProps {
  tickets: Ticket[]
}

const statusLabels: TicketStatus[] = ['open', 'in_progress', 'resolved', 'closed']
const priorityLabels: TicketPriority[] = ['low', 'medium', 'high']
const sentimentLabels = ['positive', 'neutral', 'negative', 'unknown']
const chartColors = ['#2563eb', '#d97706', '#059669', '#7c3aed', '#dc2626']
const timeRanges = [
  { value: 7, label: '7 days' },
  { value: 30, label: '30 days' },
  { value: 90, label: '90 days' },
]

function label(value: string) {
  return value.replaceAll('_', ' ')
}

function series(tickets: Ticket[], values: string[], getValue: (ticket: Ticket) => string | null | undefined) {
  return values.map((name) => ({
    name,
    label: label(name),
    value: tickets.filter((ticket) => (getValue(ticket) ?? 'unknown') === name).length,
  }))
}

function validTickets(tickets: Ticket[]) {
  return tickets.filter((ticket) => ticket && Number.isFinite(Number(ticket.id)))
}

function trendSeries(tickets: Ticket[], days: number) {
  const now = new Date()
  const buckets = Array.from({ length: days }).map((_, index) => {
    const date = new Date(now)
    date.setDate(now.getDate() - (days - index - 1))
    const key = date.toISOString().slice(0, 10)
    return { key, label: date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }), tickets: 0 }
  })
  const byKey = new Map(buckets.map((bucket) => [bucket.key, bucket]))
  tickets.forEach((ticket) => {
    if (!ticket.created_at) return
    const key = new Date(ticket.created_at).toISOString().slice(0, 10)
    const bucket = byKey.get(key)
    if (bucket) bucket.tickets += 1
  })
  return buckets
}

function ChartCard({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <h3 className="text-sm font-semibold">{title}</h3>
      <div className="mt-4 h-64">{children}</div>
    </div>
  )
}

export function DashboardCharts({ tickets }: DashboardChartsProps) {
  const [range, setRange] = useState(30)
  const safeTickets = useMemo(() => validTickets(Array.isArray(tickets) ? tickets : []), [tickets])

  if (safeTickets.length === 0) {
    return (
      <EmptyState
        title="No chart data yet"
        description="Charts will appear once tickets are available for this workspace."
      />
    )
  }

  const statusData = series(safeTickets, statusLabels, (ticket) => ticket.status)
  const priorityData = series(safeTickets, priorityLabels, (ticket) => ticket.priority)
  const sentimentData = series(safeTickets, sentimentLabels, (ticket) => ticket.sentiment ?? 'unknown')
  const trends = trendSeries(safeTickets, range)
  const resolved = safeTickets.filter((ticket) => ticket.status === 'resolved' || ticket.status === 'closed').length
  const unresolved = Math.max(safeTickets.length - resolved, 0)
  const ratioData = [
    { name: 'resolved', label: 'resolved', value: resolved },
    { name: 'unresolved', label: 'unresolved', value: unresolved },
  ]

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <select
          aria-label="Chart time range"
          value={range}
          onChange={(event) => setRange(Number(event.target.value))}
          className="h-9 rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {timeRanges.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Recent ticket trends">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends} margin={{ left: -20, right: 12, top: 8 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 12 }} minTickGap={20} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="tickets" stroke="#2563eb" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Resolved vs unresolved">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={ratioData} dataKey="value" nameKey="label" innerRadius={54} outerRadius={86}>
                {ratioData.map((entry, index) => (
                  <Cell key={entry.name} fill={index === 0 ? '#059669' : '#d97706'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
      <ChartCard title="Tickets by status">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={statusData} margin={{ left: -20, right: 8, top: 8 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
      <ChartCard title="Tickets by priority">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={priorityData} margin={{ left: -20, right: 8, top: 8 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="#d97706" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
      <ChartCard title="Sentiment distribution">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={sentimentData} dataKey="value" nameKey="label" innerRadius={54} outerRadius={86}>
              {sentimentData.map((entry, index) => (
                <Cell key={entry.name} fill={chartColors[index % chartColors.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>
      </div>
    </div>
  )
}
