import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { TicketTable } from './TicketTable'
import type { Ticket } from '@/types/api'

const ticket: Ticket = {
  id: 42,
  title: 'Payment refund needed',
  description: 'The payment was deducted twice.',
  status: 'open',
  priority: 'high',
  customer_id: 1,
  assigned_agent_id: 7,
  sentiment: 'negative',
  urgency_score: 3,
  created_at: '2026-05-14T12:00:00Z',
  updated_at: '2026-05-14T12:00:00Z',
}

describe('TicketTable', () => {
  it('renders ticket rows with an accessible detail link', () => {
    render(
      <MemoryRouter>
        <TicketTable tickets={[ticket]} />
      </MemoryRouter>,
    )

    expect(screen.getByRole('table', { name: /support tickets/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /payment refund needed/i })).toHaveAttribute(
      'href',
      '/tickets/42',
    )
    expect(screen.getByText('high')).toBeInTheDocument()
  })
})
