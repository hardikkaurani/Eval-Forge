from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.jobs.models.job import ExecutionHistory, Job, Queue, Worker
from app.jobs.queue.tasks import run_background_job
from app.jobs.repositories.job import JobRepository
from app.jobs.schemas.job import (
    JobCreate,
    SystemMetricsResponse,
)


class JobService:
    """Service layer coordinating Job database interactions with Celery tasks dispatching."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = JobRepository(db)

    async def create_job(self, project_id: str, request: JobCreate) -> Job:
        # Create DB record in CREATED state
        job = await self.repo.create_job(
            name=request.name,
            queue_name=request.queue_name,
            payload={**request.payload, "project_id": project_id},
            max_retries=request.max_retries,
            scheduled_at=request.scheduled_at,
            recurring_cron=request.recurring_cron,
            timezone=request.timezone,
        )

        # Ensure target queue exists in DB config
        await self.repo.create_queue(request.queue_name)

        # Dispatch task to Celery
        if request.scheduled_at:
            # Delayed execution
            delay_seconds = int(
                (request.scheduled_at - datetime.utcnow()).total_seconds()
            )
            if delay_seconds > 0:
                run_background_job.apply_async(
                    args=[job.id],
                    countdown=delay_seconds,
                    queue=request.queue_name,
                )
            else:
                run_background_job.apply_async(args=[job.id], queue=request.queue_name)
        else:
            # Immediate dispatch
            run_background_job.apply_async(args=[job.id], queue=request.queue_name)

        # Transition job status to QUEUED in DB
        await self.repo.update_job_status(job.id, "QUEUED")
        return job

    async def get_job(self, job_id: str) -> Job:
        job = await self.repo.get_job(job_id, include_details=True)
        if not job:
            raise NotFoundException(f"Job with ID '{job_id}' not found.")
        return job

    async def list_jobs(
        self,
        queue_name: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Job], int]:
        skip = (page - 1) * page_size
        return await self.repo.list_jobs(
            queue_name=queue_name,
            status=status,
            search=search,
            skip=skip,
            limit=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def cancel_job(self, job_id: str, reason: Optional[str] = None) -> Job:
        job = await self.repo.get_job(job_id)
        if not job:
            raise NotFoundException(f"Job with ID '{job_id}' not found.")

        # Transition to CANCELLED state
        cancelled_job = await self.repo.cancel_job(
            job_id, reason=reason, cancelled_by="user"
        )
        return cancelled_job

    async def list_queues(self) -> List[Queue]:
        return await self.repo.list_queues()

    async def list_workers(self) -> List[Worker]:
        return await self.repo.list_workers()

    async def get_system_metrics(self) -> SystemMetricsResponse:
        """Aggregates execution rates, queue latency, and load metrics for the entire jobs system."""
        # Active/Queued/Running/Failed counts
        q_size_res = await self.db.execute(
            select(func.count(Job.id)).where(Job.status == "QUEUED")
        )
        queue_size = q_size_res.scalar_one()

        running_res = await self.db.execute(
            select(func.count(Job.id)).where(Job.status == "RUNNING")
        )
        running_jobs = running_res.scalar_one()

        failed_res = await self.db.execute(
            select(func.count(Job.id)).where(Job.status == "FAILED")
        )
        failed_jobs = failed_res.scalar_one()

        completed_res = await self.db.execute(
            select(func.count(Job.id)).where(Job.status == "COMPLETED")
        )
        completed_jobs = completed_res.scalar_one()

        workers = await self.repo.list_workers()
        worker_count = len(workers)

        # Average duration calculation
        dur_res = await self.db.execute(
            select(func.avg(ExecutionHistory.duration_seconds))
        )
        avg_exec = dur_res.scalar() or 0.0

        # Success rate
        total_runs = completed_jobs + failed_jobs
        success_rate = (completed_jobs / total_runs) if total_runs > 0 else 1.0

        # Calculate average queue latency (started_at - queued_at) in seconds
        latency_stmt = select(Job.started_at, Job.queued_at).where(
            and_(Job.started_at.is_not(None), Job.queued_at.is_not(None))
        )
        latency_res = await self.db.execute(latency_stmt)
        latencies = []
        for row in latency_res.all():
            if row[0] and row[1]:
                latencies.append((row[0] - row[1]).total_seconds())
        avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0

        # System load/health
        utilization = 0.0
        if worker_count > 0:
            active_workers = sum(1 for w in workers if w.status == "BUSY")
            utilization = active_workers / worker_count

        # Build dummy metrics for error frequencies and LLM providers
        error_frequencies = {}
        provider_latencies = {"openai": 1.24, "gemini": 1.86, "anthropic": 2.11}

        return SystemMetricsResponse(
            queue_size=queue_size,
            worker_count=worker_count,
            running_jobs=running_jobs,
            failed_jobs=failed_jobs,
            average_execution_time=round(avg_exec, 2),
            retry_rate=0.05,
            success_rate=round(success_rate, 4),
            queue_latency=round(avg_latency, 2),
            worker_utilization=round(utilization, 2),
            error_frequency=error_frequencies,
            provider_latency=provider_latencies,
        )
