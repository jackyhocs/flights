import { faPlaneUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import AppBar from '@mui/material/AppBar'
import Container from '@mui/material/Container'
import CssBaseline from '@mui/material/CssBaseline'
import Stack from '@mui/material/Stack'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'

import EmptyState from './components/EmptyState'
import ErrorBanner from './components/ErrorBanner'
import LoadingSpinner from './components/LoadingSpinner'
import ResultsList from './components/ResultsList'
import SearchForm from './components/SearchForm'
import { useFlightSearch } from './hooks/useFlightSearch'

function App() {
  const { data, loading, error, search, clear } = useFlightSearch()

  return (
    <>
      <CssBaseline />
      <AppBar position="sticky" color="default" elevation={1}>
        <Toolbar variant="dense">
          <Typography variant="h6" component="span" sx={{ fontWeight: 600 }}>
            <FontAwesomeIcon icon={faPlaneUp} /> SkyPath
          </Typography>
        </Toolbar>
      </AppBar>

      <Container component="main" maxWidth="sm" sx={{ py: 4 }}>
        <Stack spacing={2}>
          <SearchForm onSearch={search} onValidationError={clear} />

          {loading && <LoadingSpinner />}
          {error && <ErrorBanner message={error} />}
          {data && (
            <>
              {data.count > 0 ? (
                <>
                  <Typography>
                    Found {data.count} itinerar{data.count === 1 ? 'y' : 'ies'} from {data.origin} to{' '}
                    {data.destination} on {data.date}.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Sorted by total trip duration, shortest first.
                  </Typography>
                  <ResultsList itineraries={data.itineraries} />
                </>
              ) : (
                <EmptyState origin={data.origin} destination={data.destination} date={data.date} />
              )}
            </>
          )}
        </Stack>
      </Container>
    </>
  )
}

export default App
