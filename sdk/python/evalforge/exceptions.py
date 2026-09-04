from typing import Any, Dict, Optional


class EvalForgeError(Exception):
    """Base exception for all Eval-Forge SDK errors."""

    def __init__(self, message: str, request_id: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.request_id = request_id

    def __str__(self) -> str:
        if self.request_id:
            return f"[{self.request_id}] {self.message}"
        return self.message


class APIError(EvalForgeError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        request_id: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, request_id)
        self.status_code = status_code
        self.body = body or {}


class AuthenticationError(APIError):
    """Raised when authentication fails (401)."""

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: int = 401,
        request_id: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, request_id, body)


class NotFoundError(APIError):
    """Raised when the requested resource is not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        status_code: int = 404,
        request_id: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, request_id, body)


class RateLimitError(APIError):
    """Raised when requests exceed rate limits (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int = 429,
        request_id: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, request_id, body)


class APIConnectionError(EvalForgeError):
    """Raised when a network or transport connection failure occurs."""

    pass


class APIResponseValidationError(EvalForgeError):
    """Raised when the response payload does not match the expected schema."""

    pass
