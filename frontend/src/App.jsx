import { faPlaneUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import AppBar from '@mui/material/AppBar'
import Container from '@mui/material/Container'
import CssBaseline from '@mui/material/CssBaseline'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'

import SearchForm from './components/SearchForm'

function App() {
  const handleSearch = (params) => {
    // API wiring lands in the next step; log for now.
    console.log('search', params)
  }

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
        <SearchForm onSearch={handleSearch} />
      </Container>
    </>
  )
}

export default App
