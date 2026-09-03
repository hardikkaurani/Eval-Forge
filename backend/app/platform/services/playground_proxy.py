import ipaddress
import time
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from fastapi.testclient import TestClient

# Blocked IP ranges (SSRF prevention)
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local / Cloud metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


def validate_playground_target(endpoint: str) -> str:
    """Validates that the target endpoint is a clean relative API path and prevents SSRF."""
    endpoint = endpoint.strip()
    parsed = urlparse(endpoint)
    if parsed.scheme or parsed.netloc:
        raise ValueError("Arbitrary external URLs and schemes are not permitted in the playground.")

    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    # Must target /api/v1 or /health or /metrics
    if not (
        endpoint.startswith("/api/v1")
        or endpoint.startswith("/health")
        or endpoint.startswith("/metrics")
    ):
        raise ValueError("Playground target must be an allowlisted /api/v1/* endpoint.")

    return endpoint


class PlaygroundProxyService:
    """SSRF-guarded Playground Request Runner."""

    def execute_request(
        self,
        endpoint: str,
        method: str = "GET",
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        clean_endpoint = validate_playground_target(endpoint)
        method = method.upper()

        req_headers = dict(headers or {})
        if api_key:
            req_headers["X-API-Key"] = api_key
        req_headers.setdefault("Content-Type", "application/json")

        from app.main import app

        start_time = time.perf_counter()

        with TestClient(app) as client:
            if method == "GET":
                response = client.get(clean_endpoint, headers=req_headers)
            elif method == "POST":
                response = client.post(clean_endpoint, json=payload, headers=req_headers)
            elif method == "PUT":
                response = client.put(clean_endpoint, json=payload, headers=req_headers)
            elif method == "DELETE":
                response = client.delete(clean_endpoint, headers=req_headers)
            else:
                raise ValueError(f"HTTP method '{method}' not supported in playground.")

        latency = int((time.perf_counter() - start_time) * 1000)

        # Parse response safely
        try:
            body = response.json()
        except Exception:
            body = response.text[:2000]

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": body,
            "latency_ms": latency,
            "request_id": response.headers.get("X-Request-ID", "req_local_playground"),
        }


playground_proxy_service = PlaygroundProxyService()
