class AdvancedAIError(Exception):
    """Base exception for all advanced AI evaluation errors."""

    pass


class RAGEvaluationError(AdvancedAIError):
    """Raised when RAG evaluation calculation fails."""

    pass


class SafetyEvaluationError(AdvancedAIError):
    """Raised when Safety evaluation calculation fails."""

    pass


class SecurityEvaluationError(AdvancedAIError):
    """Raised when Security evaluation calculation fails."""

    pass


class AgentEvaluationError(AdvancedAIError):
    """Raised when Agent evaluation calculation fails."""

    pass


class ConversationEvaluationError(AdvancedAIError):
    """Raised when Conversation evaluation calculation fails."""

    pass


class PolicyNotFoundError(AdvancedAIError):
    """Raised when a specified policy is not found."""

    pass


class RegressionRunError(AdvancedAIError):
    """Raised when regression analysis fails."""

    pass
