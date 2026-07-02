from app.core.exceptions import EvalForgeException


class EvaluationException(EvalForgeException):
    """Base exception for all evaluation-related errors."""

    pass


class ProviderUnavailableException(EvaluationException):
    """Raised when an LLM provider is down or unresponsive."""

    def __init__(self, provider: str, details: str = ""):
        message = f"Provider '{provider}' is currently unavailable. {details}".strip()
        super().__init__(message=message, status_code=503)


class TimeoutException(EvaluationException):
    """Raised when a request to a provider times out."""

    def __init__(self, provider: str, timeout_seconds: float):
        message = (
            f"Request to provider '{provider}' timed out after {timeout_seconds}s."
        )
        super().__init__(message=message, status_code=504)


class RateLimitException(EvaluationException):
    """Raised when provider rate limits are hit."""

    def __init__(self, provider: str, details: str = ""):
        message = f"Rate limit exceeded for provider '{provider}'. {details}".strip()
        super().__init__(message=message, status_code=429)


class InvalidConfigException(EvaluationException):
    """Raised when evaluation run configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class UnsupportedProviderException(EvaluationException):
    """Raised when an unsupported provider is requested."""

    def __init__(self, provider: str):
        message = f"LLM Provider '{provider}' is not supported."
        super().__init__(message=message, status_code=400)


class UnsupportedJudgeException(EvaluationException):
    """Raised when an unsupported judge is requested."""

    def __init__(self, judge: str):
        message = f"Judge type '{judge}' is not supported."
        super().__init__(message=message, status_code=400)


class UnsupportedMetricException(EvaluationException):
    """Raised when a metric is not registered."""

    def __init__(self, metric: str):
        message = f"Metric '{metric}' is not supported."
        super().__init__(message=message, status_code=400)


class InvalidPromptException(EvaluationException):
    """Raised when a prompt template or rendered prompt is invalid."""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class EvaluationFailureException(EvaluationException):
    """Raised when the evaluation pipeline cannot complete successfully."""

    def __init__(self, message: str, details: str | None = None):
        super().__init__(message=message, status_code=500, details=details)
