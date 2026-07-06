import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import ItineraryCard from '../../src/components/ItineraryCard'

const NONSTOP_ITINERARY = {
  id: 'SP101',
  stops: 0,
  totalDurationMinutes: 195,
  totalPrice: 299,
  tripType: 'domestic',
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
  tripType: 'domestic',
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

const INTERNATIONAL_ITINERARY = {
  id: 'SP301-SP302',
  stops: 1,
  totalDurationMinutes: 600,
  totalPrice: 900,
  tripType: 'international',
  segments: [
    {
      flightNumber: 'SP301',
      airline: 'SkyPath Airways',
      origin: 'JFK',
      destination: 'LHR',
      departureTimeLocal: '2024-03-15T20:00:00',
      arrivalTimeLocal: '2024-03-16T08:00:00',
      price: 500,
      aircraft: 'A330',
    },
    {
      flightNumber: 'SP302',
      airline: 'SkyPath Airways',
      origin: 'LHR',
      destination: 'CDG',
      departureTimeLocal: '2024-03-16T10:00:00',
      arrivalTimeLocal: '2024-03-16T12:00:00',
      price: 400,
      aircraft: 'A320',
    },
  ],
  layovers: [{ airport: 'LHR', durationMinutes: 120, type: 'international' }],
}

describe('ItineraryCard', () => {
  it('renders a nonstop itinerary with no layover badges', () => {
    render(<ItineraryCard itinerary={NONSTOP_ITINERARY} />)

    expect(screen.getByText('Nonstop')).toBeInTheDocument()
    expect(screen.getByText('Domestic')).toBeInTheDocument()
    expect(screen.getByText(/3h 15m/)).toBeInTheDocument()
    expect(screen.getAllByText('$299.00')).toHaveLength(2)
    expect(screen.getByText('JFK → LAX')).toBeInTheDocument()
    expect(screen.queryByText(/layover/)).not.toBeInTheDocument()
  })

  it('renders a one-stop itinerary with both segments and the layover badge between them', () => {
    render(<ItineraryCard itinerary={ONE_STOP_ITINERARY} />)

    expect(screen.getByText('1 stop')).toBeInTheDocument()
    expect(screen.getByText('Domestic')).toBeInTheDocument()
    expect(screen.getByText(/5h 30m/)).toBeInTheDocument()
    expect(screen.getByText('$450.00')).toBeInTheDocument()
    expect(screen.getByText('JFK → ORD')).toBeInTheDocument()
    expect(screen.getByText('ORD → LAX')).toBeInTheDocument()
    expect(screen.getByText(/1h 30m layover in ORD \(domestic\)/)).toBeInTheDocument()
  })

  it('labels an itinerary with an international layover as International', () => {
    render(<ItineraryCard itinerary={INTERNATIONAL_ITINERARY} />)

    expect(screen.getByText('International')).toBeInTheDocument()
  })
})
