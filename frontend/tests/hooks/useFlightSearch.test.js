import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { useFlightSearch } from '../../src/hooks/useFlightSearch'

vi.mock('../../src/api/searchApi', () => ({
  searchFlights: vi.fn(),
}))

import { searchFlights } from '../../src/api/searchApi'

describe('useFlightSearch', () => {
  it('starts with no data, no error, and not loading', () => {
    const { result } = renderHook(() => useFlightSearch())

    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
    expect(result.current.loading).toBe(false)
  })

  it('sets data on a successful search', async () => {
    const responseBody = { origin: 'JFK', destination: 'LAX', date: '2024-03-15', count: 1, itineraries: [] }
    searchFlights.mockResolvedValueOnce(responseBody)

    const { result } = renderHook(() => useFlightSearch())

    act(() => {
      result.current.search({ origin: 'JFK', destination: 'LAX', date: '2024-03-15' })
    })

    expect(result.current.loading).toBe(true)

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.data).toEqual(responseBody)
    expect(result.current.error).toBeNull()
  })

  it('sets an error message and clears data on a failed search', async () => {
    searchFlights.mockRejectedValueOnce(new Error('unknown airport code: XXX'))

    const { result } = renderHook(() => useFlightSearch())

    act(() => {
      result.current.search({ origin: 'XXX', destination: 'LAX', date: '2024-03-15' })
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.error).toBe('unknown airport code: XXX')
    expect(result.current.data).toBeNull()
  })

  it('clears existing data via clear()', async () => {
    const responseBody = { origin: 'JFK', destination: 'LAX', date: '2024-03-15', count: 1, itineraries: [] }
    searchFlights.mockResolvedValueOnce(responseBody)

    const { result } = renderHook(() => useFlightSearch())

    act(() => {
      result.current.search({ origin: 'JFK', destination: 'LAX', date: '2024-03-15' })
    })
    await waitFor(() => expect(result.current.data).toEqual(responseBody))

    act(() => {
      result.current.clear()
    })

    expect(result.current.data).toBeNull()
  })
})
