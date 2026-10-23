import { createContext, useContext, useState, useEffect } from 'react'
import { loginApi, logoutApi, getMeApi } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('mlm_research_token'))
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('mlm_research_user')
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function initAuth() {
      const savedToken = localStorage.getItem('mlm_research_token')
      if (savedToken) {
        try {
          const profile = await getMeApi()
          setUser(profile)
          localStorage.setItem('mlm_research_user', JSON.stringify(profile))
        } catch {
          // Token invalid or expired
          logout()
        }
      }
      setLoading(false)
    }

    initAuth()

    function handleUnauthorized() {
      setToken(null)
      setUser(null)
    }

    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [])

  async function login(username, password, honeypot = '') {
    const data = await loginApi(username, password, honeypot)
    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem('mlm_research_token', data.access_token)
    localStorage.setItem('mlm_research_user', JSON.stringify(data.user))
    return data.user
  }

  async function logout() {
    try {
      if (token) await logoutApi()
    } catch {
      // Ignore network errors on logout
    } finally {
      setToken(null)
      setUser(null)
      localStorage.removeItem('mlm_research_token')
      localStorage.removeItem('mlm_research_user')
    }
  }

  const value = {
    user,
    token,
    isAuthenticated: Boolean(token && user),
    loading,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
