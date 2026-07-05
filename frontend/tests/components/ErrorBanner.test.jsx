import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import ErrorBanner from '../../src/components/ErrorBanner'

describe('ErrorBanner', () => {
  it('renders the given error message', () => {
    render(<ErrorBanner message="Something went wrong." />)

    expect(screen.getByText('Something went wrong.')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })
})
