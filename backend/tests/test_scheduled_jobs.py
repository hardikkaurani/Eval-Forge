import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.jobs.routes.scheduler_routes import router as scheduler_router
from app.jobs.scheduler.cron_manager import CronSchedulerManager


@pytest.mark.asyncio
async def test_cron_scheduler_manager_registration_and_execution():
    scheduler = CronSchedulerManager()

    executed = False

    async def mock_handler():
        nonlocal executed
        executed = True
        return "Handler executed"

    scheduler.register_job(
        job_id="test-job",
        name="Test Job",
        description="A test cron job",
        schedule_cron="* * * * *",
        interval_seconds=60,
        handler=mock_handler,
    )

    jobs = scheduler.list_jobs()
    assert len(jobs) == 1
    assert jobs[0]["job_id"] == "test-job"
    assert jobs[0]["is_enabled"] is True

    # Execute job
    log = await scheduler.execute_job("test-job")
    assert executed is True
    assert log["status"] == "SUCCESS"
    assert "Handler executed" in log["details"]

    # Toggle job
    toggled = scheduler.toggle_job("test-job")
    assert toggled.is_enabled is False


def test_scheduler_api_routes():
    app = FastAPI()
    app.include_router(scheduler_router)

    client = TestClient(app)

    # Test list jobs endpoint
    res = client.get("/jobs/scheduler/jobs")
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert isinstance(res.json()["data"], list)

    # Test history endpoint
    res_history = client.get("/jobs/scheduler/history")
    assert res_history.status_code == 200
    assert res_history.json()["success"] is True
    assert isinstance(res_history.json()["data"], list)
