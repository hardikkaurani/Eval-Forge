from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import (
    Evaluation,
    EvaluationResult,
    EvaluationRun,
    ProviderMetadata,
    RubricScore,
)
from app.utils.time import get_utc_now


class EvaluationRepository:
    """Repository class managing async database persistence for evaluation engine entities."""

    @staticmethod
    async def create_evaluation(
        db: AsyncSession,
        project_id: str,
        name: str,
        description: str | None = None
    ) -> Evaluation:
        evaluation = Evaluation(
            project_id=project_id,
            name=name,
            description=description
        )
        db.add(evaluation)
        await db.flush()
        return evaluation

    @staticmethod
    async def get_evaluation(db: AsyncSession, id: str) -> Optional[Evaluation]:
        stmt = select(Evaluation).where(
            and_(Evaluation.id == id, Evaluation.deleted_at.is_(None))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_evaluations(
        db: AsyncSession,
        project_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Evaluation]:
        stmt = (
            select(Evaluation)
            .where(and_(Evaluation.project_id == project_id, Evaluation.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .order_by(Evaluation.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_evaluation(db: AsyncSession, id: str) -> bool:
        stmt = select(Evaluation).where(
            and_(Evaluation.id == id, Evaluation.deleted_at.is_(None))
        )
        result = await db.execute(stmt)
        evaluation = result.scalar_one_or_none()
        if not evaluation:
            return False

        evaluation.deleted_at = get_utc_now()
        db.add(evaluation)
        await db.flush()
        return True

    @staticmethod
    async def create_run(
        db: AsyncSession,
        evaluation_id: str,
        judge: str,
        provider: str,
        configuration: Dict[str, Any],
        total_cases: int
    ) -> EvaluationRun:
        run = EvaluationRun(
            evaluation_id=evaluation_id,
            status="PENDING",
            judge=judge,
            provider=provider,
            configuration=configuration,
            total_cases=total_cases,
            started_at=get_utc_now()
        )
        db.add(run)
        await db.flush()
        return run

    @staticmethod
    async def get_run(db: AsyncSession, run_id: str) -> Optional[EvaluationRun]:
        stmt = select(EvaluationRun).where(EvaluationRun.id == run_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_run(
        db: AsyncSession,
        run_id: str,
        **updates
    ) -> Optional[EvaluationRun]:
        stmt = select(EvaluationRun).where(EvaluationRun.id == run_id)
        result = await db.execute(stmt)
        run = result.scalar_one_or_none()
        if not run:
            return None

        for key, value in updates.items():
            if hasattr(run, key):
                setattr(run, key, value)

        db.add(run)
        await db.flush()
        return run

    @staticmethod
    async def create_result(
        db: AsyncSession,
        run_id: str,
        input_prompt: str,
        model_output: str,
        score: float,
        passed: bool,
        reference: str | None = None,
        confidence: float | None = None,
        reasoning: str | None = None
    ) -> EvaluationResult:
        result = EvaluationResult(
            run_id=run_id,
            input_prompt=input_prompt,
            model_output=model_output,
            reference=reference,
            score=score,
            passed=passed,
            confidence=confidence,
            reasoning=reasoning
        )
        db.add(result)
        await db.flush()
        return result

    @staticmethod
    async def create_rubric_score(
        db: AsyncSession,
        result_id: str,
        criterion_name: str,
        score: float,
        reasoning: str | None = None
    ) -> RubricScore:
        rubric_score = RubricScore(
            result_id=result_id,
            criterion_name=criterion_name,
            score=score,
            reasoning=reasoning
        )
        db.add(rubric_score)
        await db.flush()
        return rubric_score

    @staticmethod
    async def create_provider_metadata(
        db: AsyncSession,
        result_id: str,
        model_name: str,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        latency_ms: int | None = None
    ) -> ProviderMetadata:
        metadata = ProviderMetadata(
            result_id=result_id,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms
        )
        db.add(metadata)
        await db.flush()
        return metadata
