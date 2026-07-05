import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import ResultsList from '../../src/components/ResultsList'

function itinerary(id, price) {
  return {
    id,
    stops: 0,
    totalDurationMinutes: 195,
    totalPrice: price,
    segments: [
      {
        flightNumber: id,
        airline: 'SkyPath Airways',
        origin: 'JFK',
        destination: 'LAX',
        departureTimeLocal: '2024-03-15T08:30:00',
        arrivalTimeLocal: '2024-03-15T11:45:00',
        price,
        aircraft: 'A320',
      },
    ],
    layovers: [],
  }
}

describe('ResultsList', () => {
  it('renders no cards when there are no itineraries', () => {
    render(<ResultsList itineraries={[]} />)

    expect(screen.queryByText(/Nonstop/)).not.toBeInTheDocument()
  })

  it('renders one card per itinerary', () => {
    render(<ResultsList itineraries={[itinerary('SP101', 299), itinerary('SP102', 349)]} />)

    expect(screen.getAllByText(/Nonstop/)).toHaveLength(2)
    expect(screen.getAllByText('$299.00')).toHaveLength(2)
    expect(screen.getAllByText('$349.00')).toHaveLength(2)
  })
})
