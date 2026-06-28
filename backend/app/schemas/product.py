from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class ProductScore(BaseModel):
    ml_id: str
    title: str
    price: float
    sold_quantity: Optional[int]
    thumbnail_url: str
    estimated_monthly_sales: Optional[float]
    score: float
    demand_score: Optional[float]
    competition_score: float
    trend_score: Optional[float]
    trend_available: bool


class SearchResponse(BaseModel):
    keyword: str
    products: list[ProductScore]
    trend_available: bool
    analysis_id: Optional[int] = None
