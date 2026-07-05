import CircularProgress from '@mui/material/CircularProgress'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

function LoadingSpinner() {
  return (
    <Stack direction="row" spacing={1.5} alignItems="center" sx={{ py: 2 }}>
      <CircularProgress size={20} />
      <Typography color="text.secondary">Searching for itineraries...</Typography>
    </Stack>
  )
}

export default LoadingSpinner
