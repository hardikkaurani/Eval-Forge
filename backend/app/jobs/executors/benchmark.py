from typing import Any, Dict

from app.datasets.services.benchmark import BenchmarkService
from app.datasets.services.experiment import ExperimentService
from app.jobs.executors.base import BaseJobExecutor, ProgressCallback
from app.jobs.models.job import Job


class BenchmarkExecutor(BaseJobExecutor):
    """Executor that runs all evaluations of a Benchmark Suite across multiple datasets."""

    async def execute(
        self, job: Job, progress_callback: ProgressCallback
    ) -> Dict[str, Any]:
        payload = job.payload
        suite_id = payload.get("suite_id")
        judge = payload.get("judge", "rubric")
        provider = payload.get("provider", "openai")
        model = payload.get("model")
        configuration = payload.get("configuration") or {}

        if not suite_id:
            raise ValueError("Payload missing required 'suite_id' key.")

        await progress_callback(10.0, "Resolving benchmark suite datasets mapping...")

        from app.database.session import SessionLocal

        async with SessionLocal() as db:
            benchmark_service = BenchmarkService(db)
            experiment_service = ExperimentService(db)

            suite = await benchmark_service.get_benchmark_suite(suite_id)
            datasets = suite.datasets

            if not datasets:
                raise ValueError(
                    "No datasets associated with this benchmark suite to execute."
                )

            runs = []
            total_datasets = len(datasets)
            for idx, dataset in enumerate(datasets):
                step_progress = 10.0 + (idx / total_datasets) * 80.0
                await progress_callback(
                    step_progress,
                    f"Evaluating dataset '{dataset.name}' ({idx + 1}/{total_datasets})...",
                )

                versions = dataset.versions
                if not versions:
                    continue
                latest_version = versions[-1]

                # Create evaluation experiment under this suite run
                experiment = await experiment_service.create_experiment(
                    project_id=suite.project_id,
                    dataset_version_id=latest_version.id,
                    name=f"Benchmark: {suite.name} - {dataset.name}",
                    description=f"Automated benchmark suite evaluation run for suite: {suite.name}",
                    judge=judge,
                    provider=provider,
                    model=model,
                    configuration=configuration,
                )

                # Run the evaluation experiment
                completed_exp = await experiment_service.execute_experiment(
                    experiment.id
                )
                runs.append(
                    {
                        "dataset_id": dataset.id,
                        "dataset_name": dataset.name,
                        "experiment_id": completed_exp.id,
                        "status": completed_exp.status,
                        "metrics": completed_exp.metrics,
                    }
                )

            await progress_callback(100.0, "Benchmark suite evaluations run completed.")
            return {"suite_id": suite_id, "dataset_runs": runs}
