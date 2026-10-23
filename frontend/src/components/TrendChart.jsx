import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const MONTHS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

export default function TrendChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-44 text-gray-500 font-mono text-xs rounded-xl bg-white/[0.02] border border-white/[0.06]">
        • Sin datos de tendencia disponibles •
      </div>
    )
  }
  const chartData = data.map((v, i) => ({ month: MONTHS[i % 12], interest: v }))

  return (
    <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] backdrop-blur-md">
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="flameTrendGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#F65058" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#F65058" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="month"
            tick={{ fontSize: 11, fill: '#9CA3AF', fontFamily: 'JetBrains Mono' }}
            axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
            tickLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: '#9CA3AF', fontFamily: 'JetBrains Mono' }}
            axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
            tickLine={false}
          />
          <Tooltip
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="bg-[#12141D] border border-white/20 p-2.5 rounded-xl shadow-xl text-xs font-mono">
                    <p className="text-gray-400 font-semibold">{label}</p>
                    <p className="text-[#F65058] font-bold text-sm mt-0.5">
                      Interés: {payload[0].value}/100
                    </p>
                  </div>
                )
              }
              return null
            }}
          />
          <Area
            type="monotone"
            dataKey="interest"
            stroke="#F65058"
            strokeWidth={3}
            fillOpacity={1}
            fill="url(#flameTrendGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

