const BASE = '/api'

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('mlm_research_token')
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {}

  const resp = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader,
      ...options.headers,
    },
  })

  if (resp.status === 401 && path !== '/auth/login') {
    localStorage.removeItem('mlm_research_token')
    localStorage.removeItem('mlm_research_user')
    window.dispatchEvent(new Event('auth:unauthorized'))
    throw new Error('Sesión expirada o no autorizada. Inicia sesión nuevamente.')
  }

  if (!resp.ok) {
    let errorDetail = `API error ${resp.status}`
    try {
      const errJson = await resp.json()
      if (errJson.detail) errorDetail = errJson.detail
    } catch {
      errorDetail = await resp.text()
    }
    throw new Error(errorDetail)
  }

  return resp.json()
}
