from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.config.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.core.redis import redis_manager
from app.database.session import engine

# Setup structured logging before importing other modules
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Tasks ---
    logger.info(
        "Starting up FastAPI application",
        app_name=settings.APP_NAME,
        env=settings.APP_ENV,
        debug_mode=settings.DEBUG,
    )

    # 1. Verification of DB connectivity
    try:
        async with engine.begin() as conn:
            await conn.exec_driver_sql("SELECT 1")
        logger.info("Database connectivity verified successfully.")
    except Exception as e:
        logger.error("Database connection check failed during startup.", error=str(e))

    # 2. Initialization of Redis connection manager
    try:
        redis_manager.init(settings.get_redis_url)
        redis_alive = await redis_manager.ping()
        if redis_alive:
            logger.info("Redis connectivity verified successfully.")
        else:
            logger.warning("Redis is unreachable or degraded.")
    except Exception as e:
        logger.error(
            "Redis connection initialization failed during startup.",
            error=str(e),
        )

    yield

    # --- Shutdown Tasks ---
    logger.info("Shutting down FastAPI application")

    # 1. Gracefully close Redis connections
    await redis_manager.close()

    # 2. Dispose of database connections
    await engine.dispose()
    logger.info("All connection resources released.")


app = FastAPI(
    title="EvalForge Core API",
    description=(
        "🚀 **EvalForge** is a production-grade open-source LLM evaluation platform.\n\n"
        "This API establishes the scalable core backend foundation supporting "
        "high-throughput project and evaluation lifecycle management.\n\n"
        "**Key Features:**\n"
        "* **Clean Architecture**: Layered API routes, service business logic, and database repositories.\n"
        "* **High Performance**: Asynchronous database connection pooling with SQLAlchemy 2.0 & PostgreSQL.\n"
        "* **Resiliency**: Built-in health check, liveness, and readiness probes.\n"
        "* **Security Headers**: Standard production-grade security and request validation middleware.\n"
        "* **Structured Logging**: Contextvars-based correlation (Request ID) tracking across operations."
    ),
    version="0.1.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    openapi_url="/openapi.json" if settings.APP_ENV != "production" else None,
    lifespan=lifespan,
)

# Register Middlewares (Outermost first for request execution, innermost first for response headers)
# 1. Custom Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 2. GZip Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# 5. Request logging and Request ID Middleware (Outermost wrapper)
app.add_middleware(RequestLoggingMiddleware)

# Register API routes under /api/v1 prefix
app.include_router(api_router, prefix=settings.API_V1_STR)

# Register custom global exception handlers
register_exception_handlers(app)


@app.get("/", tags=["System"])
async def root():
    """Welcome endpoint for root verification."""
    return {
        "success": True,
        "message": f"Welcome to {settings.APP_NAME}!",
        "data": {
            "version": "0.1.0",
            "docs_url": (
                "/docs"
                if settings.APP_ENV != "production"
                else "Disabled in production"
            ),
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development",
    )
