from typing import Any, Dict

from app.datasets.services.experiment import ExperimentService
from app.jobs.executors.base import BaseJobExecutor, ProgressCallback
from app.jobs.models.job import Job


class EvaluationExecutor(BaseJobExecutor):
    """Executor that runs LLM-as-a-Judge evaluations for an Experiment."""

    async def execute(
        self, job: Job, progress_callback: ProgressCallback
    ) -> Dict[str, Any]:
        experiment_id = job.payload.get("experiment_id")
        if not experiment_id:
            raise ValueError("Payload missing required 'experiment_id' key.")

        await progress_callback(10.0, "Locating experiment and dataset version...")

        from app.database.session import SessionLocal

        async with SessionLocal() as db:
            service = ExperimentService(db)
            await progress_callback(30.0, "Preparing test cases and configuration...")

            # Execute the evaluation pipeline
            await progress_callback(
                50.0, "Running judicial LLM evaluations (this may take a while)..."
            )
            experiment = await service.execute_experiment(experiment_id)

            await progress_callback(
                100.0, "Evaluation pipeline successfully completed."
            )
            return {
                "experiment_id": experiment.id,
                "status": experiment.status,
                "metrics": experiment.metrics,
                "cases_count": len(experiment.results),
            }
