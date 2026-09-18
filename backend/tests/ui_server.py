"""Local browser-test server: real API/auth/SQLite, explicit mock LLM, no Redis worker.

Run from the repository root with `python backend/tests/ui_server.py`.
This is test infrastructure and must never be used for deployment.
"""

import asyncio
import hashlib
import os
import sys
import tempfile
import uuid
from pathlib import Path
from unittest.mock import AsyncMock

temp_directory = tempfile.TemporaryDirectory(prefix="evalforge-ui-test-")
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "false"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///" + str(
    Path(temp_directory.name) / "browser.db"
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.models.advanced_ai  # noqa: E402, F401
import app.models.analytics  # noqa: E402, F401
import app.models.dataset  # noqa: E402, F401
import app.models.evaluation  # noqa: E402, F401
import app.platform.models  # noqa: E402, F401
from app.core.redis import redis_manager  # noqa: E402
from app.database.session import Base, SessionLocal, engine  # noqa: E402
from app.enterprise.models import (  # noqa: E402
    EnterpriseAPIKey,
    Organization,
    Workspace,
)
from app.jobs.models.job import Job  # noqa: E402
from app.main import app as application  # noqa: E402
from app.models.project import Project  # noqa: E402

redis_manager.init = lambda *args: None
redis_manager.ping = AsyncMock(return_value=False)
redis_manager.close = AsyncMock()

PROJECT_ID = "11111111-1111-4111-8111-111111111111"
SECOND_PROJECT_ID = "22222222-2222-4222-8222-222222222222"
JOB_ID = "33333333-3333-4333-8333-333333333333"


async def initialize():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        organization_id = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
        workspace_id = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
        db.add(Organization(id=organization_id, name="Browser validation"))
        db.add(
            Workspace(
                id=workspace_id,
                organization_id=organization_id,
                name="Browser validation",
            )
        )
        db.add(
            EnterpriseAPIKey(
                id=uuid.uuid4(),
                name="Local browser test key",
                key_hash=hashlib.sha256(b"ef_browser_test_only").hexdigest(),
                organization_id=organization_id,
                workspace_id=workspace_id,
                scopes=["read:all", "write:all"],
                is_active=True,
            )
        )
        db.add(
            Project(
                id=PROJECT_ID,
                workspace_id=str(workspace_id),
                name="Support assistant",
                description="Browser validation fixture · customer support evaluations",
                status="active",
            )
        )
        db.add(
            Project(
                id=SECOND_PROJECT_ID,
                workspace_id=str(workspace_id),
                name="Knowledge search",
                description="Browser validation fixture · retrieval quality",
                status="active",
            )
        )
        db.add(
            Job(
                id=JOB_ID,
                name="Dataset preparation",
                queue_name="default",
                status="COMPLETED",
                payload={"project_id": PROJECT_ID},
                progress=100,
                current_step="Ready for evaluation",
                max_retries=3,
                retry_count=0,
                timezone="UTC",
            )
        )
        db.add(
            Job(
                id="44444444-4444-4444-8444-444444444444",
                name="Running browser fixture",
                queue_name="default",
                status="RUNNING",
                payload={"project_id": PROJECT_ID},
                progress=10,
                current_step="Testing authenticated progress",
                max_retries=3,
                retry_count=0,
                timezone="UTC",
            )
        )
        await db.commit()


if __name__ == "__main__":
    import uvicorn

    asyncio.run(initialize())
    uvicorn.run(application, host="127.0.0.1", port=8000, log_level="warning")
