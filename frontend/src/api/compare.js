import { apiFetch } from './client'

export const compareProducts = (productIds) =>
  apiFetch('/compare', { method: 'POST', body: JSON.stringify({ product_ids: productIds }) })
