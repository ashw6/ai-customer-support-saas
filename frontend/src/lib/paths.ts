import type { UserRole } from '@/types/api'

export function dashboardPathForRole(role: UserRole): string {
  if (role === 'admin') return '/admin/dashboard'
  if (role === 'support_agent') return '/support/dashboard'
  return '/customer/dashboard'
}
