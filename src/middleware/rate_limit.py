import time
from collections import defaultdict
from typing import Callable

from fastapi import Request
from starlette.responses import JSONResponse

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60


async def rate_limiter_middleware(request: Request, call_next: Callable):
    if request.method == "OPTIONS":
        return await call_next(request)
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = RATE_LIMIT_WINDOW
    max_reqs = RATE_LIMIT_REQUESTS
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
    return await call_next(request)
