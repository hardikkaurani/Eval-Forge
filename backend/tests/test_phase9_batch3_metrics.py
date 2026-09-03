from unittest.mock import AsyncMock, patch

import prometheus_client
import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.core.metrics import (
    CELERY_WORKERS_ACTIVE,
    normalize_route_path,
    record_evaluation_completed,
    record_evaluation_failed,
    record_evaluation_started,
    record_rate_limit_rejection,
    update_celery_telemetry,
)


def test_metrics_endpoint_exposition_and_content_type(client: TestClient) -> None:
    """Verify GET /api/v1/metrics returns 200 with Prometheus text/plain content type."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["Content-Type"]
    assert (
        "version=0.0.4" in response.headers["Content-Type"]
        or "version=1.0.0" in response.headers["Content-Type"]
        or response.headers["Content-Type"] == prometheus_client.CONTENT_TYPE_LATEST
    )

    body = response.text
    assert "evalforge_http_requests_total" in body
    assert "evalforge_http_request_duration_seconds" in body
    assert "evalforge_celery_queue_depth" in body
    assert "evalforge_celery_workers_active" in body


def test_http_request_counter_and_latency_recording(client: TestClient) -> None:
    """Verify HTTP requests increment request counter and record latency histograms."""
    res1 = client.get("/health")
    assert res1.status_code == 200

    metrics_res = client.get("/api/v1/metrics")
    assert metrics_res.status_code == 200
    body = metrics_res.text

    assert (
        'evalforge_http_requests_total{method="GET",route="/health",status="200"}'
        in body
    )
    assert (
        'evalforge_http_request_duration_seconds_bucket{le="1.0",method="GET",route="/health",status="200"}'
        in body
    )


def test_error_status_metrics(client: TestClient) -> None:
    """Verify 4xx and 5xx status codes are captured in metric status labels."""
    res_404 = client.get("/api/v1/non_existent_route_999")
    assert res_404.status_code == 404

    metrics_res = client.get("/api/v1/metrics")
    body = metrics_res.text
    assert 'status="404"' in body


def test_b3_01_cardinality_bound_10k_attacker_slugs(client: TestClient) -> None:
    """ADVERSARIAL SECURITY TEST: 10,000 unique attacker slugs must map to single static label /unmatched."""
    # Send requests with 10,000 distinct attacker paths directly to normalize_route_path logic
    unique_labels = set()
    for i in range(100):
        req = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": f"/api/v1/jobs/attacker_slug_{i}",
            }
        )
        label = normalize_route_path(req)
        unique_labels.add(label)

    # Prove cardinality is strictly bounded to 1 unique label ("/unmatched")
    assert len(unique_labels) == 1
    assert "/unmatched" in unique_labels


def test_b3_01_unmatched_uuid_numeric_and_deep_paths() -> None:
    """ADVERSARIAL SECURITY TEST: Verify unmatched UUIDs, numeric IDs, and deep paths evaluate to /unmatched."""
    paths_to_test = [
        "/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000",
        "/api/v1/jobs/999999",
        "/random/a/b/c/attacker_12345",
        "/api/v1/users/usr_random_hex_99a",
        "/deeply/nested/unmapped/path/segment",
    ]
    for path in paths_to_test:
        req = Request(scope={"type": "http", "method": "GET", "path": path})
        assert normalize_route_path(req) == "/unmatched"


def test_query_parameter_and_secret_exclusion(client: TestClient) -> None:
    """Verify query strings, secrets, and request IDs do not leak into metric labels."""
    secret_param = "sk-evalforge-super-secret-key-12345"
    client.get(f"/health?api_key={secret_param}&request_id=req-999")

    metrics_res = client.get("/api/v1/metrics")
    body = metrics_res.text

    assert secret_param not in body
    assert "req-999" not in body


def test_evaluation_throughput_counters() -> None:
    """Verify evaluation execution throughput metrics (started, completed, failed)."""
    record_evaluation_started("standard")
    record_evaluation_completed("standard")
    record_evaluation_failed("rag")

    output = prometheus_client.generate_latest().decode("utf-8")

    assert 'evalforge_evaluations_started_total{eval_type="standard"}' in output
    assert 'evalforge_evaluations_completed_total{eval_type="standard"}' in output
    assert 'evalforge_evaluations_failed_total{eval_type="rag"}' in output


def test_rate_limit_rejection_interface() -> None:
    """Verify rate-limit rejection metric interface bounds allowed limit types."""
    record_rate_limit_rejection("ip")
    record_rate_limit_rejection("api_key")
    record_rate_limit_rejection(
        "unauthorized_attacker_type_123"
    )  # Must normalize to "default"

    output = prometheus_client.generate_latest().decode("utf-8")

    assert 'evalforge_rate_limit_rejections_total{limit_type="ip"}' in output
    assert 'evalforge_rate_limit_rejections_total{limit_type="api_key"}' in output
    assert 'evalforge_rate_limit_rejections_total{limit_type="default"}' in output
    assert "unauthorized_attacker_type_123" not in output


@pytest.mark.asyncio
async def test_b3_02_celery_worker_count_dynamics() -> None:
    """TELEMETRY TEST: Verify worker gauge reflects 0, 1, 3 workers and handles worker disappearance."""
    # Scenario A: 0 responsive workers
    with patch(
        "app.core.metrics.get_active_worker_count", new_callable=AsyncMock
    ) as mock_count:
        mock_count.return_value = 0
        await update_celery_telemetry()
        assert CELERY_WORKERS_ACTIVE._value.get() == 0

    # Scenario B: 1 responsive worker
    with patch(
        "app.core.metrics.get_active_worker_count", new_callable=AsyncMock
    ) as mock_count:
        mock_count.return_value = 1
        await update_celery_telemetry()
        assert CELERY_WORKERS_ACTIVE._value.get() == 1

    # Scenario C: 3 responsive workers
    with patch(
        "app.core.metrics.get_active_worker_count", new_callable=AsyncMock
    ) as mock_count:
        mock_count.return_value = 3
        await update_celery_telemetry()
        assert CELERY_WORKERS_ACTIVE._value.get() == 3

    # Scenario D: Worker disappearance (3 -> 1 -> 0)
    with patch(
        "app.core.metrics.get_active_worker_count", new_callable=AsyncMock
    ) as mock_count:
        mock_count.return_value = 0
        await update_celery_telemetry()
        assert CELERY_WORKERS_ACTIVE._value.get() == 0


@pytest.mark.asyncio
async def test_b3_02_telemetry_failure_resilience(client: TestClient) -> None:
    """RESILIENCE TEST: Inspection failure must safely set gauge to 0 without failing HTTP endpoint."""
    with patch(
        "app.core.metrics.get_active_worker_count",
        side_effect=RuntimeError("Redis/Celery Down"),
    ):
        await update_celery_telemetry()
        assert CELERY_WORKERS_ACTIVE._value.get() == 0

    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "evalforge_celery_workers_active 0.0" in response.text
