import prometheus_client
from fastapi import APIRouter, Response

from app.core.metrics import update_celery_telemetry

router = APIRouter(prefix="/metrics", tags=["System"])


@router.get("", summary="Expose Prometheus metrics")
async def get_metrics():
    """Generates and returns system and HTTP performance metrics for Prometheus scraping."""
    await update_celery_telemetry()
    return Response(
        content=prometheus_client.generate_latest(),
        media_type=prometheus_client.CONTENT_TYPE_LATEST,
    )
