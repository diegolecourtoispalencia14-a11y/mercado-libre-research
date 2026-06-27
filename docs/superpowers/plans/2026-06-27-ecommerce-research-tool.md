# Ecommerce Product Research Tool — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web app dashboard that helps a LATAM seller discover and validate products to sell on Mercado Libre, with opportunity scoring, niche comparison, and report export.

**Architecture:** Python FastAPI backend with PostgreSQL (data persistence) and Redis (cache); React + Vite + TailwindCSS frontend. External API calls are isolated in adapter classes (MLAdapter, TrendsAdapter) that the rest of the system never calls directly. The Scoring Engine is a pure function with no I/O.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, httpx, pytrends, Redis (redis-py), PostgreSQL 16, React 18, Vite 5, TailwindCSS 3, Recharts 2, Vitest, pytest, Docker Compose.

## Global Constraints

- Python ≥ 3.12 required
- All backend tests use pytest with mocked adapters — no real HTTP calls in tests
- Scoring Engine is a pure function: no I/O, no side effects
- ML API base URL: `https://api.mercadolibre.com`
- Products cached 1 hour in Redis; Google Trends cached 24 hours
- Retry ML API on 429 with exponential backoff (max 3 retries)
- If TrendsAdapter fails, score is computed without trend component; `trend_available: false` in response
- Products without `sold_quantity` are included with `estimated_monthly_sales: null`
- Frontend is served on port 5173 (Vite dev), backend on port 8000
- No authentication in MVP

---

## File Structure

```
project-root/
├── docker-compose.yml
├── .env.example
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── app/
│   │   ├── main.py              # FastAPI app + router mounting + CORS
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── database.py          # SQLAlchemy engine + session factory
│   │   ├── cache.py             # Redis client + get/set helpers
│   │   ├── models/
│   │   │   ├── product.py       # Product ORM model
│   │   │   └── analysis.py      # Analysis, AnalysisProduct, SavedReport ORM models
│   │   ├── schemas/
│   │   │   ├── product.py       # Pydantic response schemas
│   │   │   └── analysis.py      # Pydantic schemas for analyses + reports
│   │   ├── adapters/
│   │   │   ├── base.py          # Abstract adapter interface
│   │   │   ├── ml_adapter.py    # MercadoLibre API adapter
│   │   │   └── trends_adapter.py # pytrends adapter
│   │   ├── scoring/
│   │   │   └── engine.py        # Pure scoring function
│   │   └── routers/
│   │       ├── search.py        # GET /search
│   │       ├── analyze.py       # GET /analyze/{ml_product_id}
│   │       ├── compare.py       # POST /compare
│   │       └── reports.py       # GET/POST /reports, GET /reports/{id}/export
│   └── tests/
│       ├── conftest.py          # Fixtures: test DB, mock adapters
│       ├── test_scoring.py
│       ├── test_ml_adapter.py
│       ├── test_trends_adapter.py
│       ├── test_search.py
│       ├── test_analyze.py
│       ├── test_compare.py
│       └── test_reports.py
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api/
        │   ├── client.js        # Base fetch wrapper with error handling
        │   ├── search.js
        │   ├── analyze.js
        │   ├── compare.js
        │   └── reports.js
        ├── components/
        │   ├── SearchBar.jsx
        │   ├── ProductList.jsx
        │   ├── ScoreBadge.jsx
        │   ├── ProductDetail.jsx
        │   ├── TrendChart.jsx
        │   ├── NicheComparison.jsx
        │   └── ReportHistory.jsx
        ├── pages/
        │   ├── SearchPage.jsx
        │   ├── DetailPage.jsx
        │   ├── ComparePage.jsx
        │   └── ReportsPage.jsx
        ├── utils/
        │   └── scoring.js       # Score color/label formatting helpers
        └── tests/
            ├── ScoreBadge.test.jsx
            └── scoring.test.js
```

---

## Task 1: Project scaffolding + Docker Compose

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `backend/pyproject.toml`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/index.html`

**Interfaces:**
- Produces: running `docker compose up` starts postgres:16, redis:7, backend (port 8000), frontend (port 5173)

- [ ] **Step 1: Create `.env.example`**

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/research
REDIS_URL=redis://localhost:6379
ML_SITE_ID=MLM
```

- [ ] **Step 2: Create `docker-compose.yml`**

```yaml
version: "3.9"
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: research
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

volumes:
  pgdata:
```

- [ ] **Step 3: Create `backend/pyproject.toml`**

```toml
[project]
name = "ecommerce-research-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.111",
    "uvicorn[standard]>=0.30",
    "sqlalchemy>=2.0",
    "alembic>=1.13",
    "psycopg2-binary>=2.9",
    "redis>=5.0",
    "httpx>=0.27",
    "pytrends>=4.9",
    "pydantic-settings>=2.3",
    "reportlab>=4.2",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- [ ] **Step 4: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e ".[dev]"
COPY . .
```

- [ ] **Step 5: Create frontend scaffolding**

```bash
cd frontend
npm create vite@latest . -- --template react
npm install
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p
npm install recharts
npm install -D vitest @vitest/ui jsdom @testing-library/react @testing-library/jest-dom
```

- [ ] **Step 6: Configure `frontend/tailwind.config.js`**

```js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: { extend: {} },
  plugins: [],
}
```

- [ ] **Step 7: Configure `frontend/vite.config.js`**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', rewrite: path => path.replace(/^\/api/, '') }
    }
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.js'],
    globals: true,
  }
})
```

- [ ] **Step 8: Add test setup file**

Create `frontend/src/tests/setup.js`:
```js
import '@testing-library/jest-dom'
```

- [ ] **Step 9: Commit**

```bash
git add docker-compose.yml .env.example backend/pyproject.toml backend/Dockerfile frontend/
git commit -m "feat: project scaffolding — docker compose, backend pyproject, frontend vite+tailwind"
```

---

## Task 2: Database models + Alembic migration

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/models/product.py`
- Create: `backend/app/models/analysis.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_initial_schema.py`
- Test: `backend/tests/conftest.py`

**Interfaces:**
- Produces:
  - `get_db()` → SQLAlchemy session generator (used by all routers)
  - `Product`, `Analysis`, `AnalysisProduct`, `SavedReport` ORM classes

- [ ] **Step 1: Write test that models can be created**

Create `backend/tests/conftest.py`:
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    e = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(e)
    yield e
    Base.metadata.drop_all(e)

@pytest.fixture
def db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
```

Create `backend/tests/test_models.py`:
```python
from app.models.product import Product
from app.models.analysis import Analysis, AnalysisProduct, SavedReport
from datetime import datetime, timezone

def test_product_create(db):
    p = Product(
        ml_id="MLM123",
        title="Auriculares Bluetooth",
        price=299.0,
        sold_quantity=150,
        seller_id="seller1",
        category_id="MLM1051",
        thumbnail_url="https://example.com/img.jpg",
        fetched_at=datetime.now(timezone.utc),
    )
    db.add(p)
    db.flush()
    assert p.id is not None

def test_analysis_create(db):
    a = Analysis(keyword="auriculares", score=7.5,
                 demand_score=8.0, competition_score=4.0, trend_score=6.5)
    db.add(a)
    db.flush()
    assert a.id is not None
```

- [ ] **Step 2: Run tests — expect failure (models not defined)**

```bash
cd backend && pytest tests/test_models.py -v
```
Expected: ImportError or ModuleNotFoundError

- [ ] **Step 3: Create `backend/app/config.py`**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/research"
    redis_url: str = "redis://localhost:6379"
    ml_site_id: str = "MLM"

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 4: Create `backend/app/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: Create `backend/app/models/product.py`**

```python
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    ml_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Float)
    sold_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seller_id: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[str] = mapped_column(String(50))
    thumbnail_url: Mapped[str] = mapped_column(String(1000))
    listing_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
```

- [ ] **Step 6: Create `backend/app/models/analysis.py`**

```python
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    score: Mapped[float] = mapped_column(Float)
    demand_score: Mapped[float] = mapped_column(Float)
    competition_score: Mapped[float] = mapped_column(Float)
    trend_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    products: Mapped[list["AnalysisProduct"]] = relationship(back_populates="analysis")
    report: Mapped["SavedReport | None"] = relationship(back_populates="analysis", uselist=False)

class AnalysisProduct(Base):
    __tablename__ = "analysis_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    rank: Mapped[int] = mapped_column(Integer)
    estimated_monthly_sales: Mapped[float | None] = mapped_column(Float, nullable=True)
    analysis: Mapped["Analysis"] = relationship(back_populates="products")

class SavedReport(Base):
    __tablename__ = "saved_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    analysis: Mapped["Analysis"] = relationship(back_populates="report")
```

- [ ] **Step 7: Run tests — expect pass**

```bash
cd backend && pytest tests/test_models.py -v
```
Expected: 2 passed

- [ ] **Step 8: Initialize Alembic**

```bash
cd backend && alembic init alembic
```

Edit `backend/alembic/env.py` — replace the `target_metadata` line and add imports:
```python
from app.database import Base
from app.models.product import Product  # noqa: F401
from app.models.analysis import Analysis, AnalysisProduct, SavedReport  # noqa: F401

target_metadata = Base.metadata
```

Also update `sqlalchemy.url` in `alembic.ini` to read from env:
In `alembic/env.py` `run_migrations_online`, replace:
```python
connectable = engine_from_config(config.get_section(config.config_ini_section), ...)
```
with:
```python
from app.config import settings
connectable = create_engine(settings.database_url)
```

- [ ] **Step 9: Generate and run migration**

```bash
cd backend
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```
Expected: tables created in PostgreSQL

- [ ] **Step 10: Commit**

```bash
git add backend/
git commit -m "feat: database models and initial Alembic migration"
```

---

## Task 3: Scoring Engine

**Files:**
- Create: `backend/app/scoring/engine.py`
- Create: `backend/app/scoring/__init__.py`
- Test: `backend/tests/test_scoring.py`

**Interfaces:**
- Consumes: list of product dicts with keys `sold_quantity`, `price`, `num_sellers`, `trend_interest` (0-100 or None)
- Produces:
  - `compute_scores(products: list[dict]) -> list[dict]` — returns same list with added `score`, `demand_score`, `competition_score`, `trend_score` keys (all floats 1-10)
  - `compute_estimated_monthly_sales(sold_quantity: int | None, listing_date: datetime | None) -> float | None`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_scoring.py`:
```python
import pytest
from datetime import datetime, timezone, timedelta
from app.scoring.engine import compute_scores, compute_estimated_monthly_sales

def test_scores_are_normalized_1_to_10():
    products = [
        {"sold_quantity": 1000, "price": 100.0, "num_sellers": 5,  "trend_interest": 80},
        {"sold_quantity": 10,   "price": 500.0, "num_sellers": 50, "trend_interest": 20},
    ]
    result = compute_scores(products)
    for p in result:
        assert 1.0 <= p["score"] <= 10.0

def test_higher_demand_lower_competition_scores_higher():
    products = [
        {"sold_quantity": 1000, "price": 100.0, "num_sellers": 2,  "trend_interest": 90},
        {"sold_quantity": 5,    "price": 100.0, "num_sellers": 100, "trend_interest": 10},
    ]
    result = compute_scores(products)
    assert result[0]["score"] > result[1]["score"]

def test_missing_trend_uses_neutral_value():
    products = [
        {"sold_quantity": 500, "price": 200.0, "num_sellers": 10, "trend_interest": None},
    ]
    result = compute_scores(products)
    assert result[0]["trend_score"] is None
    assert 1.0 <= result[0]["score"] <= 10.0

def test_missing_sold_quantity_scores_without_demand():
    products = [
        {"sold_quantity": None, "price": 200.0, "num_sellers": 10, "trend_interest": 50},
    ]
    result = compute_scores(products)
    assert result[0]["demand_score"] is None
    assert 1.0 <= result[0]["score"] <= 10.0

def test_single_product_gets_score_5():
    products = [
        {"sold_quantity": 100, "price": 200.0, "num_sellers": 10, "trend_interest": 50},
    ]
    result = compute_scores(products)
    assert result[0]["score"] == 5.0

def test_estimated_monthly_sales_calculation():
    listing_date = datetime.now(timezone.utc) - timedelta(days=90)
    result = compute_estimated_monthly_sales(300, listing_date)
    assert abs(result - 100.0) < 5.0

def test_estimated_monthly_sales_none_when_no_quantity():
    result = compute_estimated_monthly_sales(None, datetime.now(timezone.utc))
    assert result is None

def test_estimated_monthly_sales_none_when_no_date():
    result = compute_estimated_monthly_sales(300, None)
    assert result is None
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd backend && pytest tests/test_scoring.py -v
```
Expected: ImportError — module does not exist yet

- [ ] **Step 3: Implement scoring engine**

Create `backend/app/scoring/__init__.py` (empty).

Create `backend/app/scoring/engine.py`:
```python
from datetime import datetime, timezone
import math

NEUTRAL_TREND = 50.0

def compute_estimated_monthly_sales(
    sold_quantity: int | None,
    listing_date: datetime | None,
) -> float | None:
    if sold_quantity is None or listing_date is None:
        return None
    days = (datetime.now(timezone.utc) - listing_date).days
    months = max(1, days / 30)
    return round(sold_quantity / months, 2)

def _raw_score(sold_quantity: int | None, trend_interest: float | None,
               num_sellers: int, price: float) -> float:
    demand = float(sold_quantity) if sold_quantity is not None else 1.0
    trend = float(trend_interest) if trend_interest is not None else NEUTRAL_TREND
    competition = max(1.0, float(num_sellers))
    price_comp = max(1.0, price)
    return (demand * trend) / (competition * math.log1p(price_comp))

def _min_max_normalize(values: list[float], target_min=1.0, target_max=10.0) -> list[float]:
    lo, hi = min(values), max(values)
    if lo == hi:
        return [5.0] * len(values)
    return [
        target_min + (v - lo) / (hi - lo) * (target_max - target_min)
        for v in values
    ]

def compute_scores(products: list[dict]) -> list[dict]:
    raw_scores = [
        _raw_score(
            p.get("sold_quantity"),
            p.get("trend_interest"),
            p.get("num_sellers", 1),
            p.get("price", 1.0),
        )
        for p in products
    ]
    normalized = _min_max_normalize(raw_scores)

    result = []
    for p, score in zip(products, normalized):
        enriched = dict(p)
        enriched["score"] = round(score, 2)
        sq = p.get("sold_quantity")
        enriched["demand_score"] = round(math.log1p(float(sq)) * 10 / math.log1p(10000), 2) if sq is not None else None
        enriched["competition_score"] = round(max(1.0, 10.0 - float(p.get("num_sellers", 1)) / 10), 2)
        ti = p.get("trend_interest")
        enriched["trend_score"] = round(float(ti) / 10, 2) if ti is not None else None
        result.append(enriched)
    return result
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd backend && pytest tests/test_scoring.py -v
```
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/scoring/ backend/tests/test_scoring.py
git commit -m "feat: scoring engine — pure function, min-max normalized 1-10"
```

---

## Task 4: MLAdapter

**Files:**
- Create: `backend/app/adapters/base.py`
- Create: `backend/app/adapters/__init__.py`
- Create: `backend/app/adapters/ml_adapter.py`
- Create: `backend/app/cache.py`
- Test: `backend/tests/test_ml_adapter.py`

**Interfaces:**
- Consumes: `settings.ml_site_id` (e.g. `"MLM"`), Redis cache
- Produces:
  - `MLAdapter.search(keyword: str, limit: int) -> list[dict]`
    Returns: `[{ml_id, title, price, sold_quantity, seller_id, category_id, thumbnail_url, listing_date, num_sellers}, ...]`
  - `MLAdapter.get_product(ml_id: str) -> dict`
    Returns: `{ml_id, title, price, sold_quantity, seller_id, category_id, thumbnail_url, listing_date, num_sellers, description}`

- [ ] **Step 1: Create `backend/app/cache.py`**

```python
import json
import redis
from app.config import settings

_client: redis.Redis | None = None

def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client

def cache_get(key: str) -> dict | list | None:
    raw = get_redis().get(key)
    return json.loads(raw) if raw else None

def cache_set(key: str, value: dict | list, ttl_seconds: int) -> None:
    get_redis().setex(key, ttl_seconds, json.dumps(value))
```

- [ ] **Step 2: Write failing tests**

Create `backend/tests/test_ml_adapter.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from app.adapters.ml_adapter import MLAdapter

MOCK_SEARCH_RESPONSE = {
    "results": [
        {
            "id": "MLM123",
            "title": "Auriculares Bluetooth",
            "price": 299.0,
            "sold_quantity": 150,
            "seller": {"id": "seller1"},
            "category_id": "MLM1051",
            "thumbnail": "https://example.com/img.jpg",
            "date_created": "2024-01-15T00:00:00.000Z",
            "seller_address": {},
        }
    ]
}

MOCK_CATEGORY_RESPONSE = {"total": 42}

@pytest.fixture
def adapter():
    return MLAdapter(site_id="MLM")

def test_search_returns_normalized_list(adapter):
    with patch("app.adapters.ml_adapter.cache_get", return_value=None), \
         patch("app.adapters.ml_adapter.cache_set"), \
         patch("httpx.get") as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: MOCK_SEARCH_RESPONSE, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: MOCK_CATEGORY_RESPONSE, raise_for_status=lambda: None),
        ]
        results = adapter.search("auriculares", limit=10)
    assert len(results) == 1
    assert results[0]["ml_id"] == "MLM123"
    assert results[0]["num_sellers"] == 42

def test_search_uses_cache(adapter):
    cached = [{"ml_id": "CACHED", "title": "From cache", "price": 100.0,
               "sold_quantity": 10, "seller_id": "s1", "category_id": "c1",
               "thumbnail_url": "", "listing_date": None, "num_sellers": 5}]
    with patch("app.adapters.ml_adapter.cache_get", return_value=cached):
        results = adapter.search("auriculares")
    assert results[0]["ml_id"] == "CACHED"

def test_search_retries_on_429(adapter):
    with patch("app.adapters.ml_adapter.cache_get", return_value=None), \
         patch("app.adapters.ml_adapter.cache_set"), \
         patch("app.adapters.ml_adapter.time.sleep"), \
         patch("httpx.get") as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=429, json=lambda: {}, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: MOCK_SEARCH_RESPONSE, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: MOCK_CATEGORY_RESPONSE, raise_for_status=lambda: None),
        ]
        results = adapter.search("auriculares")
    assert results[0]["ml_id"] == "MLM123"
```

- [ ] **Step 3: Run tests — expect failure**

```bash
cd backend && pytest tests/test_ml_adapter.py -v
```
Expected: ImportError

- [ ] **Step 4: Create `backend/app/adapters/base.py`**

```python
from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    def search(self, keyword: str, limit: int = 50) -> list[dict]:
        ...

    @abstractmethod
    def get_product(self, ml_id: str) -> dict:
        ...
```

- [ ] **Step 5: Create `backend/app/adapters/__init__.py`** (empty)

- [ ] **Step 6: Create `backend/app/adapters/ml_adapter.py`**

```python
import time
import httpx
from datetime import datetime, timezone
from app.adapters.base import BaseAdapter
from app.cache import cache_get, cache_set

ML_BASE = "https://api.mercadolibre.com"
CACHE_TTL = 3600  # 1 hour


def _parse_listing_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def _get_with_retry(url: str, params: dict | None = None, max_retries: int = 3) -> dict:
    delay = 1.0
    for attempt in range(max_retries):
        resp = httpx.get(url, params=params, timeout=10)
        if resp.status_code == 429:
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"ML API rate limit exceeded after {max_retries} retries")


class MLAdapter(BaseAdapter):
    def __init__(self, site_id: str = "MLM"):
        self.site_id = site_id

    def search(self, keyword: str, limit: int = 50) -> list[dict]:
        cache_key = f"ml:search:{self.site_id}:{keyword}:{limit}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        data = _get_with_retry(
            f"{ML_BASE}/sites/{self.site_id}/search",
            params={"q": keyword, "limit": limit},
        )

        results = []
        for item in data.get("results", []):
            category_id = item.get("category_id", "")
            num_sellers = self._get_category_seller_count(category_id)
            results.append({
                "ml_id": item["id"],
                "title": item["title"],
                "price": float(item.get("price", 0)),
                "sold_quantity": item.get("sold_quantity"),
                "seller_id": str(item.get("seller", {}).get("id", "")),
                "category_id": category_id,
                "thumbnail_url": item.get("thumbnail", ""),
                "listing_date": item.get("date_created"),
                "num_sellers": num_sellers,
            })

        cache_set(cache_key, results, CACHE_TTL)
        return results

    def get_product(self, ml_id: str) -> dict:
        cache_key = f"ml:product:{ml_id}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        item = _get_with_retry(f"{ML_BASE}/items/{ml_id}")
        category_id = item.get("category_id", "")
        num_sellers = self._get_category_seller_count(category_id)

        result = {
            "ml_id": item["id"],
            "title": item["title"],
            "price": float(item.get("price", 0)),
            "sold_quantity": item.get("sold_quantity"),
            "seller_id": str(item.get("seller_id", "")),
            "category_id": category_id,
            "thumbnail_url": item.get("thumbnail", ""),
            "listing_date": item.get("date_created"),
            "num_sellers": num_sellers,
            "description": item.get("plain_text", ""),
        }

        cache_set(cache_key, result, CACHE_TTL)
        return result

    def _get_category_seller_count(self, category_id: str) -> int:
        if not category_id:
            return 1
        try:
            data = _get_with_retry(
                f"{ML_BASE}/sites/{self.site_id}/search",
                params={"category": category_id, "limit": 1},
            )
            return data.get("paging", {}).get("total", 1)
        except Exception:
            return 1
```

- [ ] **Step 7: Run tests — expect pass**

```bash
cd backend && pytest tests/test_ml_adapter.py -v
```
Expected: 3 passed

- [ ] **Step 8: Commit**

```bash
git add backend/app/adapters/ backend/app/cache.py backend/tests/test_ml_adapter.py
git commit -m "feat: MLAdapter with Redis caching and exponential backoff retry"
```

---

## Task 5: TrendsAdapter

**Files:**
- Create: `backend/app/adapters/trends_adapter.py`
- Test: `backend/tests/test_trends_adapter.py`

**Interfaces:**
- Produces:
  - `TrendsAdapter.get_interest(keyword: str) -> float | None`
    Returns: average Google Trends interest (0-100) over last 12 months, or `None` if pytrends fails

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_trends_adapter.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from app.adapters.trends_adapter import TrendsAdapter

@pytest.fixture
def adapter():
    return TrendsAdapter()

def test_returns_average_interest(adapter):
    mock_df = pd.DataFrame({"auriculares": [70, 80, 90, 75]})
    with patch("app.adapters.trends_adapter.cache_get", return_value=None), \
         patch("app.adapters.trends_adapter.cache_set"), \
         patch("app.adapters.trends_adapter.TrendReq") as mock_trend_cls:
        mock_pytrends = MagicMock()
        mock_pytrends.interest_over_time.return_value = mock_df
        mock_trend_cls.return_value = mock_pytrends
        result = adapter.get_interest("auriculares")
    assert result == pytest.approx(78.75)

def test_returns_none_on_empty_dataframe(adapter):
    mock_df = pd.DataFrame()
    with patch("app.adapters.trends_adapter.cache_get", return_value=None), \
         patch("app.adapters.trends_adapter.cache_set"), \
         patch("app.adapters.trends_adapter.TrendReq") as mock_trend_cls:
        mock_pytrends = MagicMock()
        mock_pytrends.interest_over_time.return_value = mock_df
        mock_trend_cls.return_value = mock_pytrends
        result = adapter.get_interest("xyznonexistent")
    assert result is None

def test_returns_none_on_exception(adapter):
    with patch("app.adapters.trends_adapter.cache_get", return_value=None), \
         patch("app.adapters.trends_adapter.TrendReq") as mock_trend_cls:
        mock_trend_cls.side_effect = Exception("pytrends error")
        result = adapter.get_interest("auriculares")
    assert result is None

def test_uses_cache(adapter):
    with patch("app.adapters.trends_adapter.cache_get", return_value=72.5):
        result = adapter.get_interest("auriculares")
    assert result == 72.5
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd backend && pytest tests/test_trends_adapter.py -v
```
Expected: ImportError

- [ ] **Step 3: Create `backend/app/adapters/trends_adapter.py`**

```python
from pytrends.request import TrendReq
from app.cache import cache_get, cache_set

CACHE_TTL = 86400  # 24 hours


class TrendsAdapter:
    def get_interest(self, keyword: str) -> float | None:
        cache_key = f"trends:{keyword}"
        cached = cache_get(cache_key)
        if cached is not None:
            return float(cached)

        try:
            pytrends = TrendReq(hl="es-MX", tz=360)
            pytrends.build_payload([keyword], timeframe="today 12-m", geo="MX")
            df = pytrends.interest_over_time()

            if df.empty or keyword not in df.columns:
                return None

            avg = float(df[keyword].mean())
            cache_set(cache_key, avg, CACHE_TTL)
            return avg
        except Exception:
            return None
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd backend && pytest tests/test_trends_adapter.py -v
```
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/adapters/trends_adapter.py backend/tests/test_trends_adapter.py
git commit -m "feat: TrendsAdapter with graceful degradation and 24h Redis cache"
```

---

## Task 6: FastAPI app + search endpoint

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/schemas/product.py`
- Create: `backend/app/schemas/analysis.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/routers/search.py`
- Test: `backend/tests/test_search.py`

**Interfaces:**
- Consumes: `MLAdapter.search()`, `TrendsAdapter.get_interest()`, `compute_scores()`, `compute_estimated_monthly_sales()`
- Produces: `GET /search?q=&category=&limit=` → `SearchResponse`

```python
# SearchResponse shape (Pydantic)
class ProductScore(BaseModel):
    ml_id: str
    title: str
    price: float
    sold_quantity: int | None
    thumbnail_url: str
    estimated_monthly_sales: float | None
    score: float
    demand_score: float | None
    competition_score: float
    trend_score: float | None
    trend_available: bool

class SearchResponse(BaseModel):
    keyword: str
    products: list[ProductScore]
    trend_available: bool
```

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_search.py`:
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

ML_PRODUCTS = [
    {"ml_id": "MLM1", "title": "Auriculares BT", "price": 299.0,
     "sold_quantity": 500, "seller_id": "s1", "category_id": "c1",
     "thumbnail_url": "https://img.jpg", "listing_date": "2024-01-01T00:00:00+00:00",
     "num_sellers": 10},
    {"ml_id": "MLM2", "title": "Auriculares Pro", "price": 599.0,
     "sold_quantity": 50, "seller_id": "s2", "category_id": "c1",
     "thumbnail_url": "https://img2.jpg", "listing_date": "2024-03-01T00:00:00+00:00",
     "num_sellers": 10},
]

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

def test_search_returns_scored_products(client):
    with patch("app.routers.search.MLAdapter") as MockML, \
         patch("app.routers.search.TrendsAdapter") as MockTrends:
        MockML.return_value.search.return_value = ML_PRODUCTS
        MockTrends.return_value.get_interest.return_value = 65.0
        resp = client.get("/search?q=auriculares&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["keyword"] == "auriculares"
    assert len(data["products"]) == 2
    assert all(1 <= p["score"] <= 10 for p in data["products"])
    assert data["trend_available"] is True

def test_search_without_trend(client):
    with patch("app.routers.search.MLAdapter") as MockML, \
         patch("app.routers.search.TrendsAdapter") as MockTrends:
        MockML.return_value.search.return_value = ML_PRODUCTS
        MockTrends.return_value.get_interest.return_value = None
        resp = client.get("/search?q=auriculares")
    assert resp.status_code == 200
    data = resp.json()
    assert data["trend_available"] is False
    assert all(p["trend_score"] is None for p in data["products"])
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd backend && pytest tests/test_search.py -v
```
Expected: ImportError

- [ ] **Step 3: Create Pydantic schemas**

Create `backend/app/schemas/__init__.py` (empty).

Create `backend/app/schemas/product.py`:
```python
from pydantic import BaseModel

class ProductScore(BaseModel):
    ml_id: str
    title: str
    price: float
    sold_quantity: int | None
    thumbnail_url: str
    estimated_monthly_sales: float | None
    score: float
    demand_score: float | None
    competition_score: float
    trend_score: float | None
    trend_available: bool

class SearchResponse(BaseModel):
    keyword: str
    products: list[ProductScore]
    trend_available: bool
```

- [ ] **Step 4: Create `backend/app/routers/search.py`**

```python
from fastapi import APIRouter
from datetime import datetime, timezone
from app.adapters.ml_adapter import MLAdapter
from app.adapters.trends_adapter import TrendsAdapter
from app.scoring.engine import compute_scores, compute_estimated_monthly_sales
from app.schemas.product import ProductScore, SearchResponse

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search(q: str, category: str | None = None, limit: int = 50):
    ml = MLAdapter()
    trends = TrendsAdapter()

    raw_products = ml.search(q, limit=limit)
    trend_interest = trends.get_interest(q)
    trend_available = trend_interest is not None

    for p in raw_products:
        p["trend_interest"] = trend_interest

    scored = compute_scores(raw_products)

    products = []
    for p in scored:
        listing_date_str = p.get("listing_date")
        listing_dt = None
        if listing_date_str:
            try:
                listing_dt = datetime.fromisoformat(
                    listing_date_str.replace("Z", "+00:00")
                )
            except ValueError:
                pass

        products.append(ProductScore(
            ml_id=p["ml_id"],
            title=p["title"],
            price=p["price"],
            sold_quantity=p.get("sold_quantity"),
            thumbnail_url=p.get("thumbnail_url", ""),
            estimated_monthly_sales=compute_estimated_monthly_sales(
                p.get("sold_quantity"), listing_dt
            ),
            score=p["score"],
            demand_score=p.get("demand_score"),
            competition_score=p["competition_score"],
            trend_score=p.get("trend_score"),
            trend_available=trend_available,
        ))

    return SearchResponse(keyword=q, products=products, trend_available=trend_available)
```

- [ ] **Step 5: Create `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search, analyze, compare, reports

app = FastAPI(title="Ecommerce Research API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(analyze.router)
app.include_router(compare.router)
app.include_router(reports.router)
```

Also create empty stub routers so `main.py` imports don't fail yet:

`backend/app/routers/__init__.py` (empty)

`backend/app/routers/analyze.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`backend/app/routers/compare.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`backend/app/routers/reports.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

- [ ] **Step 6: Run tests — expect pass**

```bash
cd backend && pytest tests/test_search.py -v
```
Expected: 2 passed

- [ ] **Step 7: Commit**

```bash
git add backend/app/main.py backend/app/schemas/ backend/app/routers/ backend/tests/test_search.py
git commit -m "feat: FastAPI app + GET /search with scoring and trend integration"
```

---

## Task 7: Analyze endpoint

**Files:**
- Create: `backend/app/schemas/analysis.py`
- Modify: `backend/app/routers/analyze.py`
- Test: `backend/tests/test_analyze.py`

**Interfaces:**
- Consumes: `MLAdapter.get_product(ml_id)`, `TrendsAdapter.get_interest(keyword)`, `compute_scores()`, `compute_estimated_monthly_sales()`
- Produces: `GET /analyze/{ml_product_id}` → `ProductDetailResponse`

```python
class ProductDetailResponse(BaseModel):
    ml_id: str
    title: str
    price: float
    sold_quantity: int | None
    seller_id: str
    category_id: str
    thumbnail_url: str
    estimated_monthly_sales: float | None
    score: float
    demand_score: float | None
    competition_score: float
    trend_score: float | None
    trend_available: bool
    trend_timeline: list[float]  # 12 monthly values, empty if unavailable
    description: str
```

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_analyze.py`:
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

MOCK_PRODUCT = {
    "ml_id": "MLM123", "title": "Auriculares BT", "price": 299.0,
    "sold_quantity": 500, "seller_id": "seller1", "category_id": "MLM1051",
    "thumbnail_url": "https://img.jpg", "listing_date": "2024-01-01T00:00:00+00:00",
    "num_sellers": 15, "description": "Gran producto",
}

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

def test_analyze_returns_detail(client):
    with patch("app.routers.analyze.MLAdapter") as MockML, \
         patch("app.routers.analyze.TrendsAdapter") as MockTrends:
        MockML.return_value.get_product.return_value = MOCK_PRODUCT
        MockTrends.return_value.get_interest.return_value = 70.0
        resp = client.get("/analyze/MLM123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ml_id"] == "MLM123"
    assert 1 <= data["score"] <= 10
    assert data["trend_available"] is True

def test_analyze_handles_missing_trend(client):
    with patch("app.routers.analyze.MLAdapter") as MockML, \
         patch("app.routers.analyze.TrendsAdapter") as MockTrends:
        MockML.return_value.get_product.return_value = MOCK_PRODUCT
        MockTrends.return_value.get_interest.return_value = None
        resp = client.get("/analyze/MLM123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["trend_available"] is False
    assert data["trend_score"] is None
    assert data["trend_timeline"] == []
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd backend && pytest tests/test_analyze.py -v
```
Expected: 404 or missing schema

- [ ] **Step 3: Create `backend/app/schemas/analysis.py`**

```python
from pydantic import BaseModel
from datetime import datetime

class ProductDetailResponse(BaseModel):
    ml_id: str
    title: str
    price: float
    sold_quantity: int | None
    seller_id: str
    category_id: str
    thumbnail_url: str
    estimated_monthly_sales: float | None
    score: float
    demand_score: float | None
    competition_score: float
    trend_score: float | None
    trend_available: bool
    trend_timeline: list[float]
    description: str

class CompareRequest(BaseModel):
    product_ids: list[str]

class CompareResponse(BaseModel):
    products: list[ProductDetailResponse]

class SaveReportRequest(BaseModel):
    analysis_id: int
    name: str
    notes: str | None = None

class SavedReportResponse(BaseModel):
    id: int
    analysis_id: int
    name: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 4: Implement `backend/app/routers/analyze.py`**

```python
from fastapi import APIRouter
from datetime import datetime
from app.adapters.ml_adapter import MLAdapter
from app.adapters.trends_adapter import TrendsAdapter
from app.scoring.engine import compute_scores, compute_estimated_monthly_sales
from app.schemas.analysis import ProductDetailResponse

router = APIRouter()


def _to_detail(p: dict, scored: dict, trend_interest: float | None,
               trend_available: bool) -> ProductDetailResponse:
    listing_dt = None
    listing_date_str = p.get("listing_date")
    if listing_date_str:
        try:
            listing_dt = datetime.fromisoformat(
                listing_date_str.replace("Z", "+00:00")
            )
        except ValueError:
            pass

    return ProductDetailResponse(
        ml_id=p["ml_id"],
        title=p["title"],
        price=p["price"],
        sold_quantity=p.get("sold_quantity"),
        seller_id=p.get("seller_id", ""),
        category_id=p.get("category_id", ""),
        thumbnail_url=p.get("thumbnail_url", ""),
        estimated_monthly_sales=compute_estimated_monthly_sales(
            p.get("sold_quantity"), listing_dt
        ),
        score=scored["score"],
        demand_score=scored.get("demand_score"),
        competition_score=scored["competition_score"],
        trend_score=scored.get("trend_score"),
        trend_available=trend_available,
        trend_timeline=[],
        description=p.get("description", ""),
    )


@router.get("/analyze/{ml_product_id}", response_model=ProductDetailResponse)
def analyze(ml_product_id: str):
    ml = MLAdapter()
    trends = TrendsAdapter()

    product = ml.get_product(ml_product_id)
    trend_interest = trends.get_interest(product["title"].split()[0])
    trend_available = trend_interest is not None

    product["trend_interest"] = trend_interest
    scored_list = compute_scores([product])
    scored = scored_list[0]

    return _to_detail(product, scored, trend_interest, trend_available)
```

- [ ] **Step 5: Run tests — expect pass**

```bash
cd backend && pytest tests/test_analyze.py -v
```
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/analyze.py backend/app/schemas/analysis.py backend/tests/test_analyze.py
git commit -m "feat: GET /analyze/{id} — detailed product report with scoring"
```

---

## Task 8: Compare + Reports endpoints

**Files:**
- Modify: `backend/app/routers/compare.py`
- Modify: `backend/app/routers/reports.py`
- Test: `backend/tests/test_compare.py`
- Test: `backend/tests/test_reports.py`

**Interfaces:**
- Consumes: `MLAdapter.get_product()`, `compute_scores()`, `ProductDetailResponse`, `SavedReport` ORM, `get_db()`
- Produces:
  - `POST /compare` → `CompareResponse`
  - `GET /reports` → `list[SavedReportResponse]`
  - `POST /reports` → `SavedReportResponse`
  - `GET /reports/{id}/export?format=csv|pdf` → file download

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_compare.py`:
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

PRODUCT_A = {
    "ml_id": "MLM1", "title": "Prod A", "price": 200.0,
    "sold_quantity": 300, "seller_id": "s1", "category_id": "c1",
    "thumbnail_url": "", "listing_date": None, "num_sellers": 5,
    "description": "",
}
PRODUCT_B = {
    "ml_id": "MLM2", "title": "Prod B", "price": 500.0,
    "sold_quantity": 30, "seller_id": "s2", "category_id": "c1",
    "thumbnail_url": "", "listing_date": None, "num_sellers": 50,
    "description": "",
}

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

def test_compare_returns_multiple_products(client):
    def get_product_side_effect(ml_id):
        return PRODUCT_A if ml_id == "MLM1" else PRODUCT_B

    with patch("app.routers.compare.MLAdapter") as MockML, \
         patch("app.routers.compare.TrendsAdapter") as MockTrends:
        MockML.return_value.get_product.side_effect = get_product_side_effect
        MockTrends.return_value.get_interest.return_value = 60.0
        resp = client.post("/compare", json={"product_ids": ["MLM1", "MLM2"]})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["products"]) == 2
    assert data["products"][0]["ml_id"] in ["MLM1", "MLM2"]
```

Create `backend/tests/test_reports.py`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_reports_returns_list(client):
    resp = client.get("/reports")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd backend && pytest tests/test_compare.py tests/test_reports.py -v
```
Expected: failures or 404

- [ ] **Step 3: Implement `backend/app/routers/compare.py`**

```python
from fastapi import APIRouter
from app.adapters.ml_adapter import MLAdapter
from app.adapters.trends_adapter import TrendsAdapter
from app.scoring.engine import compute_scores, compute_estimated_monthly_sales
from app.schemas.analysis import CompareRequest, CompareResponse, ProductDetailResponse
from app.routers.analyze import _to_detail

router = APIRouter()


@router.post("/compare", response_model=CompareResponse)
def compare(body: CompareRequest):
    ml = MLAdapter()
    trends = TrendsAdapter()

    products = [ml.get_product(pid) for pid in body.product_ids]
    trend_interest = trends.get_interest(products[0]["title"].split()[0]) if products else None
    trend_available = trend_interest is not None

    for p in products:
        p["trend_interest"] = trend_interest

    scored_list = compute_scores(products)

    details = [
        _to_detail(p, scored, trend_interest, trend_available)
        for p, scored in zip(products, scored_list)
    ]

    return CompareResponse(products=details)
```

- [ ] **Step 4: Implement `backend/app/routers/reports.py`**

```python
import csv
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analysis import SavedReport, Analysis
from app.schemas.analysis import SaveReportRequest, SavedReportResponse

router = APIRouter()


@router.get("/reports", response_model=list[SavedReportResponse])
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(SavedReport).order_by(SavedReport.id.desc()).all()
    return [
        SavedReportResponse(
            id=r.id,
            analysis_id=r.analysis_id,
            name=r.name,
            notes=r.notes,
            created_at=r.analysis.created_at,
        )
        for r in reports
    ]


@router.post("/reports", response_model=SavedReportResponse)
def save_report(body: SaveReportRequest, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == body.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    report = SavedReport(
        analysis_id=body.analysis_id,
        name=body.name,
        notes=body.notes,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return SavedReportResponse(
        id=report.id,
        analysis_id=report.analysis_id,
        name=report.name,
        notes=report.notes,
        created_at=analysis.created_at,
    )


@router.get("/reports/{report_id}/export")
def export_report(report_id: int, format: str = "csv", db: Session = Depends(get_db)):
    report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    analysis = report.analysis
    products = [ap for ap in analysis.products]

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["rank", "product_id", "estimated_monthly_sales"])
        for ap in products:
            writer.writerow([ap.rank, ap.product_id, ap.estimated_monthly_sales])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"},
        )

    if format == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        data = [["Rank", "Product ID", "Est. Monthly Sales"]]
        for ap in products:
            data.append([str(ap.rank), str(ap.product_id), str(ap.estimated_monthly_sales)])
        doc.build([Table(data)])
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"},
        )

    raise HTTPException(status_code=400, detail="format must be csv or pdf")
```

- [ ] **Step 5: Run tests — expect pass**

```bash
cd backend && pytest tests/test_compare.py tests/test_reports.py -v
```
Expected: 2 passed

- [ ] **Step 6: Run full backend test suite**

```bash
cd backend && pytest -v
```
Expected: all tests pass

- [ ] **Step 7: Commit**

```bash
git add backend/app/routers/compare.py backend/app/routers/reports.py backend/tests/
git commit -m "feat: POST /compare and GET/POST /reports with CSV and PDF export"
```

---

## Task 9: Frontend API client + utilities

**Files:**
- Create: `frontend/src/api/client.js`
- Create: `frontend/src/api/search.js`
- Create: `frontend/src/api/analyze.js`
- Create: `frontend/src/api/compare.js`
- Create: `frontend/src/api/reports.js`
- Create: `frontend/src/utils/scoring.js`
- Test: `frontend/src/tests/scoring.test.js`

**Interfaces:**
- Produces:
  - `searchProducts(q, limit)` → `SearchResponse`
  - `analyzeProduct(mlId)` → `ProductDetailResponse`
  - `compareProducts(productIds)` → `CompareResponse`
  - `getReports()` → `SavedReportResponse[]`
  - `saveReport(analysisId, name, notes)` → `SavedReportResponse`
  - `getExportUrl(reportId, format)` → `string` (URL)
  - `scoreColor(score: number)` → `string` (Tailwind color class)
  - `scoreLabel(score: number)` → `string`

- [ ] **Step 1: Write failing utility tests**

Create `frontend/src/tests/scoring.test.js`:
```js
import { describe, it, expect } from 'vitest'
import { scoreColor, scoreLabel } from '../utils/scoring'

describe('scoreColor', () => {
  it('returns green for high scores', () => {
    expect(scoreColor(8.5)).toBe('text-green-600')
  })
  it('returns yellow for medium scores', () => {
    expect(scoreColor(5.0)).toBe('text-yellow-500')
  })
  it('returns red for low scores', () => {
    expect(scoreColor(2.0)).toBe('text-red-500')
  })
})

describe('scoreLabel', () => {
  it('labels high scores as Alta oportunidad', () => {
    expect(scoreLabel(8)).toBe('Alta oportunidad')
  })
  it('labels medium scores as Oportunidad media', () => {
    expect(scoreLabel(5)).toBe('Oportunidad media')
  })
  it('labels low scores as Baja oportunidad', () => {
    expect(scoreLabel(2)).toBe('Baja oportunidad')
  })
})
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd frontend && npx vitest run src/tests/scoring.test.js
```
Expected: module not found

- [ ] **Step 3: Create `frontend/src/utils/scoring.js`**

```js
export function scoreColor(score) {
  if (score >= 7) return 'text-green-600'
  if (score >= 4) return 'text-yellow-500'
  return 'text-red-500'
}

export function scoreLabel(score) {
  if (score >= 7) return 'Alta oportunidad'
  if (score >= 4) return 'Oportunidad media'
  return 'Baja oportunidad'
}
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd frontend && npx vitest run src/tests/scoring.test.js
```
Expected: 6 passed

- [ ] **Step 5: Create `frontend/src/api/client.js`**

```js
const BASE = '/api'

export async function apiFetch(path, options = {}) {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!resp.ok) throw new Error(`API error ${resp.status}: ${await resp.text()}`)
  return resp.json()
}
```

- [ ] **Step 6: Create remaining API modules**

`frontend/src/api/search.js`:
```js
import { apiFetch } from './client'
export const searchProducts = (q, limit = 50) =>
  apiFetch(`/search?q=${encodeURIComponent(q)}&limit=${limit}`)
```

`frontend/src/api/analyze.js`:
```js
import { apiFetch } from './client'
export const analyzeProduct = (mlId) => apiFetch(`/analyze/${mlId}`)
```

`frontend/src/api/compare.js`:
```js
import { apiFetch } from './client'
export const compareProducts = (productIds) =>
  apiFetch('/compare', { method: 'POST', body: JSON.stringify({ product_ids: productIds }) })
```

`frontend/src/api/reports.js`:
```js
import { apiFetch } from './client'
export const getReports = () => apiFetch('/reports')
export const saveReport = (analysisId, name, notes = null) =>
  apiFetch('/reports', { method: 'POST', body: JSON.stringify({ analysis_id: analysisId, name, notes }) })
export const getExportUrl = (reportId, format = 'csv') =>
  `/api/reports/${reportId}/export?format=${format}`
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/api/ frontend/src/utils/ frontend/src/tests/
git commit -m "feat: frontend API client and scoring utility functions"
```

---

## Task 10: SearchBar + ProductList + ScoreBadge components

**Files:**
- Create: `frontend/src/components/SearchBar.jsx`
- Create: `frontend/src/components/ScoreBadge.jsx`
- Create: `frontend/src/components/ProductList.jsx`
- Test: `frontend/src/tests/ScoreBadge.test.jsx`

**Interfaces:**
- `SearchBar` props: `{ onSearch: (q: string) => void, loading: boolean }`
- `ScoreBadge` props: `{ score: number, trendAvailable: boolean }`
- `ProductList` props: `{ products: ProductScore[], onSelect: (mlId: string) => void, onCompare: (mlId: string) => void, selectedForCompare: string[] }`

- [ ] **Step 1: Write failing ScoreBadge test**

Create `frontend/src/tests/ScoreBadge.test.jsx`:
```jsx
import { render, screen } from '@testing-library/react'
import ScoreBadge from '../components/ScoreBadge'

test('shows score value', () => {
  render(<ScoreBadge score={7.5} trendAvailable={true} />)
  expect(screen.getByText('7.5')).toBeInTheDocument()
})

test('shows sin datos badge when trend unavailable', () => {
  render(<ScoreBadge score={5.0} trendAvailable={false} />)
  expect(screen.getByText(/sin datos de tendencia/i)).toBeInTheDocument()
})
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd frontend && npx vitest run src/tests/ScoreBadge.test.jsx
```
Expected: module not found

- [ ] **Step 3: Create `frontend/src/components/ScoreBadge.jsx`**

```jsx
import { scoreColor, scoreLabel } from '../utils/scoring'

export default function ScoreBadge({ score, trendAvailable }) {
  return (
    <div className="flex flex-col items-center gap-1">
      <span className={`text-2xl font-bold ${scoreColor(score)}`}>{score}</span>
      <span className="text-xs text-gray-500">{scoreLabel(score)}</span>
      {!trendAvailable && (
        <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">
          sin datos de tendencia
        </span>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd frontend && npx vitest run src/tests/ScoreBadge.test.jsx
```
Expected: 2 passed

- [ ] **Step 5: Create `frontend/src/components/SearchBar.jsx`**

```jsx
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
```

- [ ] **Step 6: Create `frontend/src/components/ProductList.jsx`**

```jsx
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
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/ frontend/src/tests/
git commit -m "feat: SearchBar, ProductList, ScoreBadge components"
```

---

## Task 11: Pages — SearchPage + DetailPage + TrendChart

**Files:**
- Create: `frontend/src/components/TrendChart.jsx`
- Create: `frontend/src/components/ProductDetail.jsx`
- Create: `frontend/src/pages/SearchPage.jsx`
- Create: `frontend/src/pages/DetailPage.jsx`
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/main.jsx`

**Interfaces:**
- `TrendChart` props: `{ data: number[] }` — array of 12 monthly trend values
- `ProductDetail` props: `{ detail: ProductDetailResponse }`
- `SearchPage` — manages search state, renders SearchBar + ProductList, navigates to DetailPage
- `DetailPage` — fetches `/analyze/{id}`, renders ProductDetail + TrendChart

- [ ] **Step 1: Install react-router-dom**

```bash
cd frontend && npm install react-router-dom
```

- [ ] **Step 2: Create `frontend/src/components/TrendChart.jsx`**

```jsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const MONTHS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

export default function TrendChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-400 text-sm">
        Sin datos de tendencia disponibles
      </div>
    )
  }
  const chartData = data.map((v, i) => ({ month: MONTHS[i % 12], interest: v }))
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={chartData}>
        <XAxis dataKey="month" tick={{ fontSize: 12 }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Line type="monotone" dataKey="interest" stroke="#2563eb" dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 3: Create `frontend/src/components/ProductDetail.jsx`**

```jsx
import ScoreBadge from './ScoreBadge'
import TrendChart from './TrendChart'

export default function ProductDetail({ detail }) {
  return (
    <div className="space-y-6">
      <div className="flex gap-4 items-start">
        {detail.thumbnail_url && (
          <img src={detail.thumbnail_url} alt="" className="w-24 h-24 object-contain border rounded" />
        )}
        <div className="flex-1">
          <h2 className="text-xl font-semibold">{detail.title}</h2>
          <p className="text-gray-500 text-sm mt-1">Categoría: {detail.category_id}</p>
        </div>
        <ScoreBadge score={detail.score} trendAvailable={detail.trend_available} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Precio promedio', value: `$${detail.price.toLocaleString('es-MX')}` },
          { label: 'Ventas/mes est.', value: detail.estimated_monthly_sales != null ? Math.round(detail.estimated_monthly_sales).toLocaleString('es-MX') : 'N/D' },
          { label: 'Vendedores en nicho', value: detail.competition_score != null ? detail.competition_score.toFixed(1) : 'N/D' },
          { label: 'Demanda', value: detail.demand_score != null ? detail.demand_score.toFixed(1) : 'N/D' },
        ].map(({ label, value }) => (
          <div key={label} className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">{label}</p>
            <p className="text-lg font-semibold">{value}</p>
          </div>
        ))}
      </div>

      <div>
        <h3 className="font-medium mb-2">Tendencia (12 meses)</h3>
        <TrendChart data={detail.trend_timeline} />
      </div>

      {detail.description && (
        <div>
          <h3 className="font-medium mb-1">Descripción</h3>
          <p className="text-sm text-gray-600 line-clamp-4">{detail.description}</p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Create `frontend/src/pages/SearchPage.jsx`**

```jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import SearchBar from '../components/SearchBar'
import ProductList from '../components/ProductList'
import { searchProducts } from '../api/search'

export default function SearchPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [selectedForCompare, setSelectedForCompare] = useState([])

  async function handleSearch(q) {
    setLoading(true)
    setError(null)
    setSelectedForCompare([])
    try {
      const data = await searchProducts(q)
      setResults(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function toggleCompare(mlId) {
    setSelectedForCompare(prev =>
      prev.includes(mlId) ? prev.filter(id => id !== mlId) : [...prev, mlId]
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-2xl font-bold">Research de Productos</h1>
      <SearchBar onSearch={handleSearch} loading={loading} />

      {error && <p className="text-red-600">{error}</p>}

      {results && (
        <>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">
              {results.products.length} productos para "{results.keyword}"
              {!results.trend_available && (
                <span className="ml-2 bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded">
                  sin datos de tendencia
                </span>
              )}
            </p>
            {selectedForCompare.length >= 2 && (
              <button
                onClick={() => navigate('/compare', { state: { ids: selectedForCompare } })}
                className="bg-purple-600 text-white px-4 py-1.5 rounded text-sm"
              >
                Comparar {selectedForCompare.length} productos
              </button>
            )}
          </div>
          <ProductList
            products={results.products}
            onSelect={mlId => navigate(`/product/${mlId}`)}
            onCompare={toggleCompare}
            selectedForCompare={selectedForCompare}
          />
        </>
      )}
    </div>
  )
}
```

- [ ] **Step 5: Create `frontend/src/pages/DetailPage.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import ProductDetail from '../components/ProductDetail'
import { analyzeProduct } from '../api/analyze'

export default function DetailPage() {
  const { mlId } = useParams()
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    analyzeProduct(mlId)
      .then(setDetail)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [mlId])

  if (loading) return <div className="p-8 text-center text-gray-500">Analizando producto...</div>
  if (error) return <div className="p-8 text-red-600">{error}</div>
  if (!detail) return null

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <Link to="/" className="text-blue-600 text-sm">← Volver a resultados</Link>
      <ProductDetail detail={detail} />
    </div>
  )
}
```

- [ ] **Step 6: Create `frontend/src/pages/ComparePage.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { compareProducts } from '../api/compare'
import ScoreBadge from '../components/ScoreBadge'

export default function ComparePage() {
  const { state } = useLocation()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    compareProducts(state?.ids || [])
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-8 text-center text-gray-500">Comparando...</div>
  if (error) return <div className="p-8 text-red-600">{error}</div>
  if (!data) return null

  const products = data.products
  const ROWS = [
    { label: 'Precio', key: p => `$${p.price.toLocaleString('es-MX')}` },
    { label: 'Ventas/mes est.', key: p => p.estimated_monthly_sales != null ? Math.round(p.estimated_monthly_sales).toLocaleString('es-MX') : 'N/D' },
    { label: 'Demanda', key: p => p.demand_score?.toFixed(1) ?? 'N/D' },
    { label: 'Competencia', key: p => p.competition_score?.toFixed(1) ?? 'N/D' },
    { label: 'Tendencia', key: p => p.trend_score?.toFixed(1) ?? 'N/D' },
  ]

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <Link to="/" className="text-blue-600 text-sm">← Volver</Link>
      <h1 className="text-2xl font-bold">Comparativa de productos</h1>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr>
              <th className="p-3 border-b text-left w-32">Métrica</th>
              {products.map(p => (
                <th key={p.ml_id} className="p-3 border-b text-center">
                  <div className="line-clamp-2">{p.title}</div>
                  <ScoreBadge score={p.score} trendAvailable={p.trend_available} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map(row => (
              <tr key={row.label} className="hover:bg-gray-50">
                <td className="p-3 border-b font-medium">{row.label}</td>
                {products.map(p => (
                  <td key={p.ml_id} className="p-3 border-b text-center">{row.key(p)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

- [ ] **Step 7: Create `frontend/src/pages/ReportsPage.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getReports, getExportUrl } from '../api/reports'

export default function ReportsPage() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getReports().then(setReports).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-8 text-center text-gray-500">Cargando reportes...</div>

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Reportes guardados</h1>
        <Link to="/" className="text-blue-600 text-sm">← Volver</Link>
      </div>
      {reports.length === 0 && <p className="text-gray-500">No hay reportes guardados aún.</p>}
      {reports.map(r => (
        <div key={r.id} className="border rounded p-4 flex justify-between items-center">
          <div>
            <p className="font-medium">{r.name}</p>
            {r.notes && <p className="text-sm text-gray-500">{r.notes}</p>}
            <p className="text-xs text-gray-400">
              {new Date(r.created_at).toLocaleDateString('es-MX')}
            </p>
          </div>
          <div className="flex gap-2">
            <a href={getExportUrl(r.id, 'csv')}
               className="text-sm border rounded px-3 py-1 hover:bg-gray-50">
              CSV
            </a>
            <a href={getExportUrl(r.id, 'pdf')}
               className="text-sm border rounded px-3 py-1 hover:bg-gray-50">
              PDF
            </a>
          </div>
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 8: Wire up `frontend/src/App.jsx`**

```jsx
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
```

- [ ] **Step 9: Update `frontend/src/main.jsx`**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

Add Tailwind directives to `frontend/src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 10: Run frontend tests**

```bash
cd frontend && npx vitest run
```
Expected: all tests pass

- [ ] **Step 11: Commit**

```bash
git add frontend/src/
git commit -m "feat: complete frontend — search, detail, compare, reports pages"
```

---

## Task 12: Docker Compose integration + smoke test

**Files:**
- Modify: `backend/Dockerfile` (ensure alembic runs on startup)

**Goal:** `docker compose up` starts everything, `GET /search?q=auriculares` returns scores.

- [ ] **Step 1: Add startup script to backend**

Create `backend/start.sh`:
```bash
#!/bin/sh
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Update `docker-compose.yml` backend command:
```yaml
command: sh /app/start.sh
```

- [ ] **Step 2: Start the stack**

```bash
cp .env.example .env
docker compose up --build
```
Expected: all 4 services start without errors

- [ ] **Step 3: Smoke test the backend**

```bash
curl "http://localhost:8000/search?q=auriculares&limit=5"
```
Expected: JSON with `keyword`, `products` array, each product has a `score` between 1 and 10

- [ ] **Step 4: Smoke test the frontend**

Open `http://localhost:5173` in browser.
- Type "auriculares" in the search box → results appear with scores
- Click a product → detail page loads
- Check two products → "Comparar" button appears → click → comparison table shows

- [ ] **Step 5: Commit**

```bash
git add backend/start.sh docker-compose.yml
git commit -m "feat: docker compose integration with auto-migration on startup"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Search by keyword — Task 6
- ✅ Opportunity score (1-10, demand × trend / competition) — Task 3
- ✅ Product detail report — Task 7
- ✅ Niche comparison side-by-side — Task 8 + Task 11
- ✅ Save reports — Task 8
- ✅ Export CSV + PDF — Task 8
- ✅ ML API adapter with 1h Redis cache — Task 4
- ✅ Google Trends adapter with 24h cache — Task 5
- ✅ Exponential backoff on 429 — Task 4
- ✅ Graceful trend degradation — Tasks 5, 6, 7
- ✅ Products without sold_quantity included with null — Tasks 3, 6
- ✅ Docker Compose — Tasks 1, 12
- ✅ PostgreSQL + Alembic migrations — Task 2
- ✅ estimated_monthly_sales formula — Tasks 3, 6

**No placeholders found.**

**Type consistency:** `_to_detail()` defined in `analyze.py` Task 7 and reused in `compare.py` Task 8 — consistent. `ProductDetailResponse` schema defined once in Task 7 and consumed in Tasks 8 and 11. `compute_scores()` signature consistent across Tasks 3, 6, 7, 8.
