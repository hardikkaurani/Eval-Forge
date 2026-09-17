"""Provision a workspace and its initial administrator key using database access."""

import argparse
import asyncio
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database.session import SessionLocal, engine  # noqa: E402
from app.enterprise.models import (  # noqa: E402
    Membership,
    Organization,
    Role,
    Workspace,
)
from app.enterprise.services.apikey_service import EnterpriseAPIKeyService  # noqa: E402


async def provision(name: str, expires: int):
    async with SessionLocal() as db:
        org = Organization(id=uuid.uuid4(), name=name)
        workspace = Workspace(id=uuid.uuid4(), organization_id=org.id, name=name)
        db.add(org)
        await db.flush()
        db.add(workspace)
        await db.flush()
        raw, key = await EnterpriseAPIKeyService().generate_key(
            db,
            name="Workspace administrator",
            org_id=org.id,
            workspace_id=workspace.id,
            scopes=["read:all", "write:all"],
            expires_in_days=expires,
        )
        role = Role(
            id=uuid.uuid4(), organization_id=org.id, name="Owner", permissions=[]
        )
        db.add(role)
        await db.flush()
        db.add(
            Membership(
                organization_id=org.id,
                workspace_id=workspace.id,
                user_id=key.id,
                role_id=role.id,
            )
        )
        await db.commit()
        print(f"Workspace: {workspace.id}")
        print(f"API key (save now; expires in {expires} days): {raw}")
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--expires-days", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.expires_days <= 365:
        parser.error("--expires-days must be between 1 and 365")
    asyncio.run(provision(args.name, args.expires_days))
