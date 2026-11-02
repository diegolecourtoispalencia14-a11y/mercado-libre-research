from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session

from app.adapters.ml_adapter import MLAdapter
from app.adapters.trends_adapter import TrendsAdapter
from app.database import SessionLocal
from app.models.opportunity import MarketOpportunity
from app.scoring.engine import (
    compute_scores,
    compute_estimated_monthly_sales,
    detect_market_gaps,
)
from app.scoring.economics import compute_reverse_unit_economics

logger = logging.getLogger(__name__)

# Strategic Seed Niches (Curated for Mexican e-commerce volume and high margin voids)
SEED_CATEGORIES = [
    "Repisas y Soportes de Pared",
    "Herramientas de Precisión",
    "Soporte Celular para Moto",
    "Accesorios de Ciclismo",
    "Mochilas y Equipaje Táctico",
    "Iluminación LED Solar",
    "Hamacas y Muebles de Descanso",
    "Organizadores para Cocina",
]


class OpportunityScannerService:
    def __init__(self):
        self.is_scanning: bool = False
        self.last_scan_at: datetime | None = None
        self.categories: List[str] = SEED_CATEGORIES

    def run_scan(self, min_score: float = 6.8, target_margin_pct: float = 0.30) -> int:
        """
        Runs a deep scan across monitored categories.
        Filters products strictly with Score >= min_score and viable reverse unit economics.
        Upserts high-yield opportunities into database.
        """
        if self.is_scanning:
            logger.info("Scan already in progress, skipping duplicate invocation.")
            return 0

        self.is_scanning = True
        new_or_updated = 0
        db: Session = SessionLocal()

        try:
            ml = MLAdapter()
            trends = TrendsAdapter()

            for category_keyword in self.categories:
                try:
                    raw_products = ml.search(category_keyword, limit=20)
                    if not raw_products:
                        continue

                    trend_interest = trends.get_interest(category_keyword.split()[0])
                    for p in raw_products:
                        p["trend_interest"] = trend_interest

                    scored_products = compute_scores(raw_products)
                    raw_gaps = detect_market_gaps(raw_products, trend_interest)

                    for p in scored_products:
                        score = p.get("score", 0.0)
                        sold_qty = p.get("sold_quantity") or 0
                        is_archetype = p.get("is_archetype", False)
                        lev_score = p.get("leverage_score")

                        # Strict criteria: Score >= min_score OR key archetype with solid score
                        if score >= min_score or (is_archetype and score >= 6.0):
                            price = float(p.get("price") or 0)
                            if price < 50:
                                continue

                            # Find matching market gap if any
                            matching_gap = None
                            for g in raw_gaps:
                                if g["price_min"] <= price <= g["price_max"]:
                                    matching_gap = g["gap_type"]
                                    break

                            econ = compute_reverse_unit_economics(
                                retail_price=price,
                                desired_margin_pct=target_margin_pct,
                            )

                            listing_dt = None
                            if p.get("listing_date"):
                                try:
                                    listing_dt = datetime.fromisoformat(
                                        p["listing_date"].replace("Z", "+00:00")
                                    )
                                except Exception:
                                    pass

                            est_sales = compute_estimated_monthly_sales(sold_qty, listing_dt)

                            # Upsert into market_opportunities
                            existing = (
                                db.query(MarketOpportunity)
                                .filter(MarketOpportunity.ml_id == p["ml_id"])
                                .first()
                            )

                            if existing:
                                existing.price = price
                                existing.target_supplier_cost = econ["max_supplier_cost"]
                                existing.target_profit = econ["target_profit"]
                                existing.score = score
                                existing.demand_score = p.get("demand_score")
                                existing.competition_score = p.get("competition_score", 0)
                                existing.estimated_monthly_sales = est_sales
                                existing.is_archetype = is_archetype
                                existing.leverage_score = lev_score
                                existing.gap_type = matching_gap
                                existing.detected_at = datetime.now(timezone.utc)
                                new_or_updated += 1
                            else:
                                opp = MarketOpportunity(
                                    ml_id=p["ml_id"],
                                    title=p["title"],
                                    category_name=category_keyword,
                                    price=price,
                                    target_supplier_cost=econ["max_supplier_cost"],
                                    target_profit=econ["target_profit"],
                                    estimated_monthly_sales=est_sales,
                                    score=score,
                                    demand_score=p.get("demand_score"),
                                    competition_score=p.get("competition_score", 0),
                                    is_archetype=is_archetype,
                                    leverage_score=lev_score,
                                    gap_type=matching_gap,
                                    permalink=p.get("permalink") or f"https://listado.mercadolibre.com.mx/{p['title']}",
                                    thumbnail_url=p.get("thumbnail_url", ""),
                                    status="active",
                                    detected_at=datetime.now(timezone.utc),
                                )
                                db.add(opp)
                                new_or_updated += 1

                    db.commit()
                except Exception as exc:
                    logger.error(f"Error scanning category '{category_keyword}': {exc}")
                    db.rollback()

            self.last_scan_at = datetime.now(timezone.utc)
            return new_or_updated
        finally:
            self.is_scanning = False
            db.close()


scanner_service = OpportunityScannerService()
