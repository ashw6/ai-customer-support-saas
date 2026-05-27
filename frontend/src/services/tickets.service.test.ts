import { describe, expect, it, vi } from 'vitest'
import { fetchAllTicketsPage } from './tickets.service'
import { api, parseApiError } from './api'

vi.mock('./api', async () => {
  const actual = await vi.importActual<typeof import('./api')>('./api')
  return {
    ...actual,
    api: {
      get: vi.fn(),
    },
  }
})

describe('tickets service', () => {
  it('maps UI query params to the Phase 2 backend API shape', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({
      data: {
        success: true,
        data: { items: [], total: 0, page: 2, limit: 25, pages: 0 },
      },
    })

    await fetchAllTicketsPage({
      page: 2,
      limit: 25,
      search: 'payment',
      priority: 'high',
      sentiment: 'negative',
      assigned_agent_id: 7,
      sort: 'oldest',
    })

    expect(api.get).toHaveBeenCalledWith('/tickets', {
      params: expect.objectContaining({
        page: 2,
        limit: 25,
        search: 'payment',
        priority: 'high',
        sentiment: 'negative',
        assigned_agent_id: 7,
        sort_by: 'created_at',
        order: 'asc',
      }),
    })
  })
})

describe('parseApiError', () => {
  it('normalizes backend error messages', () => {
    expect(
      parseApiError({
        isAxiosError: true,
        response: { status: 422, data: { message: 'Invalid limit' } },
      }),
    ).toBe('Invalid limit')
  })
})
