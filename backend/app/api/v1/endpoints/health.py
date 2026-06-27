import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

router = APIRouter()
logger = structlog.get_logger()


@router.get("/health", summary="Health check endpoint")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint to verify system status.

    Checks:
    - FastAPI API status
    - Database connectivity (via SELECT 1)
    """
    database_ok = False
    try:
        # Simple query to check database availability
        await db.execute(text("SELECT 1"))
        database_ok = True
    except Exception as e:
        logger.error("Health check database connection failed", error=str(e))

    return {
        "status": "healthy" if database_ok else "degraded",
        "services": {
            "api": "healthy",
            "database": "healthy" if database_ok else "unhealthy",
            # Redis check can be added here in the future
        },
    }
