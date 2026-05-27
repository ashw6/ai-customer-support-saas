import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  hint?: string
  className?: string
}

export function StatCard({ title, value, hint, className }: StatCardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-card p-5 shadow-sm transition-shadow hover:shadow-md',
        className,
      )}
    >
      <p className="text-sm font-medium text-muted-foreground">{title}</p>
      <p className="mt-2 text-2xl font-semibold tracking-tight text-card-foreground sm:text-3xl">{value}</p>
      {hint ? <p className="mt-1 text-xs text-muted-foreground">{hint}</p> : null}
    </div>
  )
}
