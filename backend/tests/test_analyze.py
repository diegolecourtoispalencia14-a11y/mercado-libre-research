import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

MOCK_PRODUCT = {
    "ml_id": "MLM123", "title": "Auriculares BT", "price": 299.0,
    "sold_quantity": 500, "seller_id": "seller1", "category_id": "MLM1051",
    "thumbnail_url": "https://img.jpg", "listing_date": "2024-01-01T00:00:00+00:00",
    "num_sellers": 15, "description": "Gran producto",
}

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

def test_analyze_returns_detail(client):
    with patch("app.routers.analyze.MLAdapter") as MockML, \
         patch("app.routers.analyze.TrendsAdapter") as MockTrends:
        MockML.return_value.get_product.return_value = MOCK_PRODUCT
        MockTrends.return_value.get_interest.return_value = 70.0
        resp = client.get("/analyze/MLM123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ml_id"] == "MLM123"
    assert 1 <= data["score"] <= 10
    assert data["trend_available"] is True

def test_analyze_handles_missing_trend(client):
    with patch("app.routers.analyze.MLAdapter") as MockML, \
         patch("app.routers.analyze.TrendsAdapter") as MockTrends:
        MockML.return_value.get_product.return_value = MOCK_PRODUCT
        MockTrends.return_value.get_interest.return_value = None
        resp = client.get("/analyze/MLM123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["trend_available"] is False
    assert data["trend_score"] is None
    assert data["trend_timeline"] == []
