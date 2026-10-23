import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isAuthenticated } = useAuth()

  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('Admin!Riviera2026')
  const [honeypot, setHoneypot] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lockoutRemaining, setLockoutRemaining] = useState(0)

  const from = location.state?.from?.pathname || '/'

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, from])

  // Countdown timer for brute-force lockouts
  useEffect(() => {
    if (lockoutRemaining <= 0) return
    const timer = setInterval(() => {
      setLockoutRemaining(prev => (prev > 1 ? prev - 1 : 0))
    }, 1000)
    return () => clearInterval(timer)
  }, [lockoutRemaining])

  async function handleSubmit(e) {
    e.preventDefault()
    if (lockoutRemaining > 0) return

    setLoading(true)
    setError(null)

    try {
      await login(username, password, honeypot)
      navigate(from, { replace: true })
    } catch (err) {
      const msg = err.message || 'Error de autenticación'
      setError(msg)
      // If error message indicates lockout seconds, start countdown
      const match = msg.match(/(\d+)\s*segundos/)
      if (match && match[1]) {
        setLockoutRemaining(parseInt(match[1], 10))
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[75vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Glowing aura background */}
        <div className="relative">
          <div className="absolute -inset-1 rounded-3xl bg-gradient-to-r from-flamante-flame/20 via-orange-500/10 to-transparent blur-xl pointer-events-none" />

          <div className="relative bg-flamante-card border border-white/[0.08] rounded-2xl p-8 shadow-2xl backdrop-blur-xl space-y-6">
            {/* Header / Brand */}
            <div className="text-center space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-flamante-flame/10 border border-flamante-flame/20 text-flamante-flame text-[10px] font-mono tracking-widest uppercase">
                <span>🛡️</span> Control Perimetral OWASP 2025
              </div>
              <h1 className="text-2xl font-extrabold text-white tracking-tight">
                Acceso al <span className="text-transparent bg-clip-text bg-gradient-to-r from-flamante-flame to-orange-400">Panel Central</span>
              </h1>
              <p className="text-xs text-white/50">
                Suite de Investigación Algorítmica & Arbitraje Unitario Mercado Libre
              </p>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl p-3.5 text-xs font-mono space-y-1">
                <div className="flex items-center gap-2 font-bold">
                  <span>⚠️</span> Acceso Denegado
                </div>
                <div>{error}</div>
                {lockoutRemaining > 0 && (
                  <div className="text-amber-400 font-semibold pt-1">
                    Espera: {lockoutRemaining}s para volver a intentar.
                  </div>
                )}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Invisible Honeypot Anti-Bot Field */}
              <input
                type="text"
                name="honeypot"
                value={honeypot}
                onChange={e => setHoneypot(e.target.value)}
                tabIndex="-1"
                autoComplete="off"
                className="hidden opacity-0 absolute pointer-events-none h-0 w-0"
              />

              {/* Username Input */}
              <div className="space-y-1.5">
                <label className="block text-xs font-mono text-white/70 uppercase tracking-wider">
                  Usuario Administrador
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-white/40 text-sm">
                    👤
                  </span>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    placeholder="admin"
                    className="w-full pl-10 pr-4 py-2.5 bg-black/40 border border-white/10 rounded-xl text-sm text-white placeholder-white/30 focus:outline-none focus:border-flamante-flame focus:ring-1 focus:ring-flamante-flame transition-all"
                  />
                </div>
              </div>

              {/* Password Input */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <label className="block text-xs font-mono text-white/70 uppercase tracking-wider">
                    Contraseña Maestra
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-[11px] font-mono text-white/40 hover:text-white transition-colors"
                  >
                    {showPassword ? 'Ocultar' : 'Mostrar'}
                  </button>
                </div>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-white/40 text-sm">
                    🔒
                  </span>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full pl-10 pr-4 py-2.5 bg-black/40 border border-white/10 rounded-xl text-sm text-white placeholder-white/30 focus:outline-none focus:border-flamante-flame focus:ring-1 focus:ring-flamante-flame transition-all"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || lockoutRemaining > 0}
                className="w-full py-3 px-4 rounded-xl font-mono text-xs uppercase tracking-wider font-bold text-white bg-gradient-to-r from-flamante-flame to-orange-500 hover:from-flamante-flame hover:to-orange-400 active:scale-[0.99] transition-all shadow-glow disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Autenticando...</span>
                  </>
                ) : lockoutRemaining > 0 ? (
                  <span>Bloqueado ({lockoutRemaining}s)</span>
                ) : (
                  <span>Ingresar al Sistema →</span>
                )}
              </button>
            </form>

            {/* Quick credentials chip */}
            <div className="pt-2 border-t border-white/[0.06] text-center">
              <p className="text-[11px] font-mono text-white/40">
                Credencial Inicial: <span className="text-white/70">admin</span> / <span className="text-flamante-flame">Admin!Riviera2026</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
