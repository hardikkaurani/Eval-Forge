import structlog
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import settings
from app.core.redis import redis_manager
from app.database.session import get_db
from app.utils.responses import ApiResponse, create_response

router = APIRouter()
logger = structlog.get_logger()


@router.get(
    "/health",
    response_model=ApiResponse[dict],
    summary="Detailed health check of application services",
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """General health check endpoint.

    Verifies connection status of critical infrastructure services like the
    relational database and Redis.
    """
    database_ok = False
    try:
        await db.execute(text("SELECT 1"))
        database_ok = True
    except Exception as e:
        logger.error("Health check: Database query failed", error=str(e))

    redis_ok = await redis_manager.ping()

    status_str = "healthy"
    if not database_ok and not redis_ok:
        status_str = "unhealthy"
    elif not database_ok or not redis_ok:
        status_str = "degraded"

    return create_response(
        success=status_str != "unhealthy",
        message="System health check completed.",
        data={
            "status": status_str,
            "services": {
                "api": "healthy",
                "database": "healthy" if database_ok else "unhealthy",
                "redis": "healthy" if redis_ok else "unhealthy",
            },
        },
    )


@router.get(
    "/ready",
    response_model=ApiResponse[dict],
    summary="Readiness check for load balancers",
)
async def readiness_check(
    response: Response, db: AsyncSession = Depends(get_db)
):
    """Readiness probe.

    Returns HTTP 200 OK only if all key backend dependencies (Postgres & Redis)
    are online, otherwise returns HTTP 503.
    """
    database_ok = False
    try:
        await db.execute(text("SELECT 1"))
        database_ok = True
    except Exception as e:
        logger.error("Readiness check: Database query failed", error=str(e))

    redis_ok = await redis_manager.ping()

    is_ready = database_ok and redis_ok
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return create_response(
        success=is_ready,
        message=(
            "System is ready to receive traffic."
            if is_ready
            else "System is not ready."
        ),
        data={
            "ready": is_ready,
            "services": {
                "database": "healthy" if database_ok else "unhealthy",
                "redis": "healthy" if redis_ok else "unhealthy",
            },
        },
    )


@router.get(
    "/live",
    response_model=ApiResponse[dict],
    summary="Liveness check for container orchestration",
)
async def liveness_check():
    """Liveness probe.

    Returns HTTP 200 OK immediately if the FastAPI runtime is online.
    """
    return create_response(
        success=True,
        message="System is running.",
        data={"status": "alive"},
    )


@router.get(
    "/version",
    response_model=ApiResponse[dict],
    summary="Retrieve application version",
)
async def version_check():
    """Returns application metadata containing version and environment details."""
    return create_response(
        success=True,
        message="Version information retrieved.",
        data={
            "version": "0.1.0",
            "environment": settings.APP_ENV,
        },
    )
