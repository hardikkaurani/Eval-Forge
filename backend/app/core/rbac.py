from enum import Enum
from typing import Dict, Set

from fastapi import HTTPException, status


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    AUDITOR = "auditor"


# Mapping roles to their allowed scopes/permissions
ROLE_PERMISSIONS: Dict[Role, Set[str]] = {
    Role.OWNER: {
        "projects:create",
        "projects:read",
        "projects:update",
        "projects:delete",
        "evaluations:create",
        "evaluations:read",
        "evaluations:update",
        "evaluations:delete",
        "datasets:create",
        "datasets:read",
        "datasets:update",
        "datasets:delete",
        "policies:manage",
        "users:manage",
        "billing:manage",
        "audit_logs:read",
    },
    Role.ADMIN: {
        "projects:create",
        "projects:read",
        "projects:update",
        "evaluations:create",
        "evaluations:read",
        "evaluations:update",
        "evaluations:delete",
        "datasets:create",
        "datasets:read",
        "datasets:update",
        "datasets:delete",
        "policies:manage",
        "audit_logs:read",
    },
    Role.DEVELOPER: {
        "projects:read",
        "evaluations:create",
        "evaluations:read",
        "evaluations:update",
        "datasets:create",
        "datasets:read",
        "datasets:update",
    },
    Role.VIEWER: {"projects:read", "evaluations:read", "datasets:read"},
    Role.AUDITOR: {"projects:read", "evaluations:read", "audit_logs:read"},
}


class PermissionChecker:
    """Dependency that checks if a user's role has the required permission/scope."""

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, user_role: str = "viewer") -> bool:
        try:
            role_enum = Role(user_role.lower())
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid user role: {user_role}",
            ) from e

        allowed_permissions = ROLE_PERMISSIONS.get(role_enum, set())
        if self.required_permission not in allowed_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation forbidden. Required permission: '{self.required_permission}'",
            )
        return True
