import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import ProductDetail from '../components/ProductDetail'
import { analyzeProduct } from '../api/analyze'

export default function DetailPage() {
  const { mlId } = useParams()
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    analyzeProduct(mlId)
      .then(setDetail)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [mlId])

  if (loading) return (
    <div className="max-w-5xl mx-auto px-4 py-20 text-center">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-flamante-flame border-t-transparent mb-4" />
      <div className="text-white/60 font-mono text-sm">Analizando métricas algorítmicas y unit economics...</div>
    </div>
  )
  if (error) return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl p-4 text-xs font-mono">
        [ERROR] {error}
      </div>
    </div>
  )
  if (!detail) return null

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-xs font-mono text-white/60 hover:text-flamante-flame transition-colors bg-white/5 hover:bg-white/10 px-3.5 py-1.5 rounded-lg border border-white/10"
      >
        ← Volver a resultados
      </Link>
      <ProductDetail detail={detail} />
    </div>
  )
}
