import { apiFetch } from './client'

export const analyzeProduct = (mlId) => apiFetch(`/analyze/${mlId}`)
