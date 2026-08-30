from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_engine, cache_response
from app.core.dependencies import extract_workspace_id, get_current_api_key
from app.database.session import get_db
from app.datasets.exceptions.exceptions import (
    BenchmarkSuiteNotFoundException,
    DatasetException,
)
from app.datasets.schemas.benchmark import (
    BenchmarkSuiteCreate,
    BenchmarkSuiteDetailResponse,
    BenchmarkSuiteListResponse,
    BenchmarkSuiteUpdate,
)
from app.datasets.services.benchmark import BenchmarkService

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.post("/", response_model=BenchmarkSuiteDetailResponse, status_code=201)
async def create_benchmark_suite(
    request: BenchmarkSuiteCreate,
    project_id: str = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = BenchmarkService(db)
    try:
        suite = await service.create_benchmark_suite(
            project_id=project_id,
            name=request.name,
            description=request.description,
            tags=request.tags,
            dataset_ids=request.dataset_ids,
            workspace_id=workspace_id,
        )
        await cache_engine.clear_prefix("benchmarks")
        return suite
    except BenchmarkSuiteNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except DatasetException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/", response_model=BenchmarkSuiteListResponse)
@cache_response(prefix="benchmarks", ttl_seconds=300)
async def list_benchmark_suites(
    project_id: str = Query(..., description="Project ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search name/description"),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = BenchmarkService(db)
    try:
        suites, total = await service.list_benchmark_suites(
            project_id=project_id,
            skip=skip,
            limit=limit,
            search=search,
            workspace_id=workspace_id,
        )
    except BenchmarkSuiteNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return {
        "benchmark_suites": suites,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/dashboard/metrics", response_model=Dict[str, Any])
@cache_response(prefix="benchmarks", ttl_seconds=300)
async def get_dashboard_metrics(
    project_id: str = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = BenchmarkService(db)
    try:
        return await service.get_dashboard_metrics(
            project_id, workspace_id=workspace_id
        )
    except BenchmarkSuiteNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch dashboard metrics: {str(e)}"
        ) from e


@router.get("/{suite_id}", response_model=BenchmarkSuiteDetailResponse)
async def get_benchmark_suite(
    suite_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = BenchmarkService(db)
    try:
        return await service.get_benchmark_suite(suite_id, workspace_id=workspace_id)
    except BenchmarkSuiteNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.put("/{suite_id}", response_model=BenchmarkSuiteDetailResponse)
async def update_benchmark_suite(
    suite_id: str,
    request: BenchmarkSuiteUpdate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = BenchmarkService(db)
    try:
        updated = await service.update_benchmark_suite(
            suite_id,
            request.model_dump(exclude_unset=True),
            workspace_id=workspace_id,
        )
        await cache_engine.clear_prefix("benchmarks")
        return updated
    except BenchmarkSuiteNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{suite_id}", status_code=204)
async def delete_benchmark_suite(
    suite_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = BenchmarkService(db)
    try:
        await service.delete_benchmark_suite(suite_id, workspace_id=workspace_id)
        await cache_engine.clear_prefix("benchmarks")
    except BenchmarkSuiteNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
