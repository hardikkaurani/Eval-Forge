from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel, Field


class MetricResult(BaseModel):
    """Structured result of a single metric evaluation."""

    score: float
    normalized_score: float
    passed: bool
    confidence: float | None = None
    reasoning: str | None = None
    explanation: str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseMetric(ABC):
    """Abstract metric plugin used by the scoring engine."""

    key: str = "metric"
    display_name: str = "Metric"
    description: str = "Generic metric"

    @abstractmethod
    def evaluate(self, **kwargs: Any) -> MetricResult:
        """Evaluate a metric from the supplied context."""

