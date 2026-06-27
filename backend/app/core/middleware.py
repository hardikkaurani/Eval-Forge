import time
import uuid
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config.config import settings

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking request correlation IDs and logging execution time.

    Generates a unique request ID (Correlation ID) for every incoming request,
    binds it to structlog contextvars, measures request execution time, and
    logs structured request/response information.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Clear contextvars from previous requests on this thread/task
        structlog.contextvars.clear_contextvars()

        # Retrieve request ID from headers or generate a new one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Set path and method in log context
        structlog.contextvars.bind_contextvars(
            method=request.method,
            path=request.url.path,
        )

        start_time = time.perf_counter()

        logger.info(
            "Request started",
            client_host=request.client.host if request.client else None,
            query_params=str(request.query_params),
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = time.perf_counter() - start_time
            logger.error(
                "Request failed with unhandled exception",
                duration_ms=round(duration * 1000, 2),
                error=str(exc),
            )
            raise exc from None

        duration = time.perf_counter() - start_time
        duration_ms = round(duration * 1000, 2)

        # Log completion
        logger.info(
            "Request finished",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        # Attach request ID and process time to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.6f}s"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to inject standard production-grade security headers."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Set standard security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"

        # Content-Security-Policy setup
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )

        # HSTS header (Strict-Transport-Security) for HTTPS in production
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )

        return response
