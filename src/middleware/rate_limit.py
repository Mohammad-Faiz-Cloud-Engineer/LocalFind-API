import time
from collections import defaultdict
from typing import Callable

from fastapi import Request
from starlette.responses import JSONResponse

from src.config import settings

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_last_cleanup: float = 0.0
_CLEANUP_INTERVAL: float = 300.0  # purge stale IPs every 5 minutes


async def rate_limiter_middleware(request: Request, call_next: Callable):
    global _last_cleanup
    if request.method == "OPTIONS":
        return await call_next(request)
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = settings.rate_limit_window
    max_reqs = settings.rate_limit_requests
    if "/api/v1/contact" in request.url.path:
        max_reqs = 5
        window = 3600
    timestamps = _rate_limit_store[client_ip]
    timestamps[:] = [t for t in timestamps if now - t < window]
    if len(timestamps) >= max_reqs:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": f"Too many requests. Limit: {max_reqs} per {window}s",
            },
        )
    timestamps.append(now)
    # Periodic cleanup of stale IPs to prevent unbounded memory growth
    if now - _last_cleanup > _CLEANUP_INTERVAL:
        _last_cleanup = now
        stale_ips = [ip for ip, ts in _rate_limit_store.items() if not ts or now - ts[-1] > window]
        for ip in stale_ips:
            del _rate_limit_store[ip]
    return await call_next(request)
