import { faPlaneUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import AppBar from '@mui/material/AppBar'
import Container from '@mui/material/Container'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'

function App() {
  return (
    <>
      <AppBar position="sticky" color="default" elevation={1}>
        <Toolbar variant="dense">
          <Typography variant="h6" component="span" sx={{ fontWeight: 600 }}>
            <FontAwesomeIcon icon={faPlaneUp} /> SkyPath
          </Typography>
        </Toolbar>
      </AppBar>

      <Container component="main" maxWidth="sm" sx={{ py: 4 }}>
        <Typography variant="body1">Hello world.</Typography>
      </Container>
    </>
  )
}

export default App
