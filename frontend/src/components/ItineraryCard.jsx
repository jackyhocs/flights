import { faClock, faTag } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Chip from '@mui/material/Chip'
import Divider from '@mui/material/Divider'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

import { formatCurrency, formatDuration } from '../utils/format'
import LayoverBadge from './LayoverBadge'
import SegmentRow from './SegmentRow'

function stopsLabel(stops) {
  if (stops === 0) return 'Nonstop '
  return `${stops} stop${stops > 1 ? 's' : ''} `
}

function ItineraryCard({ itinerary }) {
  const domestic = itinerary.tripType === 'domestic'

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack direction="row" justifyContent="flex-start" alignItems="center">
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip
              label={stopsLabel(itinerary.stops)}
              size="small"
              sx={{ backgroundColor: '#cdeafe', color: '#0d3b66', fontWeight: 600 }}
            />
            <Chip
              label={domestic ? 'Domestic' : 'International'}
              size="small"
              variant="outlined"
              color={domestic ? 'default' : 'warning'}
            />
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              <FontAwesomeIcon icon={faClock} /> {formatDuration(itinerary.totalDurationMinutes)}
            </Typography>
          </Stack>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, ml: 'auto' }}>
            <FontAwesomeIcon icon={faTag} /> {formatCurrency(itinerary.totalPrice)}
          </Typography>
        </Stack>

        <Divider sx={{ my: 1 }} />

        {itinerary.segments.map((segment, index) => (
          <div key={segment.flightNumber}>
            <SegmentRow segment={segment} />
            {itinerary.layovers[index] && (
              <Stack sx={{ py: 1 }}>
                <LayoverBadge layover={itinerary.layovers[index]} />
              </Stack>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

export default ItineraryCard
