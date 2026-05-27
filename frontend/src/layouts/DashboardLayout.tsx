import { useState, type ReactNode } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  LogOut,
  MessageCircle,
  Menu,
  PanelLeftClose,
  Sparkles,
  Ticket,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { dashboardPathForRole } from '@/lib/paths'
import { cn } from '@/lib/utils'
import type { UserRole } from '@/types/api'

export interface NavItem {
  to: string
  label: string
  icon: typeof LayoutDashboard
}

interface DashboardLayoutProps {
  title: string
  subtitle?: string
  navItems: NavItem[]
  children: ReactNode
}

export function DashboardLayout({ title, subtitle, navItems, children }: DashboardLayoutProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const roleLabel: Record<UserRole, string> = {
    customer: 'Customer / Client',
    support_agent: 'Support',
    admin: 'Company Owner',
  }

  return (
    <div className="min-h-screen bg-muted/30">
      {sidebarOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          aria-label="Close menu"
          onClick={() => setSidebarOpen(false)}
        />
      ) : null}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 border-r border-border bg-card shadow-lg transition-transform md:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
        )}
      >
        <div className="flex h-16 items-center gap-2 border-b border-border px-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Sparkles className="h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold">AI Support</p>
            <p className="truncate text-xs text-muted-foreground">SaaS Console</p>
          </div>
          <button
            type="button"
            className="hidden rounded-md p-1.5 text-muted-foreground hover:bg-muted md:inline-flex"
            onClick={() => setSidebarOpen(false)}
            aria-label="Collapse sidebar"
          >
            <PanelLeftClose className="h-4 w-4" />
          </button>
        </div>

        <nav className="space-y-1 p-3">
          {navItems.map((item) => (
            <NavLink
              key={`${item.to}-${item.label}`}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                )
              }
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 border-t border-border p-3">
          <div className="mb-2 rounded-lg bg-muted/60 px-3 py-2 text-xs">
            <p className="truncate font-medium text-foreground">{user?.name}</p>
            <p className="truncate text-muted-foreground">{user?.email}</p>
            <p className="mt-1 inline-flex rounded-full bg-secondary px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-secondary-foreground">
              {user ? roleLabel[user.role] : ''}
            </p>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-destructive hover:bg-destructive/10"
          >
            <LogOut className="h-4 w-4" />
            Log out
          </button>
        </div>
      </aside>

      <div className="md:pl-64">
        <header className="sticky top-0 z-30 border-b border-border bg-background/90 backdrop-blur">
          <div className="flex h-16 items-center gap-3 px-4 sm:px-6">
            <button
              type="button"
              className="inline-flex rounded-md p-2 text-muted-foreground hover:bg-muted md:hidden"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="min-w-0 flex-1">
              <h1 className="truncate text-lg font-semibold tracking-tight">{title}</h1>
              {subtitle ? (
                <p className="truncate text-sm text-muted-foreground">{subtitle}</p>
              ) : null}
            </div>
            <Link
              to={user ? dashboardPathForRole(user.role) : '/login'}
              className="hidden text-sm text-muted-foreground hover:text-foreground sm:inline"
            >
              Home
            </Link>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  )
}

export const customerNav: NavItem[] = [
  { to: '/customer/dashboard', label: 'Overview', icon: LayoutDashboard },
  { to: '/chat', label: 'AI Chat', icon: MessageCircle },
]

export const supportNav: NavItem[] = [
  { to: '/support/dashboard', label: 'Queue', icon: Ticket },
  { to: '/chat', label: 'AI Chat', icon: MessageCircle },
  { to: '/admin/documents', label: 'Documents', icon: FileText },
]

export const adminNav: NavItem[] = [
  { to: '/admin/dashboard', label: 'Overview', icon: LayoutDashboard },
  { to: '/admin/documents', label: 'Documents', icon: FileText },
]
