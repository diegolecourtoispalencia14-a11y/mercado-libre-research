from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.adapters.ml_adapter import MLAdapter
from app.adapters.trends_adapter import TrendsAdapter
from app.scoring.engine import compute_scores
from app.schemas.analysis import CompareRequest, CompareResponse, ProductDetailResponse
from app.routers.analyze import _to_detail

router = APIRouter()


@router.post("/compare", response_model=CompareResponse)
def compare(body: CompareRequest):
    if not body.product_ids:
        raise HTTPException(status_code=400, detail="product_ids must not be empty")
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
