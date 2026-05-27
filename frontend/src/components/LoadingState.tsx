import { cn } from '@/lib/utils'

interface LoadingStateProps {
  label?: string
  className?: string
}

export function LoadingState({ label = 'Loading', className }: LoadingStateProps) {
  return (
    <div className={cn('flex min-h-[220px] items-center justify-center', className)}>
      <div className="flex flex-col items-center gap-3 text-sm text-muted-foreground">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <span>{label}</span>
      </div>
    </div>
  )
}

export function SkeletonBlock({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-lg bg-muted', className)} />
}

export function StatCardsSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="rounded-lg border border-border bg-card p-5 shadow-sm">
          <SkeletonBlock className="h-4 w-28" />
          <SkeletonBlock className="mt-4 h-8 w-16" />
          <SkeletonBlock className="mt-3 h-3 w-24" />
        </div>
      ))}
    </div>
  )
}

export function DetailSkeleton() {
  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-border bg-card p-6 shadow-sm">
        <SkeletonBlock className="h-4 w-24" />
        <SkeletonBlock className="mt-4 h-8 w-2/3" />
        <SkeletonBlock className="mt-6 h-24 w-full" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 8 }).map((_, index) => (
          <div key={index} className="rounded-lg border border-border bg-card p-4">
            <SkeletonBlock className="h-3 w-20" />
            <SkeletonBlock className="mt-3 h-5 w-28" />
          </div>
        ))}
      </div>
    </div>
  )
}

export function SessionSkeleton() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 px-4">
      <div className="w-full max-w-md rounded-lg border border-border bg-card p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <SkeletonBlock className="h-10 w-10 rounded-full" />
          <div className="flex-1">
            <SkeletonBlock className="h-4 w-36" />
            <SkeletonBlock className="mt-2 h-3 w-48" />
          </div>
        </div>
        <SkeletonBlock className="mt-6 h-10 w-full" />
        <SkeletonBlock className="mt-3 h-10 w-full" />
        <SkeletonBlock className="mt-5 h-10 w-full" />
      </div>
    </div>
  )
}
