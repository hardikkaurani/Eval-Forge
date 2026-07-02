from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.evaluation.pipelines.pipeline import EvaluationPipeline
from app.evaluation.repositories.evaluation import EvaluationRepository
from app.evaluation.schemas.evaluation import BatchEvaluationRequest
from app.models.evaluation import Evaluation, EvaluationRun


class EvaluationService:
    """Service class encapsulating business validation boundaries for evaluations."""

    @staticmethod
    async def create_evaluation(
        db: AsyncSession, project_id: str, name: str, description: str | None = None
    ) -> Evaluation:
        from app.database.repository import ProjectRepository

        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException(f"Project with ID '{project_id}' not found.")

        return await EvaluationRepository.create_evaluation(
            db=db, project_id=project_id, name=name, description=description
        )

    @staticmethod
    async def get_evaluation(db: AsyncSession, id: str) -> Evaluation:
        evaluation = await EvaluationRepository.get_evaluation(db, id)
        if not evaluation:
            raise NotFoundException(f"Evaluation with ID '{id}' not found.")
        return evaluation

    @staticmethod
    async def list_evaluations(
        db: AsyncSession, project_id: str, page: int = 1, page_size: int = 10
    ) -> Tuple[List[Evaluation], int]:
        skip = (page - 1) * page_size
        evals = await EvaluationRepository.list_evaluations(
            db, project_id, skip=skip, limit=page_size
        )

        from sqlalchemy import and_, func, select

        stmt = select(func.count(Evaluation.id)).where(
            and_(Evaluation.project_id == project_id, Evaluation.deleted_at.is_(None))
        )
        total_res = await db.execute(stmt)
        total = total_res.scalar_one()

        return evals, total

    @staticmethod
    async def delete_evaluation(db: AsyncSession, id: str) -> None:
        success = await EvaluationRepository.delete_evaluation(db, id)
        if not success:
            raise NotFoundException(f"Evaluation with ID '{id}' not found.")

    @staticmethod
    async def run_batch_evaluation(
        db: AsyncSession, request: BatchEvaluationRequest
    ) -> EvaluationRun:
        from app.database.repository import ProjectRepository

        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(request.project_id)
        if not project:
            raise NotFoundException(
                f"Project with ID '{request.project_id}' not found."
            )

        return await EvaluationPipeline.run(db, request)


class EvaluationCatalogService:
    """Read-only service for registered providers, judges, and rubrics."""

    @staticmethod
    def list_providers() -> list[dict[str, str | None]]:
        from app.evaluation.registry.registry import provider_registry

        return [
            {
                "key": entry.key,
                "name": entry.name,
                "description": entry.description,
            }
            for entry in provider_registry.list_entries()
        ]

    @staticmethod
    def list_judges() -> list[dict[str, str | None]]:
        from app.evaluation.registry.registry import judge_registry

        return [
            {
                "key": entry.key,
                "name": entry.name,
                "description": entry.description,
            }
            for entry in judge_registry.list_entries()
        ]

    @staticmethod
    def list_rubrics() -> list[dict[str, str | int | None]]:
        from app.evaluation.rubrics.rubrics import list_rubrics

        return [
            {
                "key": key,
                "name": rubric.name,
                "description": rubric.description,
                "scoring_scale": rubric.scoring_scale,
            }
            for key, rubric in list_rubrics().items()
        ]
