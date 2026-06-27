from datetime import datetime, timezone
import math

NEUTRAL_TREND = 50.0

def compute_estimated_monthly_sales(
    sold_quantity: int | None,
    listing_date: datetime | None,
) -> float | None:
    if sold_quantity is None or listing_date is None:
        return None
    days = (datetime.now(timezone.utc) - listing_date).days
    months = max(1, days / 30)
    return round(sold_quantity / months, 2)

def _raw_score(sold_quantity: int | None, trend_interest: float | None,
               num_sellers: int, price: float) -> float:
    demand = float(sold_quantity) if sold_quantity is not None else 1.0
    trend = float(trend_interest) if trend_interest is not None else NEUTRAL_TREND
    competition = max(1.0, float(num_sellers))
    price_comp = max(1.0, price)
    return (demand * trend) / (competition * math.log1p(price_comp))

def _min_max_normalize(values: list[float], target_min=1.0, target_max=10.0) -> list[float]:
    lo, hi = min(values), max(values)
    if lo == hi:
        return [5.0] * len(values)
    return [
        target_min + (v - lo) / (hi - lo) * (target_max - target_min)
        for v in values
    ]

def compute_scores(products: list[dict]) -> list[dict]:
    raw_scores = [
        _raw_score(
            p.get("sold_quantity"),
            p.get("trend_interest"),
            p.get("num_sellers", 1),
            p.get("price", 1.0),
        )
        for p in products
    ]
    normalized = _min_max_normalize(raw_scores)

    result = []
    for p, score in zip(products, normalized):
        enriched = dict(p)
        enriched["score"] = round(score, 2)
        sq = p.get("sold_quantity")
        enriched["demand_score"] = round(math.log1p(float(sq)) * 10 / math.log1p(10000), 2) if sq is not None else None
        enriched["competition_score"] = round(max(1.0, 10.0 - float(p.get("num_sellers", 1)) / 10), 2)
        ti = p.get("trend_interest")
        enriched["trend_score"] = round(float(ti) / 10, 2) if ti is not None else None
        result.append(enriched)
    return result
