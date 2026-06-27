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

  if (loading) return <div className="p-8 text-center text-gray-500">Analizando producto...</div>
  if (error) return <div className="p-8 text-red-600">{error}</div>
  if (!detail) return null

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <Link to="/" className="text-blue-600 text-sm">← Volver a resultados</Link>
      <ProductDetail detail={detail} />
    </div>
  )
}
