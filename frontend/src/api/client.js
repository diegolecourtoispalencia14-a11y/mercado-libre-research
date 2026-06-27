const BASE = '/api'

export async function apiFetch(path, options = {}) {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!resp.ok) throw new Error(`API error ${resp.status}: ${await resp.text()}`)
  return resp.json()
}
