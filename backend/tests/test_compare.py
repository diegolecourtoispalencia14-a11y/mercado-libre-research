import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

PRODUCT_A = {
    "ml_id": "MLM1", "title": "Prod A", "price": 200.0,
    "sold_quantity": 300, "seller_id": "s1", "category_id": "c1",
    "thumbnail_url": "", "listing_date": None, "num_sellers": 5,
    "description": "",
}
PRODUCT_B = {
    "ml_id": "MLM2", "title": "Prod B", "price": 500.0,
    "sold_quantity": 30, "seller_id": "s2", "category_id": "c1",
    "thumbnail_url": "", "listing_date": None, "num_sellers": 50,
    "description": "",
}

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

def test_compare_returns_multiple_products(client):
    def get_product_side_effect(ml_id):
        return PRODUCT_A if ml_id == "MLM1" else PRODUCT_B

    with patch("app.routers.compare.MLAdapter") as MockML, \
         patch("app.routers.compare.TrendsAdapter") as MockTrends:
        MockML.return_value.get_product.side_effect = get_product_side_effect
        MockTrends.return_value.get_interest.return_value = 60.0
        resp = client.post("/compare", json={"product_ids": ["MLM1", "MLM2"]})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["products"]) == 2
    assert data["products"][0]["ml_id"] in ["MLM1", "MLM2"]
