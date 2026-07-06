import { useState } from 'react'
import Button from '@mui/material/Button'
import MenuItem from '@mui/material/MenuItem'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'

import { AIRPORTS } from '../data/airports'
import { validate } from './searchFormValidation'

function SearchForm({ onSearch, onValidationError }) {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [date, setDate] = useState('')
  const [error, setError] = useState(null)

  const handleSubmit = (event) => {
    event.preventDefault()

    const validationError = validate({ origin, destination, date })
    setError(validationError)
    if (validationError) {
      onValidationError?.()
      return
    }

    onSearch({ origin, destination, date })
  }

  return (
    <Stack component="form" onSubmit={handleSubmit} spacing={2} noValidate>
      <TextField
        select
        label="Origin"
        value={origin}
        onChange={(event) => setOrigin(event.target.value)}
      >
        {AIRPORTS.map((airport) => (
          <MenuItem key={airport.code} value={airport.code}>
            {airport.code} - {airport.city}
          </MenuItem>
        ))}
      </TextField>

      <TextField
        select
        label="Destination"
        value={destination}
        onChange={(event) => setDestination(event.target.value)}
      >
        {AIRPORTS.map((airport) => (
          <MenuItem key={airport.code} value={airport.code}>
            {airport.code} - {airport.city}
          </MenuItem>
        ))}
      </TextField>

      <TextField
        label="Date"
        type="date"
        value={date}
        onChange={(event) => setDate(event.target.value)}
        slotProps={{ inputLabel: { shrink: true } }}
      />

      {error && (
        <Typography color="error" variant="body2">
          {error}
        </Typography>
      )}

      <Button type="submit" variant="contained">
        Search
      </Button>
    </Stack>
  )
}

export default SearchForm
