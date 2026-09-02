import os
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import extract_workspace_id, get_current_api_key
from app.database.repository import ProjectRepository
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
    DatasetRecordCreate,
    DatasetRecordResponse,
    DatasetRecordsPaginated,
    DatasetRecordUpdate,
    DatasetResponse,
    DatasetUpdate,
    DatasetVersionResponse,
)
from app.datasets.services.dataset import DatasetService
from app.datasets.services.import_export import ImportExportService
from app.models.dataset import ExportJob, ImportJob

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


ALLOWED_UPLOAD_EXTENSIONS = {"csv", "json", "jsonl"}
ALLOWED_MIME_TYPES = {
    "text/csv",
    "application/json",
    "text/plain",
    "application/x-ndjson",
    "application/jsonlines",
    "text/x-csv",
    "application/csv",
    "application/octet-stream",
}
DISALLOWED_SUB_EXTENSIONS = {"exe", "php", "sh", "bat", "cmd", "dll", "so", "py", "js", "vbs", "scr", "ps1", "asp", "aspx", "jsp", "cgi"}
MAX_UPLOAD_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB


async def validate_and_read_upload_file(file: UploadFile) -> tuple[str, bytes]:
    """Validates filename normalization, path safety, size limits, extension, MIME type, and content structure."""
    raw_filename = file.filename or ""

    # Null byte check
    if "\x00" in raw_filename or "%00" in raw_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: null byte sequence detected.",
        )

    # Path traversal check (handles raw and URL-encoded sequences)
    lowered_filename = raw_filename.lower()
    if ".." in raw_filename or "/" in raw_filename or "\\" in raw_filename or "%2e%2e" in lowered_filename or "%2f" in lowered_filename or "%5c" in lowered_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: path traversal sequence detected.",
        )

    parts = [p for p in raw_filename.split(".") if p]
    if not parts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: missing extension.",
        )

    ext = parts[-1].lower()

    # Double extension / executable extension check
    if len(parts) > 2 and any(p.lower() in DISALLOWED_SUB_EXTENSIONS for p in parts[:-1]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported double extension format: .{ext}",
        )

    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension: .{ext}. Allowed formats: .csv, .json, .jsonl",
        )

    # MIME type validation
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported MIME type: {file.content_type}.",
        )

    # Stream read with size enforcement (100 MB)
    total_bytes = 0
    chunk_size = 64 * 1024  # 64 KB chunks
    chunks = []

    await file.seek(0)
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_bytes += len(chunk)
        if total_bytes > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Uploaded file size exceeds maximum limit of 100 MB.",
            )
        chunks.append(chunk)

    if total_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    file_content = b"".join(chunks)

    import codecs
    import csv
    import json

    # Stream validation over file.file to prevent 100MB string allocations and memory amplification
    if ext == "jsonl":
        await file.seek(0)
        has_records = False
        reader = codecs.iterdecode(file.file, "utf-8")
        line_num = 0
        try:
            for line in reader:
                line_num += 1
                stripped = line.strip()
                if not stripped:
                    continue
                has_records = True
                if len(stripped) > 10 * 1024 * 1024:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"JSONL line {line_num} exceeds maximum line length limit.",
                    )
                json.loads(stripped)
        except UnicodeDecodeError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File encoding check failed: UTF-8 required ({str(err)})",
            ) from err
        except json.JSONDecodeError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSONL record at line {line_num}: {str(err)}",
            ) from err

        if not has_records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSONL file contains no valid records.",
            )

    elif ext == "csv":
        await file.seek(0)
        has_rows = False
        try:
            stream = codecs.iterdecode(file.file, "utf-8")
            csv_reader = csv.reader(stream)
            for row in csv_reader:
                if row:
                    has_rows = True
                    break
        except UnicodeDecodeError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File encoding check failed: UTF-8 required ({str(err)})",
            ) from err
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CSV format: {str(err)}",
            ) from err

        if not has_rows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file contains no rows.",
            )

    elif ext == "json":
        await file.seek(0)
        try:
            stream = codecs.iterdecode(file.file, "utf-8")
            content_str = ""
            for chunk in stream:
                content_str += chunk
            json.loads(content_str)
        except UnicodeDecodeError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File encoding check failed: UTF-8 required ({str(err)})",
            ) from err
        except json.JSONDecodeError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON content structure: {str(err)}",
            ) from err

    return ext, file_content




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

    # Validate file size, extension, path security, and structure
    file_format, content = await validate_and_read_upload_file(file)

    # Sanitize UI-rendered metadata strings
    from app.core.sanitization import sanitize_xss

    dataset_name = sanitize_xss(dataset_name)
    description = sanitize_xss(description) if description else None

    try:
        # Start the job
        job = await import_export_service.create_import_job(
            project_id, file_format, workspace_id=workspace_id
        )

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


@router.post(
    "/versions/{version_id}/records",
    response_model=List[DatasetRecordResponse],
    status_code=201,
)
async def create_version_records(
    version_id: str,
    records: List[DatasetRecordCreate],
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    records_data = [r.model_dump() for r in records]
    try:
        return await service.create_records(
            version_id, records_data, workspace_id=workspace_id
        )
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/records/{record_id}", response_model=DatasetRecordResponse)
async def get_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        return await service.get_single_record(record_id, workspace_id=workspace_id)
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.put("/records/{record_id}", response_model=DatasetRecordResponse)
async def update_record(
    record_id: str,
    request: DatasetRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        return await service.update_record(
            record_id, request.model_dump(exclude_unset=True), workspace_id=workspace_id
        )
    except DatasetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/records/{record_id}", status_code=204)
async def delete_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = extract_workspace_id(current_key)
    service = DatasetService(db)
    try:
        await service.delete_record(record_id, workspace_id=workspace_id)
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
        file_path = await import_export_service.execute_export(
            job.id, version_id, workspace_id=workspace_id
        )
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

    if (
        not os.path.exists(target_path)
        or not os.path.isfile(target_path)
        or os.path.islink(target_path)
    ):
        raise HTTPException(status_code=404, detail="File not found")

    clean_fn = os.path.basename(target_path)
    relative_path = os.path.relpath(target_path, base_dir).replace("\\", "/")

    project_repo = ProjectRepository(db)
    is_authorized = False

    # 1. Check ExportJob ownership
    if clean_fn.startswith("export_"):
        export_stmt = select(ExportJob).where(
            (ExportJob.file_path == target_path)
            | (ExportJob.file_path == relative_path)
            | (ExportJob.file_path == clean_fn)
        )
        export_res = (await db.execute(export_stmt)).scalars().all()

        if not export_res:
            parts = clean_fn.split(".")
            if len(parts) >= 2:
                job_id = parts[0].replace("export_", "")
                job = await db.get(ExportJob, job_id)
                if job and (
                    job.file_path == target_path
                    or job.file_path == relative_path
                    or job.file_path == clean_fn
                    or os.path.basename(job.file_path) == clean_fn
                ):
                    export_res = [job]

        for job in export_res:
            proj = await project_repo.get_by_id(
                job.project_id, workspace_id=workspace_id
            )
            if proj:
                is_authorized = True
                break

    # 2. Check ImportJob ownership
    if not is_authorized and clean_fn.startswith("import_"):
        import_stmt = select(ImportJob).where(
            (ImportJob.file_path == target_path)
            | (ImportJob.file_path == relative_path)
            | (ImportJob.file_path == clean_fn)
        )
        import_res = (await db.execute(import_stmt)).scalars().all()

        if not import_res:
            parts = clean_fn.split(".")
            if len(parts) >= 2:
                job_id = parts[0].replace("import_", "")
                job = await db.get(ImportJob, job_id)
                if job and (
                    job.file_path == target_path
                    or job.file_path == relative_path
                    or job.file_path == clean_fn
                    or os.path.basename(job.file_path) == clean_fn
                ):
                    import_res = [job]

        for job in import_res:
            proj = await project_repo.get_by_id(
                job.project_id, workspace_id=workspace_id
            )
            if proj:
                is_authorized = True
                break

    # 3. DENY access if ownership cannot be established for caller's workspace
    if not is_authorized:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(target_path, filename=clean_fn)
