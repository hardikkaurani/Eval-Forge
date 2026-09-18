"""Regression checks using real API key validation, not the shared auth override."""

import asyncio
import hashlib
import uuid
from datetime import datetime

from app.core.dependencies import get_current_api_key
from app.enterprise.models import EnterpriseAPIKey
from app.jobs.models.job import Job
from app.models.project import Project


def seed(db, workspace_id=None, count=0, scopes=None):
    raw_key = f"release-test-{uuid.uuid4()}"
    project_id = str(uuid.uuid4())

    async def insert():
        key = EnterpriseAPIKey(
            id=uuid.uuid4(),
            name="Release test",
            key_hash=hashlib.sha256(raw_key.encode()).hexdigest(),
            workspace_id=workspace_id,
            scopes=scopes or ["read:all"],
            is_active=True,
        )
        project = Project(
            id=project_id,
            workspace_id=str(workspace_id) if workspace_id else None,
            name="Release project",
            status="active",
        )
        db.add_all([key, project])
        for index in range(count):
            db.add(
                Job(
                    id=str(uuid.uuid4()),
                    name=f"Job {index:04}",
                    queue_name="default",
                    status="COMPLETED",
                    progress=100,
                    max_retries=3,
                    retry_count=0,
                    timezone="UTC",
                    payload={"project_id": project_id},
                    created_at=datetime.utcnow(),
                )
            )
        await db.commit()

    asyncio.run(insert())
    return raw_key, project_id


def authenticate(client, raw_key):
    client.app.dependency_overrides.pop(get_current_api_key, None)
    client.headers["X-API-Key"] = raw_key


def test_connection_validates_real_key_and_omits_secret(client, db_session):
    key, _ = seed(db_session)
    authenticate(client, key)
    response = client.get("/api/v1/connection")
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Release test"
    assert key not in response.text
    assert "key_hash" not in response.text
    client.headers["X-API-Key"] = "invalid-release-key"
    assert client.get("/api/v1/connection").status_code == 401


def test_unscoped_key_cannot_read_scoped_jobs(client, db_session):
    scoped, project = seed(db_session, uuid.uuid4(), count=1)
    unscoped, _ = seed(db_session)
    authenticate(client, scoped)
    response = client.get(f"/api/v1/jobs?project_id={project}")
    assert response.status_code == 200
    job_id = response.json()["data"]["items"][0]["id"]
    client.headers["X-API-Key"] = unscoped
    assert client.get(f"/api/v1/jobs/{job_id}").status_code == 404
    assert client.get(f"/api/v1/jobs?project_id={project}").status_code == 404
    assert client.get("/api/v1/jobs").json()["data"]["items"] == []


def test_job_pagination_counts_all_authorized_records(client, db_session):
    key, project = seed(db_session, count=1005)
    authenticate(client, key)
    response = client.get(f"/api/v1/jobs?project_id={project}&page=51&page_size=20")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["meta"]["total_items"] == 1005
    assert len(data["items"]) == 5


def test_empty_project_counts_are_zero(client, db_session):
    key, project = seed(db_session)
    authenticate(client, key)
    for route, field in [("datasets", "datasets"), ("experiments", "experiments")]:
        response = client.get(f"/api/v1/{route}/?project_id={project}")
        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()[field] == []


def test_read_only_key_cannot_mutate(client, db_session):
    key, _ = seed(db_session)
    authenticate(client, key)
    response = client.post("/api/v1/projects", json={"name": "Forbidden write"})
    assert response.status_code == 403


def test_generated_keys_inherit_workspace_and_cannot_escape(client, db_session):
    workspace = uuid.uuid4()
    key, _ = seed(db_session, workspace, scopes=["read:all", "write:all"])
    authenticate(client, key)
    response = client.post(
        "/api/v1/api-keys", json={"name": "Child", "scopes": ["read:all"]}
    )
    assert response.status_code == 201
    assert response.json()["data"]["details"]["workspace_id"] == str(workspace)
    assert (
        client.post(
            "/api/v1/api-keys",
            json={"name": "Escape", "workspace_id": str(uuid.uuid4())},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/api-keys", json={"name": "Escalate", "scopes": ["*"]}
        ).status_code
        == 403
    )
    unscoped, _ = seed(db_session, scopes=["read:all", "write:all"])
    authenticate(client, unscoped)
    assert (
        client.post(
            "/api/v1/api-keys", json={"name": "Escape", "workspace_id": str(workspace)}
        ).status_code
        == 404
    )
    child_id = response.json()["data"]["details"]["id"]
    assert client.delete(f"/api/v1/api-keys/{child_id}").status_code == 404


def test_request_cannot_override_provider_network_destination():
    import pytest

    from app.evaluation.exceptions.exceptions import InvalidConfigException
    from app.evaluation.pipelines.pipeline import EvaluationPipeline
    from app.evaluation.schemas.evaluation import BatchEvaluationRequest

    request = BatchEvaluationRequest(
        evaluation_name="URL validation",
        project_id=str(uuid.uuid4()),
        provider="ollama",
        judge="rubric",
        test_cases=[],
        configuration={"base_url": "http://169.254.169.254"},
    )
    with pytest.raises(InvalidConfigException):
        EvaluationPipeline._build_provider(request)


def test_idempotency_cache_isolated_and_rechecks_auth(client, db_session, monkeypatch):
    from unittest.mock import AsyncMock

    from app.core.redis import redis_manager

    cache = {}

    async def get(key):
        return cache.get(key)

    async def setex(key, ttl, value):
        cache[key] = value

    redis = AsyncMock()
    redis.get.side_effect = get
    redis.setex.side_effect = setex
    monkeypatch.setattr(redis_manager, "client", redis)
    key_a, _ = seed(db_session, scopes=["read:all", "write:all"])
    key_b, _ = seed(db_session, scopes=["read:all", "write:all"])
    authenticate(client, key_a)
    headers = {"X-Idempotency-Key": "same-client-value"}
    a = client.post(
        "/api/v1/projects", json={"name": "Cached project"}, headers=headers
    )
    assert a.status_code == 201
    repeated = client.post(
        "/api/v1/projects", json={"name": "Cached project"}, headers=headers
    )
    assert a.json()["data"]["id"] == repeated.json()["data"]["id"]
    authenticate(client, key_b)
    b = client.post(
        "/api/v1/projects", json={"name": "Cached project"}, headers=headers
    )
    assert b.status_code == 201
    assert a.json()["data"]["id"] != b.json()["data"]["id"]
    from sqlalchemy import update

    async def revoke():
        await db_session.execute(
            update(EnterpriseAPIKey)
            .where(
                EnterpriseAPIKey.key_hash == hashlib.sha256(key_a.encode()).hexdigest()
            )
            .values(is_active=False)
        )
        await db_session.commit()

    asyncio.run(revoke())
    authenticate(client, key_a)
    assert (
        client.post(
            "/api/v1/projects", json={"name": "Cached project"}, headers=headers
        ).status_code
        == 401
    )


def test_workspace_key_cannot_control_global_scheduler(client, db_session):
    key, _ = seed(db_session, scopes=["read:all", "write:all"])
    authenticate(client, key)
    assert (
        client.post(
            "/api/v1/jobs/scheduler/jobs/cron-leaderboard-recalc/toggle"
        ).status_code
        == 403
    )


def test_webhook_delivery_pins_public_ip_and_preserves_origin(monkeypatch):
    import socket

    from app.platform.services.webhook_outbox import pin_webhook_destination

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, *a, **kw: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))
        ],
    )
    target, sni, host = pin_webhook_destination("https://example.com:8443/events?q=1")
    assert target == "https://8.8.8.8:8443/events?q=1"
    assert sni == "example.com"
    assert host == "example.com:8443"


def test_webhook_rebinding_to_private_address_is_blocked(monkeypatch):
    import socket

    import pytest

    from app.platform.services.webhook_outbox import pin_webhook_destination

    calls = 0

    def resolve(host, *args, **kwargs):
        nonlocal calls
        calls += 1
        address = "8.8.8.8" if calls == 1 else "169.254.169.254"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))]

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    with pytest.raises(ValueError):
        pin_webhook_destination("https://attacker.example/events")


def test_bootstrap_provisions_an_authenticated_workspace_owner(
    client, db_session, capsys
):
    import importlib.util
    from pathlib import Path

    script = Path(__file__).resolve().parents[1] / "scripts" / "bootstrap_workspace.py"
    spec = importlib.util.spec_from_file_location("bootstrap_workspace", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    asyncio.run(module.provision("Bootstrap regression", 30))
    output = capsys.readouterr().out
    raw = output.split("days): ")[1].splitlines()[0]
    authenticate(client, raw)
    connection = client.get("/api/v1/connection")
    assert connection.status_code == 200
    scope = connection.json()["data"]
    assert scope["workspace_id"]
    members = client.get(f"/api/v1/organizations/{scope['organization_id']}/members")
    assert members.status_code == 200
    assert len(members.json()["data"]) == 1


def test_job_is_queued_before_worker_dispatch(db_session, monkeypatch):
    from app.jobs.schemas.job import JobCreate
    from app.jobs.services.job import JobService, run_background_job

    _, project = seed(db_session)
    observed = []

    def dispatch(*args, **kwargs):
        jobs = [obj for obj in db_session.identity_map.values() if isinstance(obj, Job)]
        observed.extend(job.status for job in jobs)
        assert observed == ["QUEUED"]

    monkeypatch.setattr(run_background_job, "apply_async", dispatch)
    result = asyncio.run(
        JobService(db_session).create_job(project, JobCreate(name="Dispatch ordering"))
    )
    assert result.status == "QUEUED"
    assert observed == ["QUEUED"]
