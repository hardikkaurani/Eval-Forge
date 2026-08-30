import uuid

import pytest
from fastapi.testclient import TestClient

from app.platform.cli.cli_app import EvalForgeCLI


def test_generate_and_list_api_keys(client):
    # 1. Create a key profile
    user_id = str(uuid.uuid4())
    payload = {"user_id": user_id, "scope": "read:all", "quota_limit": 1000}

    response = client.post("/api/v1/public/keys", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "Copy your API Key:" in data["message"]
    assert data["data"]["scope"] == "read:all"
    assert data["data"]["quota_limit"] == 1000

    # 2. List the keys
    list_response = client.get(f"/api/v1/public/keys?user_id={user_id}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["success"] is True
    assert len(list_data["data"]) == 1


def test_webhook_subscriptions_and_deliveries(client):
    # Create project first
    project_payload = {
        "name": "Platform Test Project",
        "description": "Integration testing for developer platform",
    }
    project_response = client.post("/api/v1/projects", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 1. Create a webhook subscription
    target_url = "https://mywebhook.com/receiver"
    payload = {
        "project_id": project_id,
        "target_url": target_url,
        "events": ["eval_completed", "job_failed"],
        "is_active": True,
    }

    response = client.post("/api/v1/webhooks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["target_url"] == target_url
    assert data["data"]["is_active"] is True

    sub_id = data["data"]["id"]

    # 2. List subscriptions
    list_response = client.get(f"/api/v1/webhooks?project_id={project_id}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data["data"]) == 1

    # 3. Retrieve deliveries list
    del_response = client.get(f"/api/v1/webhooks/{sub_id}/deliveries")
    assert del_response.status_code == 200
    del_data = del_response.json()
    assert isinstance(del_data["data"], list)


def test_plugin_registration_and_execution(client):
    # 1. Register plugin
    identifier = "com.evalforge.test-plugin"
    payload = {
        "name": "Test Custom Metric",
        "identifier": identifier,
        "version": "1.0.0",
        "plugin_type": "metric",
        "configuration_schema": {"scale": "integer"},
        "settings": {"weight": 1.2},
    }
    response = client.post("/api/v1/plugins", json=payload)
    assert response.status_code == 201
    assert response.json()["success"] is True

    # 2. List discovered plugins
    list_response = client.get("/api/v1/plugins")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) > 0

    # 3. Execute plugin
    exec_response = client.post(
        f"/api/v1/plugins/{identifier}/execute", json={"prompt": "test"}
    )
    assert exec_response.status_code == 200
    exec_data = exec_response.json()
    assert exec_data["success"] is True
    assert exec_data["data"]["plugin"] == identifier
    assert exec_data["data"]["metric_score"] == pytest.approx(0.85 * 1.2)


def test_mcp_tool_listing_and_execution(client):
    # 1. Get available MCP tools
    response = client.get("/api/v1/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["data"][0]["name"] == "get_project_summary"

    # 2. Call an MCP tool
    call_payload = {
        "name": "get_project_summary",
        "arguments": {"project_id": str(uuid.uuid4())},
    }
    call_response = client.post("/api/v1/mcp/tools/call", json=call_payload)
    assert call_response.status_code == 200
    call_data = call_response.json()
    assert call_data["is_error"] is False
    assert "Total Runs: 42" in call_data["content"][0]["text"]


def test_playground_sdk_generation(client):
    payload = {
        "endpoint": "/keys",
        "method": "POST",
        "payload_sample": {"user_id": str(uuid.uuid4())},
    }
    response = client.post("/api/v1/playground/generate-code", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "python" in data["data"]
    assert "typescript" in data["data"]
    assert "go" in data["data"]
    assert "java" in data["data"]


def test_cli_parser_actions():
    cli = EvalForgeCLI()
    # Test login CLI parse
    cli.run(["login", "--key", "ef_my_api_key_value"])
    # Test project create CLI parse
    cli.run(["project", "create", "--name", "EvalProj", "--desc", "Test description"])
    # Test dataset upload CLI parse
    cli.run(
        ["dataset", "upload", "--project-id", str(uuid.uuid4()), "--file", "data.csv"]
    )
    # Test evaluate trigger parse
    cli.run(
        [
            "evaluate",
            "--project-id",
            str(uuid.uuid4()),
            "--judge",
            "geval",
            "--provider",
            "openai",
        ]
    )


def test_webhooks_tenant_isolation(db_session) -> None:
    """Verifies that webhook subscription creation, listing, and delivery logs enforce strict workspace isolation."""
    from unittest.mock import MagicMock

    from app.core.dependencies import get_current_api_key, get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "wh-ws-a-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "wh-ws-b-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Tenant A creates Project A and Webhook A
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_proj_a = client_a.post(
            "/api/v1/projects", json={"name": "Webhook Project A"}
        )
        assert res_proj_a.status_code == 201
        proj_a_id = res_proj_a.json()["data"]["id"]

        res_sub_a = client_a.post(
            "/api/v1/webhooks",
            json={
                "project_id": proj_a_id,
                "target_url": "https://tenant-a.com/webhook",
                "events": ["eval_completed"],
            },
        )
        assert res_sub_a.status_code == 201
        sub_a_id = res_sub_a.json()["data"]["id"]

        # Tenant A can list webhooks for Project A
        list_own = client_a.get(f"/api/v1/webhooks?project_id={proj_a_id}")
        assert list_own.status_code == 200
        assert len(list_own.json()["data"]) == 1

    # 2. Tenant B attempts cross-tenant webhook access
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        # Tenant B list webhooks for Project A -> 404
        assert (
            client_b.get(f"/api/v1/webhooks?project_id={proj_a_id}").status_code == 404
        )

        # Tenant B list deliveries for Sub A -> 404
        assert (
            client_b.get(f"/api/v1/webhooks/{sub_a_id}/deliveries").status_code == 404
        )

        # Tenant B create webhook under Project A -> 404
        create_cross = client_b.post(
            "/api/v1/webhooks",
            json={
                "project_id": proj_a_id,
                "target_url": "https://attacker.com/webhook",
                "events": ["eval_completed"],
            },
        )
        assert create_cross.status_code == 404

    app.dependency_overrides.clear()
