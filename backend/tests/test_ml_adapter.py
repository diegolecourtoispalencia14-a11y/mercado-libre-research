import pytest
from unittest.mock import patch, MagicMock
from app.adapters.ml_adapter import MLAdapter

MOCK_SEARCH_RESPONSE = {
    "results": [
        {
            "id": "MLM123",
            "title": "Auriculares Bluetooth",
            "price": 299.0,
            "sold_quantity": 150,
            "seller": {"id": "seller1"},
            "category_id": "MLM1051",
            "thumbnail": "https://example.com/img.jpg",
            "date_created": "2024-01-15T00:00:00.000Z",
            "seller_address": {},
        }
    ]
}

# Brief had {"total": 42} but _get_category_seller_count reads data.get("paging", {}).get("total", 1)
# so the mock must include the "paging" wrapper to produce num_sellers == 42.
MOCK_CATEGORY_RESPONSE = {"paging": {"total": 42}}


@pytest.fixture
def adapter():
    return MLAdapter(site_id="MLM")


def test_search_returns_normalized_list(adapter):
    with patch("app.adapters.ml_adapter.cache_get", return_value=None), \
         patch("app.adapters.ml_adapter.cache_set"), \
         patch("httpx.get") as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: MOCK_SEARCH_RESPONSE, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: MOCK_CATEGORY_RESPONSE, raise_for_status=lambda: None),
        ]
        results = adapter.search("auriculares", limit=10)
    assert len(results) == 1
    assert results[0]["ml_id"] == "MLM123"
    assert results[0]["num_sellers"] == 42


def test_search_uses_cache(adapter):
    cached = [{"ml_id": "CACHED", "title": "From cache", "price": 100.0,
               "sold_quantity": 10, "seller_id": "s1", "category_id": "c1",
               "thumbnail_url": "", "listing_date": None, "num_sellers": 5}]
    with patch("app.adapters.ml_adapter.cache_get", return_value=cached):
        results = adapter.search("auriculares")
    assert results[0]["ml_id"] == "CACHED"


def test_search_retries_on_429(adapter):
    with patch("app.adapters.ml_adapter.cache_get", return_value=None), \
         patch("app.adapters.ml_adapter.cache_set"), \
         patch("app.adapters.ml_adapter.time.sleep"), \
         patch("httpx.get") as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=429, json=lambda: {}, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: MOCK_SEARCH_RESPONSE, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: MOCK_CATEGORY_RESPONSE, raise_for_status=lambda: None),
        ]
        results = adapter.search("auriculares")
    assert results[0]["ml_id"] == "MLM123"
