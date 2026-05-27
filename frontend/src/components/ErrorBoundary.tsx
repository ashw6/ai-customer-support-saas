import { Component, type ErrorInfo, type ReactNode } from 'react'
import { AlertTriangle, RotateCcw } from 'lucide-react'

interface ErrorBoundaryProps {
  children: ReactNode
  label?: string
  /** Use `page` for root-level boundaries (full viewport). */
  variant?: 'section' | 'page'
}

interface ErrorBoundaryState {
  failed: boolean
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { failed: false }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { failed: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(this.props.label ?? 'UI section failed', error, info)
  }

  retry = () => this.setState({ failed: false })

  render() {
    if (!this.state.failed) return this.props.children

    const isPage = this.props.variant === 'page'

    if (isPage) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-muted/30 px-4">
          <div className="w-full max-w-md rounded-lg border border-border bg-card p-6 shadow-sm">
            <div className="flex gap-3">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-foreground">Something went wrong</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  The application hit an unexpected error. You can try reloading the page.
                </p>
                <button
                  type="button"
                  onClick={this.retry}
                  className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <RotateCcw className="h-4 w-4" />
                  Try again
                </button>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-5 text-amber-900">
        <div className="flex gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
          <div className="min-w-0 flex-1">
            <h3 className="text-sm font-semibold">This section could not be displayed.</h3>
            <p className="mt-1 text-sm text-amber-800">
              Try again. The rest of the workspace is still available.
            </p>
            <button
              type="button"
              onClick={this.retry}
              className="mt-3 inline-flex items-center gap-2 rounded-lg bg-amber-900 px-3 py-2 text-sm font-medium text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <RotateCcw className="h-4 w-4" />
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }
}
