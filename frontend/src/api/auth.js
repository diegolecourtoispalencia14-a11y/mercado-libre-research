import { apiFetch } from './client'

export async function loginApi(username, password, honeypot = '') {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password, honeypot }),
  })
}

export async function getMeApi() {
  return apiFetch('/auth/me')
}

export async function logoutApi() {
  return apiFetch('/auth/logout', { method: 'POST' })
}
