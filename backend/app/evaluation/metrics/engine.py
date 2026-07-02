from __future__ import annotations

from typing import Any, Dict, Iterable, List

from app.evaluation.metrics.base import BaseMetric, MetricResult
from app.evaluation.registry.registry import metric_registry


@metric_registry.register("numeric_score")
class NumericScoreMetric(BaseMetric):
    key = "numeric_score"
    display_name = "Numeric Score"
    description = "Normalizes a raw numeric judge score into a 0-1 score."

    def evaluate(self, **kwargs: Any) -> MetricResult:
        score = float(kwargs.get("score", 0.0))
        max_scale = float(kwargs.get("max_scale", 5.0))
        threshold = float(kwargs.get("threshold", 0.7))
        normalized = MetricsCalculator.normalize(score, max_scale)
        return MetricResult(
            score=score,
            normalized_score=normalized,
            passed=normalized >= threshold,
            confidence=kwargs.get("confidence"),
            reasoning=kwargs.get("reasoning"),
            explanation=kwargs.get("explanation"),
            metadata={"max_scale": max_scale, "threshold": threshold},
        )


@metric_registry.register("weighted_score")
class WeightedScoreMetric(BaseMetric):
    key = "weighted_score"
    display_name = "Weighted Score"
    description = "Applies rubric weights to a list of score values."

    def evaluate(self, **kwargs: Any) -> MetricResult:
        score = float(kwargs.get("score", 0.0))
        weight = float(kwargs.get("weight", 1.0))
        max_scale = float(kwargs.get("max_scale", 5.0))
        threshold = float(kwargs.get("threshold", 0.7))
        weighted_score = score * weight
        normalized = MetricsCalculator.normalize(weighted_score, max_scale * weight)
        return MetricResult(
            score=weighted_score,
            normalized_score=normalized,
            passed=normalized >= threshold,
            confidence=kwargs.get("confidence"),
            reasoning=kwargs.get("reasoning"),
            metadata={"base_score": score, "weight": weight},
        )


@metric_registry.register("pass_fail")
class PassFailMetric(BaseMetric):
    key = "pass_fail"
    display_name = "Pass/Fail"
    description = "Produces a binary pass/fail result from a normalized score."

    def evaluate(self, **kwargs: Any) -> MetricResult:
        normalized_score = float(kwargs.get("normalized_score", 0.0))
        threshold = float(kwargs.get("threshold", 0.7))
        return MetricResult(
            score=1.0 if normalized_score >= threshold else 0.0,
            normalized_score=normalized_score,
            passed=normalized_score >= threshold,
            confidence=kwargs.get("confidence"),
            reasoning=kwargs.get("reasoning"),
            metadata={"threshold": threshold},
        )


class MetricsCalculator:
    """Helper class to calculate metrics normalization and aggregations."""

    @staticmethod
    def normalize(score: float, max_scale: float) -> float:
        """Normalizes a raw score on a scale of [0, max_scale] or [1, max_scale] to a [0.0, 1.0] range."""
        if max_scale <= 0:
            return 0.0
        if score > max_scale:
            return 1.0
        if score < 0.0:
            return 0.0
        if max_scale == 1:
            return 1.0 if score >= 1.0 else 0.0
        return max(0.0, min(1.0, score / max_scale))

    @staticmethod
    def calculate_passed(score: float, max_scale: float, threshold: float) -> bool:
        """Determines if the score meets or exceeds a given threshold percentage (0.0 to 1.0)."""
        normalized = MetricsCalculator.normalize(score, max_scale)
        return normalized >= threshold

    @staticmethod
    def aggregate_weighted_score(scores: Iterable[float], weights: Iterable[float]) -> float | None:
        score_list = list(scores)
        weight_list = list(weights)
        if not score_list or not weight_list:
            return None
        if len(score_list) != len(weight_list):
            raise ValueError("Scores and weights must have the same length.")

        total_weight = sum(weight_list)
        if total_weight <= 0:
            return None
        return round(sum(s * w for s, w in zip(score_list, weight_list)) / total_weight, 4)

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
                return sorted_scores[f] + (sorted_scores[c] - sorted_scores[f]) * (
                    k - f
                )
            return sorted_scores[f]

        p10_val = percentile(0.1)
        p90_val = percentile(0.9)

        return {
            "mean": round(mean_val, 4),
            "median": round(median_val, 4),
            "p10": round(p10_val, 4),
            "p90": round(p90_val, 4),
        }
