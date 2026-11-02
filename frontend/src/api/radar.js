import { apiFetch } from './client'

export async function getOpportunities(status = 'active') {
  return apiFetch(`/radar?status=${encodeURIComponent(status)}`)
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
