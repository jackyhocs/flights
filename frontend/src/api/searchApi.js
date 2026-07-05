const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5000'

export async function searchFlights({ origin, destination, date }) {
  const params = new URLSearchParams({ origin, destination, date })
  const response = await fetch(`${API_BASE_URL}/api/search?${params}`)
  const body = await response.json()

  if (!response.ok) {
    throw new Error(body.error ?? 'Something went wrong while searching for flights.')
  }

  return body
}
