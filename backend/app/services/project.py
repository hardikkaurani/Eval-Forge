import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.database.repository import ProjectRepository
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.utils.pagination import PageMetadata, create_pagination_meta, get_limit_offset
from app.utils.validation import validate_uuid

logger = structlog.get_logger()


class ProjectService:
    """Service class encapsulating the business logic for Project resources."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = ProjectRepository(db)

    async def create_project(self, schema: ProjectCreate) -> Project:
        """Handles business logic and persistence for creating a project."""
        logger.info("Service: Creating project", name=schema.name)
        return await self.repo.create(schema)

    async def get_project(self, project_id: str) -> Project:
        """Retrieves a project by ID, ensuring UUID format validation."""
        validate_uuid(project_id, "project_id")
        project = await self.repo.get_by_id(project_id)
        if not project:
            logger.warning("Service: Project not found", project_id=project_id)
            raise NotFoundException(
                message=f"Project with ID '{project_id}' was not found."
            )
        return project

    async def list_projects(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Project], PageMetadata]:
        """Validates sorting query parameters and lists projects with pagination metadata."""
        limit, offset = get_limit_offset(page, page_size)

        # Restrict sortable attributes to avoid schema vulnerabilities or query errors
        allowed_sort_fields = {"created_at", "updated_at", "name", "status"}
        if sort_by not in allowed_sort_fields:
            raise ValidationException(
                message=f"Sorting by '{sort_by}' is not supported.",
                details={"allowed_fields": list(allowed_sort_fields)},
            )

        if sort_order.lower() not in {"asc", "desc"}:
            raise ValidationException(message="Sort order must be 'asc' or 'desc'.")

        items, total = await self.repo.list(
            skip=offset,
            limit=limit,
            search=search,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        meta = create_pagination_meta(page=page, page_size=limit, total_items=total)
        return items, meta

    async def update_project(self, project_id: str, schema: ProjectUpdate) -> Project:
        """Validates UUID and performs project updates."""
        validate_uuid(project_id, "project_id")
        logger.info("Service: Updating project", project_id=project_id)
        return await self.repo.update(project_id, schema)

    async def delete_project(self, project_id: str) -> Project:
        """Validates UUID and performs soft deletion of a project."""
        validate_uuid(project_id, "project_id")
        logger.info("Service: Soft deleting project", project_id=project_id)
        return await self.repo.soft_delete(project_id)
