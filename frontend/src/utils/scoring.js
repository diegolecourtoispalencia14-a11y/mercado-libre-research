export function scoreColor(score) {
  if (score >= 7) return 'text-green-600'
  if (score >= 4) return 'text-yellow-500'
  return 'text-red-500'
}

export function scoreLabel(score) {
  if (score >= 7) return 'Alta oportunidad'
  if (score >= 4) return 'Oportunidad media'
  return 'Baja oportunidad'
}
