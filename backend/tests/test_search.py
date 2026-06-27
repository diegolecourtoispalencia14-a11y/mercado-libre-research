import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

ML_PRODUCTS = [
    {"ml_id": "MLM1", "title": "Auriculares BT", "price": 299.0,
     "sold_quantity": 500, "seller_id": "s1", "category_id": "c1",
     "thumbnail_url": "https://img.jpg", "listing_date": "2024-01-01T00:00:00+00:00",
     "num_sellers": 10},
    {"ml_id": "MLM2", "title": "Auriculares Pro", "price": 599.0,
     "sold_quantity": 50, "seller_id": "s2", "category_id": "c1",
     "thumbnail_url": "https://img2.jpg", "listing_date": "2024-03-01T00:00:00+00:00",
     "num_sellers": 10},
]


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_search_returns_scored_products(client):
    with patch("app.routers.search.MLAdapter") as MockML, \
         patch("app.routers.search.TrendsAdapter") as MockTrends:
        MockML.return_value.search.return_value = ML_PRODUCTS
        MockTrends.return_value.get_interest.return_value = 65.0
        resp = client.get("/search?q=auriculares&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["keyword"] == "auriculares"
    assert len(data["products"]) == 2
    assert all(1 <= p["score"] <= 10 for p in data["products"])
    assert data["trend_available"] is True


def test_search_without_trend(client):
    with patch("app.routers.search.MLAdapter") as MockML, \
         patch("app.routers.search.TrendsAdapter") as MockTrends:
        MockML.return_value.search.return_value = ML_PRODUCTS
        MockTrends.return_value.get_interest.return_value = None
        resp = client.get("/search?q=auriculares")
    assert resp.status_code == 200
    data = resp.json()
    assert data["trend_available"] is False
    assert all(p["trend_score"] is None for p in data["products"])
