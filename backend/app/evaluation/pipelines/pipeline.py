import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.evaluation.metrics.engine import MetricsCalculator
from app.evaluation.registry.registry import judge_registry, provider_registry
from app.evaluation.repositories.evaluation import EvaluationRepository
from app.evaluation.rubrics.rubrics import BUILT_IN_RUBRICS, Rubric
from app.evaluation.schemas.evaluation import BatchEvaluationRequest
from app.evaluation.validators.validators import EvaluationValidator
from app.models.evaluation import EvaluationRun
from app.utils.time import get_utc_now

logger = logging.getLogger(__name__)

class EvaluationPipeline:
    """Orchestrates validation, LLM execution, metrics calculations, and DB persistence for batch runs."""

    @staticmethod
    async def run(db: AsyncSession, request: BatchEvaluationRequest) -> EvaluationRun:
        # 1. Validation
        EvaluationValidator.validate_provider(request.provider)
        EvaluationValidator.validate_judge(request.judge)
        EvaluationValidator.validate_configuration(request.configuration)

        # 2. Rubric Resolution
        if request.rubric:
            rubric = Rubric(
                name=request.rubric.name,
                description=request.rubric.description,
                weight=request.rubric.weight,
                scoring_scale=request.rubric.scoring_scale,
                prompt_template=request.rubric.prompt_template
            )
        else:
            # Default to Correctness rubric
            rubric = BUILT_IN_RUBRICS["correctness"]

        # 3. Provider & Judge Instantiation
        provider_cls = provider_registry.get(request.provider)
        # Setup specific provider model from configuration if provided
        model_name = request.configuration.get("model")
        if model_name:
            provider = provider_cls(model=model_name)
        else:
            provider = provider_cls()

        judge_cls = judge_registry.get(request.judge)
        judge = judge_cls(provider=provider)

        # 4. DB Entity Creation (Evaluation & EvaluationRun)
        evaluation = await EvaluationRepository.create_evaluation(
            db=db,
            project_id=request.project_id,
            name=request.evaluation_name,
            description=request.evaluation_description
        )

        run = await EvaluationRepository.create_run(
            db=db,
            evaluation_id=evaluation.id,
            judge=request.judge,
            provider=request.provider,
            configuration=request.configuration,
            total_cases=len(request.test_cases)
        )

        await db.commit()

        # Update status to RUNNING
        run = await EvaluationRepository.update_run(db, run.id, status="RUNNING")
        await db.commit()

        scores: List[float] = []
        completed_count = 0
        threshold = request.configuration.get("threshold", 0.7)

        # 5. Execute Test Cases
        for case in request.test_cases:
            try:
                # Validate case input
                EvaluationValidator.validate_case(
                    prompt=case.input_prompt,
                    output=case.model_output,
                    reference=case.reference,
                    judge=request.judge
                )

                # Execute LLM Judge
                judge_result = await judge.evaluate(
                    prompt=case.input_prompt,
                    output=case.model_output,
                    reference=case.reference,
                    rubric=rubric,
                    temperature=request.configuration.get("temperature", 0.0),
                    max_tokens=request.configuration.get("max_tokens"),
                    timeout=request.configuration.get("timeout", 30.0),
                    response_b=case.response_b
                )

                # Metrics calculation
                normalized = MetricsCalculator.normalize(judge_result.score, rubric.scoring_scale)
                passed = MetricsCalculator.calculate_passed(judge_result.score, rubric.scoring_scale, threshold)

                # Persist result
                result_record = await EvaluationRepository.create_result(
                    db=db,
                    run_id=run.id,
                    input_prompt=case.input_prompt,
                    model_output=case.model_output,
                    reference=case.reference,
                    score=judge_result.score,
                    passed=passed,
                    confidence=judge_result.confidence,
                    reasoning=judge_result.reasoning
                )

                # Persist Rubric/Criterion sub-scores if G-Eval
                if request.judge == "geval" and "step_scores" in judge_result.criterion_scores:
                    for step_score in judge_result.criterion_scores["step_scores"]:
                        await EvaluationRepository.create_rubric_score(
                            db=db,
                            result_id=result_record.id,
                            criterion_name=step_score.get("step", "Step"),
                            score=float(step_score.get("score", 0.0))
                        )

                # Persist Provider Metadata
                await EvaluationRepository.create_provider_metadata(
                    db=db,
                    result_id=result_record.id,
                    model_name=judge_result.metadata.get("model_name", request.provider),
                    prompt_tokens=judge_result.metadata.get("prompt_tokens"),
                    completion_tokens=judge_result.metadata.get("completion_tokens"),
                    latency_ms=judge_result.metadata.get("latency_ms")
                )

                scores.append(normalized)
                completed_count += 1

                # Update run progress incrementally
                await EvaluationRepository.update_run(db, run.id, completed_cases=completed_count)
                await db.commit()

            except Exception as e:
                logger.error(f"Failed to evaluate test case: {case.input_prompt[:50]}... Error: {str(e)}")
                # Isolation: we continue execution of other cases to ensure partial completion
                continue

        # 6. Run Completion Aggregations
        status = "COMPLETED" if completed_count > 0 else "FAILED"
        agg_score = sum(scores) / len(scores) if scores else 0.0

        run = await EvaluationRepository.update_run(
            db=db,
            run_id=run.id,
            status=status,
            completed_cases=completed_count,
            completed_at=get_utc_now(),
            aggregate_score=agg_score
        )
        await db.commit()

        # Reload relation data for response formatting
        await db.refresh(run)
        return run
