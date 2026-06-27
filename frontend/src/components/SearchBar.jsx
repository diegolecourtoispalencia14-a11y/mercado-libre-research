import { useState } from 'react'

export default function SearchBar({ onSearch, loading }) {
  const [q, setQ] = useState('')
  return (
    <form
      className="flex gap-2"
      onSubmit={e => { e.preventDefault(); if (q.trim()) onSearch(q.trim()) }}
    >
      <input
        className="flex-1 border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={q}
        onChange={e => setQ(e.target.value)}
        placeholder="¿Qué quieres vender? Ej: auriculares bluetooth"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !q.trim()}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Buscando...' : 'Buscar'}
      </button>
    </form>
  )
}
