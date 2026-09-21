from evalforge.client import AsyncEvalForge, EvalForge
from evalforge.exceptions import (
    APIConnectionError,
    APIError,
    APIResponseValidationError,
    AuthenticationError,
    EvalForgeError,
    NotFoundError,
    RateLimitError,
)

# Primary brand aliases
Evalium = EvalForge
AsyncEvalium = AsyncEvalForge
EvaliumError = EvalForgeError

__all__ = [
    "Evalium",
    "AsyncEvalium",
    "EvaliumError",
    "EvalForge",
    "AsyncEvalForge",
    "EvalForgeError",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "APIConnectionError",
    "APIResponseValidationError",
]
__version__ = "1.0.0"
