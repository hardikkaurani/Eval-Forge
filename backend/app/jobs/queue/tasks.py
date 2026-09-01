import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from app.jobs.progress.websocket import websocket_manager
from app.jobs.queue.celery_app import celery_app
from app.jobs.registry import job_registry

logger = logging.getLogger(__name__)


async def async_run_background_job(job_id: str, celery_task_id: str) -> Dict[str, Any]:
    """Runs a background job asynchronously by locating its registered executor."""
    from app.database.session import SessionLocal
    from app.jobs.repositories.job import JobRepository

    async with SessionLocal() as db:
        repo = JobRepository(db)
        job = await repo.get_job(job_id)
        if not job:
            logger.error(f"Job with ID '{job_id}' not found.")
            return {"status": "error", "message": f"Job {job_id} not found."}

        # If job is already cancelled, stop execution immediately
        if job.status == "CANCELLED":
            await repo.add_job_log(
                job_id, "Job was cancelled before execution could begin.", "WARNING"
            )
            return {"status": "cancelled"}

        # 1. Update job to RUNNING status
        await repo.update_job_status(job_id, "RUNNING", worker_id=celery_task_id)
        execution_history = await repo.record_execution_start(job_id, celery_task_id)
        await repo.add_job_log(
            job_id, f"Job execution started on worker task: {celery_task_id}"
        )

        # Broadcast start event
        await websocket_manager.broadcast_job_update(
            job_id,
            {
                "event": "started",
                "job_id": job_id,
                "status": "RUNNING",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        # Define progress callback
        async def progress_callback(progress: float, step: str) -> None:
            # Refresh DB session & check cancellation status
            async with SessionLocal() as callback_db:
                callback_repo = JobRepository(callback_db)
                current_job = await callback_repo.get_job(job_id)
                if current_job and current_job.status == "CANCELLED":
                    raise asyncio.CancelledError("Job was cancelled by the user.")

                await callback_repo.update_job_progress(job_id, progress, step)
                await callback_repo.add_job_log(
                    job_id, f"Progress: {progress:.1f}% - {step}"
                )

            await websocket_manager.broadcast_job_update(
                job_id,
                {
                    "event": "progress",
                    "job_id": job_id,
                    "progress": progress,
                    "current_step": step,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        try:
            # Get executor from registry
            executor_cls = job_registry.get(job.name)
            executor = executor_cls()

            # Execute the job
            result = await executor.execute(job, progress_callback)

            # 2. Update status to COMPLETED
            await repo.update_job_status(job_id, "COMPLETED", result=result)
            await repo.record_execution_end(execution_history.id, "COMPLETED")
            await repo.add_job_log(job_id, "Job execution completed successfully.")

            # Broadcast completion
            await websocket_manager.broadcast_job_update(
                job_id,
                {
                    "event": "completed",
                    "job_id": job_id,
                    "status": "COMPLETED",
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return {"status": "completed", "result": result}

        except asyncio.CancelledError as e:
            # Handle cancellation
            await repo.update_job_status(job_id, "CANCELLED", error_message=str(e))
            await repo.record_execution_end(execution_history.id, "CANCELLED")
            await repo.add_job_log(job_id, f"Job cancelled: {str(e)}", "WARNING")

            await websocket_manager.broadcast_job_update(
                job_id,
                {
                    "event": "cancelled",
                    "job_id": job_id,
                    "status": "CANCELLED",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            return {"status": "cancelled"}

        except Exception as e:
            logger.exception(f"Error executing job {job_id}")
            # Determine if retry is possible
            if job.retry_count < job.max_retries:
                retry_attempt = job.retry_count + 1
                delay_seconds = 2**retry_attempt  # Exponential backoff: 2s, 4s, 8s...

                await repo.record_retry(
                    job_id, error_message=str(e), delay_seconds=delay_seconds
                )
                await repo.update_job_status(job_id, "RETRYING", error_message=str(e))
                await repo.record_execution_end(execution_history.id, "RETRYING")
                await repo.add_job_log(
                    job_id,
                    f"Job failed with error: {str(e)}. Scheduling retry attempt #{retry_attempt} in {delay_seconds} seconds.",
                    "WARNING",
                )

                # Broadcast retry state
                await websocket_manager.broadcast_job_update(
                    job_id,
                    {
                        "event": "retrying",
                        "job_id": job_id,
                        "status": "RETRYING",
                        "retry_count": retry_attempt,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

                # Schedule retry in Celery
                run_background_job.apply_async(args=[job_id], countdown=delay_seconds)
                return {"status": "retrying", "error": str(e)}
            else:
                # 3. Update status to FAILED
                await repo.update_job_status(job_id, "FAILED", error_message=str(e))
                await repo.record_execution_end(execution_history.id, "FAILED")
                await repo.add_job_log(
                    job_id, f"Job execution failed permanently: {str(e)}", "ERROR"
                )

                # Broadcast failure
                await websocket_manager.broadcast_job_update(
                    job_id,
                    {
                        "event": "failed",
                        "job_id": job_id,
                        "status": "FAILED",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                return {"status": "failed", "error": str(e)}


@celery_app.task(name="app.jobs.tasks.run_background_job", bind=True)
def run_background_job(self, job_id: str) -> Any:
    """Celery task wrapper around the asynchronous job executor run function."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # Eager mode (testing) or already running loop
        future = asyncio.run_coroutine_threadsafe(
            async_run_background_job(job_id, self.request.id or "eager_task"), loop
        )
        return future.result()
    else:
        return loop.run_until_complete(
            async_run_background_job(job_id, self.request.id or "eager_task")
        )


@celery_app.task(name="app.jobs.tasks.run_evaluation_job", bind=True)
def run_evaluation_job(self, job_id: str) -> Any:
    """Dedicated Celery task wrapper for high-priority evaluation jobs."""
    return run_background_job(self, job_id)

