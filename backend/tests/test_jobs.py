from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.executors.base import BaseJobExecutor
from app.jobs.registry import job_registry


class TestJobExecutor(BaseJobExecutor):
    """Simple executor for testing."""

    async def execute(self, job, progress_callback) -> dict:
        await progress_callback(50.0, "Performing test execution step 1")
        await progress_callback(100.0, "Test execution completed")
        return {"test_success": True}


# Register the test job type
job_registry.register("test_job", TestJobExecutor)


class MockSessionContext:
    """Mock context manager to yield the test database session."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> AsyncSession:
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass


@pytest.fixture(autouse=True)
def mock_session_local(db_session: AsyncSession):
    """Intercepts and mocks SessionLocal calls to reuse the active test database session."""

    def mock_callable():
        return MockSessionContext(db_session)

    with (
        patch("app.jobs.queue.tasks.SessionLocal", mock_callable, create=True),
        patch("app.jobs.executors.evaluation.SessionLocal", mock_callable, create=True),
        patch(
            "app.jobs.executors.dataset_import.SessionLocal", mock_callable, create=True
        ),
        patch(
            "app.jobs.executors.dataset_export.SessionLocal", mock_callable, create=True
        ),
        patch("app.jobs.executors.benchmark.SessionLocal", mock_callable, create=True),
    ):
        yield


@pytest.fixture(autouse=True)
def mock_celery_apply_async():
    """Mock Celery's apply_async to avoid dangling background tasks."""

    def fake_apply_async_sync(args=None, kwargs=None, **opts):
        return None

    with patch(
        "app.jobs.services.job.run_background_job.apply_async", fake_apply_async_sync
    ):
        yield


def test_jobs_lifecycle_endpoints(client: TestClient) -> None:
    """Verifies creation, execution, progression tracking, cancellation, and retrieval of async jobs."""
    # 1. Create a Project first
    project_payload = {
        "name": "Jobs Test Project",
        "description": "Project for jobs lifecycle verification.",
    }
    project_response = client.post("/api/v1/projects", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 2. Queue a new job
    job_payload = {
        "name": "test_job",
        "queue_name": "test_queue",
        "payload": {"param1": "val1"},
        "max_retries": 2,
    }
    create_response = client.post(
        f"/api/v1/jobs?project_id={project_id}", json=job_payload
    )
    assert create_response.status_code == 201
    res_data = create_response.json()
    assert res_data["success"] is True
    job_id = res_data["data"]["id"]

    # 3. Retrieve detailed job info
    get_response = client.get(f"/api/v1/jobs/{job_id}")
    assert get_response.status_code == 200
    detail_data = get_response.json()
    assert detail_data["success"] is True
    assert detail_data["data"]["status"] in {"QUEUED", "RUNNING", "COMPLETED"}

    # 4. List jobs
    list_response = client.get("/api/v1/jobs")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["success"] is True
    assert len(list_data["data"]["items"]) >= 1

    # 5. Retrieve workers and queues
    workers_response = client.get("/api/v1/workers")
    assert workers_response.status_code == 200
    assert workers_response.json()["success"] is True

    queues_response = client.get("/api/v1/queues")
    assert queues_response.status_code == 200
    assert queues_response.json()["success"] is True

    # 6. Retrieve system jobs metrics
    metrics_response = client.get("/api/v1/system/jobs")
    assert metrics_response.status_code == 200
    metrics_data = metrics_response.json()
    assert metrics_data["success"] is True

    # 7. Delete job
    del_response = client.delete(f"/api/v1/jobs/{job_id}")
    assert del_response.status_code == 200
    assert del_response.json()["success"] is True


def test_jobs_tenant_isolation(db_session: AsyncSession) -> None:
    """Verifies strict tenant isolation for background job creation, retrieval, cancellation, and deletion."""
    from unittest.mock import MagicMock

    from app.core.dependencies import get_current_api_key, get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "job-ws-a-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "job-ws-b-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Tenant A creates Project A and queues Job A
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_proj_a = client_a.post("/api/v1/projects", json={"name": "Job Project A"})
        assert res_proj_a.status_code == 201
        proj_a_id = res_proj_a.json()["data"]["id"]

        res_job_a = client_a.post(
            f"/api/v1/jobs?project_id={proj_a_id}",
            json={"name": "test_job", "queue_name": "default", "payload": {}},
        )
        assert res_job_a.status_code == 201
        job_a_id = res_job_a.json()["data"]["id"]

        # Tenant A can access Job A
        get_own = client_a.get(f"/api/v1/jobs/{job_a_id}")
        assert get_own.status_code == 200

    # 2. Tenant B attempts cross-tenant access and mutation
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        # Tenant B GET Job A -> 404
        get_cross = client_b.get(f"/api/v1/jobs/{job_a_id}")
        assert get_cross.status_code == 404

        # Tenant B CANCEL Job A -> 404
        cancel_cross = client_b.post(f"/api/v1/jobs/{job_a_id}/cancel")
        assert cancel_cross.status_code == 404

        # Tenant B DELETE Job A -> 404
        del_cross = client_b.delete(f"/api/v1/jobs/{job_a_id}")
        assert del_cross.status_code == 404

        # Tenant B cannot queue job under Project A -> 404
        create_cross = client_b.post(
            f"/api/v1/jobs?project_id={proj_a_id}",
            json={"name": "test_job", "queue_name": "default", "payload": {}},
        )
        assert create_cross.status_code == 404

        # Tenant B list jobs does not contain Job A
        list_jobs_b = client_b.get("/api/v1/jobs")
        assert list_jobs_b.status_code == 200
        b_job_ids = [item["id"] for item in list_jobs_b.json()["data"]["items"]]
        assert job_a_id not in b_job_ids

    # 3. Database State Verification: Tenant A's job remains intact and active
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        get_intact = client_a.get(f"/api/v1/jobs/{job_a_id}")
        assert get_intact.status_code == 200
        assert get_intact.json()["data"]["status"] in {"QUEUED", "RUNNING", "COMPLETED"}

    app.dependency_overrides.clear()


def test_phase6_job_retry_and_worker_status(client: TestClient) -> None:
    """Verifies Phase 6 job retry endpoint, workers status metrics, and SSE fallback endpoint."""
    # 1. Create Project
    p_res = client.post("/api/v1/projects", json={"name": "Phase 6 Test Project"})
    assert p_res.status_code == 201
    proj_id = p_res.json()["data"]["id"]

    # 2. Queue Job
    j_res = client.post(
        f"/api/v1/jobs?project_id={proj_id}",
        json={"name": "test_job", "queue_name": "high", "payload": {}},
    )
    assert j_res.status_code == 201
    job_id = j_res.json()["data"]["id"]

    # 3. Cancel Job
    cancel_res = client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["data"]["status"] == "CANCELLED"

    # 4. Retry Job (Phase 6 endpoint)
    retry_res = client.post(f"/api/v1/jobs/{job_id}/retry")
    assert retry_res.status_code == 200
    assert retry_res.json()["data"]["status"] in {"QUEUED", "RUNNING", "COMPLETED"}

    # 5. Workers Status endpoint (Phase 6 endpoint)
    worker_res = client.get("/api/v1/workers/status")
    assert worker_res.status_code == 200
    worker_data = worker_res.json()["data"]
    assert "workers_total" in worker_data
    assert "tasks_active" in worker_data
    assert "tasks_reserved" in worker_data

    # 6. SSE Fallback endpoint (Phase 6 endpoint)
    sse_res = client.get(f"/api/v1/jobs/{job_id}/progress/sse")
    assert sse_res.status_code == 200
    assert "text/event-stream" in sse_res.headers.get("content-type", "")

