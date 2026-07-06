import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.enterprise.models import Workspace, Organization
from app.enterprise.exceptions import TenantAccessViolationException


class WorkspaceService:
    """Manages workspaces (e.g. staging, prod, dev) under organizations with custom configuration."""

    async def create_workspace(self, db: AsyncSession, org_id: uuid.UUID, name: str, description: str = None) -> Workspace:
        # Check if organization exists
        stmt = select(Organization).where(Organization.id == org_id)
        org_res = await db.execute(stmt)
        if not org_res.scalar_one_or_none():
            raise TenantAccessViolationException("Target organization does not exist.")

        workspace = Workspace(
            id=uuid.uuid4(),
            organization_id=org_id,
            name=name,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)
        return workspace

    async def list_workspaces(self, db: AsyncSession, org_id: uuid.UUID) -> list[Workspace]:
        stmt = select(Workspace).where(Workspace.organization_id == org_id)
        res = await db.execute(stmt)
        return list(res.scalars().all())
