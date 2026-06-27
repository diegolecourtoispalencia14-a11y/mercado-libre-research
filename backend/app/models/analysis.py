from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Float, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    score: Mapped[float] = mapped_column(Float)
    demand_score: Mapped[float] = mapped_column(Float)
    competition_score: Mapped[float] = mapped_column(Float)
    trend_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    products: Mapped[List["AnalysisProduct"]] = relationship(back_populates="analysis")
    report: Mapped[Optional["SavedReport"]] = relationship(back_populates="analysis", uselist=False)


class AnalysisProduct(Base):
    __tablename__ = "analysis_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    rank: Mapped[int] = mapped_column(Integer)
    estimated_monthly_sales: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    analysis: Mapped["Analysis"] = relationship(back_populates="products")


class SavedReport(Base):
    __tablename__ = "saved_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    analysis: Mapped["Analysis"] = relationship(back_populates="report")
