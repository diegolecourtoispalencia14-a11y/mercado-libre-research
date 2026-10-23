import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import SearchBar from '../components/SearchBar'
import ProductList from '../components/ProductList'
import { searchProducts } from '../api/search'
import { saveReport } from '../api/reports'

export default function SearchPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [selectedForCompare, setSelectedForCompare] = useState([])
  const [analysisId, setAnalysisId] = useState(null)

  async function handleSearch(q) {
    setLoading(true)
    setError(null)
    setSelectedForCompare([])
    try {
      const data = await searchProducts(q)
      setResults(data)
      setAnalysisId(data.analysis_id ?? null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function toggleCompare(mlId) {
    setSelectedForCompare(prev =>
      prev.includes(mlId) ? prev.filter(id => id !== mlId) : [...prev, mlId]
    )
  }

  const [onlyArchetypes, setOnlyArchetypes] = useState(false)

  const displayedProducts = onlyArchetypes && results?.products
    ? results.products.filter(p => p.is_archetype)
    : (results?.products || [])

  const archetypeCount = results?.products?.filter(p => p.is_archetype).length || 0

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-white/[0.06]">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-flamante-flame/10 border border-flamante-flame/20 text-flamante-flame text-[10px] font-mono tracking-wider uppercase mb-2">
            Algorithmic Market Discovery // SVD & TDA NeurIPS
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Research de <span className="text-transparent bg-clip-text bg-gradient-to-r from-flamante-flame to-orange-400">Productos</span>
          </h1>
          <p className="text-xs text-white/50 mt-1 max-w-xl">
            Detección de vacíos de oferta, arquetipos ortogonales de mercado y simulador de arbitraje unitario en tiempo real para Mercado Libre México.
          </p>
        </div>
      </div>

      <SearchBar onSearch={handleSearch} loading={loading} />

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl p-4 text-xs font-mono">
          [ERROR] {error}
        </div>
      )}

      {results && (
        <>
          {results.is_simulation && (
            <div className="bg-amber-500/10 border border-amber-500/30 text-amber-200 rounded-xl p-4 text-xs flex items-center justify-between shadow-lg backdrop-blur-md">
              <div className="flex items-center gap-3">
                <span className="text-xl">⚡</span>
                <div>
                  <span className="font-bold text-amber-300">Modo de Simulación de Mercado Activo:</span>{' '}
                  El token de la API de Mercado Libre en <code className="bg-black/40 px-1.5 py-0.5 rounded font-mono text-amber-400">.env</code> ha caducado. El motor algorítmico activó el modelo de distribución paramétrica para estimar Arquetipos y Océanos Azules sin interrupción.
                </div>
              </div>
            </div>
          )}

          {/* Tarjeta de Océanos Azules (Vacíos de Oferta) */}
          {results.market_gaps && results.market_gaps.length > 0 && (
            <div className="bg-gradient-to-br from-flamante-dark/90 via-flamante-card to-flamante-dark border border-cyan-500/20 rounded-2xl p-6 space-y-4 shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
              <div className="flex items-center gap-3">
                <span className="text-2xl">🌊</span>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-white text-base md:text-lg tracking-tight">
                      Océanos Azules Detectados (Vacíos de Oferta)
                    </h3>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-400/10 text-cyan-300 border border-cyan-400/20 uppercase tracking-widest">
                      TDA & Clustering
                    </span>
                  </div>
                  <p className="text-xs text-white/50">
                    Segmentos de precio con baja densidad de competidores y oportunidad de diferenciación.
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {results.market_gaps.map((gap, i) => (
                  <div
                    key={i}
                    className="bg-flamante-dark/80 hover:bg-flamante-dark border border-white/[0.08] hover:border-cyan-500/30 rounded-xl p-4 shadow-lg flex flex-col justify-between transition-all duration-300"
                  >
                    <div>
                      <div className="flex justify-between items-start gap-1">
                        <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                          {gap.gap_type}
                        </span>
                        <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
                          Score {gap.opportunity_score}/10
                        </span>
                      </div>
                      <p className="text-base font-mono font-bold text-white mt-2">
                        ${gap.price_min.toLocaleString('es-MX')} – ${gap.price_max.toLocaleString('es-MX')} <span className="text-xs text-white/40 font-normal">MXN</span>
                      </p>
                      <p className="text-xs text-white/60 mt-1 leading-relaxed">{gap.description}</p>
                    </div>
                    <div className="mt-3 pt-2.5 border-t border-white/[0.06] text-[11px] text-cyan-300 font-medium">
                      → {gap.recommendation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
            <div className="flex items-center gap-3">
              <p className="text-sm text-white/60">
                {displayedProducts.length} de {results.products.length} productos
                {!results.trend_available && (
                  <span className="ml-2 bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 text-xs px-2 py-0.5 rounded font-mono">
                    sin datos de tendencia
                  </span>
                )}
              </p>
              {archetypeCount > 0 && (
                <button
                  type="button"
                  onClick={() => setOnlyArchetypes(!onlyArchetypes)}
                  className={`text-xs px-3 py-1.5 rounded-lg font-mono tracking-wide transition-all border ${
                    onlyArchetypes
                      ? 'bg-flamante-flame text-white border-flamante-flame shadow-glow'
                      : 'bg-white/5 text-white/70 border-white/10 hover:border-flamante-flame/40 hover:text-white'
                  }`}
                >
                  {onlyArchetypes ? '✓ Mostrando solo arquetipos' : `Filtrar arquetipos (${archetypeCount})`}
                </button>
              )}
            </div>
            <div className="flex gap-2">
              {selectedForCompare.length >= 2 && (
                <button
                  onClick={() => navigate('/compare', { state: { ids: selectedForCompare } })}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-xs px-4 py-2 rounded-lg border border-indigo-400/30 shadow-lg transition-all"
                >
                  Comparar {selectedForCompare.length} productos
                </button>
              )}
              {analysisId && (
                <button
                  onClick={async () => {
                    const name = prompt('Nombre para este reporte:')
                    if (name) {
                      await saveReport(analysisId, name)
                      alert('Reporte guardado')
                    }
                  }}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs px-4 py-2 rounded-lg border border-emerald-400/30 shadow-lg transition-all"
                >
                  Guardar análisis
                </button>
              )}
            </div>
          </div>
          <ProductList
            products={displayedProducts}
            onSelect={mlId => navigate(`/product/${mlId}`)}
            onCompare={toggleCompare}
            selectedForCompare={selectedForCompare}
          />
        </>
      )}
    </div>
  )
}
