from datetime import datetime, timezone, timedelta
from app.scoring.engine import compute_scores, compute_estimated_monthly_sales

def test_scores_are_normalized_1_to_10():
    products = [
        {"sold_quantity": 1000, "price": 100.0, "num_sellers": 5,  "trend_interest": 80},
        {"sold_quantity": 10,   "price": 500.0, "num_sellers": 50, "trend_interest": 20},
    ]
    result = compute_scores(products)
    for p in result:
        assert 1.0 <= p["score"] <= 10.0

def test_higher_demand_lower_competition_scores_higher():
    products = [
        {"sold_quantity": 1000, "price": 100.0, "num_sellers": 2,  "trend_interest": 90},
        {"sold_quantity": 5,    "price": 100.0, "num_sellers": 100, "trend_interest": 10},
    ]
    result = compute_scores(products)
    assert result[0]["score"] > result[1]["score"]

def test_missing_trend_uses_neutral_value():
    products = [
        {"sold_quantity": 500, "price": 200.0, "num_sellers": 10, "trend_interest": None},
    ]
    result = compute_scores(products)
    assert result[0]["trend_score"] is None
    assert 1.0 <= result[0]["score"] <= 10.0

def test_missing_sold_quantity_scores_without_demand():
    products = [
        {"sold_quantity": None, "price": 200.0, "num_sellers": 10, "trend_interest": 50},
    ]
    result = compute_scores(products)
    assert result[0]["demand_score"] is None
    assert 1.0 <= result[0]["score"] <= 10.0

def test_single_product_gets_score_5():
    products = [
        {"sold_quantity": 100, "price": 200.0, "num_sellers": 10, "trend_interest": 50},
    ]
    result = compute_scores(products)
    assert result[0]["score"] == 5.0

def test_estimated_monthly_sales_calculation():
    listing_date = datetime.now(timezone.utc) - timedelta(days=90)
    result = compute_estimated_monthly_sales(300, listing_date)
    assert abs(result - 100.0) < 5.0

def test_estimated_monthly_sales_none_when_no_quantity():
    result = compute_estimated_monthly_sales(None, datetime.now(timezone.utc))
    assert result is None

def test_estimated_monthly_sales_none_when_no_date():
    result = compute_estimated_monthly_sales(300, None)
    assert result is None

def test_leverage_scores_and_archetypes():
    from app.scoring.engine import compute_leverage_scores
    products = [
        {"sold_quantity": 5000, "price": 120.0, "num_sellers": 3, "trend_interest": 90},
        {"sold_quantity": 20, "price": 2500.0, "num_sellers": 1, "trend_interest": 40},
        {"sold_quantity": 100, "price": 500.0, "num_sellers": 40, "trend_interest": 50},
        {"sold_quantity": 110, "price": 510.0, "num_sellers": 42, "trend_interest": 50},
        {"sold_quantity": 105, "price": 495.0, "num_sellers": 39, "trend_interest": 50},
    ]
    scores, archetypes = compute_leverage_scores(products)
    assert len(scores) == 5
    assert len(archetypes) == 5
    for s in scores:
        assert 1.0 <= s <= 10.0
    # Extreme/outlier listings (high volume budget or high price) should have higher leverage
    assert scores[0] >= scores[2] or scores[1] >= scores[2]
    assert any(archetypes)

def test_detect_market_gaps():
    from app.scoring.engine import detect_market_gaps
    products = [
        {"price": 100.0, "sold_quantity": 500},
        {"price": 120.0, "sold_quantity": 400},
        {"price": 150.0, "sold_quantity": 300},
        {"price": 1500.0, "sold_quantity": 50},
        {"price": 1800.0, "sold_quantity": 40},
    ]
    gaps = detect_market_gaps(products, trend_interest=75.0)
    assert len(gaps) >= 1
    gap = gaps[0]
    assert gap["price_min"] == 150.0
    assert gap["price_max"] == 1500.0
    assert gap["midpoint_price"] == 825.0
    assert 5.0 <= gap["opportunity_score"] <= 10.0
    assert "Vacío de competencia" in gap["description"]
