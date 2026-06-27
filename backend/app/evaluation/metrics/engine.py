from typing import Any, Dict, List

from pydantic import BaseModel, Field


class MetricResult(BaseModel):
    """Structured result of a single metric evaluation."""
    score: float
    normalized_score: float  # scaled to 0.0 - 1.0 range
    passed: bool
    confidence: float | None = None
    reasoning: str | None = None
    explanation: str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MetricsCalculator:
    """Helper class to calculate metrics normalization and aggregations."""

    @staticmethod
    def normalize(score: float, max_scale: float) -> float:
        """Normalizes a raw score on a scale of [0, max_scale] or [1, max_scale] to a [0.0, 1.0] range."""
        if max_scale <= 0:
            return 0.0
        # If the scale is 1-based, we map [1, max_scale] to [0.0, 1.0]
        # In typical LLM evals, G-Eval uses 1 to 5 or 1 to 10
        # Let's support normalized mapping:
        # normalized = (score - 1) / (max_scale - 1) if scale starts at 1, else score / max_scale
        # For generality, let's treat it as score / max_scale unless score has offset
        if score > max_scale:
            return 1.0
        if score < 0.0:
            return 0.0
        return score / max_scale

    @staticmethod
    def calculate_passed(score: float, max_scale: float, threshold: float) -> bool:
        """Determines if the score meets or exceeds a given threshold percentage (0.0 to 1.0)."""
        normalized = MetricsCalculator.normalize(score, max_scale)
        return normalized >= threshold

    @staticmethod
    def compute_aggregates(scores: List[float]) -> Dict[str, float | None]:
        """Computes statistical metrics (mean, median, p10, p90) from a list of scores."""
        if not scores:
            return {
                "mean": None,
                "median": None,
                "p10": None,
                "p90": None,
            }

        sorted_scores = sorted(scores)
        n = len(sorted_scores)

        # Mean
        mean_val = sum(sorted_scores) / n

        # Median
        if n % 2 == 1:
            median_val = sorted_scores[n // 2]
        else:
            median_val = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2.0

        # Percentiles (interpolated)
        def percentile(p: float) -> float:
            k = (n - 1) * p
            f = int(k)
            c = f + 1
            if c < n:
                return sorted_scores[f] + (sorted_scores[c] - sorted_scores[f]) * (k - f)
            return sorted_scores[f]

        p10_val = percentile(0.1)
        p90_val = percentile(0.9)

        return {
            "mean": round(mean_val, 4),
            "median": round(median_val, 4),
            "p10": round(p10_val, 4),
            "p90": round(p90_val, 4),
        }
