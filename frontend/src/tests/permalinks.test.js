import { describe, it, expect } from 'vitest'
import { getMercadoLibreUrl } from '../utils/permalinks'

describe('getMercadoLibreUrl', () => {
  it('returns valid permalink when already present', () => {
    const p = {
      title: 'Bicicleta Montaña',
      permalink: 'https://articulo.mercadolibre.com.mx/MLM-123456-test',
    }
    expect(getMercadoLibreUrl(p)).toBe('https://articulo.mercadolibre.com.mx/MLM-123456-test')
  })

  it('generates clean slug-based search URL without special characters or spaces', () => {
    const p = {
      title: 'Estante Repisa Ménsula Hierro 45x15 | Mite Color Blanco/Blanco',
      ml_id: 'SIM001',
    }
    const url = getMercadoLibreUrl(p)
    expect(url).toBe('https://listado.mercadolibre.com.mx/estante-repisa-mensula-hierro-45x15')
    expect(url).not.toContain('%20')
    expect(url).not.toContain(' ')
    expect(url).not.toContain('|')
  })

  it('handles simulated products safely', () => {
    const p = {
      title: 'Ménsula Reforzada Mod. 1',
      ml_id: 'SIM5162000',
    }
    const url = getMercadoLibreUrl(p)
    expect(url).toBe('https://listado.mercadolibre.com.mx/mensula-reforzada')
  })

  it('falls back gracefully when title is empty', () => {
    expect(getMercadoLibreUrl({})).toBe('https://www.mercadolibre.com.mx')
  })
})
