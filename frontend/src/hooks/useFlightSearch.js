import { useCallback, useState } from 'react'

import { searchFlights } from '../api/searchApi'

export function useFlightSearch() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const search = useCallback(async (params) => {
    setLoading(true)
    setError(null)

    try {
      const result = await searchFlights(params)
      setData(result)
    } catch (err) {
      setError(err.message)
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, search }
}
