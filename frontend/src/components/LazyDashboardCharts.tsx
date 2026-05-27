import { lazy, Suspense } from 'react'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { SkeletonBlock } from '@/components/LoadingState'
import type { Ticket } from '@/types/api'

const DashboardCharts = lazy(() =>
  import('@/components/DashboardCharts').then((module) => ({ default: module.DashboardCharts })),
)

function ChartsSkeleton() {
  return (
    <div className="grid gap-4 xl:grid-cols-3">
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={index} className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <SkeletonBlock className="h-4 w-36" />
          <SkeletonBlock className="mt-4 h-64 w-full" />
        </div>
      ))}
    </div>
  )
}

export function LazyDashboardCharts({ tickets }: { tickets: Ticket[] }) {
  return (
    <ErrorBoundary label="Dashboard charts">
      <Suspense fallback={<ChartsSkeleton />}>
        <DashboardCharts tickets={tickets} />
      </Suspense>
    </ErrorBoundary>
  )
}
