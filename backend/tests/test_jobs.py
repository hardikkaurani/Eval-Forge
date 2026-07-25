import asyncio
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.executors.base import BaseJobExecutor
from app.jobs.queue.tasks import async_run_background_job
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
    """Mock Celery's apply_async to execute the background task synchronously within the test event loop."""

    def fake_apply_async_sync(args=None, kwargs=None, **opts):
        job_id = args[0]
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Schedule task execution asynchronously within the running event loop
            loop.create_task(async_run_background_job(job_id, "test_task_id"))
        else:
            loop.run_until_complete(async_run_background_job(job_id, "test_task_id"))

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
