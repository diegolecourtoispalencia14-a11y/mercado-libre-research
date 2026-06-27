import { describe, it, expect } from 'vitest'
import { scoreColor, scoreLabel } from '../utils/scoring'

describe('scoreColor', () => {
  it('returns green for high scores', () => {
    expect(scoreColor(8.5)).toBe('text-green-600')
  })
  it('returns yellow for medium scores', () => {
    expect(scoreColor(5.0)).toBe('text-yellow-500')
  })
  it('returns red for low scores', () => {
    expect(scoreColor(2.0)).toBe('text-red-500')
  })
})

describe('scoreLabel', () => {
  it('labels high scores as Alta oportunidad', () => {
    expect(scoreLabel(8)).toBe('Alta oportunidad')
  })
  it('labels medium scores as Oportunidad media', () => {
    expect(scoreLabel(5)).toBe('Oportunidad media')
  })
  it('labels low scores as Baja oportunidad', () => {
    expect(scoreLabel(2)).toBe('Baja oportunidad')
  })
})
