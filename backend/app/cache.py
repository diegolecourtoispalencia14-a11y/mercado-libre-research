from __future__ import annotations

import json
import redis
from app.config import settings

_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def cache_get(key: str) -> dict | list | None:
    raw = get_redis().get(key)
    return json.loads(raw) if raw else None


def cache_set(key: str, value: dict | list, ttl_seconds: int) -> None:
    get_redis().setex(key, ttl_seconds, json.dumps(value))
