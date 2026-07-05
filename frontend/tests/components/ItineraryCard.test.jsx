import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import ItineraryCard from '../../src/components/ItineraryCard'

const NONSTOP_ITINERARY = {
  id: 'SP101',
  stops: 0,
  totalDurationMinutes: 195,
  totalPrice: 299,
  segments: [
    {
      flightNumber: 'SP101',
      airline: 'SkyPath Airways',
      origin: 'JFK',
      destination: 'LAX',
      departureTimeLocal: '2024-03-15T08:30:00',
      arrivalTimeLocal: '2024-03-15T11:45:00',
      price: 299,
      aircraft: 'A320',
    },
  ],
  layovers: [],
}

const ONE_STOP_ITINERARY = {
  id: 'SP101-SP202',
  stops: 1,
  totalDurationMinutes: 330,
  totalPrice: 450,
  segments: [
    {
      flightNumber: 'SP101',
      airline: 'SkyPath Airways',
      origin: 'JFK',
      destination: 'ORD',
      departureTimeLocal: '2024-03-15T08:30:00',
      arrivalTimeLocal: '2024-03-15T10:00:00',
      price: 200,
      aircraft: 'A320',
    },
    {
      flightNumber: 'SP202',
      airline: 'SkyPath Airways',
      origin: 'ORD',
      destination: 'LAX',
      departureTimeLocal: '2024-03-15T11:30:00',
      arrivalTimeLocal: '2024-03-15T14:00:00',
      price: 250,
      aircraft: 'A321',
    },
  ],
  layovers: [{ airport: 'ORD', durationMinutes: 90, type: 'domestic' }],
}

describe('ItineraryCard', () => {
  it('renders a nonstop itinerary with no layover badges', () => {
    render(<ItineraryCard itinerary={NONSTOP_ITINERARY} />)

    expect(screen.getByText('Nonstop')).toBeInTheDocument()
    expect(screen.getByText(/3h 15m/)).toBeInTheDocument()
    expect(screen.getAllByText('$299.00')).toHaveLength(2)
    expect(screen.getByText('JFK → LAX')).toBeInTheDocument()
    expect(screen.queryByText(/layover/)).not.toBeInTheDocument()
  })

  it('renders a one-stop itinerary with both segments and the layover badge between them', () => {
    render(<ItineraryCard itinerary={ONE_STOP_ITINERARY} />)

    expect(screen.getByText('1 stop')).toBeInTheDocument()
    expect(screen.getByText(/5h 30m/)).toBeInTheDocument()
    expect(screen.getByText('$450.00')).toBeInTheDocument()
    expect(screen.getByText('JFK → ORD')).toBeInTheDocument()
    expect(screen.getByText('ORD → LAX')).toBeInTheDocument()
    expect(screen.getByText(/1h 30m layover in ORD \(domestic\)/)).toBeInTheDocument()
  })
})
