from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ProductDetailResponse(BaseModel):
    ml_id: str
    title: str
    price: float
    sold_quantity: Optional[int]
    seller_id: str
    category_id: str
    thumbnail_url: str
    estimated_monthly_sales: Optional[float]
    score: float
    demand_score: Optional[float]
    competition_score: float
    trend_score: Optional[float]
    trend_available: bool
    trend_timeline: List[float]
    description: str


class CompareRequest(BaseModel):
    product_ids: List[str]


class CompareResponse(BaseModel):
    products: List[ProductDetailResponse]


class SaveReportRequest(BaseModel):
    analysis_id: int
    name: str
    notes: Optional[str] = None


class SavedReportResponse(BaseModel):
    id: int
    analysis_id: int
    name: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
