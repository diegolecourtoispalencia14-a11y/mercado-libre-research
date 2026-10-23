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
    leverage_score: Optional[float] = None
    is_archetype: bool = False
    permalink: Optional[str] = None


class MarketGap(BaseModel):
    price_min: float
    price_max: float
    midpoint_price: float
    opportunity_score: float
    gap_type: str
    description: str
    recommendation: str


class SearchResponse(BaseModel):
    keyword: str
    products: list[ProductScore]
    trend_available: bool
    analysis_id: Optional[int] = None
    market_gaps: list[MarketGap] = []
    is_simulation: bool = False
