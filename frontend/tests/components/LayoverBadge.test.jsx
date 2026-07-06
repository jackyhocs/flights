import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import LayoverBadge from '../../src/components/LayoverBadge'

describe('LayoverBadge', () => {
  it('renders a domestic layover', () => {
    render(<LayoverBadge layover={{ airport: 'ORD', durationMinutes: 90, type: 'domestic' }} />)

    expect(screen.getByText(/1h 30m layover in ORD/)).toBeInTheDocument()
  })

  it('renders an international layover', () => {
    render(<LayoverBadge layover={{ airport: 'LHR', durationMinutes: 130, type: 'international' }} />)

    expect(screen.getByText(/2h 10m layover in LHR/)).toBeInTheDocument()
  })
})
