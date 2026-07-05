import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Divider from '@mui/material/Divider'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

import { formatCurrency, formatDuration } from '../utils/format'
import LayoverBadge from './LayoverBadge'
import SegmentRow from './SegmentRow'

function stopsLabel(stops) {
  if (stops === 0) return 'Nonstop'
  return `${stops} stop${stops > 1 ? 's' : ''}`
}

function ItineraryCard({ itinerary }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="baseline">
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            {stopsLabel(itinerary.stops)} · {formatDuration(itinerary.totalDurationMinutes)}
          </Typography>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            {formatCurrency(itinerary.totalPrice)}
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
