import structlog
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseException, NotFoundException
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.utils.time import get_utc_now
from app.utils.uuid import generate_uuid

logger = structlog.get_logger()


class ProjectRepository:
    """Repository class for handling async database operations on the Project model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, schema: ProjectCreate) -> Project:
        """Creates a new project record in the database."""
        try:
            project = Project(
                id=generate_uuid(),
                name=schema.name,
                description=schema.description,
                status=schema.status,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            )
            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)
            return project
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Database error during project creation", error=str(e)
            )
            raise DatabaseException(
                message="Failed to create project due to a database error.",
                details=str(e),
            ) from e

    async def get_by_id(
        self, project_id: str, include_deleted: bool = False
    ) -> Project | None:
        """Retrieves a single project by its unique ID."""
        try:
            stmt = select(Project).where(Project.id == project_id)
            if not include_deleted:
                stmt = stmt.where(Project.deleted_at.is_(None))
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                "Database error during project retrieval by ID",
                project_id=project_id,
                error=str(e),
            )
            raise DatabaseException(
                message=f"Failed to retrieve project {project_id}.",
                details=str(e),
            ) from e

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[list[Project], int]:
        """Lists projects matching filters, pagination, and sorting criteria.

        Returns a tuple of (items, total_count).
        """
        try:
            # Build filters
            filters = []
            if not include_deleted:
                filters.append(Project.deleted_at.is_(None))

            if status:
                filters.append(Project.status == status)

            if search:
                search_filter = or_(
                    Project.name.ilike(f"%{search}%"),
                    Project.description.ilike(f"%{search}%"),
                )
                filters.append(search_filter)

            # Count query
            count_stmt = select(func.count()).select_from(Project)
            if filters:
                count_stmt = count_stmt.where(and_(*filters))

            count_result = await self.db.execute(count_stmt)
            total = count_result.scalar_one()

            # Base select query
            stmt = select(Project)
            if filters:
                stmt = stmt.where(and_(*filters))

            # Sorting
            sort_attr = getattr(Project, sort_by, Project.created_at)
            if sort_order.lower() == "desc":
                stmt = stmt.order_by(desc(sort_attr))
            else:
                stmt = stmt.order_by(asc(sort_attr))

            # Pagination
            stmt = stmt.offset(skip).limit(limit)

            result = await self.db.execute(stmt)
            items = list(result.scalars().all())

            return items, total
        except Exception as e:
            logger.error(
                "Database error during project listing", error=str(e)
            )
            raise DatabaseException(
                message="Failed to retrieve list of projects.",
                details=str(e),
            ) from e

    async def update(self, project_id: str, schema: ProjectUpdate) -> Project:
        """Performs a sparse update of a project's fields."""
        project = await self.get_by_id(project_id)
        if not project:
            raise NotFoundException(
                message=f"Project with ID {project_id} not found."
            )

        try:
            update_data = schema.model_dump(exclude_unset=True)
            if update_data:
                update_data["updated_at"] = get_utc_now()
                for key, val in update_data.items():
                    setattr(project, key, val)

                await self.db.commit()
                await self.db.refresh(project)
            return project
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Database error during project update",
                project_id=project_id,
                error=str(e),
            )
            raise DatabaseException(
                message=f"Failed to update project {project_id}.",
                details=str(e),
            ) from e

    async def soft_delete(self, project_id: str) -> Project:
        """Marks a project as soft-deleted by setting deleted_at to current UTC time."""
        project = await self.get_by_id(project_id)
        if not project:
            raise NotFoundException(
                message=f"Project with ID {project_id} not found."
            )

        try:
            project.deleted_at = get_utc_now()
            project.updated_at = get_utc_now()
            await self.db.commit()
            await self.db.refresh(project)
            return project
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Database error during project soft deletion",
                project_id=project_id,
                error=str(e),
            )
            raise DatabaseException(
                message=f"Failed to delete project {project_id}.",
                details=str(e),
            ) from e
