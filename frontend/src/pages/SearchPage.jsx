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

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-2xl font-bold">Research de Productos</h1>
      <SearchBar onSearch={handleSearch} loading={loading} />

      {error && <p className="text-red-600">{error}</p>}

      {results && (
        <>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">
              {results.products.length} productos para "{results.keyword}"
              {!results.trend_available && (
                <span className="ml-2 bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded">
                  sin datos de tendencia
                </span>
              )}
            </p>
            <div className="flex gap-2">
              {selectedForCompare.length >= 2 && (
                <button
                  onClick={() => navigate('/compare', { state: { ids: selectedForCompare } })}
                  className="bg-purple-600 text-white px-4 py-1.5 rounded text-sm"
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
                  className="bg-green-600 text-white px-4 py-1.5 rounded text-sm"
                >
                  Guardar análisis
                </button>
              )}
            </div>
          </div>
          <ProductList
            products={results.products}
            onSelect={mlId => navigate(`/product/${mlId}`)}
            onCompare={toggleCompare}
            selectedForCompare={selectedForCompare}
          />
        </>
      )}
    </div>
  )
}
