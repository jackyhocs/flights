export function validate({ origin, destination, date }) {
  if (!origin || !destination || !date) {
    return 'Please select an origin, destination, and date.'
  }
  if (origin === destination) {
    return 'Origin and destination must be different airports.'
  }
  return null
}
