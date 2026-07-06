import uuid
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.enterprise.models import Membership, Role
from app.enterprise.exceptions import TenantAccessViolationException

# Default permission sets
ROLE_PERMISSIONS = {
    "Owner": {
        "org:read", "org:write", "org:delete",
        "workspace:read", "workspace:write", "workspace:delete",
        "billing:read", "billing:write",
        "member:invite", "member:remove", "member:update"
    },
    "Admin": {
        "org:read", "org:write",
        "workspace:read", "workspace:write", "workspace:delete",
        "billing:read", "billing:write",
        "member:invite", "member:remove"
    },
    "Manager": {
        "org:read",
        "workspace:read", "workspace:write",
        "billing:read",
        "member:invite"
    },
    "Developer": {
        "org:read",
        "workspace:read", "workspace:write"
    },
    "Viewer": {
        "org:read",
        "workspace:read"
    },
    "Auditor": {
        "org:read",
        "workspace:read",
        "audit:read"
    }
}


class RBACService:
    """Manages role-based access control, custom organization roles, and permission inheritance."""

    async def get_user_permissions(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Set[str]:
        stmt = select(Membership).where(
            Membership.organization_id == org_id,
            Membership.user_id == user_id,
            Membership.is_active == True
        )
        res = await db.execute(stmt)
        membership = res.scalar_one_or_none()

        if not membership:
            return set()

        permissions = set()
        
        # If custom role is linked
        if membership.role_id:
            role_stmt = select(Role).where(Role.id == membership.role_id)
            role_res = await db.execute(role_stmt)
            role = role_res.scalar_one_or_none()
            if role:
                permissions.update(role.permissions)
        else:
            # Default fallback role mapping (Default Developer role)
            permissions.update(ROLE_PERMISSIONS.get("Developer", []))

        return permissions

    async def verify_permission(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        required_permission: str
    ) -> bool:
        user_perms = await self.get_user_permissions(db, org_id, user_id)
        # Owner bypass
        if "org:delete" in user_perms:
            return True
        return required_permission in user_perms

    async def create_custom_role(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        name: str,
        permissions: List[str]
    ) -> Role:
        role = Role(
            id=uuid.uuid4(),
            organization_id=org_id,
            name=name,
            permissions=permissions
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role
