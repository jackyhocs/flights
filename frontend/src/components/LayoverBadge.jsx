import Chip from '@mui/material/Chip'

import { formatDuration } from '../utils/format'

function LayoverBadge({ layover }) {
  return (
    <Chip
      size="small"
      variant="outlined"
      color={layover.type === 'international' ? 'warning' : 'default'}
      label={`${formatDuration(layover.durationMinutes)} layover in ${layover.airport} (${layover.type})`}
    />
  )
}

export default LayoverBadge
