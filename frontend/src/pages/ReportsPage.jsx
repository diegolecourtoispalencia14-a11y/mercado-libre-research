import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getReports, getExportUrl } from '../api/reports'

export default function ReportsPage() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getReports().then(setReports).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-8 text-center text-gray-500">Cargando reportes...</div>

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Reportes guardados</h1>
        <Link to="/" className="text-blue-600 text-sm">← Volver</Link>
      </div>
      {reports.length === 0 && <p className="text-gray-500">No hay reportes guardados aún.</p>}
      {reports.map(r => (
        <div key={r.id} className="border rounded p-4 flex justify-between items-center">
          <div>
            <p className="font-medium">{r.name}</p>
            {r.notes && <p className="text-sm text-gray-500">{r.notes}</p>}
            <p className="text-xs text-gray-400">
              {new Date(r.created_at).toLocaleDateString('es-MX')}
            </p>
          </div>
          <div className="flex gap-2">
            <a href={getExportUrl(r.id, 'csv')}
               className="text-sm border rounded px-3 py-1 hover:bg-gray-50">
              CSV
            </a>
            <a href={getExportUrl(r.id, 'pdf')}
               className="text-sm border rounded px-3 py-1 hover:bg-gray-50">
              PDF
            </a>
          </div>
        </div>
      ))}
    </div>
  )
}
