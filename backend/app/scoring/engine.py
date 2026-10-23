from __future__ import annotations

from datetime import datetime, timezone
import math
import numpy as np

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
    if not values:
        return []
    lo, hi = min(values), max(values)
    if lo == hi:
        return [5.0] * len(values)
    return [
        target_min + (v - lo) / (hi - lo) * (target_max - target_min)
        for v in values
    ]

def compute_leverage_scores(products: list[dict]) -> tuple[list[float], list[bool]]:
    """
    Computes statistical leverage scores (h_i = sum(U_ij^2)) for each listing
    using Singular Value Decomposition (SVD) on the standardized feature matrix.
    
    Inspired by geometric data valuation (R. Mendoza-Smith, NeurIPS 2025).
    Identifies archetype competitors defining market boundaries while filtering
    redundant copycat listings.
    """
    n = len(products)
    if n == 0:
        return [], []
    if n < 3:
        return [5.0] * n, [True] * n

    rows = []
    for p in products:
        price = max(1.0, float(p.get("price") or 1.0))
        sold = float(p.get("sold_quantity") or 0.0)
        sellers = max(1.0, float(p.get("num_sellers") or 1.0))
        trend = float(p.get("trend_interest") if p.get("trend_interest") is not None else NEUTRAL_TREND)
        rows.append([
            math.log1p(price),
            math.log1p(sold),
            math.log1p(sellers),
            trend / 100.0,
        ])

    X = np.array(rows, dtype=float)
    # Center the matrix
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    std[std == 0] = 1.0
    X_norm = (X - mean) / std

    try:
        U, s, _ = np.linalg.svd(X_norm, full_matrices=False)
        # Principal subspace leverage: use top-k components to measure influence in dominant market dimensions
        k = min(2, U.shape[1])
        h = np.sum(U[:, :k]**2, axis=1)
    except Exception:
        h = np.ones(n) / n

    h_min, h_max = float(np.min(h)), float(np.max(h))
    if h_max > h_min:
        scaled_h = [round(float(1.0 + 9.0 * (val - h_min) / (h_max - h_min)), 2) for val in h]
    else:
        scaled_h = [5.0] * n

    # Threshold for archetypes: upper quartile or above twice the mean leverage
    mean_leverage = float(np.mean(h))
    threshold = max(float(np.percentile(h, 75)), 1.5 * mean_leverage) if n >= 4 else mean_leverage
    is_archetype = [bool(val >= threshold) for val in h]

    return scaled_h, is_archetype

def detect_market_gaps(products: list[dict], trend_interest: float | None = None) -> list[dict]:
    """
    Detects market gaps ('Océanos Azules') across the price distribution.
    Identifies price ranges with significant gaps where competition density is low
    while underlying market demand is supported.
    """
    valid_products = [p for p in products if p.get("price") and float(p.get("price")) > 0]
    if len(valid_products) < 4:
        return []

    sorted_prods = sorted(valid_products, key=lambda p: float(p["price"]))
    prices = [float(p["price"]) for p in sorted_prods]

    min_p, max_p = prices[0], prices[-1]
    if max_p <= min_p:
        return []

    spread = max_p - min_p
    avg_step = spread / max(1, len(prices) - 1)
    trend_factor = (float(trend_interest) / 50.0) if trend_interest is not None else 1.0

    gaps = []
    # Identify price leaps using persistent homology (TDA) concept: distance exceeds local density
    for i in range(len(prices) - 1):
        p_low = prices[i]
        p_high = prices[i + 1]

        diff = p_high - p_low
        ratio = p_high / max(1.0, p_low)

        # Meaningful topological gap condition:
        # Distance between consecutive listings is at least double average density step,
        # or price jumps by 20%+, or gap spans at least 6% of entire market spread
        is_gap = (
            (diff >= 2.0 * avg_step and diff >= 10.0)
            or (ratio >= 1.20 and diff >= 8.0)
            or (diff >= spread * 0.06 and diff >= 10.0)
        )

        if is_gap:
            mid = round((p_low + p_high) / 2.0, 2)
            rel_diff = diff / max(1.0, avg_step)
            opp_score = min(10.0, round(float(math.log1p(rel_diff) * 3.2 * trend_factor + 4.0), 1))
            opp_score = max(5.0, min(9.9, opp_score))

            if p_low < (min_p + spread * 0.35):
                gap_type = "Gama Entrada / Media Accesible"
            elif p_high > (min_p + spread * 0.70):
                gap_type = "Gama Alta / Premium Desatendida"
            else:
                gap_type = "Gama Media Estratégica"

            gaps.append({
                "price_min": round(p_low, 2),
                "price_max": round(p_high, 2),
                "midpoint_price": mid,
                "opportunity_score": opp_score,
                "gap_type": gap_type,
                "description": f"Vacío de competencia entre ${p_low:,.0f} y ${p_high:,.0f} MXN (salto de ${diff:,.0f} MXN sin oferentes).",
                "recommendation": f"Oportunidad de posicionar oferta diferenciada alrededor de ${mid:,.0f} MXN con baja fricción.",
            })

    gaps.sort(key=lambda g: (g["price_max"] - g["price_min"]), reverse=True)
    return gaps[:3]

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
    lev_scores, archetypes = compute_leverage_scores(products)

    result = []
    for p, score, lev, is_arch in zip(products, normalized, lev_scores, archetypes):
        enriched = dict(p)
        enriched["score"] = round(score, 2)
        sq = p.get("sold_quantity")
        enriched["demand_score"] = round(math.log1p(float(sq)) * 10 / math.log1p(10000), 2) if sq is not None else None
        enriched["competition_score"] = round(max(1.0, 10.0 - float(p.get("num_sellers", 1)) / 10), 2)
        ti = p.get("trend_interest")
        enriched["trend_score"] = round(float(ti) / 10, 2) if ti is not None else None
        enriched["leverage_score"] = lev
        enriched["is_archetype"] = is_arch
        result.append(enriched)
    return result
