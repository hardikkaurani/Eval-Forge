from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.responses import ApiResponse, create_response
from app.utils.pagination import PaginatedResponse, create_pagination_meta
from app.analytics.schemas import (
    AnalyticsOverview,
    ReportCreate,
    ReportResponse,
    LeaderboardResponse,
    InsightResponse,
    TrendResponse,
    SystemMetrics,
    DashboardSnapshotCreate,
    DashboardSnapshotResponse,
)
from app.analytics.services import AnalyticsService, ObservabilityService
from app.analytics.repositories import AnalyticsRepository
from app.models.analytics import DashboardSnapshot

# Separate routers for different prefix paths
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])
reports_router = APIRouter(prefix="/reports", tags=["Reports"])
leaderboards_router = APIRouter(prefix="/leaderboards", tags=["Leaderboards"])
insights_router = APIRouter(prefix="/insights", tags=["Insights"])
trends_router = APIRouter(prefix="/trends", tags=["Trends"])
system_router = APIRouter(prefix="/system", tags=["System"])


# --- Analytics Router ---

@analytics_router.get(
    "",
    response_model=ApiResponse[AnalyticsOverview],
    summary="Get project analytics overview",
)
async def get_project_analytics(
    project_id: str = Query(..., description="Project UUID to fetch analytics for"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves high-level aggregated evaluation statistics and trends for a project."""
    service = AnalyticsService(db)
    overview = await service.get_overview(project_id)
    return create_response(
        success=True,
        message="Analytics overview fetched successfully.",
        data=overview,
    )


@analytics_router.post(
    "/snapshots",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_201_CREATED,
    summary="Trigger aggregate snapshots manually",
)
async def trigger_analytics_snapshot(
    project_id: str = Query(..., description="Project UUID"),
    scope: str = Query("project", description="Scope: project, dataset, evaluation_run"),
    scope_id: Optional[str] = Query(None, description="Identifier of the scope element"),
    db: AsyncSession = Depends(get_db),
):
    """Triggers background data aggregation and persists a new AnalyticsSnapshot."""
    service = AnalyticsService(db)
    snapshot = await service.compute_and_save_snapshot(project_id, scope, scope_id)
    return create_response(
        success=True,
        message="Analytics snapshot aggregated and stored successfully.",
        data={"snapshot_id": snapshot.id, "timestamp": snapshot.timestamp},
    )


@analytics_router.post(
    "/dashboards",
    response_model=ApiResponse[DashboardSnapshotResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Save a custom dashboard layout snapshot",
)
async def save_dashboard_snapshot(
    payload: DashboardSnapshotCreate,
    project_id: str = Query(..., description="Project UUID"),
    db: AsyncSession = Depends(get_db),
):
    """Stores a dashboard layout grid snapshot configuration for a project."""
    repo = AnalyticsRepository(db)
    snap = DashboardSnapshot(
        project_id=project_id,
        name=payload.name,
        layout=payload.layout
    )
    saved = await repo.save_dashboard_snapshot(snap)
    await db.commit()
    return create_response(
        success=True,
        message="Dashboard snapshot saved.",
        data=DashboardSnapshotResponse.model_validate(saved)
    )


@analytics_router.get(
    "/dashboards",
    response_model=ApiResponse[List[DashboardSnapshotResponse]],
    summary="List saved dashboard snapshots",
)
async def list_dashboard_snapshots(
    project_id: str = Query(..., description="Project UUID"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves all stored dashboard layouts for a project."""
    repo = AnalyticsRepository(db)
    items = await repo.list_dashboard_snapshots(project_id)
    return create_response(
        success=True,
        message="Dashboard snapshots list retrieved.",
        data=[DashboardSnapshotResponse.model_validate(i) for i in items]
    )


# --- Reports Router ---

@reports_router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[ReportResponse]],
    summary="List generated reports",
)
async def list_reports(
    project_id: str = Query(..., description="Project UUID"),
    type: Optional[str] = Query(None, description="PDF or CSV"),
    status: Optional[str] = Query(None, description="PENDING, COMPLETED, etc."),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lists compiled and pending executive reports for a project."""
    repo = AnalyticsRepository(db)
    skip = (page - 1) * page_size
    items, total = await repo.list_reports(project_id, type, status, skip, page_size)
    meta = create_pagination_meta(page, page_size, total)
    paginated = PaginatedResponse(
        items=[ReportResponse.model_validate(item) for item in items],
        meta=meta
    )
    return create_response(
        success=True,
        message="Reports listed successfully.",
        data=paginated
    )


@reports_router.post(
    "/generate",
    response_model=ApiResponse[ReportResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger executive report generation",
)
async def generate_report(
    payload: ReportCreate,
    project_id: str = Query(..., description="Project UUID"),
    db: AsyncSession = Depends(get_db),
):
    """Triggers background generation of a PDF or CSV format executive evaluation report."""
    service = AnalyticsService(db)
    report = await service.generate_report_file(project_id, payload.name, payload.type, payload.filters)
    return create_response(
        success=True,
        message="Report generation triggered.",
        data=ReportResponse.model_validate(report)
    )


@reports_router.get(
    "/{id}/download",
    summary="Download report binary file",
)
async def download_report(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """Downloads the compiled PDF or CSV file binary."""
    repo = AnalyticsRepository(db)
    report = await repo.get_report(id)
    if not report or not report.file_path:
        raise HTTPException(status_code=404, detail="Compiled report file not found.")
    
    media_type = "application/pdf" if report.type.upper() == "PDF" else "text/csv"
    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=f"{report.name.replace(' ', '_')}.{report.type.lower()}"
    )


# --- Leaderboards Router ---

@leaderboards_router.get(
    "",
    response_model=ApiResponse[LeaderboardResponse],
    summary="Retrieve leaderboard standings",
)
async def get_leaderboard(
    project_id: str = Query(..., description="Project UUID"),
    entity_type: str = Query("model", description="model, provider, dataset, or benchmark"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves ranked standings of models or providers based on quality scores."""
    service = AnalyticsService(db)
    items = await service.get_leaderboard(project_id, entity_type)
    return create_response(
        success=True,
        message="Leaderboard standings fetched.",
        data={"entity_type": entity_type, "items": items}
    )


# --- Insights Router ---

@insights_router.get(
    "",
    response_model=ApiResponse[List[InsightResponse]],
    summary="List auto-generated quality insights",
)
async def list_insights(
    project_id: str = Query(..., description="Project UUID"),
    type: Optional[str] = Query(None, description="regression, improvement, latency, hallucination"),
    severity: Optional[str] = Query(None, description="low, medium, high, critical"),
    db: AsyncSession = Depends(get_db),
):
    """Lists auto-detected performance regression and latency spike insights."""
    repo = AnalyticsRepository(db)
    items = await repo.list_insights(project_id, type, severity)
    return create_response(
        success=True,
        message="Insights fetched.",
        data=[InsightResponse.model_validate(i) for i in items]
    )


# --- Trends Router ---

@trends_router.get(
    "",
    response_model=ApiResponse[TrendResponse],
    summary="Retrieve historical performance trends",
)
async def get_trends(
    project_id: str = Query(..., description="Project UUID"),
    metric_name: str = Query("avg_score", description="avg_score, success_rate, avg_latency_ms, estimated_cost"),
    granularity: str = Query("daily", description="daily, weekly, monthly"),
    compare: bool = Query(True, description="Compare with previous period"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves quality score, token count, cost, or failure rate trends over time."""
    service = AnalyticsService(db)
    trends = await service.get_trends(project_id, metric_name, granularity, compare)
    return create_response(
        success=True,
        message="Trends data compiled successfully.",
        data=trends
    )


# --- System Observability Router ---

@system_router.get(
    "/metrics",
    response_model=ApiResponse[SystemMetrics],
    summary="Retrieve system observability metrics",
)
async def get_system_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Retrieves CPU, Memory, Redis pool connection sizes, and database transaction health metrics."""
    service = ObservabilityService(db)
    metrics = await service.collect_health_metrics()
    return create_response(
        success=True,
        message="System observability metrics retrieved.",
        data=metrics
    )
