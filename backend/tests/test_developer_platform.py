import uuid
import pytest

from app.platform.cli.cli_app import EvalForgeCLI


def test_generate_and_list_api_keys(client):
    # 1. Create a key profile
    user_id = str(uuid.uuid4())
    payload = {
        "user_id": user_id,
        "scope": "read:all",
        "quota_limit": 1000
    }
    
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
        "description": "Integration testing for developer platform"
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
        "is_active": True
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
        "settings": {"weight": 1.2}
    }
    response = client.post("/api/v1/plugins", json=payload)
    assert response.status_code == 201
    assert response.json()["success"] is True

    # 2. List discovered plugins
    list_response = client.get("/api/v1/plugins")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) > 0

    # 3. Execute plugin
    exec_response = client.post(f"/api/v1/plugins/{identifier}/execute", json={"prompt": "test"})
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
        "arguments": {"project_id": str(uuid.uuid4())}
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
        "payload_sample": {"user_id": str(uuid.uuid4())}
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
    cli.run(["dataset", "upload", "--project-id", str(uuid.uuid4()), "--file", "data.csv"])
    # Test evaluate trigger parse
    cli.run(["evaluate", "--project-id", str(uuid.uuid4()), "--judge", "geval", "--provider", "openai"])
