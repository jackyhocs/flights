import { faPlaneSlash } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

function EmptyState({ origin, destination, date }) {
  return (
    <Stack spacing={1} alignItems="center" sx={{ py: 4, color: 'text.secondary' }}>
      <FontAwesomeIcon icon={faPlaneSlash} size="2x" />
      <Typography>
        No itineraries found from {origin} to {destination} on {date}.
      </Typography>
      <Typography variant="body2">Try a different date or route.</Typography>
    </Stack>
  )
}

export default EmptyState
