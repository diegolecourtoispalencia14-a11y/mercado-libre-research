import { render, screen } from '@testing-library/react'
import ScoreBadge from '../components/ScoreBadge'

test('shows score value', () => {
  render(<ScoreBadge score={7.5} trendAvailable={true} />)
  expect(screen.getByText('7.5')).toBeInTheDocument()
})

test('shows sin datos badge when trend unavailable', () => {
  render(<ScoreBadge score={5.0} trendAvailable={false} />)
  expect(screen.getByText(/sin datos de tendencia/i)).toBeInTheDocument()
})
