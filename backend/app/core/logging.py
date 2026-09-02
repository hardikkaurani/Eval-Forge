import logging
import re
import sys
from typing import Any, Dict

import structlog

from app.config.config import settings

SENSITIVE_KEYWORDS = (
    "password",
    "passwd",
    "secret",
    "client_secret",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "bearer",
    "private_key",
    "credentials",
    "connectionstring",
    "dsn",
    "database_url",
    "db_uri",
    "db_url",
    "connection_url",
)

# Pattern to match URI credentials: e.g. scheme://username:password@host
URI_CREDENTIAL_PATTERN = re.compile(
    r"(?i)\b([a-z0-9+.-]+://[^:\s@]+:)([^@\s]+)(@[^\s]+)"
)

# Pattern to match Bearer tokens: e.g. Bearer abc123XYZ...
BEARER_TOKEN_PATTERN = re.compile(
    r"(?i)\b(bearer\s+)(?!status\b|type\b|mode\b|auth\b)([A-Za-z0-9._~+/-]{4,})\b"
)


def redact_sensitive_string(val: str) -> str:
    """Redacts passwords in URI/DSN strings and Bearer tokens within text."""
    if not isinstance(val, str) or not val:
        return val

    # 1. Redact URI credentials (e.g. postgresql://user:password@host)
    if "://" in val and "@" in val:
        val = URI_CREDENTIAL_PATTERN.sub(r"\1[REDACTED]\3", val)

    # 2. Redact Bearer tokens (e.g. Bearer secret_token_value)
    if "bearer" in val.lower():
        val = BEARER_TOKEN_PATTERN.sub(r"\1[REDACTED]", val)

    return val


def redact_sensitive_data(
    logger: Any, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Recursively redacts sensitive keys and values from structlog event dicts."""
    return _redact_dict(event_dict)


def _redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}
    for key, val in data.items():
        key_lower = str(key).lower()
        if any(keyword in key_lower for keyword in SENSITIVE_KEYWORDS):
            cleaned[key] = "[REDACTED]"
        else:
            cleaned[key] = _redact_val(val)
    return cleaned


def _redact_val(val: Any) -> Any:
    if isinstance(val, dict):
        return _redact_dict(val)
    elif isinstance(val, list):
        return [_redact_val(item) for item in val]
    elif isinstance(val, tuple):
        # Handle tuple pairs such as ("Authorization", "Bearer SECRET")
        if len(val) == 2 and isinstance(val[0], str):
            k_lower = val[0].lower()
            if any(keyword in k_lower for keyword in SENSITIVE_KEYWORDS):
                return (val[0], "[REDACTED]")
        return tuple(_redact_val(item) for item in val)
    elif isinstance(val, str):
        return redact_sensitive_string(val)
    return val


def add_logger_name(
    logger: Any, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Adds logger name if not present."""
    if "logger" not in event_dict and hasattr(logger, "name"):
        event_dict["logger"] = logger.name
    return event_dict


def setup_logging() -> None:
    """Configures structlog and stdlib logging for structured JSON production logs."""
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        add_logger_name,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        redact_sensitive_data,
    ]

    if settings.JSON_LOGS or settings.APP_ENV == "production":
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]

    log_level = logging.getLevelName(settings.LOG_LEVEL.upper())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Obtains a bound structlog logger instance."""
    return structlog.get_logger(name)


def bind_correlation_context(**kwargs: Any) -> None:
    """Binds request/trace/user/org/workspace correlation fields to the current contextvars."""
    valid_context = {k: v for k, v in kwargs.items() if v is not None}
    if valid_context:
        structlog.contextvars.bind_contextvars(**valid_context)


def clear_correlation_context() -> None:
    """Clears all correlation fields from structlog contextvars."""
    structlog.contextvars.clear_contextvars()
