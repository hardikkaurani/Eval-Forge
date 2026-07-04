from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.datasets.exceptions.exceptions import ExperimentNotFoundException
from app.datasets.schemas.experiment import (
    ExperimentCreate,
    ExperimentDetailResponse,
    ExperimentListResponse,
    ExperimentResponse,
)
from app.datasets.services.experiment import ExperimentService

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("/", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    request: ExperimentCreate,
    project_id: str = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db),
):
    service = ExperimentService(db)
    try:
        return await service.create_experiment(
            project_id=project_id,
            dataset_version_id=request.dataset_version_id,
            name=request.name,
            description=request.description,
            judge=request.judge,
            provider=request.provider,
            model=request.model,
            configuration=request.configuration,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/", response_model=ExperimentListResponse)
async def list_experiments(
    project_id: str = Query(..., description="Project ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search name/description"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    service = ExperimentService(db)
    experiments, total = await service.list_experiments(
        project_id=project_id,
        skip=skip,
        limit=limit,
        search=search,
        status=status,
    )
    return {
        "experiments": experiments,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{experiment_id}", response_model=ExperimentDetailResponse)
async def get_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = ExperimentService(db)
    try:
        return await service.get_experiment(experiment_id)
    except ExperimentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/{experiment_id}/execute", response_model=ExperimentDetailResponse)
async def execute_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = ExperimentService(db)
    try:
        return await service.execute_experiment(experiment_id)
    except ExperimentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Execution failed: {str(e)}"
        ) from e


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = ExperimentService(db)
    try:
        await service.delete_experiment(experiment_id)
    except ExperimentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
