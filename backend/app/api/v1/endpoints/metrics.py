from fastapi import APIRouter, Response
import prometheus_client

router = APIRouter(prefix="/metrics", tags=["System"])


# Define basic Prometheus metric collectors
REQUEST_COUNT = prometheus_client.Counter(
    "evalforge_http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = prometheus_client.Histogram(
    "evalforge_http_request_latency_seconds",
    "HTTP Request Latency in seconds",
    ["method", "endpoint"]
)


@router.get("", summary="Expose Prometheus metrics")
def get_metrics():
    """Generates and returns system and HTTP performance metrics for Prometheus scraping."""
    return Response(
        content=prometheus_client.generate_latest(),
        media_type=prometheus_client.CONTENT_TYPE_LATEST
    )
