import { afterEach, describe, expect, it, vi } from 'vitest'

import { searchFlights } from '../../src/api/searchApi'

function mockFetchOnce({ ok, body }) {
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok,
    json: () => Promise.resolve(body),
  })
}

describe('searchFlights', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('requests the search endpoint with the given params and returns the parsed body', async () => {
    const responseBody = { origin: 'JFK', destination: 'LAX', date: '2024-03-15', count: 0, itineraries: [] }
    mockFetchOnce({ ok: true, body: responseBody })

    const result = await searchFlights({ origin: 'JFK', destination: 'LAX', date: '2024-03-15' })

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/search\?origin=JFK&destination=LAX&date=2024-03-15$/),
    )
    expect(result).toEqual(responseBody)
  })

  it('throws the backend error message when the response is not ok', async () => {
    mockFetchOnce({ ok: false, body: { error: 'unknown airport code: XXX' } })

    await expect(
      searchFlights({ origin: 'XXX', destination: 'LAX', date: '2024-03-15' }),
    ).rejects.toThrow('unknown airport code: XXX')
  })

  it('falls back to a generic message when the error response has no error key', async () => {
    mockFetchOnce({ ok: false, body: {} })

    await expect(
      searchFlights({ origin: 'JFK', destination: 'LAX', date: '2024-03-15' }),
    ).rejects.toThrow('Something went wrong while searching for flights.')
  })
})
