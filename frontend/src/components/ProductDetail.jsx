import ScoreBadge from './ScoreBadge'
import TrendChart from './TrendChart'

export default function ProductDetail({ detail }) {
  return (
    <div className="space-y-6">
      <div className="flex gap-4 items-start">
        {detail.thumbnail_url && (
          <img src={detail.thumbnail_url} alt="" className="w-24 h-24 object-contain border rounded" />
        )}
        <div className="flex-1">
          <h2 className="text-xl font-semibold">{detail.title}</h2>
          <p className="text-gray-500 text-sm mt-1">Categoría: {detail.category_id}</p>
        </div>
        <ScoreBadge score={detail.score} trendAvailable={detail.trend_available} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Precio promedio', value: `$${detail.price.toLocaleString('es-MX')}` },
          { label: 'Ventas/mes est.', value: detail.estimated_monthly_sales != null ? Math.round(detail.estimated_monthly_sales).toLocaleString('es-MX') : 'N/D' },
          { label: 'Vendedores en nicho', value: detail.competition_score != null ? detail.competition_score.toFixed(1) : 'N/D' },
          { label: 'Demanda', value: detail.demand_score != null ? detail.demand_score.toFixed(1) : 'N/D' },
        ].map(({ label, value }) => (
          <div key={label} className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">{label}</p>
            <p className="text-lg font-semibold">{value}</p>
          </div>
        ))}
      </div>

      <div>
        <h3 className="font-medium mb-2">Tendencia (12 meses)</h3>
        <TrendChart data={detail.trend_timeline} />
      </div>

      {detail.description && (
        <div>
          <h3 className="font-medium mb-1">Descripción</h3>
          <p className="text-sm text-gray-600 line-clamp-4">{detail.description}</p>
        </div>
      )}
    </div>
  )
}
