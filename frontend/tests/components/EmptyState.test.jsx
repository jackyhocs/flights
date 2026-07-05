import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import EmptyState from '../../src/components/EmptyState'

describe('EmptyState', () => {
  it('renders a message naming the searched route and date', () => {
    render(<EmptyState origin="JFK" destination="LAX" date="2024-03-15" />)

    expect(screen.getByText('No itineraries found from JFK to LAX on 2024-03-15.')).toBeInTheDocument()
  })
})
