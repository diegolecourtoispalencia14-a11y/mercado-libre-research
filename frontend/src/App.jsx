import { BrowserRouter, Routes, Route } from 'react-router-dom'
import SearchPage from './pages/SearchPage'
import DetailPage from './pages/DetailPage'
import ComparePage from './pages/ComparePage'
import ReportsPage from './pages/ReportsPage'

export default function App() {
  return (
    <BrowserRouter>
      <nav className="border-b px-4 py-3 flex gap-6 text-sm">
        <a href="/" className="font-semibold text-blue-700">Research Tool</a>
        <a href="/reports" className="text-gray-600 hover:text-gray-900">Reportes</a>
      </nav>
      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/product/:mlId" element={<DetailPage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/reports" element={<ReportsPage />} />
      </Routes>
    </BrowserRouter>
  )
}
