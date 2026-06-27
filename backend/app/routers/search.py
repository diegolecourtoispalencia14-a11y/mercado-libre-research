from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter

from app.adapters.ml_adapter import MLAdapter
from app.adapters.trends_adapter import TrendsAdapter
from app.scoring.engine import compute_scores, compute_estimated_monthly_sales
from app.schemas.product import ProductScore, SearchResponse

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search(q: str, category: Optional[str] = None, limit: int = 50):
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
