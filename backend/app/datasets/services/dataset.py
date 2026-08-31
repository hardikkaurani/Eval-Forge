from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import ProjectRepository
from app.datasets.exceptions.exceptions import (
    DatasetNotFoundException,
)
from app.datasets.repositories.dataset import DatasetRepository
from app.datasets.schemas.dataset import DatasetDiffItem
from app.models.dataset import Dataset, DatasetRecord, DatasetVersion


class DatasetService:
    """Service orchestrating general dataset lifecycle operations, version management, and diff generation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.dataset_repo = DatasetRepository(db)
        self.project_repo = ProjectRepository(db)

    async def create_empty_dataset(
        self,
        project_id: str,
        name: str,
        description: Optional[str] = None,
        visibility: str = "private",
        owner: Optional[str] = None,
        source: Optional[str] = None,
        language: Optional[str] = "en",
        license: Optional[str] = None,
        tags: List[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dataset:
        project = await self.project_repo.get_by_id(
            project_id, workspace_id=workspace_id
        )
        if not project:
            raise DatasetNotFoundException(
                project_id, f"Project '{project_id}' not found."
            )

        tags = tags or []
        dataset = await self.dataset_repo.create_dataset(
            project_id=project_id,
            name=name,
            description=description,
            visibility=visibility,
            owner=owner,
            source=source,
            language=language,
            license=license,
            tags=tags,
            metadata_json={"data_quality_score": 100.0},
        )
        # Create an empty initial v1 version
        await self.dataset_repo.create_version(
            dataset_id=dataset.id,
            version="v1",
            record_count=0,
            schema_version="1.0",
            hash_val=None,
            checksum=None,
            metadata_json={},
        )
        await self.db.commit()
        return dataset

    async def get_dataset(
        self, dataset_id: str, workspace_id: Optional[str] = None
    ) -> Dataset:
        dataset = await self.dataset_repo.get_dataset(dataset_id)
        if not dataset:
            raise DatasetNotFoundException(dataset_id)
        project = await self.project_repo.get_by_id(
            dataset.project_id, workspace_id=workspace_id
        )
        if not project:
            raise DatasetNotFoundException(dataset_id)
        return dataset

    async def list_datasets(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        tag: Optional[str] = None,
        language: Optional[str] = None,
        visibility: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Tuple[List[Dataset], int]:
        project = await self.project_repo.get_by_id(
            project_id, workspace_id=workspace_id
        )
        if not project:
            raise DatasetNotFoundException(
                project_id, f"Project '{project_id}' not found."
            )

        return await self.dataset_repo.list_datasets(
            project_id=project_id,
            skip=skip,
            limit=limit,
            search=search,
            tag=tag,
            language=language,
            visibility=visibility,
        )

    async def update_dataset(
        self,
        dataset_id: str,
        update_data: Dict[str, Any],
        workspace_id: Optional[str] = None,
    ) -> Dataset:
        await self.get_dataset(dataset_id, workspace_id=workspace_id)
        dataset = await self.dataset_repo.update_dataset(dataset_id, update_data)
        if not dataset:
            raise DatasetNotFoundException(dataset_id)
        await self.db.commit()
        return dataset

    async def delete_dataset(
        self, dataset_id: str, workspace_id: Optional[str] = None
    ) -> None:
        await self.get_dataset(dataset_id, workspace_id=workspace_id)
        success = await self.dataset_repo.delete_dataset(dataset_id)
        if not success:
            raise DatasetNotFoundException(dataset_id)
        await self.db.commit()

    async def get_dataset_version_by_label(
        self, dataset_id: str, version_label: str, workspace_id: Optional[str] = None
    ) -> DatasetVersion:
        await self.get_dataset(dataset_id, workspace_id=workspace_id)
        version = await self.dataset_repo.get_version_by_label(
            dataset_id, version_label
        )
        if not version:
            raise DatasetNotFoundException(
                dataset_id, f"Version '{version_label}' not found."
            )
        return version

    async def list_versions(
        self, dataset_id: str, workspace_id: Optional[str] = None
    ) -> List[DatasetVersion]:
        await self.get_dataset(dataset_id, workspace_id=workspace_id)
        return await self.dataset_repo.list_versions(dataset_id)

    async def get_records(
        self,
        version_id: str,
        skip: int = 0,
        limit: int = 100,
        workspace_id: Optional[str] = None,
    ) -> Tuple[Any, int]:
        version = await self.dataset_repo.get_version(version_id)
        if not version:
            raise DatasetNotFoundException(
                version_id, f"Version '{version_id}' not found."
            )
        await self.get_dataset(version.dataset_id, workspace_id=workspace_id)
        return await self.dataset_repo.get_records(version_id, skip=skip, limit=limit)

    async def create_records(
        self,
        version_id: str,
        records_data: List[Dict[str, Any]],
        workspace_id: Optional[str] = None,
    ) -> List[DatasetRecord]:
        version = await self.dataset_repo.get_version(version_id)
        if not version:
            raise DatasetNotFoundException(
                version_id, f"Version '{version_id}' not found."
            )
        await self.get_dataset(version.dataset_id, workspace_id=workspace_id)
        created_records = await self.dataset_repo.bulk_create_records(
            version_id, records_data
        )
        version.record_count += len(created_records)
        await self.db.commit()
        return created_records

    async def get_single_record(
        self,
        record_id: str,
        workspace_id: Optional[str] = None,
    ) -> DatasetRecord:
        record = await self.dataset_repo.get_record(record_id)
        if not record:
            raise DatasetNotFoundException(
                record_id, f"Record '{record_id}' not found."
            )
        version = await self.dataset_repo.get_version(record.version_id)
        if not version:
            raise DatasetNotFoundException(record_id)
        await self.get_dataset(version.dataset_id, workspace_id=workspace_id)
        return record

    async def update_record(
        self,
        record_id: str,
        update_data: Dict[str, Any],
        workspace_id: Optional[str] = None,
    ) -> DatasetRecord:
        await self.get_single_record(record_id, workspace_id=workspace_id)
        record = await self.dataset_repo.update_record(record_id, update_data)
        if not record:
            raise DatasetNotFoundException(record_id)
        await self.db.commit()
        return record

    async def delete_record(
        self,
        record_id: str,
        workspace_id: Optional[str] = None,
    ) -> None:
        record = await self.get_single_record(record_id, workspace_id=workspace_id)
        version = await self.dataset_repo.get_version(record.version_id)
        success = await self.dataset_repo.delete_record(record_id)
        if not success:
            raise DatasetNotFoundException(record_id)
        if version and version.record_count > 0:
            version.record_count -= 1
        await self.db.commit()

    async def generate_diff(
        self,
        dataset_id: str,
        version_a_label: str,
        version_b_label: str,
        workspace_id: Optional[str] = None,
    ) -> List[DatasetDiffItem]:
        """Compares two versions of a dataset and returns detailed changes per record."""
        ver_a = await self.get_dataset_version_by_label(
            dataset_id, version_a_label, workspace_id=workspace_id
        )
        ver_b = await self.get_dataset_version_by_label(
            dataset_id, version_b_label, workspace_id=workspace_id
        )

        records_a, _ = await self.dataset_repo.get_records(ver_a.id, skip=0, limit=1000)
        records_b, _ = await self.dataset_repo.get_records(ver_b.id, skip=0, limit=1000)

        map_a = {rec.prompt.strip(): rec for rec in records_a}
        map_b = {rec.prompt.strip(): rec for rec in records_b}

        diffs: List[DatasetDiffItem] = []

        # Find deleted and modified
        for prompt, rec_a in map_a.items():
            if prompt not in map_b:
                diffs.append(
                    DatasetDiffItem(
                        record_id=rec_a.id,
                        change_type="removed",
                        prompt_diff=f"- {prompt}",
                    )
                )
            else:
                rec_b = map_b[prompt]
                field_diffs = {}
                for field in [
                    "input",
                    "context",
                    "reference_output",
                    "candidate_output",
                    "ground_truth",
                    "expected_score",
                ]:
                    val_a = getattr(rec_a, field)
                    val_b = getattr(rec_b, field)
                    if val_a != val_b:
                        field_diffs[field] = {"old": val_a, "new": val_b}

                if field_diffs:
                    diffs.append(
                        DatasetDiffItem(
                            record_id=rec_b.id,
                            change_type="modified",
                            field_diffs=field_diffs,
                        )
                    )

        # Find added
        for prompt, rec_b in map_b.items():
            if prompt not in map_a:
                diffs.append(
                    DatasetDiffItem(
                        record_id=rec_b.id,
                        change_type="added",
                        prompt_diff=f"+ {prompt}",
                    )
                )

        return diffs

    async def rollback_version(
        self,
        dataset_id: str,
        target_version_label: str,
        workspace_id: Optional[str] = None,
    ) -> DatasetVersion:
        """Promotes an old version by creating a new version cloned from the target version."""
        target_version = await self.get_dataset_version_by_label(
            dataset_id, target_version_label, workspace_id=workspace_id
        )

        # Find all current versions to compute next label index
        versions = await self.dataset_repo.list_versions(dataset_id)
        next_version_num = len(versions) + 1
        new_version_label = f"v{next_version_num}"

        # Create cloned version
        new_version = await self.dataset_repo.create_version(
            dataset_id=dataset_id,
            version=new_version_label,
            record_count=target_version.record_count,
            schema_version=target_version.schema_version,
            hash_val=target_version.hash,
            checksum=target_version.checksum,
            metadata_json=target_version.metadata_json,
        )

        # Chunked copy of records (1,000 records per chunk) to avoid memory spikes
        chunk_size = 1000
        offset = 0
        total_records = target_version.record_count

        while offset < total_records or offset == 0:
            records, count = await self.dataset_repo.get_records(
                target_version.id, skip=offset, limit=chunk_size
            )
            if not records:
                break

            records_data = [
                {
                    "prompt": r.prompt,
                    "input": r.input,
                    "context": r.context,
                    "reference_output": r.reference_output,
                    "candidate_output": r.candidate_output,
                    "ground_truth": r.ground_truth,
                    "expected_score": r.expected_score,
                    "tags": r.tags,
                    "custom_fields": r.custom_fields,
                    "metadata_json": r.metadata_json,
                }
                for r in records
            ]
            await self.dataset_repo.bulk_create_records(new_version.id, records_data)
            offset += len(records)
            if offset >= count:
                break

        await self.db.commit()
        return new_version
