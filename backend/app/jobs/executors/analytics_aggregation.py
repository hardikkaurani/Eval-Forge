from typing import Any, Dict

from app.analytics.services import AnalyticsService
from app.jobs.executors.base import BaseJobExecutor, ProgressCallback
from app.jobs.models.job import Job


class AnalyticsAggregationExecutor(BaseJobExecutor):
    """Executor that runs aggregate snapshot compilations in the background."""

    async def execute(
        self, job: Job, progress_callback: ProgressCallback
    ) -> Dict[str, Any]:
        project_id = job.payload.get("project_id")
        scope = job.payload.get("scope", "project")
        scope_id = job.payload.get("scope_id")

        if not project_id:
            raise ValueError("Payload missing required 'project_id' key.")

        await progress_callback(10.0, "Starting background analytics aggregation...")

        from app.database.session import SessionLocal

        async with SessionLocal() as db:
            service = AnalyticsService(db)
            await progress_callback(
                40.0, "Computing averages, medians, latencies, and token costs..."
            )

            snapshot = await service.compute_and_save_snapshot(
                project_id, scope, scope_id
            )

            await progress_callback(
                100.0, "Analytics snapshot aggregation successfully completed."
            )
            return {
                "snapshot_id": snapshot.id,
                "project_id": snapshot.project_id,
                "total_evaluations": snapshot.total_evaluations,
                "success_rate": snapshot.success_rate,
                "avg_score": snapshot.avg_score,
                "avg_latency_ms": snapshot.avg_latency_ms,
                "total_tokens": snapshot.total_tokens,
                "estimated_cost": snapshot.estimated_cost,
            }
