import Stack from '@mui/material/Stack'

import ItineraryCard from './ItineraryCard'

function ResultsList({ itineraries }) {
  return (
    <Stack spacing={2}>
      {itineraries.map((itinerary) => (
        <ItineraryCard key={itinerary.id} itinerary={itinerary} />
      ))}
    </Stack>
  )
}

export default ResultsList
