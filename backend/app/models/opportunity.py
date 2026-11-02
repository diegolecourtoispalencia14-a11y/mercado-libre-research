from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MarketOpportunity(Base):
    __tablename__ = "market_opportunities"

    id: Mapped[int] = mapped_column(primary_key=True)
    ml_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    category_name: Mapped[str] = mapped_column(String(100), default="General")
    price: Mapped[float] = mapped_column(Float)
    target_supplier_cost: Mapped[float] = mapped_column(Float)
    target_profit: Mapped[float] = mapped_column(Float)
    estimated_monthly_sales: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score: Mapped[float] = mapped_column(Float)
    demand_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    competition_score: Mapped[float] = mapped_column(Float)
    permalink: Mapped[str] = mapped_column(String(1000))
    thumbnail_url: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)  # active, dismissed, contacted
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
