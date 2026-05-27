import type { Lead, LeadAnalytics, LeadCreatePayload, LeadPageData } from '@/types/api'
import { api } from './api'

export async function createLead(payload: LeadCreatePayload): Promise<Lead> {
  const { data } = await api.post<Lead>('/leads', payload)
  return data
}

export async function fetchLeads(skip: number = 0, limit: number = 50): Promise<LeadPageData> {
  const { data } = await api.get<LeadPageData>('/leads', { params: { skip, limit } })
  return data
}

export async function fetchLeadAnalytics(): Promise<LeadAnalytics> {
  const { data } = await api.get<LeadAnalytics>('/leads/analytics')
  return data
}
