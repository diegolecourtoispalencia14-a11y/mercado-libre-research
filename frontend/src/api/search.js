import { apiFetch } from './client'

export const searchProducts = (q, limit = 50) =>
  apiFetch(`/search?q=${encodeURIComponent(q)}&limit=${limit}`)
