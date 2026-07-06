from typing import List, Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.jobs.progress.websocket import websocket_manager
from app.jobs.schemas.job import (
    JobCreate,
    JobDetailResponse,
    JobResponse,
    QueueResponse,
    SystemMetricsResponse,
    WorkerResponse,
)
from app.jobs.services.job import JobService
from app.utils.pagination import PaginatedResponse, create_pagination_meta
from app.utils.responses import ApiResponse, create_response

router = APIRouter()


@router.post(
    "/jobs",
    response_model=ApiResponse[JobResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create and queue a new background job",
    tags=["Jobs"],
)
async def create_job(
    payload: JobCreate,
    project_id: str = Query(..., description="Project UUID to associate with this job"),
    db: AsyncSession = Depends(get_db),
):
    """Submits a job request and dispatches it to Celery workers."""
    service = JobService(db)
    job = await service.create_job(project_id, payload)
    return create_response(
        success=True,
        message="Background job queued successfully.",
        data=JobResponse.model_validate(job),
    )


@router.get(
    "/jobs",
    response_model=ApiResponse[PaginatedResponse[JobResponse]],
    summary="List background jobs",
    tags=["Jobs"],
)
async def list_jobs(
    queue_name: Optional[str] = Query(None, description="Filter by queue name"),
    status: Optional[str] = Query(None, description="Filter by job status"),
    search: Optional[str] = Query(None, description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: str = Query("created_at", description="Sort field name"),
    sort_order: str = Query("desc", description="Sort direction order"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a paginated list of background jobs matching query filters."""
    service = JobService(db)
    items, total = await service.list_jobs(
        queue_name=queue_name,
        status=status,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    meta = create_pagination_meta(page=page, page_size=page_size, total_items=total)
    paginated_data = PaginatedResponse(
        items=[JobResponse.model_validate(item) for item in items],
        meta=meta,
    )
    return create_response(
        success=True,
        message="Jobs list retrieved successfully.",
        data=paginated_data,
    )


@router.get(
    "/jobs/{id}",
    response_model=ApiResponse[JobDetailResponse],
    summary="Retrieve job details by ID",
    tags=["Jobs"],
)
async def get_job(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full detail data, execution logs, and histories for a background job."""
    service = JobService(db)
    job = await service.get_job(id)
    return create_response(
        success=True,
        message="Job details retrieved successfully.",
        data=JobDetailResponse.model_validate(job),
    )


@router.delete(
    "/jobs/{id}",
    response_model=ApiResponse[None],
    summary="Delete job from the database",
    tags=["Jobs"],
)
async def delete_job(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """Deletes a job and all its related cascades from the database."""
    from app.jobs.models.job import Job

    job = await db.get(Job, id)
    if not job:
        return create_response(
            success=False,
            message=f"Job with ID '{id}' not found.",
            status_code=404,
        )
    await db.delete(job)
    await db.commit()
    return create_response(
        success=True,
        message="Job record deleted successfully.",
    )


@router.post(
    "/jobs/{id}/cancel",
    response_model=ApiResponse[JobResponse],
    summary="Cancel a queued or running job",
    tags=["Jobs"],
)
async def cancel_job(
    id: str,
    reason: Optional[str] = Query(None, description="Reason for cancellation"),
    db: AsyncSession = Depends(get_db),
):
    """Flags a running or queued job as cancelled to interrupt workers execution loop."""
    service = JobService(db)
    job = await service.cancel_job(id, reason=reason)
    return create_response(
        success=True,
        message="Job cancellation request received.",
        data=JobResponse.model_validate(job),
    )


@router.get(
    "/queues",
    response_model=ApiResponse[List[QueueResponse]],
    summary="List virtual and configuration queues",
    tags=["Queues"],
)
async def list_queues(
    db: AsyncSession = Depends(get_db),
):
    """Lists queues configured inside the EvalForge jobs platform."""
    service = JobService(db)
    queues = await service.list_queues()
    return create_response(
        success=True,
        message="Queues retrieved successfully.",
        data=[QueueResponse.model_validate(q) for q in queues],
    )


@router.get(
    "/workers",
    response_model=ApiResponse[List[WorkerResponse]],
    summary="List active background workers",
    tags=["Workers"],
)
async def list_workers(
    db: AsyncSession = Depends(get_db),
):
    """Lists all active and offline workers registered with the platform."""
    service = JobService(db)
    workers = await service.list_workers()
    return create_response(
        success=True,
        message="Workers retrieved successfully.",
        data=[WorkerResponse.model_validate(w) for w in workers],
    )


@router.get(
    "/system/jobs",
    response_model=ApiResponse[SystemMetricsResponse],
    summary="Retrieve queue metrics and health",
    tags=["System"],
)
async def get_system_jobs_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Retrieves high-level performance and error metrics for monitoring dashboards."""
    service = JobService(db)
    metrics = await service.get_system_metrics()
    return create_response(
        success=True,
        message="Jobs system health metrics compiled successfully.",
        data=metrics,
    )


# WebSocket connection routes
@router.websocket("/jobs/{id}/progress")
async def job_progress_websocket(websocket: WebSocket, id: str):
    """Subscribes client socket to receive progress frames for a specific job."""
    await websocket_manager.connect_job(id, websocket)
    try:
        while True:
            # Keeps connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect_job(id, websocket)


@router.websocket("/projects/{id}/jobs/progress")
async def project_jobs_websocket(websocket: WebSocket, id: str):
    """Subscribes client socket to receive project-wide progress frames."""
    await websocket_manager.connect_project(id, websocket)
    try:
        while True:
            # Keeps connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect_project(id, websocket)
