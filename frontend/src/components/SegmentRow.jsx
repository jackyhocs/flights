import { faPlaneDeparture } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

import { formatCurrency, formatLocalDateTime } from '../utils/format'

function SegmentRow({ segment }) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ py: 1 }}>
      <Stack>
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          <FontAwesomeIcon icon={faPlaneDeparture} /> {segment.origin} → {segment.destination}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {formatLocalDateTime(segment.departureTimeLocal)} — {formatLocalDateTime(segment.arrivalTimeLocal)}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {segment.airline} {segment.flightNumber} · {segment.aircraft}
        </Typography>
      </Stack>

      <Typography variant="body2">{formatCurrency(segment.price)}</Typography>
    </Stack>
  )
}

export default SegmentRow
