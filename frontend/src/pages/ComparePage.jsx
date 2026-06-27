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

  if (loading) return <div className="p-8 text-center text-gray-500">Comparando...</div>
  if (error) return <div className="p-8 text-red-600">{error}</div>
  if (!data) return null

  const products = data.products
  const ROWS = [
    { label: 'Precio', key: p => `$${p.price.toLocaleString('es-MX')}` },
    { label: 'Ventas/mes est.', key: p => p.estimated_monthly_sales != null ? Math.round(p.estimated_monthly_sales).toLocaleString('es-MX') : 'N/D' },
    { label: 'Demanda', key: p => p.demand_score?.toFixed(1) ?? 'N/D' },
    { label: 'Competencia', key: p => p.competition_score?.toFixed(1) ?? 'N/D' },
    { label: 'Tendencia', key: p => p.trend_score?.toFixed(1) ?? 'N/D' },
  ]

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <Link to="/" className="text-blue-600 text-sm">← Volver</Link>
      <h1 className="text-2xl font-bold">Comparativa de productos</h1>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr>
              <th className="p-3 border-b text-left w-32">Métrica</th>
              {products.map(p => (
                <th key={p.ml_id} className="p-3 border-b text-center">
                  <div className="line-clamp-2">{p.title}</div>
                  <ScoreBadge score={p.score} trendAvailable={p.trend_available} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map(row => (
              <tr key={row.label} className="hover:bg-gray-50">
                <td className="p-3 border-b font-medium">{row.label}</td>
                {products.map(p => (
                  <td key={p.ml_id} className="p-3 border-b text-center">{row.key(p)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
