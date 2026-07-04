from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.datasets.exceptions.exceptions import DatasetException, BenchmarkSuiteNotFoundException
from app.datasets.schemas.benchmark import (
    BenchmarkSuiteCreate,
    BenchmarkSuiteDetailResponse,
    BenchmarkSuiteResponse,
    BenchmarkSuiteUpdate,
    BenchmarkSuiteListResponse,
)
from app.datasets.services.benchmark import BenchmarkService

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.post("/", response_model=BenchmarkSuiteDetailResponse, status_code=201)
async def create_benchmark_suite(
    request: BenchmarkSuiteCreate,
    project_id: str = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db),
):
    service = BenchmarkService(db)
    try:
        return await service.create_benchmark_suite(
            project_id=project_id,
            name=request.name,
            description=request.description,
            tags=request.tags,
            dataset_ids=request.dataset_ids,
        )
    except DatasetException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=BenchmarkSuiteListResponse)
async def list_benchmark_suites(
    project_id: str = Query(..., description="Project ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search name/description"),
    db: AsyncSession = Depends(get_db),
):
    service = BenchmarkService(db)
    suites, total = await service.list_benchmark_suites(
        project_id=project_id,
        skip=skip,
        limit=limit,
        search=search,
    )
    return {
        "benchmark_suites": suites,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/dashboard/metrics", response_model=Dict[str, Any])
async def get_dashboard_metrics(
    project_id: str = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db),
):
    service = BenchmarkService(db)
    try:
        return await service.get_dashboard_metrics(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard metrics: {str(e)}")


@router.get("/{suite_id}", response_model=BenchmarkSuiteDetailResponse)
async def get_benchmark_suite(
    suite_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = BenchmarkService(db)
    try:
        return await service.get_benchmark_suite(suite_id)
    except BenchmarkSuiteNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{suite_id}", response_model=BenchmarkSuiteDetailResponse)
async def update_benchmark_suite(
    suite_id: str,
    request: BenchmarkSuiteUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = BenchmarkService(db)
    try:
        return await service.update_benchmark_suite(
            suite_id, request.model_dump(exclude_unset=True)
        )
    except BenchmarkSuiteNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{suite_id}", status_code=204)
async def delete_benchmark_suite(
    suite_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = BenchmarkService(db)
    try:
        await service.delete_benchmark_suite(suite_id)
    except BenchmarkSuiteNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
