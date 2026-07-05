import { faHourglassHalf } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Chip from '@mui/material/Chip'

import { formatDuration } from '../utils/format'

function LayoverBadge({ layover }) {
  return (
    <Chip
      size="small"
      variant="outlined"
      color={layover.type === 'international' ? 'warning' : 'default'}
      icon={<FontAwesomeIcon icon={faHourglassHalf} />}
      label={`${formatDuration(layover.durationMinutes)} layover in ${layover.airport} (${layover.type})`}
    />
  )
}

export default LayoverBadge
