import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import LoadingSpinner from '../../src/components/LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders a searching message', () => {
    render(<LoadingSpinner />)

    expect(screen.getByText('Searching for itineraries...')).toBeInTheDocument()
  })
})
