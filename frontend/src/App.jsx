import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import SearchPage from './pages/SearchPage'
import DetailPage from './pages/DetailPage'
import ComparePage from './pages/ComparePage'
import ReportsPage from './pages/ReportsPage'
import LoginPage from './pages/LoginPage'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider, useAuth } from './context/AuthContext'

function Navigation() {
  const location = useLocation()
  const { user, isAuthenticated, logout } = useAuth()

  const isSearch = location.pathname === '/'
  const isReports = location.pathname === '/reports'
  const isCompare = location.pathname === '/compare'
  const isLogin = location.pathname === '/login'

  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.08] bg-[#090A0F]/85 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#F65058] to-[#FF858B] flex items-center justify-center shadow-[0_0_20px_rgba(246,80,88,0.35)] transition-transform group-hover:scale-105">
            <span className="text-white font-black text-sm tracking-tighter">FL</span>
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold tracking-tight text-white text-base leading-none">
              FLAMANTE <span className="text-[#F65058]">//</span> LAB
            </span>
            <span className="text-[10px] font-mono text-gray-400 tracking-wider uppercase mt-0.5">
              E-Commerce Intelligence
            </span>
          </div>
        </Link>

        {/* Center Nav Links (Hidden on login page) */}
        {!isLogin && (
          <nav className="flex items-center gap-1 sm:gap-2 bg-white/[0.04] p-1 rounded-full border border-white/[0.06]">
            <Link
              to="/"
              className={`px-3 sm:px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide transition-all ${
                isSearch
                  ? 'bg-[#F65058] text-white shadow-[0_0_15px_rgba(246,80,88,0.3)]'
                  : 'text-gray-400 hover:text-white hover:bg-white/[0.05]'
              }`}
            >
              RESEARCH
            </Link>
            <Link
              to="/reports"
              className={`px-3 sm:px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide transition-all ${
                isReports
                  ? 'bg-[#F65058] text-white shadow-[0_0_15px_rgba(246,80,88,0.3)]'
                  : 'text-gray-400 hover:text-white hover:bg-white/[0.05]'
              }`}
            >
              REPORTES
            </Link>
            <Link
              to="/compare"
              className={`px-3 sm:px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide transition-all ${
                isCompare
                  ? 'bg-[#F65058] text-white shadow-[0_0_15px_rgba(246,80,88,0.3)]'
                  : 'text-gray-400 hover:text-white hover:bg-white/[0.05]'
              }`}
            >
              COMPARADOR
            </Link>
          </nav>
        )}

        {/* User / Status Section */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-medium tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>API MLM EN VIVO</span>
          </div>

          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-white/80">
                <span className="text-flamante-flame">●</span>
                <span>{user?.username}</span>
                <span className="text-[9px] uppercase px-1 rounded bg-flamante-flame/20 text-flamante-flame font-bold">
                  {user?.role}
                </span>
              </div>
              <button
                onClick={logout}
                title="Cerrar sesión"
                className="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-white/60 hover:text-flamante-flame border border-white/10 transition-colors text-xs font-mono"
              >
                Salir
              </button>
            </div>
          ) : !isLogin ? (
            <Link
              to="/login"
              className="px-3 py-1.5 rounded-lg text-xs font-mono bg-flamante-flame text-white hover:bg-flamante-flame/90 transition-all shadow-glow"
            >
              Acceder
            </Link>
          ) : (
            <div className="text-[11px] font-mono text-gray-500">
              📍 RIVIERA MAYA
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navigation />
        <main className="flex-1 bg-[#090A0F]">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <SearchPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/product/:mlId"
              element={
                <ProtectedRoute>
                  <DetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/compare"
              element={
                <ProtectedRoute>
                  <ComparePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <ReportsPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
      </AuthProvider>
    </BrowserRouter>
  )
}
