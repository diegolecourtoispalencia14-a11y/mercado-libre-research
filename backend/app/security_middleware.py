from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects OWASP Top 10 recommended security headers on all responses.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Server"] = "Flamante-Engine"
        return response


class RateLimiter:
    """
    Sliding window in-memory rate limiter per IP.
    """
    def __init__(self, limit_per_minute: int = 60):
        self.limit = limit_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check(self, ip: str) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - 60.0
        # Clean older entries
        self.requests[ip] = [t for t in self.requests[ip] if t > window_start]

        if len(self.requests[ip]) >= self.limit:
            retry_after = int(60 - (now - self.requests[ip][0]))
            return False, max(1, retry_after)

        self.requests[ip].append(now)
        return True, 0


class BruteForceProtector:
    """
    Brute force defense with progressive lockout after 5 failed attempts.
    """
    def __init__(self, max_attempts: int = 5, lockout_seconds: int = 60):
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        # key -> (failed_count, lockout_until)
        self.failures: Dict[str, Tuple[int, float]] = {}

    def is_locked(self, key: str) -> Tuple[bool, int]:
        now = time.time()
        if key in self.failures:
            count, lock_until = self.failures[key]
            if lock_until > now:
                remaining = int(lock_until - now)
                return True, max(1, remaining)
            elif count >= self.max_attempts and lock_until <= now:
                # Lockout expired, reset
                del self.failures[key]
        return False, 0

    def record_failure(self, key: str) -> Tuple[int, int]:
        now = time.time()
        count, lock_until = self.failures.get(key, (0, 0.0))
        count += 1
        new_lock = 0.0
        remaining_lock = 0
        if count >= self.max_attempts:
            new_lock = now + self.lockout_seconds
            remaining_lock = self.lockout_seconds
        self.failures[key] = (count, new_lock)
        return count, remaining_lock

    def reset(self, key: str):
        if key in self.failures:
            del self.failures[key]


api_rate_limiter = RateLimiter(limit_per_minute=settings.rate_limit_per_minute)
brute_force_protector = BruteForceProtector(
    max_attempts=settings.max_login_attempts,
    lockout_seconds=settings.lockout_duration_seconds
)
