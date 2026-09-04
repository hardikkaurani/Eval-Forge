import uuid
from typing import List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.enterprise.exceptions import TenantAccessViolationException
from app.enterprise.models import Membership, Role

# Canonical permission definitions
CANONICAL_PERMISSIONS = {
    # Organization
    "org:read",
    "org:write",
    "org:delete",
    # Members & Ownership
    "members:read",
    "members:invite",
    "members:update",
    "members:remove",
    "ownership:transfer",
    # Billing
    "billing:read",
    "billing:manage",
    # Workspaces
    "workspaces:read",
    "workspaces:create",
    "workspaces:write",
    "workspaces:delete",
    # Projects
    "projects:read",
    "projects:write",
    "projects:delete",
    # Datasets
    "datasets:read",
    "datasets:write",
    "datasets:delete",
    # Evaluations
    "evaluations:read",
    "evaluations:create",
    "evaluations:cancel",
    "evaluations:delete",
    # API Keys
    "api_keys:read",
    "api_keys:create",
    "api_keys:revoke",
    # Webhooks
    "webhooks:read",
    "webhooks:write",
    "webhooks:delete",
    # Audit Logs
    "audit:read",
}

# Role to permission matrix
ROLE_PERMISSIONS: dict[str, Set[str]] = {
    "Owner": set(CANONICAL_PERMISSIONS),
    "Admin": {
        "org:read",
        "org:write",
        "members:read",
        "members:invite",
        "members:update",
        "members:remove",
        "billing:read",
        "billing:manage",
        "workspaces:read",
        "workspaces:create",
        "workspaces:write",
        "workspaces:delete",
        "projects:read",
        "projects:write",
        "projects:delete",
        "datasets:read",
        "datasets:write",
        "datasets:delete",
        "evaluations:read",
        "evaluations:create",
        "evaluations:cancel",
        "evaluations:delete",
        "api_keys:read",
        "api_keys:create",
        "api_keys:revoke",
        "webhooks:read",
        "webhooks:write",
        "webhooks:delete",
        "audit:read",
    },
    "Member": {
        "org:read",
        "members:read",
        "workspaces:read",
        "projects:read",
        "projects:write",
        "datasets:read",
        "datasets:write",
        "evaluations:read",
        "evaluations:create",
        "evaluations:cancel",
        "api_keys:read",
        "api_keys:create",
        "webhooks:read",
    },
    "Viewer": {
        "org:read",
        "members:read",
        "workspaces:read",
        "projects:read",
        "datasets:read",
        "evaluations:read",
        "api_keys:read",
        "webhooks:read",
        "audit:read",
    },
}


class RBACService:
    """Manages role-based access control, permissions resolution, and fail-closed authorization."""

    async def get_user_role(
        self, db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[str]:
        """Resolves the user's role name in the given organization."""
        stmt = (
            select(Membership)
            .options(selectinload(Membership.role))
            .where(
                Membership.organization_id == org_id,
                Membership.user_id == user_id,
                Membership.is_active.is_(True),
            )
        )
        res = await db.execute(stmt)
        membership = res.scalar_one_or_none()
        if not membership or not membership.role:
            return None
        return membership.role.name

    async def get_user_permissions(
        self, db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> Set[str]:
        """Resolves all effective permissions for a user within an organization."""
        stmt = (
            select(Membership)
            .options(selectinload(Membership.role))
            .where(
                Membership.organization_id == org_id,
                Membership.user_id == user_id,
                Membership.is_active.is_(True),
            )
        )
        res = await db.execute(stmt)
        membership = res.scalar_one_or_none()

        if not membership:
            return set()

        # If custom or standard role is linked
        if membership.role:
            role_name = membership.role.name
            if role_name in ROLE_PERMISSIONS:
                return set(ROLE_PERMISSIONS[role_name])
            if membership.role.permissions:
                return set(membership.role.permissions)

        # Fail closed fallback
        return set()

    async def has_permission(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        required_permission: str,
    ) -> bool:
        """Evaluates whether the user has the required permission in the organization (Fail-Closed)."""
        user_perms = await self.get_user_permissions(db, org_id, user_id)
        # Owner wildcard
        if "*" in user_perms:
            return True
        return required_permission in user_perms

    async def require_permission(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        required_permission: str,
    ) -> None:
        """Enforces a permission check; raises TenantAccessViolationException on denial."""
        allowed = await self.has_permission(db, org_id, user_id, required_permission)
        if not allowed:
            raise TenantAccessViolationException(
                f"Access Denied: Missing required permission '{required_permission}' for organization {org_id}."
            )

    async def create_custom_role(
        self, db: AsyncSession, org_id: uuid.UUID, name: str, permissions: List[str]
    ) -> Role:
        """Creates a custom organization-scoped role with specified permissions."""
        role = Role(
            id=uuid.uuid4(), organization_id=org_id, name=name, permissions=permissions
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role
