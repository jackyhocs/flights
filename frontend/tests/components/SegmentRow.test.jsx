import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import SegmentRow from '../../src/components/SegmentRow'

const SEGMENT = {
  flightNumber: 'SP101',
  airline: 'SkyPath Airways',
  origin: 'JFK',
  destination: 'LAX',
  departureTimeLocal: '2024-03-15T08:30:00',
  arrivalTimeLocal: '2024-03-15T11:45:00',
  durationMinutes: 195,
  price: 299,
  aircraft: 'A320',
}

describe('SegmentRow', () => {
  it('renders the route, times, flight details, duration, and price', () => {
    render(<SegmentRow segment={SEGMENT} />)

    expect(screen.getByText('JFK → LAX')).toBeInTheDocument()
    expect(screen.getByText(/Mar 15, 2024 · 8:30 AM/)).toBeInTheDocument()
    expect(screen.getByText(/Mar 15, 2024 · 11:45 AM/)).toBeInTheDocument()
    expect(screen.getByText(/SkyPath Airways SP101 · A320 · 3h 15m/)).toBeInTheDocument()
    expect(screen.getByText('$299.00')).toBeInTheDocument()
  })
})
