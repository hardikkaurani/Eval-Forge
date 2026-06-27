from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
import structlog
from pydantic import BaseModel

logger = structlog.get_logger()

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standardized API Response structure for EvalForge."""

    success: bool
    message: str
    data: T | None = None
    timestamp: str
    request_id: str


def create_response(
    success: bool,
    message: str,
    data: Any = None,
) -> dict[str, Any]:
    """Helper to build a standardized API response dictionary.

    Retrieves the correlation ID (request_id) automatically from the logging
    context variables.
    """
    ctx = structlog.contextvars.get_contextvars()
    request_id = ctx.get("request_id", "")

    return {
        "success": success,
        "message": message,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
    }
