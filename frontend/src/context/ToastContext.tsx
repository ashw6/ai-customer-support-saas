import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { CheckCircle2, X, XCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

type ToastType = 'success' | 'error'

interface Toast {
  id: number
  type: ToastType
  title: string
  message?: string
}

interface ToastContextValue {
  success: (title: string, message?: string) => void
  error: (title: string, message?: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const dismiss = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  const show = useCallback(
    (type: ToastType, title: string, message?: string) => {
      const id = Date.now() + Math.floor(Math.random() * 1000)
      setToasts((current) => [...current, { id, type, title, message }])
      window.setTimeout(() => dismiss(id), 4200)
    },
    [dismiss],
  )

  const value = useMemo(
    () => ({
      success: (title: string, message?: string) => show('success', title, message),
      error: (title: string, message?: string) => show('error', title, message),
    }),
    [show],
  )

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-[80] flex w-[calc(100%-2rem)] max-w-sm flex-col gap-3">
        {toasts.map((toast) => {
          const Icon = toast.type === 'success' ? CheckCircle2 : XCircle
          return (
            <div
              key={toast.id}
              className={cn(
                'rounded-lg border bg-background p-4 shadow-lg',
                toast.type === 'success' ? 'border-emerald-200' : 'border-rose-200',
              )}
            >
              <div className="flex gap-3">
                <Icon
                  className={cn(
                    'mt-0.5 h-5 w-5 shrink-0',
                    toast.type === 'success' ? 'text-emerald-600' : 'text-rose-600',
                  )}
                />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold">{toast.title}</p>
                  {toast.message ? (
                    <p className="mt-1 text-sm text-muted-foreground">{toast.message}</p>
                  ) : null}
                </div>
                <button
                  type="button"
                  className="rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
                  onClick={() => dismiss(toast.id)}
                  aria-label="Dismiss notification"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
