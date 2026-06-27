from __future__ import annotations

from datetime import datetime
from typing import Optional
from fastapi import APIRouter

from app.adapters.ml_adapter import MLAdapter
from app.adapters.trends_adapter import TrendsAdapter
from app.scoring.engine import compute_scores, compute_estimated_monthly_sales
from app.schemas.analysis import ProductDetailResponse

router = APIRouter()


def _to_detail(
    p: dict,
    scored: dict,
    trend_interest: Optional[float],
    trend_available: bool,
) -> ProductDetailResponse:
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
