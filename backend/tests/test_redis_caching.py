import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.cache import CacheEngine, cache_response


@pytest.mark.asyncio
async def test_cache_engine_in_memory_fallback():
    engine = CacheEngine()

    # Test set and get
    await engine.set("test_prefix", "key1", {"data": "hello"}, ttl_seconds=60)
    result = await engine.get("test_prefix", "key1")
    assert result == {"data": "hello"}

    # Test invalidation
    await engine.invalidate("test_prefix", "key1")
    result_after_invalidate = await engine.get("test_prefix", "key1")
    assert result_after_invalidate is None


@pytest.mark.asyncio
async def test_cache_engine_clear_prefix():
    engine = CacheEngine()

    await engine.set("reports", "id1", {"val": 1})
    await engine.set("reports", "id2", {"val": 2})
    await engine.set("other", "id3", {"val": 3})

    await engine.clear_prefix("reports")
    assert await engine.get("reports", "id1") is None
    assert await engine.get("reports", "id2") is None
    assert await engine.get("other", "id3") == {"val": 3}


def test_cache_response_header_injection():
    app = FastAPI()

    @app.get("/test-cached")
    @cache_response(prefix="demo", ttl_seconds=100)
    async def sample_endpoint(request: Request):
        return {"status": "ok", "timestamp": "12345"}

    client = TestClient(app)

    # First request: Cache MISS
    res1 = client.get("/test-cached")
    assert res1.status_code == 200
    assert res1.headers.get("X-Cache") == "MISS"
    assert res1.json() == {"status": "ok", "timestamp": "12345"}

    # Second request: Cache HIT
    res2 = client.get("/test-cached")
    assert res2.status_code == 200
    assert res2.headers.get("X-Cache") == "HIT"
    assert res2.json() == {"status": "ok", "timestamp": "12345"}
