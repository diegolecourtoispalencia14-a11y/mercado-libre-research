from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.adapters.ml_adapter import MLAdapter
from app.adapters.trends_adapter import TrendsAdapter
from app.database import get_db
from app.models.analysis import Analysis, AnalysisProduct
from app.models.product import Product as ProductModel
from app.scoring.engine import compute_scores, compute_estimated_monthly_sales
from app.schemas.product import ProductScore, SearchResponse

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search(q: str, category: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    ml = MLAdapter()
    trends = TrendsAdapter()

    raw_products = ml.search(q, limit=limit)
    trend_interest = trends.get_interest(q)
    trend_available = trend_interest is not None

    for p in raw_products:
        p["trend_interest"] = trend_interest

    scored = compute_scores(raw_products)

    # Persist analysis and products to DB
    analysis = Analysis(
        keyword=q,
        score=round(sum(p["score"] for p in scored) / len(scored), 2) if scored else 0,
        demand_score=round(sum(p["demand_score"] or 0 for p in scored) / len(scored), 2) if scored else 0,
        competition_score=round(sum(p["competition_score"] for p in scored) / len(scored), 2) if scored else 0,
        trend_score=round(float(trend_interest), 2) if trend_interest is not None else None,
        created_at=datetime.now(timezone.utc),
    )
    db.add(analysis)
    db.flush()  # get analysis.id

    for rank, p in enumerate(scored, start=1):
        # upsert product cache
        existing = db.query(ProductModel).filter(ProductModel.ml_id == p["ml_id"]).first()
        if not existing:
            prod = ProductModel(
                ml_id=p["ml_id"],
                title=p["title"],
                price=p["price"],
                sold_quantity=p.get("sold_quantity"),
                seller_id=p.get("seller_id", ""),
                category_id=p.get("category_id", ""),
                thumbnail_url=p.get("thumbnail_url", ""),
                fetched_at=datetime.now(timezone.utc),
            )
            db.add(prod)
            db.flush()
            product_db_id = prod.id
        else:
            product_db_id = existing.id

        listing_dt = None
        listing_date_str = p.get("listing_date")
        if listing_date_str:
            try:
                listing_dt = datetime.fromisoformat(listing_date_str.replace("Z", "+00:00"))
            except ValueError:
                pass

        ap = AnalysisProduct(
            analysis_id=analysis.id,
            product_id=product_db_id,
            rank=rank,
            estimated_monthly_sales=compute_estimated_monthly_sales(p.get("sold_quantity"), listing_dt),
        )
        db.add(ap)

    db.commit()

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

    return SearchResponse(keyword=q, products=products, trend_available=trend_available, analysis_id=analysis.id)
