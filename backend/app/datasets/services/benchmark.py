from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.datasets.exceptions.exceptions import BenchmarkSuiteNotFoundException
from app.datasets.repositories.benchmark import BenchmarkRepository
from app.datasets.repositories.dataset import DatasetRepository
from app.models.dataset import BenchmarkSuite, Dataset, DatasetVersion, Experiment


class BenchmarkService:
    """Service layer orchestrating Benchmark Suites management and dashboard data aggregation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.benchmark_repo = BenchmarkRepository(db)
        self.dataset_repo = DatasetRepository(db)

    async def create_benchmark_suite(
        self,
        project_id: str,
        name: str,
        description: Optional[str] = None,
        tags: List[str] = None,
        dataset_ids: List[str] = None,
    ) -> BenchmarkSuite:
        tags = tags or []
        dataset_ids = dataset_ids or []

        suite = await self.benchmark_repo.create_benchmark_suite(
            project_id=project_id,
            name=name,
            description=description,
            tags=tags,
            metadata_json={},
        )

        if dataset_ids:
            await self.benchmark_repo.set_suite_datasets(suite.id, dataset_ids)

        await self.db.commit()
        # Fetch populated suite
        return await self.get_benchmark_suite(suite.id)

    async def get_benchmark_suite(self, suite_id: str) -> BenchmarkSuite:
        suite = await self.benchmark_repo.get_benchmark_suite(suite_id)
        if not suite:
            raise BenchmarkSuiteNotFoundException(suite_id)
        return suite

    async def list_benchmark_suites(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> Tuple[List[BenchmarkSuite], int]:
        return await self.benchmark_repo.list_benchmark_suites(
            project_id=project_id,
            skip=skip,
            limit=limit,
            search=search,
        )

    async def update_benchmark_suite(
        self,
        suite_id: str,
        update_data: Dict[str, Any],
    ) -> BenchmarkSuite:
        dataset_ids = update_data.pop("dataset_ids", None)

        suite = await self.benchmark_repo.update_benchmark_suite(suite_id, update_data)
        if not suite:
            raise BenchmarkSuiteNotFoundException(suite_id)

        if dataset_ids is not None:
            await self.benchmark_repo.set_suite_datasets(suite_id, dataset_ids)

        await self.db.commit()
        return await self.get_benchmark_suite(suite_id)

    async def delete_benchmark_suite(self, suite_id: str) -> None:
        success = await self.benchmark_repo.delete_benchmark_suite(suite_id)
        if not success:
            raise BenchmarkSuiteNotFoundException(suite_id)
        await self.db.commit()

    async def get_dashboard_metrics(self, project_id: str) -> Dict[str, Any]:
        """Aggregates metrics and statistics for datasets and benchmarks in a project."""
        # 1. Dataset stats
        ds_count_result = await self.db.execute(
            select(func.count(Dataset.id)).where(Dataset.project_id == project_id)
        )
        total_datasets = ds_count_result.scalar() or 0

        # 2. Benchmark suite stats
        bs_count_result = await self.db.execute(
            select(func.count(BenchmarkSuite.id)).where(
                BenchmarkSuite.project_id == project_id
            )
        )
        total_suites = bs_count_result.scalar() or 0

        # 3. Experiment stats
        exp_count_result = await self.db.execute(
            select(func.count(Experiment.id)).where(Experiment.project_id == project_id)
        )
        total_experiments = exp_count_result.scalar() or 0

        # Status distribution of experiments
        exp_status_result = await self.db.execute(
            select(Experiment.status, func.count(Experiment.id))
            .where(Experiment.project_id == project_id)
            .group_by(Experiment.status)
        )
        status_distribution = dict(exp_status_result.all())

        # 4. Total record count in all dataset versions
        record_count_result = await self.db.execute(
            select(func.sum(DatasetVersion.record_count))
            .join(Dataset)
            .where(Dataset.project_id == project_id)
        )
        total_records = int(record_count_result.scalar() or 0)

        # 5. Average data quality score across datasets
        # Fetching all datasets for project to average their metadata_json.data_quality_score
        datasets_result = await self.db.execute(
            select(Dataset.metadata_json).where(Dataset.project_id == project_id)
        )
        scores = []
        for row in datasets_result.all():
            meta = row[0]
            if isinstance(meta, dict) and "data_quality_score" in meta:
                scores.append(meta["data_quality_score"])

        avg_quality_score = round(sum(scores) / len(scores), 2) if scores else 0.0

        return {
            "total_datasets": total_datasets,
            "total_benchmark_suites": total_suites,
            "total_experiments": total_experiments,
            "total_records": total_records,
            "average_data_quality_score": avg_quality_score,
            "experiments_by_status": status_distribution,
        }
