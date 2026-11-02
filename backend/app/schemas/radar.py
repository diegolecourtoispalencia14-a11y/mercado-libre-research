from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class OpportunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ml_id: str
    title: str
    category_name: str
    price: float
    target_supplier_cost: float
    target_profit: float
    estimated_monthly_sales: Optional[float] = None
    score: float
    demand_score: Optional[float] = None
    competition_score: float
    permalink: str
    thumbnail_url: str
    status: str
    detected_at: datetime
    notes: Optional[str] = None


class RadarStatusResponse(BaseModel):
    is_running: bool
    last_scan_at: Optional[datetime] = None
    total_opportunities: int
    active_opportunities: int
    categories_monitored: List[str]


class UpdateOpportunityStatusRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class TriggerScanResponse(BaseModel):
    status: str
    message: str
    new_opportunities_found: int
