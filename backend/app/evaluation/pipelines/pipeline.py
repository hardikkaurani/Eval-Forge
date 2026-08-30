from __future__ import annotations

import asyncio
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import settings
from app.evaluation.exceptions.exceptions import (
    EvaluationFailureException,
    ProviderUnavailableException,
    RateLimitException,
    TimeoutException,
)
from app.evaluation.metrics.engine import MetricsCalculator
from app.evaluation.registry.registry import judge_registry, provider_registry
from app.evaluation.repositories.evaluation import EvaluationRepository
from app.evaluation.rubrics.rubrics import BUILT_IN_RUBRICS, Rubric, get_rubric
from app.evaluation.schemas.evaluation import BatchEvaluationRequest
from app.evaluation.validators.validators import EvaluationValidator
from app.models.evaluation import EvaluationRun
from app.utils.time import get_utc_now

logger = logging.getLogger(__name__)


class EvaluationPipeline:
    """Orchestrates validation, LLM execution, metrics calculations, and DB persistence for batch runs."""

    @staticmethod
    def _build_provider(request: BatchEvaluationRequest):
        provider_cls = provider_registry.get(request.provider)
        kwargs: dict[str, object] = {}

        model_name = request.provider_model or request.configuration.get("model")
        if model_name:
            kwargs["model"] = model_name

        if request.provider == "ollama":
            kwargs["base_url"] = request.configuration.get(
                "base_url", settings.OLLAMA_BASE_URL
            )

        return provider_cls(**kwargs)

    @staticmethod
    def _retryable(exc: Exception) -> bool:
        return isinstance(
            exc,
            (ProviderUnavailableException, RateLimitException, TimeoutException),
        )

    @staticmethod
    async def run(db: AsyncSession, request: BatchEvaluationRequest) -> EvaluationRun:
        EvaluationValidator.validate_provider(request.provider)
        EvaluationValidator.validate_provider_model(
            request.provider,
            request.provider_model or request.configuration.get("model"),
        )
        EvaluationValidator.validate_judge(request.judge)
        EvaluationValidator.validate_configuration(request.configuration)
        EvaluationValidator.validate_batch_size(
            request.test_cases, settings.EVALUATION_MAX_BATCH_SIZE
        )

        if request.rubric:
            rubric = Rubric(
                name=request.rubric.name,
                description=request.rubric.description,
                weight=request.rubric.weight,
                scoring_scale=request.rubric.scoring_scale,
                prompt_template=request.rubric.prompt_template,
            )
            EvaluationValidator.validate_rubric(rubric)
        else:
            rubric = get_rubric("correctness") or BUILT_IN_RUBRICS["correctness"]

        provider = EvaluationPipeline._build_provider(request)
        judge_cls = judge_registry.get(request.judge)
        judge = judge_cls(provider=provider)

        evaluation = await EvaluationRepository.create_evaluation(
            db=db,
            project_id=request.project_id,
            name=request.evaluation_name,
            description=request.evaluation_description,
        )

        run = await EvaluationRepository.create_run(
            db=db,
            evaluation_id=evaluation.id,
            judge=request.judge,
            provider=request.provider,
            provider_model=request.provider_model or request.configuration.get("model"),
            configuration=request.configuration,
            total_cases=len(request.test_cases),
        )

        await db.commit()

        run = await EvaluationRepository.update_run(db, run.id, status="RUNNING")
        await db.commit()

        threshold = request.configuration.get(
            "threshold", settings.EVALUATION_SCORE_THRESHOLD
        )
        retry_count = request.configuration.get(
            "retry_count", settings.EVALUATION_RETRY_COUNT
        )
        prompt_version = request.configuration.get(
            "prompt_version", settings.DEFAULT_EVALUATION_PROMPT_VERSION
        )
        max_concurrency = int(request.configuration.get("max_concurrency", 5))
        semaphore = asyncio.Semaphore(max(1, max_concurrency))

        async def evaluate_single_case(index: int, case):
            async with semaphore:
                attempt = 0
                last_error: Exception | None = None

                while attempt <= retry_count:
                    try:
                        EvaluationValidator.validate_case(
                            prompt=case.input_prompt,
                            output=case.model_output,
                            reference=case.reference,
                            judge=request.judge,
                            response_b=case.response_b,
                        )

                        judge_result = await judge.evaluate(
                            prompt=case.input_prompt,
                            output=case.model_output,
                            reference=case.reference,
                            rubric=rubric,
                            temperature=request.configuration.get("temperature", 0.0),
                            max_tokens=request.configuration.get("max_tokens"),
                            timeout=request.configuration.get(
                                "timeout", settings.EVALUATION_TIMEOUT_SECONDS
                            ),
                            response_b=case.response_b,
                            prompt_version=prompt_version,
                        )

                        if judge_result.success is False:
                            raise EvaluationFailureException(
                                judge_result.error_message
                                or "Judge evaluation failed to parse response."
                            )

                        normalized = MetricsCalculator.normalize(
                            judge_result.score, rubric.scoring_scale
                        )
                        passed = MetricsCalculator.calculate_passed(
                            judge_result.score, rubric.scoring_scale, threshold
                        )

                        return {
                            "index": index,
                            "case": case,
                            "status": "COMPLETED",
                            "score": judge_result.score,
                            "normalized": normalized,
                            "passed": passed,
                            "judge_result": judge_result,
                            "error": None,
                        }

                    except Exception as exc:  # noqa: BLE001
                        last_error = exc
                        logger.error(
                            "Failed to evaluate test case: prompt=%s, attempt=%d, error=%s",
                            case.input_prompt[:120],
                            attempt + 1,
                            str(exc),
                        )
                        if (
                            not EvaluationPipeline._retryable(exc)
                            or attempt >= retry_count
                        ):
                            break
                        attempt += 1

                return {
                    "index": index,
                    "case": case,
                    "status": "FAILED",
                    "score": 0.0,
                    "normalized": 0.0,
                    "passed": False,
                    "judge_result": None,
                    "error": (
                        str(last_error) if last_error else "Unknown execution failure"
                    ),
                }

        # Concurrently execute test case evaluations
        tasks = [
            evaluate_single_case(idx, case)
            for idx, case in enumerate(request.test_cases)
        ]
        results = await asyncio.gather(*tasks)

        # Sort results by index to preserve order
        results.sort(key=lambda r: r["index"])

        scores: List[float] = []
        weights: List[float] = []
        completed_count = 0
        failed_count = 0
        total_cost: float = 0.0
        has_valid_cost: bool = False

        # Sequential DB persistence to prevent AsyncSession concurrency conflicts
        for res in results:
            case = res["case"]
            if res["status"] == "COMPLETED" and res["judge_result"] is not None:
                judge_result = res["judge_result"]
                result_record = await EvaluationRepository.create_result(
                    db=db,
                    run_id=run.id,
                    input_prompt=case.input_prompt,
                    model_output=case.model_output,
                    reference=case.reference,
                    judge=request.judge,
                    provider=request.provider,
                    prompt_version=prompt_version,
                    raw_response=judge_result.metadata.get("raw_response"),
                    status="COMPLETED",
                    score=judge_result.score,
                    passed=res["passed"],
                    confidence=judge_result.confidence,
                    reasoning=judge_result.reasoning,
                )

                if (
                    request.judge == "geval"
                    and "step_scores" in judge_result.criterion_scores
                ):
                    for step_score in judge_result.criterion_scores["step_scores"]:
                        await EvaluationRepository.create_rubric_score(
                            db=db,
                            result_id=result_record.id,
                            criterion_name=step_score.get("step", "Step"),
                            rubric_key=rubric.name.lower(),
                            score=float(step_score.get("score", 0.0)),
                            reasoning=step_score.get("reasoning"),
                        )

                pm = await EvaluationRepository.create_provider_metadata(
                    db=db,
                    result_id=result_record.id,
                    provider_name=request.provider,
                    model_name=judge_result.metadata.get(
                        "model_name", request.provider
                    ),
                    prompt_tokens=judge_result.metadata.get("prompt_tokens"),
                    completion_tokens=judge_result.metadata.get("completion_tokens"),
                    latency_ms=judge_result.metadata.get("latency_ms"),
                )

                if pm.cost_usd is not None:
                    total_cost += pm.cost_usd
                    has_valid_cost = True

                scores.append(res["normalized"])
                weights.append(rubric.weight)
                completed_count += 1
            else:
                failed_count += 1
                await EvaluationRepository.create_result(
                    db=db,
                    run_id=run.id,
                    input_prompt=case.input_prompt,
                    model_output=case.model_output,
                    reference=case.reference,
                    judge=request.judge,
                    provider=request.provider,
                    prompt_version=prompt_version,
                    raw_response=None,
                    status="FAILED",
                    error_message=res["error"],
                    score=0.0,
                    passed=False,
                    confidence=0.0,
                    reasoning=None,
                )

            await EvaluationRepository.update_run(
                db, run.id, completed_cases=completed_count, failed_cases=failed_count
            )
            await db.commit()

        if completed_count == 0 and failed_count > 0:
            status = "FAILED"
        elif failed_count > 0:
            status = "PARTIAL_SUCCESS"
        else:
            status = "COMPLETED"

        aggregate_score = MetricsCalculator.aggregate_weighted_score(scores, weights)
        if aggregate_score is None:
            aggregate_score = 0.0

        success_rate = (
            round(completed_count / len(request.test_cases), 4)
            if request.test_cases
            else 0.0
        )

        run = await EvaluationRepository.update_run(
            db=db,
            run_id=run.id,
            status=status,
            completed_cases=completed_count,
            failed_cases=failed_count,
            completed_at=get_utc_now(),
            aggregate_score=aggregate_score,
            total_cost_usd=round(total_cost, 8) if has_valid_cost else None,
            success_rate=success_rate,
            status_detail=(
                None
                if failed_count == 0
                else f"{failed_count} case(s) failed out of {len(request.test_cases)}."
            ),
        )
        await db.commit()

        if run is None:
            raise EvaluationFailureException("Evaluation run persistence failed.")

        await db.refresh(run)
        return run
