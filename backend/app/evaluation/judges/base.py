from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel, Field

from app.evaluation.providers.base import BaseProvider
from app.evaluation.rubrics.rubrics import Rubric


class JudgeResult(BaseModel):
    """Structured result returned by any Judge algorithm."""
    score: float = 0.0
    confidence: float | None = None
    reasoning: str | None = None
    criterion_scores: Dict[str, Any] = Field(default_factory=dict)
    winner: str | None = None  # Specific to pairwise comparison: "A", "B", or "Tie"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseJudge(ABC):
    """Abstract Base Class that all evaluation Judges must implement."""

    def __init__(self, provider: BaseProvider):
        self.provider = provider

    @abstractmethod
    async def evaluate(
        self,
        prompt: str,
        output: str,
        reference: str | None = None,
        rubric: Rubric | None = None,
        **kwargs
    ) -> JudgeResult:
        """Execute the judge evaluation algorithm."""
        pass
