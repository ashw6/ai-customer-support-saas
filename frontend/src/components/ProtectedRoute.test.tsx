import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { ProtectedRoute } from './ProtectedRoute'

vi.mock('@/context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, name: 'Customer', email: 'c@example.com', role: 'customer' },
    loading: false,
  }),
}))

describe('ProtectedRoute', () => {
  it('redirects users away from inaccessible role routes', () => {
    render(
      <MemoryRouter initialEntries={['/support/dashboard']}>
        <Routes>
          <Route
            path="/support/dashboard"
            element={
              <ProtectedRoute roles={['support_agent']}>
                <div>Support only</div>
              </ProtectedRoute>
            }
          />
          <Route path="/customer/dashboard" element={<div>Customer home</div>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByText('Customer home')).toBeInTheDocument()
  })
})
