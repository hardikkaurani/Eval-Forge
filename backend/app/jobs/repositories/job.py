from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.jobs.exceptions import (
    InvalidStatusTransitionException,
    JobNotFoundException,
    WorkerNotFoundException,
)
from app.jobs.models.job import (
    Cancellation,
    ExecutionHistory,
    Job,
    JobLog,
    Queue,
    RetryHistory,
    Worker,
)
from app.utils.time import get_utc_now

VALID_TRANSITIONS = {
    "CREATED": {"QUEUED", "CANCELLED"},
    "QUEUED": {"WAITING", "RUNNING", "CANCELLED"},
    "WAITING": {"RUNNING", "CANCELLED"},
    "RUNNING": {"COMPLETED", "FAILED", "CANCELLED", "RETRYING"},
    "RETRYING": {"QUEUED", "RUNNING", "FAILED", "CANCELLED"},
    "COMPLETED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
    "EXPIRED": set(),
}


class JobRepository:
    """Repository handling persistence, validation, status transitions, and queries for all job models."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_job(
        self,
        name: str,
        queue_name: str,
        payload: Dict[str, Any],
        max_retries: int = 3,
        scheduled_at: Optional[datetime] = None,
        recurring_cron: Optional[str] = None,
        timezone: str = "UTC",
    ) -> Job:
        """Creates a background job in CREATED state."""
        job = Job(
            name=name,
            queue_name=queue_name,
            payload=payload,
            max_retries=max_retries,
            status="CREATED",
            scheduled_at=scheduled_at,
            recurring_cron=recurring_cron,
            timezone=timezone,
            created_at=get_utc_now(),
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_job(
        self, job_id: str, include_details: bool = False
    ) -> Optional[Job]:
        """Retrieves a Job, optionally prefetching related history/logs."""
        if include_details:
            query = (
                select(Job)
                .where(Job.id == job_id)
                .options(
                    selectinload(Job.logs),
                    selectinload(Job.execution_history),
                    selectinload(Job.retry_history),
                    selectinload(Job.cancellation),
                )
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        return await self.db.get(Job, job_id)

    async def list_jobs(
        self,
        queue_name: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Job], int]:
        """Lists jobs with sorting, filtering, and page pagination."""
        query = select(Job)
        count_query = select(func.count(Job.id))

        # Filtering
        conditions = []
        if queue_name:
            conditions.append(Job.queue_name == queue_name)
        if status:
            conditions.append(Job.status == status)
        if search:
            conditions.append(
                or_(
                    Job.name.ilike(f"%{search}%"),
                    Job.id.ilike(f"%{search}%"),
                    Job.error_message.ilike(f"%{search}%"),
                )
            )

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Sorting
        sort_col = getattr(Job, sort_by, Job.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_col))
        else:
            query = query.order_by(asc(sort_col))

        # Pagination
        query = query.offset(skip).limit(limit)

        jobs_res = await self.db.execute(query)
        jobs = list(jobs_res.scalars().all())

        count_res = await self.db.execute(count_query)
        total = count_res.scalar_one()

        return jobs, total

    async def update_job_status(
        self,
        job_id: str,
        target_status: str,
        error_message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        worker_id: Optional[str] = None,
    ) -> Job:
        """Safely updates a job status, performing validation of the state transitions."""
        job = await self.get_job(job_id)
        if not job:
            raise JobNotFoundException(job_id)

        current = job.status
        if target_status not in VALID_TRANSITIONS[current]:
            # Allow same-status updates (e.g. updating progress during RUNNING)
            if target_status != current:
                raise InvalidStatusTransitionException(job_id, current, target_status)

        job.status = target_status
        now = get_utc_now()

        if target_status == "QUEUED":
            job.queued_at = now
        elif target_status == "RUNNING":
            job.started_at = now
            job.worker_id = worker_id or job.worker_id
        elif target_status in {"COMPLETED", "FAILED", "CANCELLED", "EXPIRED"}:
            job.completed_at = now
            if error_message:
                job.error_message = error_message
            if result:
                job.result = result

        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def update_job_progress(
        self, job_id: str, progress: float, current_step: Optional[str] = None
    ) -> Job:
        """Updates the running completion progress percentage and stage step."""
        job = await self.get_job(job_id)
        if not job:
            raise JobNotFoundException(job_id)

        job.progress = max(0.0, min(100.0, progress))
        if current_step:
            job.current_step = current_step

        await self.db.commit()
        return job

    async def add_job_log(
        self, job_id: str, message: str, log_level: str = "INFO"
    ) -> JobLog:
        """Appends a timestamped execution log line for a specific Job ID."""
        log = JobLog(
            job_id=job_id,
            log_level=log_level,
            message=message,
            created_at=get_utc_now(),
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    # Cancellation
    async def cancel_job(
        self, job_id: str, reason: Optional[str] = None, cancelled_by: str = "user"
    ) -> Job:
        """Records a job cancellation entry and transitions the job to CANCELLED state."""
        job = await self.update_job_status(job_id, "CANCELLED")

        cancellation = Cancellation(
            job_id=job_id,
            reason=reason,
            cancelled_by=cancelled_by,
            cancelled_at=get_utc_now(),
        )
        self.db.add(cancellation)
        await self.db.commit()
        return job

    # Retry History
    async def record_retry(
        self, job_id: str, error_message: Optional[str] = None, delay_seconds: int = 0
    ) -> Job:
        """Records a retry attempt, bumps retry_count, and sets future next-attempt delay."""
        job = await self.get_job(job_id)
        if not job:
            raise JobNotFoundException(job_id)

        job.retry_count += 1
        now = get_utc_now()
        next_attempt = datetime.fromtimestamp(now.timestamp() + delay_seconds)

        history = RetryHistory(
            job_id=job_id,
            retry_attempt=job.retry_count,
            error_message=error_message,
            attempted_at=now,
            next_attempt_at=next_attempt,
        )
        self.db.add(history)
        await self.db.commit()
        return job

    # Worker CRUD
    async def register_worker(
        self, worker_id: str, name: str, queue_name: str
    ) -> Worker:
        """Registers or updates a worker with a heartbeat timestamp."""
        worker = await self.db.get(Worker, worker_id)
        if worker:
            worker.status = "IDLE"
            worker.last_heartbeat = get_utc_now()
        else:
            worker = Worker(
                id=worker_id,
                name=name,
                status="IDLE",
                queue_name=queue_name,
                last_heartbeat=get_utc_now(),
                system_load={},
            )
            self.db.add(worker)
        await self.db.commit()
        await self.db.refresh(worker)
        return worker

    async def update_worker_heartbeat(
        self,
        worker_id: str,
        status: str,
        current_job_id: Optional[str] = None,
        system_load: Optional[dict] = None,
    ) -> Worker:
        """Updates worker heartbeat details, load, status, and active job ID."""
        worker = await self.db.get(Worker, worker_id)
        if not worker:
            raise WorkerNotFoundException(worker_id)

        worker.last_heartbeat = get_utc_now()
        worker.status = status
        worker.current_job_id = current_job_id
        if system_load:
            worker.system_load = system_load

        await self.db.commit()
        return worker

    async def list_workers(self) -> List[Worker]:
        """Lists all registered workers."""
        result = await self.db.execute(select(Worker))
        return list(result.scalars().all())

    # Queue CRUD
    async def create_queue(self, name: str) -> Queue:
        """Creates a job queue config entry if not already present."""
        stmt = select(Queue).where(Queue.name == name)
        res = await self.db.execute(stmt)
        queue = res.scalar_one_or_none()

        if not queue:
            queue = Queue(name=name, is_active=True, created_at=get_utc_now())
            self.db.add(queue)
            await self.db.commit()
            await self.db.refresh(queue)
        return queue

    async def list_queues(self) -> List[Queue]:
        """Lists all queues configured in the platform."""
        result = await self.db.execute(select(Queue))
        return list(result.scalars().all())

    # Execution History
    async def record_execution_start(
        self, job_id: str, worker_id: str
    ) -> ExecutionHistory:
        """Appends a new execution history entry with status RUNNING."""
        history = ExecutionHistory(
            job_id=job_id,
            worker_id=worker_id,
            status="RUNNING",
            started_at=get_utc_now(),
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def record_execution_end(
        self, history_id: str, status: str
    ) -> ExecutionHistory:
        """Finalizes an execution history entry, calculating execution duration."""
        history = await self.db.get(ExecutionHistory, history_id)
        if history:
            now = get_utc_now()
            history.ended_at = now
            history.status = status
            history.duration_seconds = (now - history.started_at).total_seconds()
            await self.db.commit()
        return history
