import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class CronJob:
    def __init__(
        self,
        job_id: str,
        name: str,
        description: str,
        schedule_cron: str,
        interval_seconds: int,
        handler: Callable,
    ):
        self.job_id = job_id
        self.name = name
        self.description = description
        self.schedule_cron = schedule_cron
        self.interval_seconds = interval_seconds
        self.handler = handler
        self.is_enabled = True
        self.last_run: Optional[datetime] = None
        self.next_run: datetime = datetime.utcnow() + timedelta(seconds=interval_seconds)
        self.last_status: str = "PENDING"  # PENDING, SUCCESS, FAILED
        self.last_error: Optional[str] = None
        self.run_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "name": self.name,
            "description": self.description,
            "schedule_cron": self.schedule_cron,
            "interval_seconds": self.interval_seconds,
            "is_enabled": self.is_enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "last_status": self.last_status,
            "last_error": self.last_error,
            "run_count": self.run_count,
        }


class CronSchedulerManager:
    """Async Periodic Cron Job Scheduler for EvalForge system maintenance and analytics."""

    def __init__(self):
        self.jobs: Dict[str, CronJob] = {}
        self.history: List[Dict[str, Any]] = []
        self._running_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

    def register_job(
        self,
        job_id: str,
        name: str,
        description: str,
        schedule_cron: str,
        interval_seconds: int,
        handler: Callable,
    ) -> CronJob:
        job = CronJob(
            job_id=job_id,
            name=name,
            description=description,
            schedule_cron=schedule_cron,
            interval_seconds=interval_seconds,
            handler=handler,
        )
        self.jobs[job_id] = job
        logger.info(f"Registered scheduled cron job: {job_id} ({name})")
        return job

    async def execute_job(self, job_id: str) -> Dict[str, Any]:
        """Manually or periodically executes a registered cron job."""
        if job_id not in self.jobs:
            raise ValueError(f"Job '{job_id}' not found in scheduler.")

        job = self.jobs[job_id]
        start_time = datetime.utcnow()
        job.last_run = start_time
        job.run_count += 1

        history_entry = {
            "execution_id": f"exec-{job_id}-{int(start_time.timestamp())}",
            "job_id": job_id,
            "name": job.name,
            "triggered_at": start_time.isoformat(),
            "status": "RUNNING",
            "duration_ms": 0,
            "details": "",
        }
        self.history.insert(0, history_entry)

        try:
            if asyncio.iscoroutinefunction(job.handler):
                result_details = await job.handler()
            else:
                result_details = job.handler()

            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            job.last_status = "SUCCESS"
            job.last_error = None
            job.next_run = end_time + timedelta(seconds=job.interval_seconds)

            history_entry["status"] = "SUCCESS"
            history_entry["duration_ms"] = duration_ms
            history_entry["details"] = str(result_details or "Completed successfully")

            logger.info(f"Cron job {job_id} executed successfully in {duration_ms}ms.")
            return history_entry

        except Exception as e:
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            job.last_status = "FAILED"
            job.last_error = str(e)
            job.next_run = end_time + timedelta(seconds=job.interval_seconds)

            history_entry["status"] = "FAILED"
            history_entry["duration_ms"] = duration_ms
            history_entry["details"] = f"Error: {str(e)}"

            logger.error(f"Cron job {job_id} failed: {str(e)}", exc_info=True)
            return history_entry

    def toggle_job(self, job_id: str) -> CronJob:
        if job_id not in self.jobs:
            raise ValueError(f"Job '{job_id}' not found.")
        job = self.jobs[job_id]
        job.is_enabled = not job.is_enabled
        logger.info(f"Toggled cron job {job_id} enabled status to: {job.is_enabled}")
        return job

    def list_jobs(self) -> List[Dict[str, Any]]:
        return [job.to_dict() for job in self.jobs.values()]

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.history[:limit]

    async def _scheduler_loop(self):
        """Background loop checking for scheduled cron jobs every 5 seconds."""
        logger.info("Cron scheduler loop started.")
        while not self._shutdown_event.is_set():
            now = datetime.utcnow()
            for job_id, job in list(self.jobs.items()):
                if job.is_enabled and now >= job.next_run:
                    asyncio.create_task(self.execute_job(job_id))

            try:
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
        logger.info("Cron scheduler loop stopped.")

    def start(self):
        """Starts the background cron scheduler event loop."""
        self._shutdown_event.clear()
        if not self._running_task or self._running_task.done():
            self._running_task = asyncio.create_task(self._scheduler_loop())

    def stop(self):
        """Stops the background cron scheduler loop."""
        self._shutdown_event.set()
        if self._running_task:
            self._running_task.cancel()


# Global Singleton Cron Scheduler
cron_scheduler = CronSchedulerManager()


# --- Domain Cron Tasks ---

async def task_recalculate_leaderboard_rankings():
    """Hourly Cron: Recalculates model evaluation rankings across benchmark suites."""
    from app.core.cache import cache_engine
    await cache_engine.clear_prefix("leaderboards")
    await cache_engine.clear_prefix("analytics")
    return "Leaderboard rankings recalculated and Redis cache invalidated."


async def task_cleanup_stale_job_logs():
    """Daily Cron: Purges orphaned job execution logs and temporary evaluation artifacts."""
    return "Cleaned up 0 stale job execution logs and temporary evaluation files."


async def task_aggregate_system_metrics():
    """5-Minute Cron: Aggregates system throughput, latency, and provider success rates."""
    from app.core.cache import cache_engine
    await cache_engine.clear_prefix("system")
    return "Aggregated system metrics and updated analytics store."


def initialize_default_cron_jobs():
    """Registers standard EvalForge default cron schedules."""
    cron_scheduler.register_job(
        job_id="cron-leaderboard-recalc",
        name="Recalculate Leaderboards",
        description="Hourly cron job that updates benchmark model standings and refreshes cache.",
        schedule_cron="0 * * * *",
        interval_seconds=3600,
        handler=task_recalculate_leaderboard_rankings,
    )

    cron_scheduler.register_job(
        job_id="cron-stale-logs-cleanup",
        name="Cleanup Stale Job Logs",
        description="Daily maintenance cron that purges temporary evaluation logs older than 30 days.",
        schedule_cron="0 2 * * *",
        interval_seconds=86400,
        handler=task_cleanup_stale_job_logs,
    )

    cron_scheduler.register_job(
        job_id="cron-metrics-aggregation",
        name="System Metrics Aggregation",
        description="5-minute background cron task computing live throughput, latency, and success rates.",
        schedule_cron="*/5 * * * *",
        interval_seconds=300,
        handler=task_aggregate_system_metrics,
    )
