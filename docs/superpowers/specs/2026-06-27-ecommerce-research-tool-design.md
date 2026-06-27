# Ecommerce Product Research Tool — Design Spec

**Date:** 2026-06-27
**Status:** Approved

## Overview

A web app dashboard that helps a seller in Mexico/LATAM discover what to sell on Mercado Libre. It covers the full research flow: keyword-based product discovery, opportunity scoring, detailed product analysis, niche comparison, and report export. Data comes from the Mercado Libre public API crossed with Google Trends via pytrends.

## Architecture

Three-layer architecture, each with a single responsibility:

```
Frontend (React)
    ↕ HTTP/JSON
Backend (FastAPI / Python)
    ↕
PostgreSQL
```

The backend never exposes raw ML API responses to the frontend — it always returns scored, enriched data. External API calls are isolated in adapter classes so the rest of the system never touches HTTP directly.

### External adapters

- **MLAdapter** — wraps `api.mercadolibre.com`. Caches responses 1 hour in Redis to avoid rate limiting.
- **TrendsAdapter** — wraps `pytrends`. Caches 24 hours (Google aggressively rate-limits this library).

Both adapters implement the same interface: `fetch(params) → normalized dict`. Scoring engine consumes normalized dicts, never raw API responses.

## User Flow

```
1. Search: user enters keyword or selects category
2. Results: ranked list of products with opportunity score (1–10)
3. Product detail: click any product → full report
4. Niche comparison: select multiple products → side-by-side table
5. Save / export: persist analysis to history, export CSV or PDF
```

## Opportunity Score

```
score = (demand × trend) / (competition × price_competitiveness)
normalized to 1–10 via min-max across all products in the same search result set
```

- `demand` — derived from `sold_quantity` in ML listing data
- `trend` — Google Trends interest over 12 months for the keyword
- `competition` — number of active sellers + listing density in category
- `price_competitiveness` — spread between cheapest and most expensive listings

Score is calculated server-side in the Scoring Engine, which is a pure function (no I/O) taking normalized product data and returning a float. This makes it easy to test and tune.

## Data Model

```sql
products
  id, ml_id, title, price, sold_quantity, seller_id,
  category_id, thumbnail_url, fetched_at

analyses
  id, keyword, category, score, demand_score,
  competition_score, trend_score, created_at

analysis_products
  analysis_id, product_id, rank, estimated_monthly_sales
  -- estimated_monthly_sales = sold_quantity / months_since_listing_created (from ML API date fields)

saved_reports
  id, analysis_id, name, notes, exported_at
```

`products` acts as a local cache — if a product was fetched less than 1 hour ago it is served from DB, not from ML API.

## API Endpoints

```
GET  /search?q={keyword}&category={id}&limit={n}
     → list of products with computed scores

GET  /analyze/{ml_product_id}
     → detailed report for a single product

POST /compare
     body: { product_ids: [...] }
     → side-by-side comparison

GET  /reports
     → saved analysis history

POST /reports
     → save current analysis

GET  /reports/{id}/export?format=csv|pdf
     → export saved report
```

## Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Frontend | React + Vite + TailwindCSS | Fast to build, clean components |
| Charts | Recharts | Simple, composable data charts |
| Backend | Python 3.12 + FastAPI | Async, strong data/ML ecosystem |
| ORM | SQLAlchemy + Alembic | Controlled migrations |
| Database | PostgreSQL | Complex queries for comparisons |
| Cache | Redis | Prevent rate limiting on external APIs |
| Runtime | Docker Compose | One command: frontend + backend + DB + Redis |

## Error Handling

- **ML API rate limit (429):** exponential backoff retry; if cached data exists, serve stale with a warning header.
- **Google Trends failure:** score computed without trend component; frontend shows "sin datos de tendencia" badge on the score.
- **Product missing `sold_quantity`:** product is included in results but demand field is displayed as "no disponible". It is not excluded — the user decides its relevance.

## Testing Strategy

- **Backend:** pytest with mocked MLAdapter and TrendsAdapter. Scoring Engine tested with unit tests — it is a pure function so no mocks needed.
- **Frontend:** Vitest for score display logic and data transformation utilities.
- **No E2E for MVP.** Browser-level tests added once the core flow is stable.

## Out of Scope (MVP)

- User authentication / multi-user support
- Amazon or other marketplaces
- Price history tracking over time
- Automated alerts ("notify me when score drops")
- Scraping (added later if API data proves insufficient)
