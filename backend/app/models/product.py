from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    ml_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Float)
    sold_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    seller_id: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[str] = mapped_column(String(50))
    thumbnail_url: Mapped[str] = mapped_column(String(1000))
    listing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
