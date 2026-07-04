import base64
from typing import Any, Dict
from app.jobs.executors.base import BaseJobExecutor, ProgressCallback
from app.jobs.models.job import Job
from app.datasets.services.import_export import ImportExportService

class DatasetImportExecutor(BaseJobExecutor):
    """Executor that handles asynchronous parsing, validation, profiling, and loading of datasets."""

    async def execute(self, job: Job, progress_callback: ProgressCallback) -> Dict[str, Any]:
        payload = job.payload
        import_job_id = payload.get("import_job_id")
        file_content_b64 = payload.get("file_content")
        dataset_name = payload.get("dataset_name")
        project_id = payload.get("project_id")
        description = payload.get("description")
        visibility = payload.get("visibility", "private")
        owner = payload.get("owner")
        source = payload.get("source")
        language = payload.get("language", "en")
        license_type = payload.get("license")
        tags = payload.get("tags", [])
        existing_dataset_id = payload.get("existing_dataset_id")
        version_label = payload.get("version_label", "v1")

        if not import_job_id or not file_content_b64:
            raise ValueError("Payload missing required 'import_job_id' or 'file_content' keys.")

        await progress_callback(10.0, "Decoding uploaded file base64 content...")
        file_content = base64.b64decode(file_content_b64)

        from app.database.session import SessionLocal
        async with SessionLocal() as db:
            service = ImportExportService(db)
            await progress_callback(30.0, "Validating and parsing file contents...")
            
            res = await service.process_import(
                job_id=import_job_id,
                file_content=file_content,
                dataset_name=dataset_name,
                project_id=project_id,
                description=description,
                visibility=visibility,
                owner=owner,
                source=source,
                language=language,
                license=license_type,
                tags=tags,
                existing_dataset_id=existing_dataset_id,
                version_label=version_label
            )
            
            await progress_callback(100.0, "Dataset version created and records imported.")
            return res
