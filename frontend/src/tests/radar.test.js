import { describe, it, expect, vi, beforeEach } from 'vitest'
import { getOpportunities, getRadarStatus, triggerScan, updateOpportunityStatus } from '../api/radar'

describe('Radar API Client', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  it('getOpportunities requests /api/radar with status param', async () => {
    const mockData = [{ id: 1, title: 'Item 1', score: 8.5 }]
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    })

    const res = await getOpportunities('active')
    expect(res).toEqual(mockData)
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/radar?status=active',
      expect.objectContaining({
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
      })
    )
  })

  it('getRadarStatus requests /api/radar/status', async () => {
    const mockStatus = { is_running: false, total_opportunities: 5, active_opportunities: 5, categories_monitored: [] }
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockStatus,
    })

    const res = await getRadarStatus()
    expect(res.total_opportunities).toBe(5)
    expect(global.fetch).toHaveBeenCalledWith('/api/radar/status', expect.anything())
  })

  it('triggerScan sends POST to /api/radar/scan', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'started', message: 'Ok', new_opportunities_found: 0 }),
    })

    const res = await triggerScan()
    expect(res.status).toBe('started')
    expect(global.fetch).toHaveBeenCalledWith('/api/radar/scan', expect.objectContaining({ method: 'POST' }))
  })

  it('updateOpportunityStatus sends PATCH to /api/radar/{id}', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 42, status: 'dismissed' }),
    })

    const res = await updateOpportunityStatus(42, 'dismissed', 'Not viable')
    expect(res.status).toBe('dismissed')
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/radar/42',
      expect.objectContaining({
        method: 'PATCH',
        body: JSON.stringify({ status: 'dismissed', notes: 'Not viable' }),
      })
    )
  })
})
