import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import extract_workspace_id, get_current_api_key
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
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
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
            workspace_id=workspace_id,
        )
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except DatasetException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


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
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        datasets, total = await service.list_datasets(
            project_id=project_id,
            skip=skip,
            limit=limit,
            search=search,
            tag=tag,
            language=language,
            visibility=visibility,
            workspace_id=workspace_id,
        )
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

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
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        return await service.get_dataset(dataset_id, workspace_id=workspace_id)
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: str,
    request: DatasetUpdate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        return await service.update_dataset(
            dataset_id,
            request.model_dump(exclude_unset=True),
            workspace_id=workspace_id,
        )
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        await service.delete_dataset(dataset_id, workspace_id=workspace_id)
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


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
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    import_export_service = ImportExportService(db)
    file_format = file.filename.split(".")[-1].lower() if file.filename else "json"

    try:
        # Start the job
        job = await import_export_service.create_import_job(
            project_id, file_format, workspace_id=workspace_id
        )

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
            workspace_id=workspace_id,
        )
        return {
            "job_id": job.id,
            "status": "COMPLETED",
            **res,
        }
    except (ValueError, DatasetNotFoundException) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except (DatasetValidationException, InvalidDatasetFormatException) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}") from e


@router.post("/{dataset_id}/rollback", response_model=DatasetVersionResponse)
async def rollback_version(
    dataset_id: str,
    target_version: str = Query(..., description="Target version label to promote"),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        return await service.rollback_version(
            dataset_id, target_version, workspace_id=workspace_id
        )
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{dataset_id}/diff", response_model=List[DatasetDiffItem])
async def get_dataset_diff(
    dataset_id: str,
    version_a: str = Query(..., description="Baseline version label"),
    version_b: str = Query(..., description="Comparison version label"),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        return await service.generate_diff(
            dataset_id, version_a, version_b, workspace_id=workspace_id
        )
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{dataset_id}/versions", response_model=List[DatasetVersionResponse])
async def list_dataset_versions(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        return await service.list_versions(dataset_id, workspace_id=workspace_id)
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/versions/{version_id}/records", response_model=DatasetRecordsPaginated)
async def list_version_records(
    version_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        records, total = await service.get_records(
            version_id, skip=skip, limit=limit, workspace_id=workspace_id
        )
        return {
            "records": records,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/export", response_model=Dict[str, Any], status_code=202)
async def export_dataset(
    project_id: str = Query(...),
    version_id: str = Query(...),
    file_format: str = Query("json", description="csv, json, jsonl"),
    dataset_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    import_export_service = ImportExportService(db)
    try:
        job = await import_export_service.create_export_job(
            project_id, file_format, dataset_id, workspace_id=workspace_id
        )
        file_path = await import_export_service.execute_export(job.id, version_id)
        return {
            "job_id": job.id,
            "status": "COMPLETED",
            "file_url": f"/api/v1/datasets/download/{os.path.basename(file_path)}",
        }
    except (ValueError, DatasetNotFoundException) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}") from e


@router.get("/download/{filename:path}")
async def download_file(
    filename: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    base_dir = os.path.realpath("datasets")
    os.makedirs(base_dir, exist_ok=True)

    try:
        if "\\" in filename or ".." in filename:
            raise HTTPException(
                status_code=400, detail="Invalid filename or path traversal detected."
            )
        target_path = os.path.realpath(os.path.join(base_dir, filename))
        if os.path.commonpath([base_dir, target_path]) != base_dir:
            raise HTTPException(
                status_code=400, detail="Invalid filename or path traversal detected."
            )
    except HTTPException:
        raise
    except (ValueError, Exception):
        raise HTTPException(
            status_code=400, detail="Invalid filename or path traversal detected."
        ) from None

    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        raise HTTPException(status_code=404, detail="File not found")

    clean_fn = os.path.basename(target_path)
    if clean_fn.startswith("export_"):
        parts = clean_fn.split(".")
        if len(parts) >= 2:
            job_id = parts[0].replace("export_", "")
            from app.database.repository import ProjectRepository
            from app.models.dataset import ExportJob

            job_res = await db.get(ExportJob, job_id)
            if not job_res:
                raise HTTPException(status_code=404, detail="File not found")
            project_repo = ProjectRepository(db)
            proj = await project_repo.get_by_id(
                job_res.project_id, workspace_id=workspace_id
            )
            if not proj:
                raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(target_path, filename=clean_fn)
