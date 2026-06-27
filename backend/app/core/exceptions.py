from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EvalForgeException)
    async def eval_forge_exception_handler(request: Request, exc: EvalForgeException):
        logger.error(
            "Application error occurred",
            path=request.url.path,
            error=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": exc.message,
                    "code": exc.__class__.__name__,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled global exception",
            path=request.url.path,
            error=str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "message": "Internal Server Error. Please contact support.",
                    "code": "InternalServerError",
                    "details": None,
                },
            },
        )
