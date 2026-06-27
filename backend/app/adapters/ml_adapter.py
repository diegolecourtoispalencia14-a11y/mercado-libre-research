from __future__ import annotations

import time
import httpx
from datetime import datetime, timezone
from app.adapters.base import BaseAdapter
from app.cache import cache_get, cache_set

ML_BASE = "https://api.mercadolibre.com"
CACHE_TTL = 3600  # 1 hour


def _parse_listing_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def _get_with_retry(url: str, params: dict | None = None, max_retries: int = 3) -> dict:
    delay = 1.0
    for attempt in range(max_retries):
        resp = httpx.get(url, params=params, timeout=10)
        if resp.status_code == 429:
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"ML API rate limit exceeded after {max_retries} retries")


class MLAdapter(BaseAdapter):
    def __init__(self, site_id: str = "MLM"):
        self.site_id = site_id

    def search(self, keyword: str, limit: int = 50) -> list[dict]:
        cache_key = f"ml:search:{self.site_id}:{keyword}:{limit}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        data = _get_with_retry(
            f"{ML_BASE}/sites/{self.site_id}/search",
            params={"q": keyword, "limit": limit},
        )

        results = []
        for item in data.get("results", []):
            category_id = item.get("category_id", "")
            num_sellers = self._get_category_seller_count(category_id)
            results.append({
                "ml_id": item["id"],
                "title": item["title"],
                "price": float(item.get("price", 0)),
                "sold_quantity": item.get("sold_quantity"),
                "seller_id": str(item.get("seller", {}).get("id", "")),
                "category_id": category_id,
                "thumbnail_url": item.get("thumbnail", ""),
                "listing_date": item.get("date_created"),
                "num_sellers": num_sellers,
            })

        cache_set(cache_key, results, CACHE_TTL)
        return results

    def get_product(self, ml_id: str) -> dict:
        cache_key = f"ml:product:{ml_id}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        item = _get_with_retry(f"{ML_BASE}/items/{ml_id}")
        category_id = item.get("category_id", "")
        num_sellers = self._get_category_seller_count(category_id)

        result = {
            "ml_id": item["id"],
            "title": item["title"],
            "price": float(item.get("price", 0)),
            "sold_quantity": item.get("sold_quantity"),
            "seller_id": str(item.get("seller_id", "")),
            "category_id": category_id,
            "thumbnail_url": item.get("thumbnail", ""),
            "listing_date": item.get("date_created"),
            "num_sellers": num_sellers,
            "description": item.get("plain_text", ""),
        }

        cache_set(cache_key, result, CACHE_TTL)
        return result

    def _get_category_seller_count(self, category_id: str) -> int:
        if not category_id:
            return 1
        try:
            data = _get_with_retry(
                f"{ML_BASE}/sites/{self.site_id}/search",
                params={"category": category_id, "limit": 1},
            )
            return data.get("paging", {}).get("total", 1)
        except Exception:
            return 1
