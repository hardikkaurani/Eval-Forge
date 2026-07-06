# ruff: noqa: E402
from typing import Dict, Type

from app.jobs.executors.base import BaseJobExecutor


class JobRegistry:
    """Registry class holding reference mappings between job type names and executors."""

    def __init__(self) -> None:
        self._executors: Dict[str, Type[BaseJobExecutor]] = {}

    def register(self, name: str, executor_cls: Type[BaseJobExecutor]) -> None:
        """Registers an executor class under a unique job type name."""
        self._executors[name] = executor_cls

    def get(self, name: str) -> Type[BaseJobExecutor]:
        """Retrieves the executor class mapped to a given job type name."""
        if name not in self._executors:
            raise KeyError(f"No background executor registered for job type '{name}'.")
        return self._executors[name]

    def list_registered_types(self) -> list[str]:
        """Lists all registered job type names."""
        return list(self._executors.keys())


job_registry = JobRegistry()

# Register built-in executors
from app.jobs.executors.analytics_aggregation import AnalyticsAggregationExecutor
from app.jobs.executors.benchmark import BenchmarkExecutor
from app.jobs.executors.dataset_export import DatasetExportExecutor
from app.jobs.executors.dataset_import import DatasetImportExecutor
from app.jobs.executors.evaluation import EvaluationExecutor

job_registry.register("evaluation", EvaluationExecutor)
job_registry.register("dataset_import", DatasetImportExecutor)
job_registry.register("dataset_export", DatasetExportExecutor)
job_registry.register("benchmark", BenchmarkExecutor)
job_registry.register("analytics_aggregation", AnalyticsAggregationExecutor)
