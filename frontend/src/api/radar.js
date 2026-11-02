import { apiFetch } from './client'

export async function getOpportunities(status = 'active', archetypeOnly = false) {
  const params = new URLSearchParams({ status })
  if (archetypeOnly) {
    params.set('archetype_only', 'true')
  }
  return apiFetch(`/radar?${params.toString()}`)
}

export async function getRadarStatus() {
  return apiFetch('/radar/status')
}

export async function triggerScan() {
  return apiFetch('/radar/scan', { method: 'POST' })
}

export async function updateOpportunityStatus(id, status, notes = '') {
  return apiFetch(`/radar/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ status, notes }),
  })
}
