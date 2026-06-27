from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger()


class EvalForgeException(Exception):
    """Base exception for all EvalForge errors."""

    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class DatabaseException(EvalForgeException):
    """Raised when a database operation fails."""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=500, details=details)


class ValidationException(EvalForgeException):
    """Raised when request payload or data validation fails."""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundException(EvalForgeException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=404, details=details)


class UnauthorizedException(EvalForgeException):
    """Raised when the user is unauthorized or authentication fails."""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=401, details=details)


class ForbiddenException(EvalForgeException):
    """Raised when the user is authenticated but does not have permission."""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=403, details=details)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers exception handlers to guarantee a consistent JSON response format."""

    def get_error_response(
        status_code: int, message: str, code: str, details: Any = None
    ) -> JSONResponse:
        ctx = structlog.contextvars.get_contextvars()
        request_id = ctx.get("request_id", "")

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "message": message,
                "data": {
                    "code": code,
                    "details": details,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
            },
        )

    @app.exception_handler(EvalForgeException)
    async def eval_forge_exception_handler(request: Request, exc: EvalForgeException):
        logger.error(
            "Application exception raised",
            path=request.url.path,
            error=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            exception_class=exc.__class__.__name__,
        )
        return get_error_response(
            status_code=exc.status_code,
            message=exc.message,
            code=exc.__class__.__name__,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        details = exc.errors()
        message = "Validation failed for request parameters or body."
        logger.warning(
            "Request validation failed",
            path=request.url.path,
            errors=details,
        )
        # Format Pydantic errors for better readability
        formatted_details = []
        for error in details:
            formatted_details.append(
                {
                    "loc": list(error.get("loc", [])),
                    "msg": error.get("msg", ""),
                    "type": error.get("type", ""),
                }
            )

        return get_error_response(
            status_code=400,
            message=message,
            code="RequestValidationError",
            details=formatted_details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            "HTTP exception occurred",
            path=request.url.path,
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return get_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            code="HTTPException",
            details=None,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled global exception caught",
            path=request.url.path,
            error=str(exc),
        )
        return get_error_response(
            status_code=500,
            message="Internal Server Error. Please contact support.",
            code="InternalServerError",
            details=None,
        )
