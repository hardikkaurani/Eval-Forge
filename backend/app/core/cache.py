import json
from functools import wraps
from typing import Any, Callable, Optional

import structlog
from fastapi import Request

from app.core.redis import redis_manager

logger = structlog.get_logger()


class CacheEngine:
    """Advanced Enterprise Caching Engine.

    Manages Redis JSON serialization, TTL settings, keyspace invalidation,
    and fallback to in-memory dictionary cache.
    """

    def __init__(self):
        self._memory_cache = {}

    def _make_key(self, prefix: str, identifier: str) -> str:
        return f"cache:{prefix}:{identifier}"

    async def get(self, prefix: str, identifier: str) -> Optional[Any]:
        key = self._make_key(prefix, identifier)
        try:
            if redis_manager.redis and redis_manager.redis.connection_pool:
                val = await redis_manager.get(key)
                if val:
                    return json.loads(val)
        except Exception as e:
            logger.warning(
                "Redis cache get failure, falling back to memory.", error=str(e)
            )

        return self._memory_cache.get(key)

    async def set(
        self, prefix: str, identifier: str, data: Any, ttl_seconds: int = 300
    ) -> None:
        key = self._make_key(prefix, identifier)
        serialized = json.dumps(data)
        try:
            if redis_manager.redis and redis_manager.redis.connection_pool:
                await redis_manager.set(key, serialized, expire=ttl_seconds)
                return
        except Exception as e:
            logger.warning(
                "Redis cache set failure, writing to memory cache.", error=str(e)
            )

        self._memory_cache[key] = data

    async def invalidate(self, prefix: str, identifier: str) -> None:
        key = self._make_key(prefix, identifier)
        try:
            if redis_manager.redis and redis_manager.redis.connection_pool:
                await redis_manager.delete(key)
                return
        except Exception as e:
            logger.warning(
                "Redis cache invalidation failure, clearing from memory cache.",
                error=str(e),
            )

        if key in self._memory_cache:
            del self._memory_cache[key]

    async def clear_prefix(self, prefix: str) -> None:
        """Invalidates all cache keys with a matching prefix."""
        local_keys = [
            k for k in self._memory_cache.keys() if k.startswith(f"cache:{prefix}:")
        ]
        for k in local_keys:
            del self._memory_cache[k]

        try:
            if redis_manager.redis and redis_manager.redis.connection_pool:
                cursor = 0
                while True:
                    cursor, keys = await redis_manager.redis.scan(
                        cursor=cursor, match=f"cache:{prefix}:*", count=100
                    )
                    if keys:
                        await redis_manager.redis.delete(*keys)
                    if cursor == 0:
                        break
        except Exception as e:
            logger.warning(
                "Redis keys scan/delete failure for prefix invalidation.", error=str(e)
            )

    async def invalidate_prefix(self, prefix: str) -> None:
        """Alias for clear_prefix."""
        await self.clear_prefix(prefix)


# Global Cache Engine Singleton
cache_engine = CacheEngine()


def cache_response(prefix: str, ttl_seconds: int = 300):
    """FastAPI Endpoint decorator to cache JSON responses by URL."""
    from fastapi.responses import JSONResponse

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to locate a FastAPI Request object in kwargs
            request: Optional[Request] = None
            for v in kwargs.values():
                if isinstance(v, Request):
                    request = v
                    break

            if not request:
                return await func(*args, **kwargs)

            # Generate cache identifier key from url query params and path
            identifier = f"{request.url.path}:{str(request.query_params)}"
            cached_val = await cache_engine.get(prefix, identifier)
            if cached_val is not None:
                logger.info("Serving response from cache", path=request.url.path)
                response = JSONResponse(content=cached_val)
                response.headers["X-Cache"] = "HIT"
                return response

            result = await func(*args, **kwargs)
            # Serialize result to JSON-compatible data if needed
            serializable_result = result
            if hasattr(result, "dict") and callable(result.dict):
                serializable_result = result.dict()
            elif isinstance(result, list):
                serializable_result = [
                    (
                        item.dict()
                        if hasattr(item, "dict") and callable(item.dict)
                        else item
                    )
                    for item in result
                ]

            await cache_engine.set(prefix, identifier, serializable_result, ttl_seconds)

            if isinstance(result, JSONResponse):
                result.headers["X-Cache"] = "MISS"
                return result
            else:
                response = JSONResponse(content=serializable_result)
                response.headers["X-Cache"] = "MISS"
                return response

        return wrapper

    return decorator
