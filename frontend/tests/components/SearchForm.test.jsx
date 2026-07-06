import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import SearchForm from '../../src/components/SearchForm'
import { validate } from '../../src/components/searchFormValidation'

// Pure validation logic, no rendering required.
describe('validate', () => {
  it('returns null when origin, destination, and date are all provided and differ', () => {
    expect(validate({ origin: 'JFK', destination: 'LAX', date: '2024-03-15' })).toBeNull()
  })

  it('rejects missing fields', () => {
    expect(validate({ origin: '', destination: 'LAX', date: '2024-03-15' })).toMatch(/select/i)
    expect(validate({ origin: 'JFK', destination: '', date: '2024-03-15' })).toMatch(/select/i)
    expect(validate({ origin: 'JFK', destination: 'LAX', date: '' })).toMatch(/select/i)
  })

  it('rejects identical origin and destination', () => {
    expect(validate({ origin: 'JFK', destination: 'JFK', date: '2024-03-15' })).toMatch(/different/i)
  })
})

// Rendered form behavior.
describe('SearchForm', () => {
  it('calls onSearch with the selected values when the form is valid', async () => {
    const user = userEvent.setup()
    const onSearch = vi.fn()
    render(<SearchForm onSearch={onSearch} />)

    await user.click(screen.getByLabelText(/origin/i))
    await user.click(await screen.findByRole('option', { name: /JFK/i }))

    await user.click(screen.getByLabelText(/destination/i))
    await user.click(await screen.findByRole('option', { name: /LAX/i }))

    await user.type(screen.getByLabelText(/date/i), '2024-03-15')
    await user.click(screen.getByRole('button', { name: /search/i }))

    expect(onSearch).toHaveBeenCalledWith({ origin: 'JFK', destination: 'LAX', date: '2024-03-15' })
  })

  it('shows a validation error and does not call onSearch when fields are missing', async () => {
    const user = userEvent.setup()
    const onSearch = vi.fn()
    render(<SearchForm onSearch={onSearch} />)

    await user.click(screen.getByRole('button', { name: /search/i }))

    expect(await screen.findByText(/please select/i)).toBeInTheDocument()
    expect(onSearch).not.toHaveBeenCalled()
  })

  it('shows a validation error when origin and destination are the same', async () => {
    const user = userEvent.setup()
    const onSearch = vi.fn()
    render(<SearchForm onSearch={onSearch} />)

    await user.click(screen.getByLabelText(/origin/i))
    await user.click(await screen.findByRole('option', { name: /JFK/i }))

    await user.click(screen.getByLabelText(/destination/i))
    await user.click(await screen.findByRole('option', { name: /JFK/i }))

    await user.type(screen.getByLabelText(/date/i), '2024-03-15')
    await user.click(screen.getByRole('button', { name: /search/i }))

    expect(await screen.findByText(/different/i)).toBeInTheDocument()
    expect(onSearch).not.toHaveBeenCalled()
  })

  it('calls onValidationError instead of onSearch when the form is invalid', async () => {
    const user = userEvent.setup()
    const onSearch = vi.fn()
    const onValidationError = vi.fn()
    render(<SearchForm onSearch={onSearch} onValidationError={onValidationError} />)

    await user.click(screen.getByRole('button', { name: /search/i }))

    expect(await screen.findByText(/please select/i)).toBeInTheDocument()
    expect(onValidationError).toHaveBeenCalledTimes(1)
    expect(onSearch).not.toHaveBeenCalled()
  })
})
