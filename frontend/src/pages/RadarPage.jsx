import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getOpportunities, getRadarStatus, triggerScan, updateOpportunityStatus } from '../api/radar'
import ScoreBadge from '../components/ScoreBadge'
import { getMercadoLibreUrl } from '../utils/permalinks'

export default function RadarPage() {
  const [opportunities, setOpportunities] = useState([])
  const [statusInfo, setStatusInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [filter, setFilter] = useState('active')
  const [archetypeOnly, setArchetypeOnly] = useState(false)
  const [actionMessage, setActionMessage] = useState('')

  const loadData = async () => {
    try {
      const [opps, st] = await Promise.all([getOpportunities(filter, archetypeOnly), getRadarStatus()])
      setOpportunities(opps)
      setStatusInfo(st)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [filter, archetypeOnly])

  const handleTriggerScan = async () => {
    setScanning(true)
    setActionMessage('Iniciando rastreo en segundo plano...')
    try {
      await triggerScan()
      setActionMessage('Rastreo iniciado con éxito. Los resultados se actualizarán automáticamente.')
      setTimeout(() => {
        loadData()
        setActionMessage('')
      }, 3500)
    } catch (err) {
      setActionMessage(err.message || 'Error al iniciar rastreo')
    } finally {
      setScanning(false)
    }
  }

  const handleDismiss = async (id, currentStatus) => {
    const newStatus = currentStatus === 'dismissed' ? 'active' : 'dismissed'
    try {
      await updateOpportunityStatus(id, newStatus)
      setOpportunities(prev => prev.filter(o => filter === 'all' ? true : o.id !== id))
      loadData()
    } catch (err) {
      console.error(err)
    }
  }

  const avgScore =
    opportunities.length > 0
      ? (opportunities.reduce((acc, o) => acc + o.score, 0) / opportunities.length).toFixed(1)
      : '0.0'

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-white/[0.08]">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] font-mono tracking-widest uppercase text-emerald-400 font-bold">
              • MOTOR 24/7 EN SEGUNDO PLANO •
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Radar de <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-[#F65058]">Oportunidades</span>
          </h1>
          <p className="text-xs text-white/50 mt-1 max-w-xl">
            Rastreo continuo de categorías ganadoras con cálculo de <b>Unit Economics Inverso</b>: te indicamos exactamente el costo máximo a negociar con fabricantes para garantizar margen neto real.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleTriggerScan}
            disabled={scanning}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-white font-mono text-xs font-bold transition-all shadow-lg active:scale-95 disabled:opacity-50"
          >
            <span className={scanning ? 'animate-spin' : ''}>↻</span>
            <span>{scanning ? 'Escaneando...' : 'Escanear Ahora'}</span>
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className="px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
          ✓ {actionMessage}
        </div>
      )}

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-4 rounded-2xl bg-[#12141D]/80 border border-white/[0.08] shadow-xl">
          <span className="text-[10px] font-mono uppercase text-gray-400 tracking-wider">Oportunidades Activas</span>
          <p className="text-2xl font-bold text-white mt-1">{statusInfo?.active_opportunities || opportunities.length}</p>
        </div>

        <div className="p-4 rounded-2xl bg-[#12141D]/80 border border-white/[0.08] shadow-xl">
          <span className="text-[10px] font-mono uppercase text-gray-400 tracking-wider">Score Promedio</span>
          <p className="text-2xl font-bold text-[#F65058] mt-1">{avgScore} <span className="text-xs text-gray-400">/ 10</span></p>
        </div>

        <div className="p-4 rounded-2xl bg-[#12141D]/80 border border-white/[0.08] shadow-xl">
          <span className="text-[10px] font-mono uppercase text-gray-400 tracking-wider">Margen Neto Exigido</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1">30% <span className="text-xs text-gray-400">libre</span></p>
        </div>

        <div className="p-4 rounded-2xl bg-[#12141D]/80 border border-white/[0.08] shadow-xl">
          <span className="text-[10px] font-mono uppercase text-gray-400 tracking-wider">Categorías Diána</span>
          <p className="text-2xl font-bold text-white mt-1">{statusInfo?.categories_monitored?.length || 8}</p>
        </div>
      </div>

      {/* Filter Tabs & Archetype Toggle */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.08] pb-3 text-xs font-mono">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilter('active')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              filter === 'active'
                ? 'bg-white/10 text-white font-bold border border-white/20'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Activas
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              filter === 'all'
                ? 'bg-white/10 text-white font-bold border border-white/20'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Todas
          </button>
          <button
            onClick={() => setFilter('dismissed')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              filter === 'dismissed'
                ? 'bg-white/10 text-white font-bold border border-white/20'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Descartadas
          </button>
        </div>

        <button
          onClick={() => setArchetypeOnly(!archetypeOnly)}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
            archetypeOnly
              ? 'bg-amber-400/20 text-amber-300 border border-amber-400/40 font-bold shadow-md shadow-amber-500/10'
              : 'bg-white/[0.03] text-gray-400 hover:text-white border border-white/[0.08]'
          }`}
        >
          <span>⭐</span>
          <span>Solo Arquetipos Clave (SVD)</span>
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="py-20 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-emerald-400 border-t-transparent mb-4" />
          <div className="text-white/60 font-mono text-sm">Consultando oportunidades cazadas en el radar...</div>
        </div>
      ) : opportunities.length === 0 ? (
        <div className="p-12 rounded-2xl bg-[#12141D]/80 border border-white/[0.08] text-center space-y-3">
          <span className="text-4xl">📡</span>
          <h3 className="text-white font-bold text-lg">No hay oportunidades en este filtro</h3>
          <p className="text-xs text-gray-400 max-w-md mx-auto">
            El motor 24/7 rastrea Mercado Libre en segundo plano. Haz clic en <b>"Escanear Ahora"</b> para forzar una búsqueda inmediata en las categorías seleccionadas.
          </p>
          <button
            onClick={handleTriggerScan}
            disabled={scanning}
            className="mt-2 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-[#F65058] text-white font-mono text-xs font-bold shadow-lg"
          >
            <span>Ejecutar Escaneo Inmediato</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {opportunities.map(opp => (
            <div
              key={opp.id}
              className="p-5 rounded-2xl bg-[#12141D]/90 border border-white/[0.08] hover:border-emerald-500/30 transition-all duration-300 shadow-2xl flex flex-col md:flex-row gap-5 items-start md:items-center justify-between"
            >
              <div className="flex gap-4 items-center flex-1 min-w-0">
                <div className="w-16 h-16 rounded-xl bg-white/[0.04] border border-white/10 p-2 flex items-center justify-center flex-shrink-0 overflow-hidden">
                  {opp.thumbnail_url ? (
                    <img src={opp.thumbnail_url} alt="" className="w-full h-full object-contain" />
                  ) : (
                    <span className="text-2xl">📦</span>
                  )}
                </div>

                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                      {opp.category_name}
                    </span>
                    {opp.is_archetype && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-300 border border-amber-400/30 font-bold flex items-center gap-1">
                        ⭐ Arquetipo Clave (Leverage: {opp.leverage_score != null ? opp.leverage_score.toFixed(1) : 'Alta'}/10)
                      </span>
                    )}
                    {opp.gap_type && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-semibold">
                        Vacío: {opp.gap_type}
                      </span>
                    )}
                    <span className="text-[10px] font-mono text-gray-500">
                      ID: {opp.ml_id}
                    </span>
                  </div>

                  <h3 className="text-sm md:text-base font-bold text-white tracking-tight line-clamp-2">
                    {opp.title}
                  </h3>

                  <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-gray-400 pt-1">
                    <span>
                      Venta en ML: <b className="text-white">${opp.price} MXN</b>
                    </span>
                    <span>
                      Ventas est.: <b className="text-white">~{Math.round(opp.estimated_monthly_sales || 0)}/mes</b>
                    </span>
                    {opp.demand_score != null && (
                      <span className="text-emerald-400/90">
                        Demanda: <b className="text-white">{opp.demand_score}/10</b>
                      </span>
                    )}
                    {opp.competition_score != null && (
                      <span className="text-orange-400/90">
                        Competencia: <b className="text-white">{opp.competition_score}/10</b>
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Target Cost & Action Box */}
              <div className="flex flex-wrap md:flex-nowrap items-center gap-4 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 pt-3 md:pt-0 border-white/5">
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-left min-w-[150px]">
                  <span className="text-[9px] font-mono uppercase tracking-wider text-emerald-400 font-bold block">
                    Costo Máx. Proveedor
                  </span>
                  <p className="text-lg font-mono font-extrabold text-emerald-300">
                    ≤ ${opp.target_supplier_cost} <span className="text-xs font-normal">MXN</span>
                  </p>
                  <span className="text-[10px] font-mono text-emerald-400/80 block mt-0.5">
                    Ganancia: +${opp.target_profit} MXN
                  </span>
                </div>

                <div className="flex flex-col items-center gap-2">
                  <ScoreBadge score={opp.score} />
                </div>

                <div className="flex flex-col gap-1.5 self-center">
                  <a
                    href={getMercadoLibreUrl(opp)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-[#F65058] to-orange-500 text-white font-mono text-xs font-bold hover:scale-[1.02] transition-all"
                  >
                    <span>Ver en ML</span>
                    <span>↗</span>
                  </a>

                  <button
                    onClick={() => handleDismiss(opp.id, opp.status)}
                    className="text-[11px] font-mono text-gray-400 hover:text-white transition-colors text-center py-0.5"
                  >
                    {opp.status === 'dismissed' ? 'Reactivar' : 'Descartar'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
