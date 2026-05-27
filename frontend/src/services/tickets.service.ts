import type { Ticket, TicketListResponse, TicketPageData, TicketQueryParams, User } from '@/types/api'
import { api } from './api'

function sortParams(sort: TicketQueryParams['sort']) {
  if (sort === 'oldest') return { sort_by: 'created_at', order: 'asc' }
  if (sort === 'priority') return { sort_by: 'priority', order: 'desc' }
  if (sort === 'status') return { sort_by: 'status', order: 'asc' }
  return { sort_by: 'created_at', order: 'desc' }
}

function toApiParams(params: TicketQueryParams) {
  const mapped = {
    page: params.page ?? 1,
    limit: params.limit ?? 10,
    search: params.search || undefined,
    status: params.status || undefined,
    priority: params.priority || undefined,
    sentiment: params.sentiment || undefined,
    assigned_agent_id: params.assigned_agent_id || undefined,
    ...sortParams(params.sort),
  }
  return mapped
}

export async function fetchMyTicketsPage(params: TicketQueryParams = {}): Promise<TicketPageData> {
  const { data } = await api.get<TicketListResponse>('/tickets/my', { params: toApiParams(params) })
  return data.data
}

export async function fetchAllTicketsPage(params: TicketQueryParams = {}): Promise<TicketPageData> {
  const { data } = await api.get<TicketListResponse>('/tickets', { params: toApiParams(params) })
  return data.data
}

export async function fetchMyTickets(): Promise<Ticket[]> {
  return (await fetchMyTicketsPage({ limit: 100 })).items
}

export async function fetchAllTickets(): Promise<Ticket[]> {
  return (await fetchAllTicketsPage({ limit: 100 })).items
}

export async function fetchTicketById(id: number): Promise<Ticket> {
  const { data } = await api.get<Ticket>(`/tickets/${id}`)
  return data
}

export async function fetchAllUsers(): Promise<User[]> {
  const { data } = await api.get<User[]>('/api/admin/users')
  return data
}
