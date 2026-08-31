from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dataset import Dataset, DatasetRecord, DatasetVersion


class DatasetRepository:
    """Repository handling all database persistence operations for datasets, versions, and records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_dataset(
        self,
        project_id: str,
        name: str,
        description: Optional[str],
        visibility: str,
        owner: Optional[str],
        source: Optional[str],
        language: Optional[str],
        license: Optional[str],
        tags: List[str],
        metadata_json: Dict[str, Any],
    ) -> Dataset:
        dataset = Dataset(
            project_id=project_id,
            name=name,
            description=description,
            visibility=visibility,
            owner=owner,
            source=source,
            language=language,
            license=license,
            tags=tags,
            metadata_json=metadata_json,
        )
        self.db.add(dataset)
        await self.db.flush()
        return dataset

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        result = await self.db.execute(
            select(Dataset)
            .where(Dataset.id == dataset_id)
            .options(selectinload(Dataset.versions))
        )
        return result.scalar_one_or_none()

    async def list_datasets(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        tag: Optional[str] = None,
        language: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> Tuple[List[Dataset], int]:
        query = select(Dataset).where(Dataset.project_id == project_id)

        if search:
            query = query.where(
                or_(
                    Dataset.name.ilike(f"%{search}%"),
                    Dataset.description.ilike(f"%{search}%"),
                )
            )

        if tag:
            # PostgreSQL-specific or JSON-fallback tag search
            query = query.where(Dataset.tags.contains([tag]))

        if language:
            query = query.where(Dataset.language == language)

        if visibility:
            query = query.where(Dataset.visibility == visibility)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Paginated query
        query = query.order_by(Dataset.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        datasets = list(result.scalars().all())

        return datasets, total

    async def update_dataset(
        self, dataset_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dataset]:
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            return None

        # Enforce field immutability: id and project_id cannot be reassigned or mutated
        update_data.pop("id", None)
        update_data.pop("project_id", None)

        for key, val in update_data.items():
            if val is not None:
                setattr(dataset, key, val)

        await self.db.flush()
        return dataset

    async def delete_dataset(self, dataset_id: str) -> bool:
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            return False

        await self.db.delete(dataset)
        await self.db.flush()
        return True

    async def create_version(
        self,
        dataset_id: str,
        version: str,
        record_count: int,
        schema_version: str,
        hash_val: Optional[str],
        checksum: Optional[str],
        metadata_json: Dict[str, Any],
    ) -> DatasetVersion:
        version_obj = DatasetVersion(
            dataset_id=dataset_id,
            version=version,
            record_count=record_count,
            schema_version=schema_version,
            hash=hash_val,
            checksum=checksum,
            metadata_json=metadata_json,
        )
        self.db.add(version_obj)
        await self.db.flush()
        return version_obj

    async def get_version(self, version_id: str) -> Optional[DatasetVersion]:
        result = await self.db.execute(
            select(DatasetVersion).where(DatasetVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    async def get_version_by_label(
        self, dataset_id: str, version_label: str
    ) -> Optional[DatasetVersion]:
        result = await self.db.execute(
            select(DatasetVersion).where(
                and_(
                    DatasetVersion.dataset_id == dataset_id,
                    DatasetVersion.version == version_label,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_versions(self, dataset_id: str) -> List[DatasetVersion]:
        result = await self.db.execute(
            select(DatasetVersion)
            .where(DatasetVersion.dataset_id == dataset_id)
            .order_by(DatasetVersion.created_at.desc())
        )
        return list(result.scalars().all())

    async def bulk_create_records(
        self, version_id: str, records_data: List[Dict[str, Any]]
    ) -> List[DatasetRecord]:
        records = []
        for row in records_data:
            rec = DatasetRecord(
                version_id=version_id,
                prompt=row.get("prompt", ""),
                input=row.get("input"),
                context=row.get("context"),
                reference_output=row.get("reference_output"),
                candidate_output=row.get("candidate_output"),
                ground_truth=row.get("ground_truth"),
                expected_score=row.get("expected_score"),
                tags=row.get("tags", []),
                custom_fields=row.get("custom_fields", {}),
                metadata_json=row.get("metadata_json", {}),
            )
            self.db.add(rec)
            records.append(rec)
        await self.db.flush()
        return records

    async def get_records(
        self,
        version_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[DatasetRecord], int]:
        # Bound and normalize pagination parameters
        skip = max(0, skip)
        if limit < 1:
            limit = 100
        else:
            limit = min(limit, 1000)

        query = select(DatasetRecord).where(DatasetRecord.version_id == version_id)

        # Count using SQL count without row materialization
        count_query = select(func.count(DatasetRecord.id)).where(
            DatasetRecord.version_id == version_id
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Paginated records with deterministic order
        query = query.order_by(DatasetRecord.created_at.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        records = list(result.scalars().all())

        return records, total

    async def get_record(self, record_id: str) -> Optional[DatasetRecord]:
        result = await self.db.execute(
            select(DatasetRecord).where(DatasetRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def update_record(
        self, record_id: str, update_data: Dict[str, Any]
    ) -> Optional[DatasetRecord]:
        record = await self.get_record(record_id)
        if not record:
            return None
        # Enforce field immutability: version_id and id cannot be mutated or reassigned
        update_data.pop("id", None)
        update_data.pop("version_id", None)
        for key, val in update_data.items():
            if val is not None and hasattr(record, key):
                setattr(record, key, val)
        await self.db.flush()
        return record

    async def delete_record(self, record_id: str) -> bool:
        record = await self.get_record(record_id)
        if not record:
            return False
        await self.db.delete(record)
        await self.db.flush()
        return True
