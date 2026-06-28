from __future__ import annotations

from pytrends.request import TrendReq
from app.cache import cache_get, cache_set

CACHE_TTL = 86400  # 24 hours


class TrendsAdapter:
    def get_interest(self, keyword: str) -> float | None:
        cache_key = f"trends:{keyword}"
        cached = cache_get(cache_key)
        if cached is not None:
            return float(cached)

        try:
            pytrends = TrendReq(hl="es-MX", tz=360)
            pytrends.build_payload([keyword], timeframe="today 12-m", geo="MX")
            df = pytrends.interest_over_time()

            if df.empty or keyword not in df.columns:
                return None

            avg = float(df[keyword].mean())
            cache_set(cache_key, avg, CACHE_TTL)
            return avg
        except Exception:
            return None

    def get_timeline(self, keyword: str) -> list:
        cache_key = f"trends_timeline:{keyword}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        try:
            pytrends = TrendReq(hl="es-MX", tz=360)
            pytrends.build_payload([keyword], timeframe="today 12-m", geo="MX")
            df = pytrends.interest_over_time()

            if df.empty or keyword not in df.columns:
                return []

            timeline = [float(v) for v in df[keyword].tolist()]
            cache_set(cache_key, timeline, CACHE_TTL)
            return timeline
        except Exception:
            return []
