from typing import Any, Dict
from app.jobs.executors.base import BaseJobExecutor, ProgressCallback
from app.jobs.models.job import Job
from app.datasets.services.import_export import ImportExportService

class DatasetExportExecutor(BaseJobExecutor):
    """Executor that serializes and packages dataset version records into CSV/JSON/JSONL files."""

    async def execute(self, job: Job, progress_callback: ProgressCallback) -> Dict[str, Any]:
        payload = job.payload
        export_job_id = payload.get("export_job_id")
        version_id = payload.get("version_id")

        if not export_job_id or not version_id:
            raise ValueError("Payload missing required 'export_job_id' or 'version_id' keys.")

        await progress_callback(20.0, "Fetching version records from storage...")

        from app.database.session import SessionLocal
        async with SessionLocal() as db:
            service = ImportExportService(db)
            await progress_callback(50.0, "Serializing dataset structure to target format...")
            
            saved_path = await service.execute_export(
                job_id=export_job_id,
                version_id=version_id
            )
            
            await progress_callback(100.0, f"Dataset export completed. File ready at: {saved_path}")
            return {
                "export_job_id": export_job_id,
                "saved_path": saved_path
            }
