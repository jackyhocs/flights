import { faPlaneArrival, faPlaneDeparture } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

import { AIRPORT_TIMEZONES } from '../data/airports'
import { formatCurrency, formatDuration, formatLocalDateTime, formatTimezoneAbbreviation } from '../utils/format'

function SegmentRow({ segment }) {
  const departureTz = formatTimezoneAbbreviation(segment.departureTimeLocal, AIRPORT_TIMEZONES[segment.origin])
  const arrivalTz = formatTimezoneAbbreviation(segment.arrivalTimeLocal, AIRPORT_TIMEZONES[segment.destination])

  return (
    <Stack direction="row" justifyContent="flex-start" alignItems="flex-start" sx={{ py: 1 }}>
      <Stack>
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          <FontAwesomeIcon icon={faPlaneDeparture} /> {segment.origin} → <FontAwesomeIcon icon={faPlaneArrival} />{' '}
          {segment.destination}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {formatLocalDateTime(segment.departureTimeLocal)} {departureTz} — {formatLocalDateTime(segment.arrivalTimeLocal)}{' '}
          {arrivalTz}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {segment.airline} {segment.flightNumber} · {segment.aircraft} · {formatDuration(segment.durationMinutes)}
        </Typography>
      </Stack>

      <Typography variant="body2" sx={{ ml: 'auto' }}>
        {formatCurrency(segment.price)}
      </Typography>
    </Stack>
  )
}

export default SegmentRow
