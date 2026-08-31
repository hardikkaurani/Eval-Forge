from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dataset import BenchmarkDataset, BenchmarkSuite


class BenchmarkRepository:
    """Repository handling database operations for Benchmark Suites."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_benchmark_suite(
        self,
        project_id: str,
        name: str,
        description: Optional[str],
        tags: List[str],
        metadata_json: Dict[str, Any],
    ) -> BenchmarkSuite:
        suite = BenchmarkSuite(
            project_id=project_id,
            name=name,
            description=description,
            tags=tags,
            metadata_json=metadata_json,
        )
        self.db.add(suite)
        await self.db.flush()
        return suite

    async def get_benchmark_suite(self, suite_id: str) -> Optional[BenchmarkSuite]:
        result = await self.db.execute(
            select(BenchmarkSuite)
            .where(BenchmarkSuite.id == suite_id)
            .options(selectinload(BenchmarkSuite.datasets))
        )
        return result.scalar_one_or_none()

    async def list_benchmark_suites(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> Tuple[List[BenchmarkSuite], int]:
        query = select(BenchmarkSuite).where(BenchmarkSuite.project_id == project_id)

        if search:
            query = query.where(
                or_(
                    BenchmarkSuite.name.ilike(f"%{search}%"),
                    BenchmarkSuite.description.ilike(f"%{search}%"),
                )
            )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Paginated query
        query = (
            query.order_by(BenchmarkSuite.created_at.desc()).offset(skip).limit(limit)
        )
        result = await self.db.execute(query)
        suites = list(result.scalars().all())

        return suites, total

    async def update_benchmark_suite(
        self, suite_id: str, update_data: Dict[str, Any]
    ) -> Optional[BenchmarkSuite]:
        suite = await self.get_benchmark_suite(suite_id)
        if not suite:
            return None

        # Enforce field immutability: id and project_id cannot be reassigned or mutated
        update_data.pop("id", None)
        update_data.pop("project_id", None)

        for key, val in update_data.items():
            if val is not None:
                setattr(suite, key, val)

        await self.db.flush()
        return suite

    async def delete_benchmark_suite(self, suite_id: str) -> bool:
        suite = await self.get_benchmark_suite(suite_id)
        if not suite:
            return False

        await self.db.delete(suite)
        await self.db.flush()
        return True

    async def set_suite_datasets(self, suite_id: str, dataset_ids: List[str]) -> None:
        # Delete old associations
        await self.db.execute(
            delete(BenchmarkDataset).where(
                BenchmarkDataset.benchmark_suite_id == suite_id
            )
        )

        # Deduplicate dataset_ids while preserving order to prevent primary key collisions
        unique_dataset_ids = list(dict.fromkeys(dataset_ids))

        # Insert new associations
        for d_id in unique_dataset_ids:
            association = BenchmarkDataset(benchmark_suite_id=suite_id, dataset_id=d_id)
            self.db.add(association)

        await self.db.flush()
