import ScoreBadge from './ScoreBadge'
import TrendChart from './TrendChart'
import { getMercadoLibreUrl } from '../utils/permalinks'

export default function ProductDetail({ detail }) {
  // Estimated Unit Economics
  const price = detail.price || 0
  const estCost = Math.round(price * 0.35)
  const estMlFee = Math.round(price * 0.17 + (price > 299 ? 85 : 30))
  const estMargin = Math.max(0, price - estCost - estMlFee)
  const marginPct = price > 0 ? Math.round((estMargin / price) * 100) : 0

  const activeMlUrl = getMercadoLibreUrl(detail)
  const isCatalog = detail.ml_id && String(detail.ml_id).startsWith('MLM')
  const catalogUrl = isCatalog ? `https://www.mercadolibre.com.mx/p/${detail.ml_id}` : null

  return (
    <div className="space-y-6 text-gray-100">
      {/* Hero Header */}
      <div className="p-6 rounded-3xl bg-[#12141D]/90 border border-white/[0.08] shadow-2xl flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
        <div className="flex gap-4 items-center flex-1 min-w-0">
          <div className="w-20 h-20 md:w-24 md:h-24 rounded-2xl bg-white/[0.04] border border-white/[0.1] p-2 flex items-center justify-center flex-shrink-0 overflow-hidden shadow-inner">
            {detail.thumbnail_url ? (
              <img src={detail.thumbnail_url} alt="" className="w-full h-full object-contain" />
            ) : (
              <span className="text-3xl">📦</span>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <span className="text-[10px] font-mono tracking-widest uppercase text-[#F65058] font-bold">
              • FICHA DE PRODUCTO CATALOG •
            </span>
            <h2 className="text-lg md:text-xl font-bold text-white tracking-tight mt-0.5 line-clamp-2">
              {detail.title}
            </h2>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-white/[0.05] text-gray-400 border border-white/[0.08]">
                ID: {detail.ml_id}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-white/[0.05] text-gray-400 border border-white/[0.08]">
                Cat: {detail.category_id}
              </span>
              {detail.is_archetype && (
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                  ⭐ Arquetipo Clave
                </span>
              )}
            </div>
            <div className="mt-3.5 flex flex-wrap items-center gap-2.5">
              <a
                href={activeMlUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-[#F65058] to-orange-500 hover:from-[#ff6169] hover:to-orange-400 text-white font-mono text-xs font-bold transition-all shadow-[0_0_15px_rgba(246,80,88,0.35)] hover:scale-[1.02] active:scale-[0.98] group"
                title="Abrir ofertas y vendedores activos con stock en Mercado Libre"
              >
                <span>Ver ofertas activas en Mercado Libre</span>
                <span className="transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 font-bold">↗</span>
              </a>
              {isCatalog && (
                <a
                  href={catalogUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-gray-300 hover:text-white font-mono text-xs transition-colors"
                  title="Ver ficha oficial de catálogo en Mercado Libre (si sigue activa)"
                >
                  <span>Ficha Catálogo ({detail.ml_id})</span>
                  <span>↗</span>
                </a>
              )}
            </div>
            <p className="text-[11px] text-gray-400 mt-2 flex items-center gap-1.5 font-mono">
              <span className="text-[#00E599] font-bold">✓</span>
              <span>El enlace te lleva a ofertas activas con stock y vendedores vigentes en Mercado Libre México.</span>
            </p>
          </div>
        </div>

        <div className="flex-shrink-0 self-end md:self-center">
          <ScoreBadge score={detail.score} trendAvailable={detail.trend_available} />
        </div>
      </div>

      {/* Unit Economics Simulator Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-[#12141D] to-emerald-950/30 border border-emerald-500/30 shadow-[0_0_25px_rgba(16,185,129,0.1)]">
        <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
          <span className="text-[10px] font-mono tracking-wider uppercase text-emerald-400 font-bold flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Simulador de Unit Economics & Arbitraje
          </span>
          <span className="text-xs font-mono font-bold text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-500/30">
            Margen Neto Est.: ~{marginPct}%
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
          <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.05]">
            <span className="text-[10px] font-mono text-gray-400 uppercase">PVP Mercado</span>
            <p className="text-base font-bold font-mono text-white mt-0.5">${price.toLocaleString('es-MX')}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.05]">
            <span className="text-[10px] font-mono text-gray-400 uppercase">Costo Est. Origen</span>
            <p className="text-base font-bold font-mono text-gray-300 mt-0.5">-${estCost.toLocaleString('es-MX')}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.05]">
            <span className="text-[10px] font-mono text-gray-400 uppercase">Tarifas ML + Full</span>
            <p className="text-base font-bold font-mono text-gray-300 mt-0.5">-${estMlFee.toLocaleString('es-MX')}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
            <span className="text-[10px] font-mono text-emerald-400 uppercase font-bold">Ganancia / Unidad</span>
            <p className="text-base font-bold font-mono text-emerald-300 mt-0.5">+${estMargin.toLocaleString('es-MX')}</p>
          </div>
        </div>
      </div>

      {/* Bento Grid KPI Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3.5">
        {[
          { label: 'Precio Promedio', value: `$${detail.price.toLocaleString('es-MX')}`, tag: 'PVP Actual' },
          { label: 'Ventas/mes est.', value: detail.estimated_monthly_sales != null ? `${Math.round(detail.estimated_monthly_sales).toLocaleString('es-MX')} u` : 'N/D', tag: 'Volumen Mensual' },
          { label: 'Vendedores en Nicho', value: detail.competition_score != null ? detail.competition_score.toFixed(1) : 'N/D', tag: 'Densidad Oferta' },
          { label: 'Score Demanda', value: detail.demand_score != null ? detail.demand_score.toFixed(1) : 'N/D', tag: 'Índice de Tracción' },
          { label: 'Leverage Score (SVD)', value: detail.leverage_score != null ? `${detail.leverage_score}/10` : 'N/D', tag: 'Singular Value' },
          { label: 'Posición Geométrica', value: detail.is_archetype ? '⭐ Arquetipo Clave' : 'Competidor Estándar', tag: 'Topología TDA' },
        ].map(({ label, value, tag }) => (
          <div key={label} className="p-4 rounded-2xl bg-[#12141D]/80 border border-white/[0.08] hover:border-white/[0.16] transition-all flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-gray-400">{label}</span>
              <span className="text-[9px] font-mono uppercase text-gray-500 tracking-wider">{tag}</span>
            </div>
            <p className="text-xl font-extrabold font-mono text-white tracking-tight mt-2">{value}</p>
          </div>
        ))}
      </div>

      {/* Trend Chart */}
      <div className="p-5 rounded-3xl bg-[#12141D]/80 border border-white/[0.08] space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-base tracking-tight">Curva de Tendencia (12 Meses)</h3>
            <p className="text-xs text-gray-400">Interés de búsqueda en Google & Mercado Libre México.</p>
          </div>
          <span className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-[#F65058]/10 text-[#F65058] border border-[#F65058]/25 font-bold uppercase">
            • Algoritmo de Tracción •
          </span>
        </div>
        <TrendChart data={detail.trend_timeline} />
      </div>

      {/* Description */}
      {detail.description && (
        <div className="p-5 rounded-3xl bg-[#12141D]/80 border border-white/[0.08] space-y-2">
          <h3 className="font-bold text-white text-sm uppercase font-mono tracking-wider text-gray-400">
            • DESCRIPCIÓN DEL LISTING •
          </h3>
          <p className="text-xs md:text-sm text-gray-300 leading-relaxed font-sans">{detail.description}</p>
        </div>
      )}
    </div>
  )
}

