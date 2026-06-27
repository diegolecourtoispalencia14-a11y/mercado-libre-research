import { apiFetch } from './client'

export const getReports = () => apiFetch('/reports')

export const saveReport = (analysisId, name, notes = null) =>
  apiFetch('/reports', { method: 'POST', body: JSON.stringify({ analysis_id: analysisId, name, notes }) })

export const getExportUrl = (reportId, format = 'csv') =>
  `/api/reports/${reportId}/export?format=${format}`
