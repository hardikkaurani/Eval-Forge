from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_current_api_key
from app.jobs.scheduler.cron_manager import cron_scheduler
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/jobs/scheduler", tags=["Scheduled Jobs / Cron"])


@router.get(
    "/jobs",
    response_model=ApiResponse[List[Dict[str, Any]]],
    summary="List all scheduled cron jobs",
)
async def list_scheduled_jobs(current_key: Any = Depends(get_current_api_key)):
    """Retrieves list of active periodic cron jobs, schedule parameters, and status."""
    jobs = cron_scheduler.list_jobs()
    return create_response(
        success=True,
        message="Scheduled cron jobs retrieved successfully.",
        data=jobs,
    )


@router.post(
    "/jobs/{job_id}/trigger",
    response_model=ApiResponse[Dict[str, Any]],
    summary="Manually trigger a scheduled cron job immediately",
)
async def trigger_scheduled_job(
    job_id: str, current_key: Any = Depends(get_current_api_key)
):
    """Executes a scheduled cron task immediately out of cycle."""
    try:
        execution_log = await cron_scheduler.execute_job(job_id)
        return create_response(
            success=True,
            message=f"Cron job '{job_id}' executed successfully.",
            data=execution_log,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to execute cron job: {str(e)}"
        ) from e


@router.post(
    "/jobs/{job_id}/toggle",
    response_model=ApiResponse[Dict[str, Any]],
    summary="Pause or resume a scheduled cron job",
)
async def toggle_scheduled_job(
    job_id: str, current_key: Any = Depends(get_current_api_key)
):
    """Toggles the enabled/disabled state of a scheduled cron job."""
    try:
        job = cron_scheduler.toggle_job(job_id)
        status_str = "enabled" if job.is_enabled else "disabled"
        return create_response(
            success=True,
            message=f"Cron job '{job_id}' has been {status_str}.",
            data=job.to_dict(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/history",
    response_model=ApiResponse[List[Dict[str, Any]]],
    summary="Get execution history of scheduled cron jobs",
)
async def get_cron_execution_history(
    limit: int = Query(50, ge=1, le=200),
    current_key: Any = Depends(get_current_api_key),
):
    """Retrieves recent execution logs and status history for scheduled cron jobs."""
    history = cron_scheduler.get_history(limit=limit)
    return create_response(
        success=True,
        message="Cron execution history retrieved successfully.",
        data=history,
    )
