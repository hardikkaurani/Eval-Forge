from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.database.session import engine

# Setup structured logging before importing other modules
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info(
        "Starting up FastAPI application",
        app_name=settings.APP_NAME,
        env=settings.APP_ENV,
        debug_mode=settings.DEBUG,
    )
    # Verification of DB connectivity during startup
    try:
        async with engine.begin() as conn:
            # Executes a lightweight check to verify DB is reachable
            await conn.exec_driver_sql("SELECT 1")
        logger.info("Successfully connected to the database during lifespan startup.")
    except Exception as e:
        logger.error(
            "Database connection check failed during startup. "
            "Database service may be down.",
            error=str(e),
        )

    yield

    # Shutdown tasks
    logger.info("Shutting down FastAPI application")
    await engine.dispose()
    logger.info("Database connections closed successfully.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade open-source LLM evaluation platform",
    version="0.1.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    openapi_url="/openapi.json" if settings.APP_ENV != "production" else None,
    lifespan=lifespan,
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)

# Register custom global exception handlers
register_exception_handlers(app)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": "0.1.0",
        "docs_url": (
            "/docs" if settings.APP_ENV != "production" else "Disabled in production"
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development",
    )
