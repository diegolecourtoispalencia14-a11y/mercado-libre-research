import ScoreBadge from './ScoreBadge'
import { getMercadoLibreUrl } from '../utils/permalinks'

export default function ProductList({ products, onSelect, onCompare, selectedForCompare }) {
  if (!products.length) return null

  return (
    <div className="overflow-hidden rounded-2xl border border-white/[0.08] bg-[#12141D]/80 backdrop-blur-xl shadow-2xl">
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-white/[0.02] text-left text-[11px] font-mono tracking-wider text-gray-400 uppercase">
              <th className="py-4 px-4 font-semibold">Producto & Arquetipo</th>
              <th className="py-4 px-3 text-center font-semibold">Score Oportunidad</th>
              <th className="py-4 px-4 text-right font-semibold">Precio (MXN)</th>
              <th className="py-4 px-4 text-right font-semibold">Ventas/mes est.</th>
              <th className="py-4 px-3 text-center font-semibold">Comparar</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {products.map(p => {
              const isSelected = selectedForCompare.includes(p.ml_id)
              return (
                <tr
                  key={p.ml_id}
                  className="hover:bg-white/[0.04] transition-all cursor-pointer group"
                  onClick={() => onSelect(p.ml_id)}
                >
                  <td className="py-3.5 px-4 flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center p-1.5 flex-shrink-0 overflow-hidden group-hover:border-[#F65058]/50 transition-colors">
                      {p.thumbnail_url ? (
                        <img src={p.thumbnail_url} alt="" className="w-full h-full object-contain" />
                      ) : (
                        <span className="text-gray-500 text-xs">📦</span>
                      )}
                    </div>
                    <div className="flex flex-col min-w-0 pr-2">
                      <span className="line-clamp-2 text-gray-200 group-hover:text-white font-medium text-xs md:text-sm transition-colors">
                        {p.title}
                      </span>
                      <div className="flex flex-wrap items-center gap-2 mt-1">
                        {p.is_archetype && (
                          <span
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 shadow-[0_0_10px_rgba(245,158,11,0.15)]"
                            title={`Leverage Score: ${p.leverage_score}/10`}
                          >
                            ⭐ Arquetipo ({p.leverage_score})
                          </span>
                        )}
                        <a
                          href={getMercadoLibreUrl(p)}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={e => e.stopPropagation()}
                          className="inline-flex items-center gap-1 text-[11px] font-mono text-gray-400 hover:text-[#F65058] transition-colors"
                          title="Abrir ofertas y vendedores activos en Mercado Libre"
                        >
                          <span>Ver en ML</span>
                          <span>↗</span>
                        </a>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-3 text-center">
                    <ScoreBadge score={p.score} trendAvailable={p.trend_available} />
                  </td>
                  <td className="py-3.5 px-4 text-right font-mono font-bold text-white text-sm md:text-base whitespace-nowrap">
                    ${p.price.toLocaleString('es-MX')}
                  </td>
                  <td className="py-3.5 px-4 text-right whitespace-nowrap">
                    <span className="font-mono text-xs md:text-sm font-semibold text-gray-300 bg-white/[0.04] px-2.5 py-1 rounded-lg border border-white/[0.06]">
                      {p.estimated_monthly_sales != null
                        ? `${Math.round(p.estimated_monthly_sales).toLocaleString('es-MX')} u/mes`
                        : 'N/D'}
                    </span>
                  </td>
                  <td className="py-3.5 px-3 text-center" onClick={e => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => onCompare(p.ml_id)}
                      className="w-4 h-4 rounded border-gray-600 text-[#F65058] focus:ring-[#F65058] focus:ring-offset-0 bg-transparent cursor-pointer"
                    />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

