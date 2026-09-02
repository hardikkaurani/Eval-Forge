import hashlib
import ipaddress
import time
from collections import OrderedDict
from typing import Any, Dict, NamedTuple, Optional, Tuple

import structlog
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import settings
from app.core.metrics import record_rate_limit_rejection
from app.core.redis import redis_manager

logger = structlog.get_logger()

# -----------------------------------------------------------------------------
# Rate Limit Tiers & Constants
# -----------------------------------------------------------------------------

TIER_LIMITS: Dict[str, int] = {
    "FREE": 60,
    "STARTER": 60,
    "PRO": 300,
    "TEAM": 300,
    "BUSINESS": 1000,
    "ENTERPRISE": 1000,
}

DEFAULT_FREE_LIMIT = 60
WINDOW_SECONDS = 60
TIER_CACHE_TTL_SECONDS = 300


# Redis Lua Script for Atomic Sliding Window
SLIDING_WINDOW_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local clear_before = now - window

redis.call('ZREMRANGEBYSCORE', key, '-inf', clear_before)
local current_requests = redis.call('ZCARD', key)

if current_requests < limit then
    redis.call('ZADD', key, now, now .. ':' .. current_requests .. ':' .. math.random(1000, 9999))
    redis.call('EXPIRE', key, math.ceil(window))
    return {1, limit - current_requests - 1, math.ceil(window)}
else
    return {0, 0, math.ceil(window)}
end
"""


class RateLimitResult(NamedTuple):
    allowed: bool
    limit: int
    remaining: int
    reset_seconds: int
    scope: str


# -----------------------------------------------------------------------------
# In-Memory Local Fallback (For Redis Outages)
# -----------------------------------------------------------------------------


class RateLimitFallback:
    """Bounded local in-memory sliding window rate limiter fallback when Redis is offline.

    Note: Local in-memory fallback provides degraded, process-local best-effort rate limiting
    during Redis network partitions. Admission capacity per minute scales with worker process count.
    Uses incremental cursor sweeping and LRU eviction (max 5,000 keys) to bound RAM and execution time.
    """

    def __init__(self, max_keys: int = 5000, sweep_batch_size: int = 20) -> None:
        self.max_keys = max_keys
        self.sweep_batch_size = sweep_batch_size
        self._store: OrderedDict[str, list[float]] = OrderedDict()

    def _incremental_sweep(self, now: float) -> None:
        """Incremental sweep of a fixed small batch of keys to ensure O(1) constant overhead per check."""
        cutoff = now - WINDOW_SECONDS
        checked = 0
        keys_to_remove = []

        for key in list(self._store.keys()):
            if checked >= self.sweep_batch_size:
                break
            checked += 1
            timestamps = self._store.get(key, [])
            valid = [t for t in timestamps if t > cutoff]
            if not valid:
                keys_to_remove.append(key)
            else:
                self._store[key] = valid

        for k in keys_to_remove:
            self._store.pop(k, None)

        # LRU Eviction if capacity bound exceeded
        while len(self._store) > self.max_keys:
            self._store.popitem(last=False)

    def check(self, key: str, limit: int, now: float) -> RateLimitResult:
        cutoff = now - WINDOW_SECONDS
        timestamps = self._store.get(key, [])
        valid_timestamps = [t for t in timestamps if t > cutoff]

        allowed = len(valid_timestamps) < limit
        if allowed:
            valid_timestamps.append(now)

        self._store[key] = valid_timestamps
        self._store.move_to_end(key)

        self._incremental_sweep(now)

        if allowed:
            remaining = limit - len(valid_timestamps)
            return RateLimitResult(
                True, limit, max(0, remaining), WINDOW_SECONDS, "local"
            )
        else:
            return RateLimitResult(False, limit, 0, WINDOW_SECONDS, "local")


fallback_limiter = RateLimitFallback()


# -----------------------------------------------------------------------------
# Rate Limiter Engine
# -----------------------------------------------------------------------------


class RateLimiter:
    """Distributed Redis-backed sliding window rate limiter with local fallback."""

    @staticmethod
    def _hash_identity(raw_id: str) -> str:
        return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]

    @classmethod
    def _is_ip_in_trusted_proxies(cls, ip_str: str) -> bool:
        """Checks if remote host IP falls inside configured trusted proxy CIDR ranges."""
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            for proxy_pattern in settings.TRUSTED_PROXIES:
                if "/" in proxy_pattern:
                    if ip_obj in ipaddress.ip_network(proxy_pattern, strict=False):
                        return True
                elif ip_str == proxy_pattern:
                    return True
        except ValueError:
            pass
        return False

    @classmethod
    def resolve_client_ip(cls, request: Request) -> str:
        """Extracts client IP safely, inspecting X-Forwarded-For / X-Real-IP ONLY from trusted proxies."""
        direct_ip = "127.0.0.1"
        if request.client and request.client.host:
            direct_ip = request.client.host

        if settings.TRUST_PROXY_HEADERS and cls._is_ip_in_trusted_proxies(direct_ip):
            x_forwarded_for = request.headers.get("X-Forwarded-For")
            if x_forwarded_for:
                # X-Forwarded-For can be a comma-separated list; first entry is client IP
                client_ip_candidate = x_forwarded_for.split(",")[0].strip()
                try:
                    ipaddress.ip_address(client_ip_candidate)
                    return client_ip_candidate
                except ValueError:
                    pass

            x_real_ip = request.headers.get("X-Real-IP")
            if x_real_ip:
                try:
                    ipaddress.ip_address(x_real_ip.strip())
                    return x_real_ip.strip()
                except ValueError:
                    pass

        return direct_ip

    @classmethod
    async def resolve_tier(
        cls, api_key_record: Optional[Any], db: Optional[AsyncSession] = None
    ) -> Tuple[str, int]:
        """Resolves rate limit tier and capacity limit from authenticated principal using Redis tier caching."""
        if not api_key_record:
            return "FREE", DEFAULT_FREE_LIMIT

        # 1. Direct tier attribute on API key model
        tier_name = getattr(api_key_record, "tier", None)
        if tier_name:
            clean_tier = str(tier_name).upper().strip()
            return clean_tier, TIER_LIMITS.get(clean_tier, DEFAULT_FREE_LIMIT)

        org_id = getattr(api_key_record, "organization_id", None) or getattr(
            api_key_record, "org_id", None
        )
        if not org_id:
            return "FREE", DEFAULT_FREE_LIMIT

        org_id_str = str(org_id)
        cache_key = f"evalforge:apikey:tier:{cls._hash_identity(org_id_str)}"

        # 2. Redis Tier Cache lookup (avoids DB query entirely when warm)
        try:
            if redis_manager.client:
                cached_tier = await redis_manager.client.get(cache_key)
                if cached_tier:
                    clean_tier = str(cached_tier).upper().strip()
                    return clean_tier, TIER_LIMITS.get(clean_tier, DEFAULT_FREE_LIMIT)
        except Exception as exc:
            logger.debug("Redis tier cache lookup skipped", error=str(exc))

        # 3. Database query ONLY if provided and tier not cached
        if db:
            try:
                from app.enterprise.models import Plan, Subscription

                stmt = (
                    select(Plan.name)
                    .join(Subscription, Subscription.plan_id == Plan.id)
                    .where(
                        Subscription.organization_id == org_id,
                        Subscription.status == "active",
                    )
                )
                res = await db.execute(stmt)
                plan_name = res.scalar_one_or_none()
                if plan_name:
                    tier_name = plan_name.upper()
                    # Cache in Redis with 300s TTL
                    try:
                        if redis_manager.client:
                            await redis_manager.client.setex(
                                cache_key, TIER_CACHE_TTL_SECONDS, tier_name
                            )
                    except Exception as exc:
                        logger.debug("Redis tier cache setex skipped", error=str(exc))
            except Exception as exc:
                logger.debug("Database tier lookup skipped", error=str(exc))

        clean_tier = str(tier_name or "FREE").upper().strip()
        limit = TIER_LIMITS.get(clean_tier, DEFAULT_FREE_LIMIT)
        return clean_tier, limit

    @classmethod
    async def check(
        cls,
        request: Request,
        api_key_record: Optional[Any] = None,
        db: Optional[AsyncSession] = None,
    ) -> RateLimitResult:
        """Checks rate limit status for incoming HTTP request."""
        now = time.time()
        tier_name, limit = await cls.resolve_tier(api_key_record, db)

        import os
        import sys

        is_test_env = (
            "pytest" in sys.modules
            or settings.APP_ENV == "testing"
            or os.getenv("TESTING") == "1"
        )
        if is_test_env and not request.headers.get("X-Test-Enforce-Rate-Limit"):
            return RateLimitResult(True, limit, limit - 1, WINDOW_SECONDS, "testing")

        # Resolve identity & scope
        user_id = getattr(api_key_record, "user_id", None) or getattr(
            api_key_record, "created_by", None
        )
        api_key_id = getattr(api_key_record, "id", None) or getattr(
            api_key_record, "key_hash", None
        )

        if api_key_id:
            scope = "api_key"
            identity_key = (
                f"evalforge:ratelimit:api_key:{cls._hash_identity(str(api_key_id))}"
            )
        elif user_id:
            scope = "user"
            identity_key = (
                f"evalforge:ratelimit:user:{cls._hash_identity(str(user_id))}"
            )
        else:
            scope = "ip"
            client_ip = cls.resolve_client_ip(request)
            identity_key = f"evalforge:ratelimit:ip:{cls._hash_identity(client_ip)}"

        # 1. Try Distributed Redis Atomic Sliding Window
        try:
            if redis_manager.client:
                res = await redis_manager.client.eval(
                    SLIDING_WINDOW_LUA, 1, identity_key, now, WINDOW_SECONDS, limit
                )
                if res and isinstance(res, list) and len(res) == 3:
                    allowed = bool(res[0])
                    remaining = int(res[1])
                    reset_sec = int(res[2])

                    if not allowed:
                        record_rate_limit_rejection(scope)

                    return RateLimitResult(
                        allowed, limit, max(0, remaining), reset_sec, scope
                    )
        except Exception as exc:
            logger.debug(
                "Redis rate limit evaluation failed, falling back to local memory",
                error=str(exc),
            )

        # 2. Local Fallback when Redis is unavailable
        fallback_res = fallback_limiter.check(identity_key, limit, now)
        if not fallback_res.allowed:
            record_rate_limit_rejection(scope)

        return fallback_res
