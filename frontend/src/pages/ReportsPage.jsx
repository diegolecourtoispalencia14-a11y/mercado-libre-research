import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getReports, getExportUrl } from '../api/reports'

export default function ReportsPage() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getReports().then(setReports).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="max-w-5xl mx-auto px-4 py-20 text-center">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-flamante-flame border-t-transparent mb-4" />
      <div className="text-white/60 font-mono text-sm">Cargando reportes archivados...</div>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-white/[0.06]">
        <div>
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-xs font-mono text-white/60 hover:text-flamante-flame transition-colors mb-3"
          >
            ← Volver al buscador
          </Link>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Archivo de <span className="text-transparent bg-clip-text bg-gradient-to-r from-flamante-flame to-orange-400">Reportes</span>
          </h1>
          <p className="text-xs text-white/50 mt-0.5">
            Historial de análisis guardados, rankings SVD y exportaciones en CSV / PDF.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-white/70 self-start md:self-auto">
          {reports.length} reportes guardados
        </span>
      </div>

      {reports.length === 0 && (
        <div className="bg-flamante-card/60 border border-white/[0.08] rounded-2xl p-12 text-center">
          <p className="text-white/40 text-sm">No hay reportes guardados aún.</p>
          <Link to="/" className="inline-block mt-4 text-xs font-mono text-flamante-flame hover:underline">
            Ir al explorador para generar un análisis →
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 gap-3">
        {reports.map(r => (
          <div
            key={r.id}
            className="bg-flamante-card/80 hover:bg-flamante-card border border-white/[0.08] hover:border-flamante-flame/30 rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all duration-300 shadow-lg"
          >
            <div>
              <div className="flex items-center gap-2">
                <p className="font-bold text-white text-base tracking-tight">{r.name}</p>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-white/50 border border-white/10">
                  ID #{r.id}
                </span>
              </div>
              {r.notes && <p className="text-xs text-white/60 mt-1">{r.notes}</p>}
              <p className="text-[11px] font-mono text-white/40 mt-1">
                Generado: {new Date(r.created_at).toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' })}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <a
                href={getExportUrl(r.id, 'csv')}
                className="text-xs font-mono font-medium border border-white/10 rounded-lg px-3.5 py-1.5 bg-white/5 hover:bg-white/10 text-white transition-colors flex items-center gap-1.5"
              >
                <span>📊</span> CSV
              </a>
              <a
                href={getExportUrl(r.id, 'pdf')}
                className="text-xs font-mono font-medium border border-flamante-flame/30 rounded-lg px-3.5 py-1.5 bg-flamante-flame/10 hover:bg-flamante-flame/20 text-flamante-flame transition-colors flex items-center gap-1.5"
              >
                <span>📄</span> PDF
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
