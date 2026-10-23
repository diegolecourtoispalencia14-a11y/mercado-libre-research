/**
 * Safely generates an active Mercado Libre México URL.
 * - If product has a valid permalink (https://...mercadolibre.com...), return it.
 * - Otherwise, cleans the title into a canonical search slug (listado.mercadolibre.com.mx/<slug>)
 *   ensuring the browser ALWAYS lands on active listings with stock and current sellers.
 */
export function getMercadoLibreUrl(product) {
  if (
    product?.permalink &&
    typeof product.permalink === 'string' &&
    product.permalink.startsWith('https://') &&
    product.permalink.includes('mercadolibre.com')
  ) {
    return product.permalink
  }

  const title = product?.title || ''
  if (!title) {
    return 'https://www.mercadolibre.com.mx'
  }

  // Remove diacritics / accents
  const normalized = title
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9\s]/g, ' ')
    .trim()

  const stopwords = new Set([
    'de', 'para', 'el', 'la', 'los', 'las', 'un', 'una', 'con', 'en', 'del',
    'por', 'y', 'o', 'al', 'mod', 'modelo', 'tipo', 'color'
  ])

  const tokens = normalized
    .split(/\s+/)
    .filter(w => w.length > 1 && !stopwords.has(w.toLowerCase()) && !/^\d+$/.test(w))
    .slice(0, 5)

  const slug = tokens.length > 0 ? tokens.join('-').toLowerCase() : 'articulos'
  return `https://listado.mercadolibre.com.mx/${slug}`
}
