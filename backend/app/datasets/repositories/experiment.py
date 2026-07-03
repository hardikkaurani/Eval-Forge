from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dataset import Experiment


class ExperimentRepository:
    """Repository handling database operations for tracking evaluation Experiments."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_experiment(
        self,
        project_id: str,
        dataset_version_id: str,
        name: str,
        description: Optional[str],
        judge: str,
        provider: str,
        model: Optional[str],
        configuration: Dict[str, Any],
    ) -> Experiment:
        experiment = Experiment(
            project_id=project_id,
            dataset_version_id=dataset_version_id,
            name=name,
            description=description,
            judge=judge,
            provider=provider,
            model=model,
            configuration=configuration,
            status="PENDING",
            metrics={},
            results=[],
        )
        self.db.add(experiment)
        await self.db.flush()
        return experiment

    async def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        result = await self.db.execute(
            select(Experiment)
            .where(Experiment.id == experiment_id)
            .options(selectinload(Experiment.dataset_version))
        )
        return result.scalar_one_or_none()

    async def list_experiments(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Experiment], int]:
        query = select(Experiment).where(Experiment.project_id == project_id)

        if search:
            query = query.where(
                or_(
                    Experiment.name.ilike(f"%{search}%"),
                    Experiment.description.ilike(f"%{search}%"),
                )
            )

        if status:
            query = query.where(Experiment.status == status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Paginated query
        query = query.order_by(Experiment.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        experiments = list(result.scalars().all())

        return experiments, total

    async def update_experiment(self, experiment_id: str, update_data: Dict[str, Any]) -> Optional[Experiment]:
        experiment = await self.get_experiment(experiment_id)
        if not experiment:
            return None

        for key, val in update_data.items():
            if val is not None:
                setattr(experiment, key, val)

        await self.db.flush()
        return experiment

    async def delete_experiment(self, experiment_id: str) -> bool:
        experiment = await self.get_experiment(experiment_id)
        if not experiment:
            return False

        await self.db.delete(experiment)
        await self.db.flush()
        return True
