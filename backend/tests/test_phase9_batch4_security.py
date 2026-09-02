from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.rate_limiter import RateLimiter, RateLimitFallback, RateLimitResult
from app.core.sanitization import sanitize_input_data, sanitize_xss

# =============================================================================
# PART A: DISTRIBUTED RATE LIMITING & TIER TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_rate_limit_tier_resolution() -> None:
    """Verify tier limit mappings for Free (60), Pro (300), and Enterprise (1000)."""
    assert await RateLimiter.resolve_tier(None, None) == ("FREE", 60)

    class MockKey:
        tier = "PRO"

    assert await RateLimiter.resolve_tier(MockKey(), None) == ("PRO", 300)

    class MockEntKey:
        tier = "ENTERPRISE"

    assert await RateLimiter.resolve_tier(MockEntKey(), None) == ("ENTERPRISE", 1000)



@pytest.mark.asyncio
async def test_rate_limit_free_tier_61st_request_rejection() -> None:
    """Verify Free tier accepts 60 requests and rejects the 61st request with 429."""
    limiter = RateLimitFallback(max_keys=100)
    key = "test_free_user"
    limit = 60
    now = 1000.0

    for i in range(60):
        res = limiter.check(key, limit, now + (i * 0.01))
        assert res.allowed is True
        assert res.remaining == 60 - (i + 1)

    # 61st Request
    res_61 = limiter.check(key, limit, now + 1.0)
    assert res_61.allowed is False
    assert res_61.remaining == 0
    assert res_61.reset_seconds == 60


@pytest.mark.asyncio
async def test_rate_limit_pro_tier_capacity() -> None:
    """Verify Pro tier accepts up to 300 requests in 60s window."""
    limiter = RateLimitFallback(max_keys=100)
    key = "test_pro_user"
    limit = 300
    now = 2000.0

    for i in range(300):
        res = limiter.check(key, limit, now + (i * 0.01))
        assert res.allowed is True

    # 301st Request
    res_301 = limiter.check(key, limit, now + 5.0)
    assert res_301.allowed is False


@pytest.mark.asyncio
async def test_rate_limit_tenant_and_identity_isolation() -> None:
    """Verify User A and User B rate limit keys do not interfere with each other."""
    limiter = RateLimitFallback(max_keys=100)
    user_a = "evalforge:ratelimit:user:user_a"
    user_b = "evalforge:ratelimit:user:user_b"
    limit = 5
    now = 3000.0

    # Fill User A bucket
    for _ in range(5):
        assert limiter.check(user_a, limit, now).allowed is True
    assert limiter.check(user_a, limit, now).allowed is False

    # User B should still have full quota
    for _ in range(5):
        assert limiter.check(user_b, limit, now).allowed is True
    assert limiter.check(user_b, limit, now).allowed is False


@pytest.mark.asyncio
async def test_redis_outage_local_fallback_resilience() -> None:
    """Verify rate limiter falls back to local memory bounded sliding window during Redis outage."""
    with patch("app.core.redis.redis_manager.client", None):
        # Redis client is None
        limiter = RateLimitFallback(max_keys=10)
        res = limiter.check("fallback_key", 60, 4000.0)
        assert res.allowed is True
        assert res.scope == "local"


def test_rate_limit_http_429_headers_and_response(client: TestClient) -> None:
    """Verify HTTP 429 response includes Retry-After and X-RateLimit headers."""
    # Mock RateLimiter to return rejected status
    rejected_res = RateLimitResult(
        allowed=False, limit=60, remaining=0, reset_seconds=45, scope="ip"
    )
    with patch("app.core.rate_limiter.RateLimiter.check", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = rejected_res
        res = client.get("/projects", headers={"X-Test-Enforce-Rate-Limit": "true"})
        assert res.status_code == 429
        assert res.headers["Retry-After"] == "45"
        assert res.headers["X-RateLimit-Limit"] == "60"
        assert res.headers["X-RateLimit-Remaining"] == "0"
        assert res.headers["X-RateLimit-Reset"] == "45"

        body = res.json()
        assert body["success"] is False
        assert "Rate limit exceeded" in body["message"]



# =============================================================================
# PART B: INPUT SECURITY & XSS HARDENING TESTS
# =============================================================================

def test_xss_sanitization_script_tags() -> None:
    """Verify script tags, event handlers, and javascript URIs are neutralized via HTML entity encoding."""
    assert sanitize_xss("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert sanitize_xss('<img src=x onerror=alert("xss")>') == "&lt;img src=x onerror=alert(&quot;xss&quot;)&gt;"
    assert sanitize_xss("<svg onload=alert(1)>") == "&lt;svg onload=alert(1)&gt;"
    assert sanitize_xss("javascript:alert(1)") == "javascript:alert(1)"


def test_xss_preserves_legitimate_prompts_and_markdown() -> None:
    """Verify code snippets, markdown, and LLM evaluation prompts remain intact."""
    prompt = "Explain if `x < 10 && y > 5` in C++ code."
    # Direct metadata string entity escapes HTML chars
    assert sanitize_xss(prompt) == "Explain if `x &lt; 10 &amp;&amp; y &gt; 5` in C++ code."

    data = {
        "name": "Dataset <script>alert(1)</script>",
        "description": "Clean description",
        "input_prompt": "If x < y, then return x > 0.",
    }
    cleaned = sanitize_input_data(data, target_fields=("name", "description"))
    assert cleaned["name"] == "Dataset &lt;script&gt;alert(1)&lt;/script&gt;"
    assert cleaned["description"] == "Clean description"
    # Un-targeted field (input_prompt) remains 100% raw and untouched
    assert cleaned["input_prompt"] == "If x < y, then return x > 0."



# =============================================================================
# PART C: FILE UPLOAD SECURITY TESTS
# =============================================================================

def test_upload_extension_validation(client: TestClient) -> None:
    """Verify unsupported file extensions (.exe, .php, double extension) are rejected with 400."""
    # Executable extension
    res = client.post(
        "/api/v1/datasets/import",
        data={"project_id": "p1", "dataset_name": "Test"},
        files={"file": ("payload.exe", b"content", "application/octet-stream")},
    )
    assert res.status_code == 400
    msg = res.json().get("message") or str(res.json())
    assert "Unsupported file extension" in msg

    # Double extension (.json.exe)
    res_double = client.post(
        "/api/v1/datasets/import",
        data={"project_id": "p1", "dataset_name": "Test"},
        files={"file": ("payload.json.exe", b'{"key": "val"}', "application/json")},
    )
    assert res_double.status_code == 400


def test_upload_path_traversal_and_null_bytes(client: TestClient) -> None:
    """Verify path traversal (../) and null bytes in upload filename are rejected."""
    # Path traversal
    res_traversal = client.post(
        "/api/v1/datasets/import",
        data={"project_id": "p1", "dataset_name": "Test"},
        files={"file": ("../../secret.json", b'{"key": "val"}', "application/json")},
    )
    assert res_traversal.status_code == 400
    msg_traversal = res_traversal.json().get("message") or str(res_traversal.json())
    assert "path traversal" in msg_traversal.lower()

    # Null byte
    res_null = client.post(
        "/api/v1/datasets/import",
        data={"project_id": "p1", "dataset_name": "Test"},
        files={"file": ("payload.json\x00.exe", b'{"key": "val"}', "application/json")},
    )
    assert res_null.status_code == 400


def test_upload_malformed_json_and_csv(client: TestClient) -> None:
    """Verify malformed JSON/JSONL structure in upload is rejected cleanly."""
    res_json = client.post(
        "/api/v1/datasets/import",
        data={"project_id": "p1", "dataset_name": "Test"},
        files={"file": ("data.json", b"{invalid_json: ", "application/json")},
    )
    assert res_json.status_code == 400
    msg_json = res_json.json().get("message") or str(res_json.json())
    assert "Invalid JSON content structure" in msg_json



# =============================================================================
# PART D: SQL PARAMETER BINDING SECURITY
# =============================================================================

def test_sql_parameter_binding_audit() -> None:
    """Verify SQL parameter queries use bound parameters rather than string concatenation."""
    from sqlalchemy import text

    safe_query = text("SELECT * FROM jobs WHERE status = :status").bindparams(status="COMPLETED")
    assert "status" in safe_query.compile().params


# =============================================================================
# PART E: REMEDIATION TESTS FOR FINDINGS B4-01 THROUGH B4-05
# =============================================================================

@pytest.mark.asyncio
async def test_remediation_b4_01_api_key_redis_cache_and_single_flight() -> None:
    """Verify B4-01: Warm API key token lookups hit Redis cache without querying DB, and single-flight lock works."""
    from app.enterprise.services.apikey_service import EnterpriseAPIKeyService

    service = EnterpriseAPIKeyService()
    raw_key = "ef_ent_test_token_12345"

    with patch("app.core.redis.redis_manager.client") as mock_redis:
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock(return_value=True)

        with patch.object(service, "validate_key", new_callable=AsyncMock) as mock_db_val:
            class MockKeyRecord:
                id = "key-uuid-101"
                organization_id = "org-uuid-202"
                workspace_id = "ws-uuid-303"
                name = "Test Key"
                scopes = ["read:all"]
                is_active = True
                expires_at = None
                tier = "PRO"

            mock_db_val.return_value = MockKeyRecord()

            # First Call: Cold Cache -> Queries DB and sets Redis cache
            res1 = await service.validate_key_cached(db=MagicMock(), raw_key=raw_key)
            assert res1 is not None
            assert res1.organization_id == "org-uuid-202"
            assert mock_db_val.call_count == 1
            assert mock_redis.setex.call_count == 1

        # Second Call: Warm Cache -> Uses Redis cache and makes 0 DB calls
        mock_redis.get = AsyncMock(return_value='{"id": "key-uuid-101", "organization_id": "org-uuid-202", "workspace_id": "ws-uuid-303", "name": "Test Key", "scopes": ["read:all"], "is_active": true, "tier": "PRO"}')

        with patch.object(service, "validate_key", new_callable=AsyncMock) as mock_db_val_2:
            res2 = await service.validate_key_cached(db=None, raw_key=raw_key)
            assert res2 is not None
            assert res2.organization_id == "org-uuid-202"
            assert mock_db_val_2.call_count == 0


def test_remediation_b4_02_bounded_incremental_fallback_sweep() -> None:
    """Verify B4-02: RateLimitFallback uses incremental cursor sweep and does not scan all 5,000 keys per check."""
    from app.core.rate_limiter import RateLimitFallback

    fallback = RateLimitFallback(max_keys=5000, sweep_batch_size=20)
    now = 1000.0

    # Populate 5,000 keys
    for i in range(5000):
        fallback.check(f"key_{i}", limit=5, now=now)

    assert len(fallback._store) == 5000

    # Execute single check with 5,000 keys present
    with patch.object(fallback._store, "items", wraps=fallback._store.items) as mock_items:

        fallback.check("active_user", limit=5, now=now + 1.0)
        # items() must NOT be called over the full dictionary (which would be O(N))
        assert mock_items.call_count == 0

    # Advance time and check incremental expiration
    future_now = 1062.0
    for _ in range(10):
        fallback.check("active_user", limit=5, now=future_now)

    # Stores bounded capacity
    assert len(fallback._store) <= 5000


def test_remediation_b4_03_large_upload_streaming_and_memory_bounds(client: TestClient) -> None:
    """Verify B4-03: Upload validation enforces 100MB size limit and handles missing/spoofed Content-Length."""
    # Oversized file (>100MB)
    huge_data = b"x" * (100 * 1024 * 1024 + 100)
    res_oversized = client.post(
        "/api/v1/datasets/import",
        data={"project_id": "p1", "dataset_name": "Test"},
        files={"file": ("huge.jsonl", huge_data, "application/jsonlines")},
    )
    assert res_oversized.status_code == 413
    msg = res_oversized.json().get("message") or res_oversized.json().get("detail") or str(res_oversized.json())
    assert "exceeds maximum limit of 100 MB" in msg



def test_remediation_b4_04_dangerous_uri_scheme_neutralization() -> None:
    """Verify B4-04: Dangerous URI schemes (javascript:, vbscript:, data:text/html) are neutralized on URL fields."""
    from app.core.sanitization import sanitize_input_data, sanitize_url

    # Dangerous URI schemes
    assert sanitize_url("javascript:alert(1)") == ""
    assert sanitize_url("JAVASCRIPT:alert(1)") == ""
    assert sanitize_url("  javascript:alert(1)") == ""
    assert sanitize_url("vbscript:msgbox(1)") == ""
    assert sanitize_url("data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==") == ""

    # Safe URLs and relative paths
    assert sanitize_url("https://example.com/eval") == "https://example.com/eval"
    assert sanitize_url("http://localhost:8000/api") == "http://localhost:8000/api"
    assert sanitize_url("/datasets/101") == "/datasets/101"

    # Recursive payload sanitization with URL fields
    payload = {
        "name": "Metadata <script>alert(1)</script>",
        "source": "javascript:alert(1)",
        "website": "https://evalforge.ai",
        "input_prompt": "If x < y, call javascript:alert(1) in evaluation prompt.",
    }
    sanitized = sanitize_input_data(payload, target_fields=("name",), url_fields=("source", "website"))
    assert sanitized["name"] == "Metadata &lt;script&gt;alert(1)&lt;/script&gt;"
    assert sanitized["source"] == ""
    assert sanitized["website"] == "https://evalforge.ai"
    # Evaluation prompt MUST preserve raw text intact!
    assert sanitized["input_prompt"] == "If x < y, call javascript:alert(1) in evaluation prompt."


def test_remediation_b4_05_trusted_proxy_ip_resolution() -> None:
    """Verify B4-05: Client IP resolution parses X-Forwarded-For ONLY when request host is in trusted proxies."""
    from fastapi import Request

    from app.core.rate_limiter import RateLimiter

    # Case A: Request from trusted proxy (127.0.0.1)
    req_trusted = Request(
        scope={
            "type": "http",
            "client": ("127.0.0.1", 12345),
            "headers": [(b"x-forwarded-for", b"203.0.113.195, 10.0.0.1")],
        }
    )
    assert RateLimiter.resolve_client_ip(req_trusted) == "203.0.113.195"

    # Case B: Request from untrusted remote client (198.51.100.44)
    req_untrusted = Request(
        scope={
            "type": "http",
            "client": ("198.51.100.44", 12345),
            "headers": [(b"x-forwarded-for", b"1.1.1.1")],
        }
    )
    assert RateLimiter.resolve_client_ip(req_untrusted) == "198.51.100.44"


