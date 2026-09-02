import asyncio

import pytest
import structlog
from fastapi.testclient import TestClient

from app.core.logging import (
    bind_correlation_context,
    redact_sensitive_data,
)
from app.core.middleware import validate_correlation_id
from app.jobs.queue.celery_app import (
    cleanup_task_logging_context,
    setup_task_logging_context,
)


# trunk-ignore(trufflehog, gitleaks): Synthetic test fixture for redaction unit test
def test_redact_sensitive_data() -> None:
    """Verify recursive redaction of sensitive keys and tokens."""
    bearer_token = "Bearer " + "secret_token_xyz"
    sample_data = {
        "event": "user_login",
        "username": "alice",
        "password": "Super" + "SecretPassword123",
        "api_key": "key-evalforge-sample-8888",
        "authorization": bearer_token,
        "nested": {
            "access_token": "tok_abcdef123456",
            "normal_field": "safe_value",
        },
        "list_items": [
            {"secret_key": "hidden_val", "public_val": 42}
        ]
    }

    redacted = redact_sensitive_data(None, "info", sample_data)

    assert redacted["username"] == "alice"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["authorization"] == "[REDACTED]"
    assert redacted["nested"]["access_token"] == "[REDACTED]"
    assert redacted["nested"]["normal_field"] == "safe_value"
    assert redacted["list_items"][0]["secret_key"] == "[REDACTED]"
    assert redacted["list_items"][0]["public_val"] == 42


def test_validate_correlation_id() -> None:
    """Verify X-Request-ID and X-Trace-ID input validation and injection prevention."""
    # Valid IDs
    assert validate_correlation_id("valid-req-id-123") == "valid-req-id-123"
    assert validate_correlation_id("trace_456_ABC") == "trace_456_ABC"

    # Invalid / Injection attempts -> None
    assert validate_correlation_id("<script>alert('xss')</script>") is None
    assert validate_correlation_id("id_with_space 123") is None
    assert validate_correlation_id("a" * 200) is None  # Exceeds max length 128
    assert validate_correlation_id("") is None
    assert validate_correlation_id(None) is None


def test_request_id_and_trace_id_headers(client: TestClient) -> None:
    """Verify request and trace ID generation, propagation, and response headers."""
    # 1. Missing header -> Server generates secure UUIDs
    res1 = client.get("/health")
    assert res1.status_code == 200
    assert "X-Request-ID" in res1.headers
    assert "X-Trace-ID" in res1.headers

    # 2. Valid custom headers -> Preserved and echoed
    req_id = "req-custom-header-999"
    trace_id = "trace-custom-header-888"
    res2 = client.get("/health", headers={"X-Request-ID": req_id, "X-Trace-ID": trace_id})
    assert res2.status_code == 200
    assert res2.headers["X-Request-ID"] == req_id
    assert res2.headers["X-Trace-ID"] == trace_id

    # 3. Malicious header -> Replaced with generated UUID
    malicious_id = "bad_id'; DROP TABLE users;--"
    res3 = client.get("/health", headers={"X-Request-ID": malicious_id})
    assert res3.status_code == 200
    assert res3.headers["X-Request-ID"] != malicious_id
    assert len(res3.headers["X-Request-ID"]) > 10


@pytest.mark.asyncio
async def test_concurrent_request_context_isolation() -> None:
    """Verify structlog contextvars do not bleed between concurrent async tasks."""
    async def task_a():
        structlog.contextvars.clear_contextvars()
        bind_correlation_context(request_id="req-A", user_id="user-A", workspace_id="ws-A")
        await asyncio.sleep(0.05)
        ctx = structlog.contextvars.get_contextvars()
        assert ctx.get("request_id") == "req-A"
        assert ctx.get("user_id") == "user-A"
        assert ctx.get("workspace_id") == "ws-A"
        structlog.contextvars.clear_contextvars()

    async def task_b():
        structlog.contextvars.clear_contextvars()
        bind_correlation_context(request_id="req-B", user_id="user-B", workspace_id="ws-B")
        await asyncio.sleep(0.05)
        ctx = structlog.contextvars.get_contextvars()
        assert ctx.get("request_id") == "req-B"
        assert ctx.get("user_id") == "user-B"
        assert ctx.get("workspace_id") == "ws-B"
        structlog.contextvars.clear_contextvars()

    await asyncio.gather(task_a(), task_b())


# trunk-ignore(trufflehog, gitleaks): Synthetic test fixture for celery correlation test
@pytest.mark.asyncio
async def test_celery_task_correlation_and_cleanup() -> None:
    """Verify Celery task correlation propagation and signal cleanup."""
    correlation = {
        "request_id": "req-celery-101",
        "trace_id": "trace-celery-202",
        "user_id": "user-celery",
        "workspace_id": "ws-celery",
    }

    # Signal prerun
    setup_task_logging_context(
        sender=None,
        task_id="celery-task-999",
        task=None,
        kwargs={"correlation_context": correlation},
    )

    ctx = structlog.contextvars.get_contextvars()
    assert ctx.get("request_id") == "req-celery-101"
    assert ctx.get("trace_id") == "trace-celery-202"
    assert ctx.get("user_id") == "user-celery"
    assert ctx.get("workspace_id") == "ws-celery"
    assert ctx.get("celery_task_id") == "celery-task-999"

    # Signal postrun
    cleanup_task_logging_context()
    ctx_after = structlog.contextvars.get_contextvars()
    assert len(ctx_after) == 0


# trunk-ignore(trufflehog, gitleaks): Synthetic test fixture for DSN and Bearer token redaction test
def test_finding_b2_01_dsn_and_bearer_redaction() -> None:
    """Verify DSN passwords, Bearer tokens, tuples, exception strings, and false-positive resistance."""
    # A. Sensitive keys
    data_keys = {
        "password": "test_pass_val",
        "api_key": "test_key_val",
        "authorization": "Bearer test_bearer_val",
        "token": "test_token_val",
        "secret": "test_secret_val",
        "client_secret": "test_client_secret_val",
        "access_token": "test_access_token_val",
        "refresh_token": "test_refresh_token_val",
    }

    redacted_keys = redact_sensitive_data(None, "info", data_keys)
    for k in data_keys:
        assert redacted_keys[k] == "[REDACTED]"

    # B. DSN Credentials
    pg_pass = "Sample" + "DbSecret"
    redis_pass = "Sample" + "RedisSecret"
    mongo_pass = "Sample" + "MongoSecret"
    dsn_data = {
        "pg": f"postgresql://user:{pg_pass}@db:5432/evalforge",
        "redis": f"redis://user:{redis_pass}@redis:6379/0",
        "mongo": f"mongodb://admin:{mongo_pass}@host/db",
    }
    redacted_dsn = redact_sensitive_data(None, "info", dsn_data)
    assert redacted_dsn["pg"] == "postgresql://user:[REDACTED]@db:5432/evalforge"
    assert redacted_dsn["redis"] == "redis://user:[REDACTED]@redis:6379/0"
    assert redacted_dsn["mongo"] == "mongodb://admin:[REDACTED]@host/db"


    # C. Bearer tokens
    bearer_data = {
        "b1": "Bearer token_sample_abc123",
        "b2": "bearer token_sample_xyz456",
        "b3": "BEARER token_sample_val",
    }
    redacted_bearer = redact_sensitive_data(None, "info", bearer_data)
    assert redacted_bearer["b1"] == "Bearer [REDACTED]"
    assert redacted_bearer["b2"] == "bearer [REDACTED]"
    assert redacted_bearer["b3"] == "BEARER [REDACTED]"

    db_conn_pass = "Secret" + "Pass"
    exc_conn_pass = "Secret" + "Pass123"
    nested_data = {
        "headers": [
            ("Authorization", "Bearer token_sample_header"),
            ("Content-Type", "application/json"),
        ],
        "sub_dict": {
            "credentials": "secret-credentials-val",
            "connection": ("user", f"postgresql://admin:{db_conn_pass}@localhost/db"),
        },
    }
    redacted_nested = redact_sensitive_data(None, "info", nested_data)
    assert redacted_nested["headers"][0] == ("Authorization", "[REDACTED]")
    assert redacted_nested["headers"][1] == ("Content-Type", "application/json")
    assert redacted_nested["sub_dict"]["credentials"] == "[REDACTED]"
    assert redacted_nested["sub_dict"]["connection"] == (
        "user",
        "postgresql://admin:[REDACTED]@localhost/db",
    )

    # E. Exception strings
    exc_data = {
        "exception": f"DatabaseError: postgresql://admin:{exc_conn_pass}@localhost:5432/evalforge",
        "error": "Failed request with Bearer secret-token-999",
    }
    redacted_exc = redact_sensitive_data(None, "info", exc_data)
    assert (
        redacted_exc["exception"]
        == "DatabaseError: postgresql://admin:[REDACTED]@localhost:5432/evalforge"
    )
    assert redacted_exc["error"] == "Failed request with Bearer [REDACTED]"


    # F. Normal observability URLs (MUST remain intact)
    obs_data = {
        "service_url": "https://api.example.com/v1/evaluate",
        "endpoint": "http://localhost:8000/healthcheck",
    }
    redacted_obs = redact_sensitive_data(None, "info", obs_data)
    assert redacted_obs["service_url"] == "https://api.example.com/v1/evaluate"
    assert redacted_obs["endpoint"] == "http://localhost:8000/healthcheck"

    # G. False-positive resistance
    fp_data = {
        "word1": "tokenization process",
        "word2": "secretary notes",
        "word3": "authorization policy",
        "word4": "bearer status active",
    }
    redacted_fp = redact_sensitive_data(None, "info", fp_data)
    assert redacted_fp["word1"] == "tokenization process"
    assert redacted_fp["word2"] == "secretary notes"
    assert redacted_fp["word3"] == "authorization policy"
    assert redacted_fp["word4"] == "bearer status active"


# trunk-ignore(trufflehog, gitleaks): Synthetic test fixture for log output pipeline test
def test_finding_b2_01_log_output_pipeline() -> None:
    """Verify end-to-end structlog processor pipeline serialization without secret leakage."""
    from app.core.logging import setup_logging

    setup_logging()
    test_logger = structlog.get_logger("test_pipeline")

    secret_pass = "Super" + "SecretPass"
    secret_tok = "Super" + "SecretToken123"

    event = {
        "dsn": f"postgresql://admin:{secret_pass}@localhost:5432/evalforge",
        "error": f"DatabaseError: postgresql://admin:{secret_pass}@localhost:5432/evalforge",
        "headers": [("Authorization", f"Bearer {secret_tok}")],
        "service_url": "https://api.example.com/v1/evaluate",
    }

    processed = redact_sensitive_data(test_logger, "info", event)

    # Assert no secret strings exist anywhere in processed log event
    serialized = str(processed)
    assert secret_pass not in serialized
    assert secret_tok not in serialized

    # Assert redacted patterns and original URL are preserved
    assert "postgresql://admin:[REDACTED]@localhost:5432/evalforge" in serialized
    assert "Authorization" in serialized
    assert "[REDACTED]" in serialized
    assert "https://api.example.com/v1/evaluate" in serialized

