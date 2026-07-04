import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.datasets.exceptions.exceptions import (
    DatasetException,
    DatasetNotFoundException,
    DatasetValidationException,
    InvalidDatasetFormatException,
)
from app.datasets.schemas.dataset import (
    DatasetCreate,
    DatasetDetailResponse,
    DatasetDiffItem,
    DatasetListResponse,
    DatasetRecordsPaginated,
    DatasetResponse,
    DatasetUpdate,
    DatasetVersionResponse,
)
from app.datasets.services.dataset import DatasetService
from app.datasets.services.import_export import ImportExportService

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/", response_model=DatasetResponse, status_code=201)
async def create_dataset(
    request: DatasetCreate,
    project_id: str = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    try:
        return await service.create_empty_dataset(
            project_id=project_id,
            name=request.name,
            description=request.description,
            visibility=request.visibility,
            owner=request.owner,
            source=request.source,
            language=request.language,
            license=request.license,
            tags=request.tags,
        )
    except DatasetException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=DatasetListResponse)
async def list_datasets(
    project_id: str = Query(..., description="Project ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search name/description"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    language: Optional[str] = Query(None, description="Filter by language"),
    visibility: Optional[str] = Query(None, description="Filter by visibility"),
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    datasets, total = await service.list_datasets(
        project_id=project_id,
        skip=skip,
        limit=limit,
        search=search,
        tag=tag,
        language=language,
        visibility=visibility,
    )
    return {
        "datasets": datasets,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
async def get_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    try:
        return await service.get_dataset(dataset_id)
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: str,
    request: DatasetUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    try:
        return await service.update_dataset(
            dataset_id, request.model_dump(exclude_unset=True)
        )
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    try:
        await service.delete_dataset(dataset_id)
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/import", response_model=Dict[str, Any], status_code=202)
async def import_dataset(
    project_id: str = Form(...),
    dataset_name: str = Form(...),
    description: Optional[str] = Form(None),
    visibility: str = Form("private"),
    owner: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),
    license: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),
    existing_dataset_id: Optional[str] = Form(None),
    version_label: str = Form("v1"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    import_export_service = ImportExportService(db)
    file_format = file.filename.split(".")[-1].lower() if file.filename else "json"

    # Start the job
    job = await import_export_service.create_import_job(project_id, file_format)

    try:
        content = await file.read()
        res = await import_export_service.process_import(
            job_id=job.id,
            file_content=content,
            dataset_name=dataset_name,
            project_id=project_id,
            description=description,
            visibility=visibility,
            owner=owner,
            source=source,
            language=language,
            license=license,
            tags=tags,
            existing_dataset_id=existing_dataset_id,
            version_label=version_label,
        )
        return {
            "job_id": job.id,
            "status": "COMPLETED",
            **res,
        }
    except (DatasetValidationException, InvalidDatasetFormatException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/{dataset_id}/rollback", response_model=DatasetVersionResponse)
async def rollback_version(
    dataset_id: str,
    target_version: str = Query(..., description="Target version label to promote"),
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    try:
        return await service.rollback_version(dataset_id, target_version)
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{dataset_id}/diff", response_model=List[DatasetDiffItem])
async def get_dataset_diff(
    dataset_id: str,
    version_a: str = Query(..., description="Baseline version label"),
    version_b: str = Query(..., description="Comparison version label"),
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    try:
        return await service.generate_diff(dataset_id, version_a, version_b)
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{dataset_id}/versions", response_model=List[DatasetVersionResponse])
async def list_dataset_versions(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    try:
        return await service.list_versions(dataset_id)
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/versions/{version_id}/records", response_model=DatasetRecordsPaginated)
async def list_version_records(
    version_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    records, total = await service.get_records(version_id, skip=skip, limit=limit)
    return {
        "records": records,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/export", response_model=Dict[str, Any], status_code=202)
async def export_dataset(
    project_id: str = Query(...),
    version_id: str = Query(...),
    file_format: str = Query("json", description="csv, json, jsonl"),
    dataset_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    import_export_service = ImportExportService(db)
    job = await import_export_service.create_export_job(
        project_id, file_format, dataset_id
    )

    try:
        file_path = await import_export_service.execute_export(job.id, version_id)
        return {
            "job_id": job.id,
            "status": "COMPLETED",
            "file_url": f"/api/v1/datasets/download/{os.path.basename(file_path)}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/download/{filename}")
async def download_file(filename: str):
    base_dir = "datasets"
    full_path = os.path.join(base_dir, filename)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path, filename=filename)
