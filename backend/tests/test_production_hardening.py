import os
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.secrets import SecretManager
from app.core.rbac import PermissionChecker, Role
from app.core.cache import CacheEngine
from app.core.production_security import RateLimiter


def test_secret_manager_retrieval_and_rotation():
    manager = SecretManager(provider="local")
    os.environ["MOCK_ENTERPRISE_SECRET"] = "secret123"
    
    assert manager.get_secret("MOCK_ENTERPRISE_SECRET") == "secret123"
    manager.rotate_key("MOCK_ENTERPRISE_SECRET", "rotated456")
    assert manager.get_secret("MOCK_ENTERPRISE_SECRET") == "rotated456"


def test_rbac_permission_checking():
    # Owner should be allowed everything
    checker = PermissionChecker("projects:delete")
    assert checker(user_role="owner") is True

    # Developer should not be allowed project deletions
    with pytest.raises(HTTPException) as exc:
        checker(user_role="developer")
    assert exc.value.status_code == 403

    # Viewer should be allowed project reads
    read_checker = PermissionChecker("projects:read")
    assert read_checker(user_role="viewer") is True


@pytest.mark.asyncio
async def test_cache_engine_operations():
    cache = CacheEngine()
    prefix = "test_run"
    
    # Store test payload
    payload = {"evaluation_score": 0.98}
    await cache.set(prefix, "123", payload)
    
    # Fetch and verify
    res = await cache.get(prefix, "123")
    assert res == payload

    # Invalidate and check
    await cache.invalidate(prefix, "123")
    res_after = await cache.get(prefix, "123")
    assert res_after is None


@pytest.mark.asyncio
async def test_rate_limiter_blocks():
    # Set a small rate limit of 2 requests/minute
    limiter = RateLimiter(requests_per_minute=2)
    client_key = "test_ip_127_0_0_1"

    # First request
    assert await limiter.is_allowed(client_key) is True
    # Second request
    assert await limiter.is_allowed(client_key) is True
    # Third request (blocked)
    assert await limiter.is_allowed(client_key) is False


def test_metrics_prometheus_endpoint(client: TestClient):
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "evalforge_http_requests_total" in response.text
