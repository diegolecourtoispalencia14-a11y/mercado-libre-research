import ScoreBadge from './ScoreBadge'

export default function ProductList({ products, onSelect, onCompare, selectedForCompare }) {
  if (!products.length) return null
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-50 text-left">
            <th className="p-3 border-b">Producto</th>
            <th className="p-3 border-b text-center">Score</th>
            <th className="p-3 border-b text-right">Precio</th>
            <th className="p-3 border-b text-right">Ventas/mes est.</th>
            <th className="p-3 border-b text-center">Comparar</th>
          </tr>
        </thead>
        <tbody>
          {products.map(p => (
            <tr
              key={p.ml_id}
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => onSelect(p.ml_id)}
            >
              <td className="p-3 border-b flex items-center gap-2">
                {p.thumbnail_url && (
                  <img src={p.thumbnail_url} alt="" className="w-10 h-10 object-contain" />
                )}
                <span className="line-clamp-2">{p.title}</span>
              </td>
              <td className="p-3 border-b text-center">
                <ScoreBadge score={p.score} trendAvailable={p.trend_available} />
              </td>
              <td className="p-3 border-b text-right">
                ${p.price.toLocaleString('es-MX')}
              </td>
              <td className="p-3 border-b text-right">
                {p.estimated_monthly_sales != null
                  ? Math.round(p.estimated_monthly_sales).toLocaleString('es-MX')
                  : 'N/D'}
              </td>
              <td className="p-3 border-b text-center" onClick={e => e.stopPropagation()}>
                <input
                  type="checkbox"
                  checked={selectedForCompare.includes(p.ml_id)}
                  onChange={() => onCompare(p.ml_id)}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
