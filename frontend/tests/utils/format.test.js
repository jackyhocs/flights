import { describe, expect, it } from 'vitest'

import { formatCurrency, formatDuration, formatLocalDateTime, formatTimezoneAbbreviation } from '../../src/utils/format'

describe('formatDuration', () => {
  it('formats whole hours and minutes', () => {
    expect(formatDuration(195)).toBe('3h 15m')
  })

  it('formats durations under an hour', () => {
    expect(formatDuration(45)).toBe('0h 45m')
  })

  it('formats durations that are exact hours', () => {
    expect(formatDuration(120)).toBe('2h 0m')
  })
})

describe('formatCurrency', () => {
  it('formats a numeric amount as USD', () => {
    expect(formatCurrency(299)).toBe('$299.00')
  })

  it('rounds to two decimal places', () => {
    expect(formatCurrency(299.5)).toBe('$299.50')
  })
})

describe('formatLocalDateTime', () => {
  it('formats a naive local ISO timestamp without applying a timezone shift', () => {
    expect(formatLocalDateTime('2024-03-15T08:30:00')).toBe('Mar 15, 2024 · 8:30 AM')
  })

  it('formats midnight as 12 AM', () => {
    expect(formatLocalDateTime('2024-03-15T00:05:00')).toBe('Mar 15, 2024 · 12:05 AM')
  })

  it('formats noon as 12 PM', () => {
    expect(formatLocalDateTime('2024-03-15T12:00:00')).toBe('Mar 15, 2024 · 12:00 PM')
  })

  it('formats a late evening time as PM', () => {
    expect(formatLocalDateTime('2024-03-15T23:45:00')).toBe('Mar 15, 2024 · 11:45 PM')
  })
})

describe('formatTimezoneAbbreviation', () => {
  it('resolves the abbreviation for a US zone observing daylight saving in March', () => {
    expect(formatTimezoneAbbreviation('2024-03-15T08:30:00', 'America/Los_Angeles')).toBe('PDT')
  })

  it('resolves the abbreviation for a Southern Hemisphere zone (used by the SYD -> LAX date-line case)', () => {
    expect(formatTimezoneAbbreviation('2024-03-16T09:00:00', 'Australia/Sydney')).toBe('GMT+11')
  })

  it('resolves a fixed-offset zone with no daylight saving', () => {
    expect(formatTimezoneAbbreviation('2024-03-15T08:30:00', 'Asia/Tokyo')).toBe('GMT+9')
  })
})
