import { useEffect, useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { compareProducts } from '../api/compare'
import ScoreBadge from '../components/ScoreBadge'

export default function ComparePage() {
  const { state } = useLocation()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    compareProducts(state?.ids || [])
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="max-w-5xl mx-auto px-4 py-20 text-center">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-flamante-flame border-t-transparent mb-4" />
      <div className="text-white/60 font-mono text-sm">Calculando matriz comparativa...</div>
    </div>
  )
  if (error) return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl p-4 text-xs font-mono">
        [ERROR] {error}
      </div>
    </div>
  )
  if (!data) return null

  const products = data.products
  const ROWS = [
    { label: 'Precio', key: p => `$${p.price.toLocaleString('es-MX')} MXN` },
    { label: 'Ventas/mes est.', key: p => p.estimated_monthly_sales != null ? `${Math.round(p.estimated_monthly_sales).toLocaleString('es-MX')} uds` : 'N/D' },
    { label: 'Demanda', key: p => p.demand_score?.toFixed(1) ?? 'N/D' },
    { label: 'Competencia', key: p => p.competition_score?.toFixed(1) ?? 'N/D' },
    { label: 'Tendencia', key: p => p.trend_score?.toFixed(1) ?? 'N/D' },
  ]

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-white/[0.06]">
        <div>
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-xs font-mono text-white/60 hover:text-flamante-flame transition-colors mb-3"
          >
            ← Volver al buscador
          </Link>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Matriz Comparativa de <span className="text-transparent bg-clip-text bg-gradient-to-r from-flamante-flame to-orange-400">Productos</span>
          </h1>
          <p className="text-xs text-white/50 mt-0.5">
            Evaluación cruzada de precio, tracción comercial estimada y scores analíticos.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-white/70">
          {products.length} productos seleccionados
        </span>
      </div>

      <div className="bg-flamante-card/90 border border-white/[0.08] rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-white/[0.08] bg-black/30">
                <th className="p-4 text-left w-44 font-mono text-xs uppercase tracking-wider text-white/40">
                  Métrica
                </th>
                {products.map(p => (
                  <th key={p.ml_id} className="p-4 text-center min-w-[200px]">
                    <div className="line-clamp-2 text-sm font-semibold text-white mb-2">
                      {p.title}
                    </div>
                    <div className="flex justify-center">
                      <ScoreBadge score={p.score} trendAvailable={p.trend_available} />
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05]">
              {ROWS.map(row => (
                <tr key={row.label} className="hover:bg-white/[0.02] transition-colors">
                  <td className="p-4 font-mono text-xs text-white/60 uppercase tracking-wider">
                    {row.label}
                  </td>
                  {products.map(p => (
                    <td key={p.ml_id} className="p-4 text-center font-mono font-medium text-white/90">
                      {row.key(p)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
