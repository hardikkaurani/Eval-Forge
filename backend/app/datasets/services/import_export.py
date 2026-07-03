import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.datasets.exceptions.exceptions import DatasetValidationException, InvalidDatasetFormatException
from app.datasets.metadata.engine import DatasetMetadataEngine
from app.datasets.parsers.parsers import DatasetParser
from app.datasets.repositories.dataset import DatasetRepository
from app.datasets.storage.local import LocalStorage
from app.datasets.validators.validators import DatasetValidator
from app.models.dataset import ImportJob, ExportJob
from app.utils.time import get_utc_now


class ImportExportService:
    """Service layer orchestrating file imports/exports, validations, storage, and status updates."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.dataset_repo = DatasetRepository(db)
        self.storage = LocalStorage()

    async def create_import_job(self, project_id: str, file_format: str) -> ImportJob:
        job = ImportJob(
            project_id=project_id,
            status="PENDING",
            file_format=file_format,
            progress=0.0,
            total_records=0,
            processed_records=0,
            validation_report={},
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def process_import(
        self,
        job_id: str,
        file_content: bytes,
        dataset_name: str,
        project_id: str,
        description: Optional[str] = None,
        visibility: str = "private",
        owner: Optional[str] = None,
        source: Optional[str] = None,
        language: Optional[str] = "en",
        license: Optional[str] = None,
        tags: List[str] = None,
        existing_dataset_id: Optional[str] = None,
        version_label: str = "v1",
    ) -> Dict[str, Any]:
        tags = tags or []

        # Find or fetch import job
        job_result = await self.db.get(ImportJob, job_id)
        if not job_result:
            raise ValueError(f"Import job '{job_id}' not found.")
        job = job_result

        try:
            job.status = "PROCESSING"
            job.progress = 10.0
            await self.db.commit()

            # 1. Encoding check
            is_valid_encoding, err = DatasetValidator.validate_file_content(file_content)
            if not is_valid_encoding:
                raise DatasetValidationException(f"Encoding check failed: {err}")

            job.progress = 25.0
            await self.db.commit()

            # 2. Parse file
            records = DatasetParser.parse(file_content, job.file_format)
            job.total_records = len(records)
            job.progress = 50.0
            await self.db.commit()

            # 3. Validate schema / integrity
            validation_report = DatasetValidator.validate_records(records)
            job.validation_report = validation_report
            if not validation_report["valid"]:
                # If there are error issues in validation, we reject the import
                raise DatasetValidationException(
                    "Dataset records validation failed.",
                    details=validation_report["errors"],
                )

            job.progress = 70.0
            await self.db.commit()

            # 4. Profile metadata and calculate fingerprint
            profile = DatasetMetadataEngine.profile_dataset(records)
            fingerprint = DatasetMetadataEngine.calculate_fingerprint(records)

            # 5. Save or find dataset
            if existing_dataset_id:
                dataset = await self.dataset_repo.get_dataset(existing_dataset_id)
                if not dataset:
                    raise ValueError(f"Dataset '{existing_dataset_id}' not found.")
            else:
                dataset = await self.dataset_repo.create_dataset(
                    project_id=project_id,
                    name=dataset_name,
                    description=description,
                    visibility=visibility,
                    owner=owner,
                    source=source,
                    language=language,
                    license=license,
                    tags=list(set(tags + profile.get("unique_tags", []))),
                    metadata_json={
                        "data_quality_score": profile.get("data_quality_score"),
                        "token_estimate": profile.get("token_estimate"),
                    },
                )

            # 6. Create dataset version & records
            version = await self.dataset_repo.create_version(
                dataset_id=dataset.id,
                version=version_label,
                record_count=len(records),
                schema_version="1.0",
                hash_val=fingerprint,
                checksum=fingerprint,
                metadata_json=profile,
            )

            await self.dataset_repo.bulk_create_records(version.id, records)

            # Update job state to completed
            job.dataset_id = dataset.id
            job.processed_records = len(records)
            job.status = "COMPLETED"
            job.progress = 100.0
            job.completed_at = get_utc_now()
            await self.db.commit()

            return {
                "dataset_id": dataset.id,
                "version_id": version.id,
                "records_imported": len(records),
                "profile": profile,
            }

        except Exception as e:
            job.status = "FAILED"
            job.error_message = str(e)
            job.completed_at = get_utc_now()
            await self.db.commit()
            raise e

    async def create_export_job(self, project_id: str, file_format: str, dataset_id: Optional[str] = None) -> ExportJob:
        job = ExportJob(
            project_id=project_id,
            dataset_id=dataset_id,
            status="PENDING",
            file_format=file_format,
            progress=0.0,
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def execute_export(self, job_id: str, version_id: str) -> str:
        job_result = await self.db.get(ExportJob, job_id)
        if not job_result:
            raise ValueError(f"Export job '{job_id}' not found.")
        job = job_result

        try:
            job.status = "PROCESSING"
            job.progress = 20.0
            await self.db.commit()

            # Retrieve version and records
            version = await self.dataset_repo.get_version(version_id)
            if not version:
                raise ValueError(f"Dataset version '{version_id}' not found.")

            records, _ = await self.dataset_repo.get_records(version_id, limit=1000000)
            job.progress = 50.0
            await self.db.commit()

            # Build list of dicts to serialize
            data = []
            for rec in records:
                row = {
                    "prompt": rec.prompt,
                    "input": rec.input,
                    "context": rec.context,
                    "reference_output": rec.reference_output,
                    "candidate_output": rec.candidate_output,
                    "ground_truth": rec.ground_truth,
                    "expected_score": rec.expected_score,
                    "tags": ",".join(rec.tags) if rec.tags else "",
                }
                # merge custom fields if they exist
                if rec.custom_fields:
                    row.update(rec.custom_fields)
                data.append(row)

            job.progress = 80.0
            await self.db.commit()

            # Write content to bytes based on format
            fmt = job.file_format.lower().strip()
            buffer = io.BytesIO()

            if fmt == "csv":
                if data:
                    text_io = io.StringIO()
                    writer = csv.DictWriter(text_io, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                    buffer.write(text_io.getvalue().encode("utf-8"))
            elif fmt == "json":
                buffer.write(json.dumps(data, indent=2, default=str).encode("utf-8"))
            elif fmt == "jsonl":
                lines = [json.dumps(row, default=str) for row in data]
                buffer.write("\n".join(lines).encode("utf-8"))
            else:
                raise InvalidDatasetFormatException(job.file_format, "Export format not supported.")

            buffer.seek(0)

            # Save in storage
            filename = f"export_{job.id}.{fmt}"
            saved_path = await self.storage.save(filename, buffer)

            job.file_path = saved_path
            job.status = "COMPLETED"
            job.progress = 100.0
            job.completed_at = get_utc_now()
            await self.db.commit()

            return saved_path

        except Exception as e:
            job.status = "FAILED"
            job.error_message = str(e)
            job.completed_at = get_utc_now()
            await self.db.commit()
            raise e
