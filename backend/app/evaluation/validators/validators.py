from typing import Any, Dict

from app.evaluation.exceptions.exceptions import (
    InvalidConfigException,
    UnsupportedJudgeException,
    UnsupportedProviderException,
)
from app.evaluation.registry.registry import judge_registry, provider_registry
from app.evaluation.rubrics.rubrics import Rubric, validate_custom_rubric


class EvaluationValidator:
    """Validates parameters, configurations, and input elements before run execution."""

    @staticmethod
    def validate_provider(provider: str) -> None:
        """Validate if the given provider is registered."""
        try:
            provider_registry.get(provider)
        except KeyError as e:
            raise UnsupportedProviderException(provider) from e

    @staticmethod
    def validate_provider_model(provider: str, model: str | None) -> None:
        """Validate if the given provider and model combination is compatible."""
        if not model or not model.strip():
            return

        provider_lower = provider.lower()
        model_lower = model.lower()

        if provider_lower == "openai" and not (
            model_lower.startswith("gpt-")
            or model_lower.startswith("o1")
            or model_lower.startswith("o3")
            or model_lower.startswith("text-embedding")
        ):
            raise InvalidConfigException(
                f"Model '{model}' is incompatible with provider 'openai'."
            )

        if provider_lower == "claude" and not model_lower.startswith("claude-"):
            raise InvalidConfigException(
                f"Model '{model}' is incompatible with provider 'claude'."
            )

        if provider_lower == "gemini" and not model_lower.startswith("gemini-"):
            raise InvalidConfigException(
                f"Model '{model}' is incompatible with provider 'gemini'."
            )

        if provider_lower == "deepseek" and not model_lower.startswith("deepseek-"):
            raise InvalidConfigException(
                f"Model '{model}' is incompatible with provider 'deepseek'."
            )

    @staticmethod
    def validate_judge(judge: str) -> None:
        """Validate if the given judge type is registered."""
        try:
            judge_registry.get(judge)
        except KeyError as e:
            raise UnsupportedJudgeException(judge) from e

    @staticmethod
    def validate_configuration(config: Dict[str, Any]) -> None:
        """Validate execution parameters (temperature, max_tokens, threshold, timeout)."""
        temperature = config.get("temperature", 0.0)
        if not (0.0 <= temperature <= 2.0):
            raise InvalidConfigException(
                f"Temperature must be between 0.0 and 2.0. Got: {temperature}"
            )

        max_tokens = config.get("max_tokens")
        if max_tokens is not None and (
            not isinstance(max_tokens, int) or max_tokens <= 0
        ):
            raise InvalidConfigException(
                f"max_tokens must be a positive integer. Got: {max_tokens}"
            )

        threshold = config.get("threshold", 0.7)
        if not (0.0 <= threshold <= 1.0):
            raise InvalidConfigException(
                f"Threshold must be a percentage between 0.0 and 1.0. Got: {threshold}"
            )

        timeout = config.get("timeout", 30.0)
        if timeout <= 0.0:
            raise InvalidConfigException(
                f"Timeout must be greater than 0. Got: {timeout}"
            )

        retry_count = config.get("retry_count", 2)
        if not isinstance(retry_count, int) or retry_count < 0:
            raise InvalidConfigException(
                f"retry_count must be a non-negative integer. Got: {retry_count}"
            )

        batch_size = config.get("batch_size")
        if batch_size is not None and (
            not isinstance(batch_size, int) or batch_size <= 0
        ):
            raise InvalidConfigException(
                f"batch_size must be a positive integer. Got: {batch_size}"
            )

        if "max_concurrency" in config:
            max_concurrency = config["max_concurrency"]
            if (
                max_concurrency is None
                or isinstance(max_concurrency, bool)
                or not isinstance(max_concurrency, int)
            ):
                raise InvalidConfigException(
                    f"max_concurrency must be an integer. Got: {max_concurrency}"
                )
            if not (1 <= max_concurrency <= 50):
                raise InvalidConfigException(
                    f"max_concurrency must be between 1 and 50. Got: {max_concurrency}"
                )

    @staticmethod
    def validate_case(
        prompt: str,
        output: str,
        reference: str | None = None,
        judge: str = "rubric",
        response_b: str | None = None,
    ) -> None:
        """Validate specific inputs for a given test case."""
        if not prompt or not prompt.strip():
            raise InvalidConfigException("Prompt cannot be empty.")
        if not output or not output.strip():
            raise InvalidConfigException("Model output response cannot be empty.")

        if judge.lower() == "reference" and (not reference or not reference.strip()):
            raise InvalidConfigException(
                "Reference ground truth is required for reference-based evaluation."
            )
        if judge.lower() == "pairwise" and (not response_b or not response_b.strip()):
            raise InvalidConfigException(
                "Response B is required for pairwise evaluation."
            )

    @staticmethod
    def validate_rubric(rubric: Rubric) -> None:
        validate_custom_rubric(rubric)

    @staticmethod
    def validate_batch_size(test_cases: list[Any], max_batch_size: int) -> None:
        if len(test_cases) > max_batch_size:
            raise InvalidConfigException(
                f"Batch size cannot exceed {max_batch_size}. Got: {len(test_cases)}"
            )
