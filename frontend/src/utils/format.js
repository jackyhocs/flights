const MONTH_NAMES = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
]

const CURRENCY_FORMATTER = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
})

export function formatDuration(totalMinutes) {
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${hours}h ${minutes}m`
}

export function formatCurrency(amount) {
  return CURRENCY_FORMATTER.format(amount)
}

// Formats a naive local ISO timestamp (e.g. "2024-03-15T08:30:00") as written,
// without letting the browser's own timezone shift the displayed wall-clock time.
export function formatLocalDateTime(isoString) {
  const [datePart, timePart] = isoString.split('T')
  const [year, month, day] = datePart.split('-').map(Number)
  const [hour24, minute] = timePart.split(':').map(Number)

  const period = hour24 < 12 ? 'AM' : 'PM'
  const hour12 = hour24 % 12 === 0 ? 12 : hour24 % 12
  const paddedMinute = String(minute).padStart(2, '0')

  return `${MONTH_NAMES[month - 1]} ${day}, ${year} · ${hour12}:${paddedMinute} ${period}`
}
