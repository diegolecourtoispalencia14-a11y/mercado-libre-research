import { useState } from 'react'

const QUICK_SEARCHES = [
  'hamaca matrimonial algodon yucateca',
  'miel melipona gotero',
  'copal blanco lagrima',
  'soporte celular moto',
  'bloqueador biodegradable reef safe',
]

export default function SearchBar({ onSearch, loading }) {
  const [q, setQ] = useState('')

  return (
    <div className="w-full space-y-3">
      <form
        className="relative flex items-center gap-2 p-1.5 rounded-2xl bg-[#12141D]/90 border border-white/[0.1] shadow-2xl focus-within:border-[#F65058] focus-within:shadow-[0_0_30px_rgba(246,80,88,0.2)] transition-all"
        onSubmit={e => { e.preventDefault(); if (q.trim()) onSearch(q.trim()) }}
      >
        <div className="pl-4 text-gray-400">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          className="flex-1 bg-transparent px-3 py-3 text-white placeholder-gray-500 focus:outline-none text-sm md:text-base font-medium"
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Busca cualquier producto o nicho en Mercado Libre México..."
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !q.trim()}
          className="bg-[#F65058] hover:bg-[#E03E46] text-white font-bold px-6 py-3 rounded-xl transition-all shadow-[0_0_20px_rgba(246,80,88,0.3)] disabled:opacity-40 disabled:hover:bg-[#F65058] flex items-center gap-2 text-sm tracking-wide"
        >
          {loading ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>ANALIZANDO...</span>
            </>
          ) : (
            <>
              <span>BUSCAR</span>
              <span className="hidden sm:inline text-xs opacity-75">↵</span>
            </>
          )}
        </button>
      </form>

      {/* Quick Search Chips */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-gray-500 font-mono uppercase tracking-wider text-[10px]">Tendencias Riviera Maya:</span>
        {QUICK_SEARCHES.map(item => (
          <button
            key={item}
            type="button"
            onClick={() => { setQ(item); onSearch(item); }}
            className="px-2.5 py-1 rounded-full bg-white/[0.04] hover:bg-white/[0.09] text-gray-300 hover:text-white border border-white/[0.06] hover:border-[#F65058]/50 transition-all font-mono text-[11px]"
          >
            • {item}
          </button>
        ))}
      </div>
    </div>
  )
}

