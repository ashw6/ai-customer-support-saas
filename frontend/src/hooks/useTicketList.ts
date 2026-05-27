import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { parseApiError } from '@/services/api'
import { fetchAllTicketsPage, fetchMyTicketsPage } from '@/services/tickets.service'
import type {
  TicketPageData,
  TicketPriority,
  TicketQueryParams,
  TicketSortOption,
  TicketStatus,
} from '@/types/api'
import { useDebouncedValue } from './useDebouncedValue'

type TicketListScope = 'my' | 'all'

const defaultPage: TicketPageData = {
  items: [],
  total: 0,
  page: 1,
  limit: 10,
  pages: 0,
}

function intParam(value: string | null, fallback: number) {
  const parsed = Number(value)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback
}

function queryFromSearchParams(searchParams: URLSearchParams, includeStaffFilters: boolean): TicketQueryParams {
  return {
    page: intParam(searchParams.get('page'), 1),
    limit: intParam(searchParams.get('limit'), 10),
    search: searchParams.get('search') ?? '',
    status: (searchParams.get('status') as TicketStatus | null) ?? '',
    priority: (searchParams.get('priority') as TicketPriority | null) ?? '',
    sentiment: searchParams.get('sentiment') ?? '',
    assigned_agent_id: includeStaffFilters
      ? intParam(searchParams.get('assigned_agent_id'), 0) || ''
      : '',
    sort: (searchParams.get('sort') as TicketSortOption | null) ?? 'newest',
  }
}

function writeParams(next: TicketQueryParams) {
  const params = new URLSearchParams()
  if (next.page && next.page > 1) params.set('page', String(next.page))
  if (next.limit && next.limit !== 10) params.set('limit', String(next.limit))
  if (next.search) params.set('search', next.search)
  if (next.status) params.set('status', next.status)
  if (next.priority) params.set('priority', next.priority)
  if (next.sentiment) params.set('sentiment', next.sentiment)
  if (next.assigned_agent_id) params.set('assigned_agent_id', String(next.assigned_agent_id))
  if (next.sort && next.sort !== 'newest') params.set('sort', next.sort)
  return params
}

export function useTicketList(scope: TicketListScope, includeStaffFilters: boolean) {
  const [searchParams, setSearchParams] = useSearchParams()
  const query = useMemo(
    () => queryFromSearchParams(searchParams, includeStaffFilters),
    [includeStaffFilters, searchParams],
  )
  const [searchDraft, setSearchDraft] = useState(query.search ?? '')
  const debouncedSearch = useDebouncedValue(searchDraft)
  const [page, setPage] = useState<TicketPageData>(defaultPage)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setSearchDraft(query.search ?? '')
  }, [query.search])

  useEffect(() => {
    if ((query.search ?? '') === debouncedSearch) return
    setSearchParams(writeParams({ ...query, search: debouncedSearch, page: 1 }), { replace: true })
  }, [debouncedSearch, query, setSearchParams])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError('')
      try {
        const data = scope === 'my' ? await fetchMyTicketsPage(query) : await fetchAllTicketsPage(query)
        if (!cancelled) setPage(data)
      } catch (e) {
        if (!cancelled) {
          setError(parseApiError(e))
          setPage(defaultPage)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [query, scope])

  const updateQuery = useCallback(
    (patch: Partial<TicketQueryParams>) => {
      setSearchParams(writeParams({ ...query, ...patch }), { replace: true })
    },
    [query, setSearchParams],
  )

  const resetFilters = useCallback(() => {
    setSearchDraft('')
    setSearchParams(writeParams({ page: 1, limit: query.limit, sort: 'newest' }), { replace: true })
  }, [query.limit, setSearchParams])

  return {
    query,
    searchDraft,
    setSearchDraft,
    page,
    loading,
    error,
    updateQuery,
    resetFilters,
  }
}
