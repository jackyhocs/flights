import Alert from '@mui/material/Alert'

function ErrorBanner({ message }) {
  return <Alert severity="error">{message}</Alert>
}

export default ErrorBanner
