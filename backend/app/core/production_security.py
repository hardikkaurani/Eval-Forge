import time
import json
from typing import Dict, Any, Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.redis import redis_manager
import structlog

logger = structlog.get_logger()


class RateLimiter:
    """Enterprise Rate Limiter utilizing Redis or fallback to local dictionary."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._local_storage: Dict[str, list] = {}

    async def is_allowed(self, client_key: str) -> bool:
        now = time.time()
        window_start = now - 60.0

        try:
            if redis_manager.redis and redis_manager.redis.connection_pool:
                redis_key = f"ratelimit:{client_key}"
                # Multi-transaction script to update slide-window in Redis
                async with redis_manager.redis.pipeline(transaction=True) as pipe:
                    pipe.zremrangebyscore(redis_key, 0, window_start)
                    pipe.zcard(redis_key)
                    pipe.zadd(redis_key, {str(now): now})
                    pipe.expire(redis_key, 65)
                    res = await pipe.execute()
                    request_count = res[1]
                    return request_count < self.requests_per_minute
        except Exception as e:
            logger.warning("Redis rate limit check failed, using fallback.", error=str(e))

        # Fallback to local memory dictionary
        timestamps = self._local_storage.setdefault(client_key, [])
        # Filter timestamps outside window
        self._local_storage[client_key] = [t for t in timestamps if t > window_start]
        if len(self._local_storage[client_key]) >= self.requests_per_minute:
            return False

        self._local_storage[client_key].append(now)
        return True


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing sliding-window rate limit checks per IP or API key."""

    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Resolve client identifier key
        api_key = request.headers.get("X-API-Key")
        client_ip = request.client.host if request.client else "unknown"
        client_key = f"api:{api_key}" if api_key else f"ip:{client_ip}"

        allowed = await self.limiter.is_allowed(client_key)
        if not allowed:
            logger.warning("Rate limit exceeded", client_key=client_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        return await call_next(request)


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Middleware validating X-Idempotency-Key headers to prevent duplicate execution of mutating actions."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in ("POST", "PUT", "PATCH"):
            return await call_next(request)

        idempotency_key = request.headers.get("X-Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        redis_key = f"idempotency:{idempotency_key}"

        try:
            if redis_manager.redis and redis_manager.redis.connection_pool:
                cached_res = await redis_manager.get(redis_key)
                if cached_res:
                    data = json.loads(cached_res)
                    logger.info("Duplicate request prevented by Idempotency Key", key=idempotency_key)
                    return Response(
                        content=data.get("body", ""),
                        status_code=data.get("status_code", 200),
                        headers=data.get("headers", {})
                    )
        except Exception as e:
            logger.warning("Redis idempotency validation error.", error=str(e))

        response: Response = await call_next(request)

        # Store response details if status is success/created
        if response.status_code in (200, 201, 202, 204):
            try:
                if redis_manager.redis and redis_manager.redis.connection_pool:
                    # Capture body if possible (only for simple text/json responses)
                    body_bytes = b""
                    # Read response body chunks safely
                    async for chunk in response.body_iterator:
                        body_bytes += chunk
                    # Reconstruct body_iterator so subsequent handlers/clients can read it
                    response.body_iterator = self._recreate_iterator(body_bytes)

                    payload = {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "body": body_bytes.decode("utf-8", errors="ignore")
                    }
                    await redis_manager.set(redis_key, json.dumps(payload), expire=86400) # 24h retention
            except Exception as e:
                logger.warning("Failed to cache response payload for idempotency key.", error=str(e))

        return response

    async def _recreate_iterator(self, body_bytes: bytes):
        yield body_bytes
