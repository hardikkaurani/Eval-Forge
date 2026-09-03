import uuid
from unittest.mock import MagicMock

import pytest
from evalforge_cli.main import main as cli_main
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_api_key, get_db, get_optional_api_key
from app.evaluation.repositories.evaluation import EvaluationRepository
from app.main import app
from app.platform.services.webhook_outbox import (
    generate_webhook_signature,
    validate_webhook_destination,
    verify_webhook_signature,
)


def test_public_spec_and_route_catalog(client: TestClient):
    """Verify OpenAPI 3.1 specification and route catalog discovery."""
    # 1. Spec endpoint
    spec_res = client.get("/api/v1/platform/spec")
    assert spec_res.status_code == 200
    spec = spec_res.json()
    assert "openapi" in spec
    assert "paths" in spec

    # 2. Routes catalog endpoint
    routes_res = client.get("/api/v1/platform/routes")
    assert routes_res.status_code == 200
    routes_data = routes_res.json()
    assert routes_data["success"] is True
    paths = [r["path"] for r in routes_data["data"]]
    assert "/api/v1/projects" in paths
    assert "/api/v1/evaluations" in paths


def test_generate_and_list_api_keys(client: TestClient):
    """Verify developer key generation and profile retrieval."""
    user_id = str(uuid.uuid4())
    payload = {"user_id": user_id, "scope": "read:all", "quota_limit": 1000}

    response = client.post("/api/v1/platform/keys", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "Copy your API Key:" in data["message"]
    assert data["data"]["scope"] == "read:all"
    assert data["data"]["quota_limit"] == 1000

    list_response = client.get(f"/api/v1/platform/keys?user_id={user_id}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["success"] is True
    assert len(list_data["data"]) == 1


def test_webhook_subscriptions_and_outbox(client: TestClient, db_session):
    """Verify Webhook subscription creation, HMAC-SHA256 signing, and outbox event recording."""
    # 1. Create project
    project_payload = {
        "name": "Platform Test Project",
        "description": "Integration testing for developer platform",
    }
    project_response = client.post("/api/v1/projects", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 2. Create a webhook subscription
    target_url = "https://example.com/receiver"
    payload = {
        "project_id": project_id,
        "target_url": target_url,
        "events": ["evaluation.completed", "job.failed"],
        "is_active": True,
    }

    response = client.post("/api/v1/webhooks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["target_url"] == target_url
    assert data["data"]["is_active"] is True
    sub_id = data["data"]["id"]
    secret = data["data"]["secret_token"]

    # 3. Test HMAC-SHA256 signature generation and verification
    sample_payload = '{"event": "evaluation.completed", "status": "PASSED"}'
    sig = generate_webhook_signature(sample_payload, secret)
    assert "t=" in sig and "v1=" in sig
    assert verify_webhook_signature(sample_payload, secret, sig) is True

    # 4. Replay attack rejection (timestamp expired)
    expired_sig = generate_webhook_signature(sample_payload, secret, timestamp=100000)
    assert verify_webhook_signature(sample_payload, secret, expired_sig) is False

    # 5. List deliveries
    del_response = client.get(f"/api/v1/webhooks/{sub_id}/deliveries")
    assert del_response.status_code == 200
    assert isinstance(del_response.json()["data"], list)


def test_db_plugin_registry_and_capability_execution(client: TestClient):
    """Verify DB-backed plugin registration, capability validation, and real scoring execution."""
    identifier = "com.evalforge.custom-metric"
    payload = {
        "name": "Custom Token Overlap Scorer",
        "identifier": identifier,
        "version": "1.0.0",
        "plugin_type": "metric",
        "capabilities": ["metric:compute"],
        "configuration_schema": {"scale": "integer"},
        "settings": {"weight": 1.0},
    }
    # 1. Register plugin
    response = client.post("/api/v1/plugins", json=payload)
    assert response.status_code == 201
    assert response.json()["success"] is True

    # 2. Duplicate registration rejected
    dup_res = client.post("/api/v1/plugins", json=payload)
    assert dup_res.status_code == 400

    # 3. Invalid capability rejected
    bad_payload = dict(payload, identifier="com.evalforge.bad", capabilities=["unrestricted:exec"])
    bad_res = client.post("/api/v1/plugins", json=bad_payload)
    assert bad_res.status_code == 400

    # 4. List active plugins
    list_response = client.get("/api/v1/plugins")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) > 0

    # 5. Execute real metric scoring
    exec_response = client.post(
        f"/api/v1/plugins/{identifier}/execute",
        json={"output": "The quick brown fox", "reference": "The quick brown fox jumps"},
    )
    assert exec_response.status_code == 200
    exec_data = exec_response.json()
    assert exec_data["success"] is True
    assert exec_data["data"]["score"] > 0.5
    assert "F1 overlap" in exec_data["data"]["reasoning"]


def test_mcp_tool_listing_and_execution(client: TestClient):
    """Verify MCP tools discovery and execution with workspace scoping."""
    # 1. Get available MCP tools
    response = client.get("/api/v1/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    tool_names = [t["name"] for t in data["data"]]
    assert "list_projects" in tool_names
    assert "list_datasets" in tool_names
    assert "get_evaluation_status" in tool_names
    assert "get_evaluation_results" in tool_names

    # 2. Call list_projects tool
    call_payload = {
        "name": "list_projects",
        "arguments": {"page": 1, "page_size": 10},
    }
    call_response = client.post("/api/v1/mcp/tools/call", json=call_payload)
    assert call_response.status_code == 200
    call_data = call_response.json()
    assert call_data["is_error"] is False
    assert "projects" in call_data["content"][0]["data"]


def test_playground_ssrf_and_execution(client: TestClient):
    """Verify API playground executes allowlisted routes and blocks SSRF / external URLs."""
    # 1. Legitimate relative route execution
    req_payload = {
        "endpoint": "/api/v1/platform/routes",
        "method": "GET",
    }
    res = client.post("/api/v1/playground/execute", json=req_payload)
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert res.json()["data"]["status_code"] == 200

    # 2. SSRF external host blocked
    ssrf_payload = {
        "endpoint": "http://169.254.169.254/latest/meta-data",
        "method": "GET",
    }
    ssrf_res = client.post("/api/v1/playground/execute", json=ssrf_payload)
    assert ssrf_res.status_code == 400
    err_body = ssrf_res.json()
    err_text = str(
        err_body.get("detail")
        or err_body.get("message")
        or err_body.get("error")
        or err_body
    )
    assert "Arbitrary external URLs" in err_text

    # 3. Code snippet generation
    gen_payload = {
        "endpoint": "/projects",
        "method": "POST",
        "payload_sample": {"name": "Test Playground"},
    }
    gen_res = client.post("/api/v1/playground/generate-code", json=gen_payload)
    assert gen_res.status_code == 200
    gen_data = gen_res.json()["data"]
    assert "python" in gen_data
    assert "typescript" in gen_data
    assert "go" in gen_data
    assert "java" in gen_data


def test_cli_parser_actions(capsys):
    """Verify evalforge CLI command dispatching."""
    # Test help flag execution
    with pytest.raises(SystemExit) as exc:
        cli_main(["--help"])
    assert exc.value.code == 0

    # Test auth status
    cli_main(["auth", "status"])
    captured = capsys.readouterr()
    assert "Authenticated" in captured.out or "Not authenticated" in captured.out


def test_webhooks_tenant_isolation(db_session) -> None:
    """Verifies that webhook subscription creation, listing, and delivery logs enforce strict workspace isolation."""
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

    try:
        # 1. Tenant A creates Project A and Webhook A
        app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
        app.dependency_overrides[get_optional_api_key] = lambda: key_tenant_a
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
                    "events": ["evaluation.completed"],
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
        app.dependency_overrides[get_optional_api_key] = lambda: key_tenant_b
        with TestClient(app) as client_b:
            assert client_b.get(f"/api/v1/webhooks?project_id={proj_a_id}").status_code == 404
            assert client_b.get(f"/api/v1/webhooks/{sub_a_id}/deliveries").status_code == 404
            create_cross = client_b.post(
                "/api/v1/webhooks",
                json={
                    "project_id": proj_a_id,
                    "target_url": "https://attacker.com/webhook",
                    "events": ["evaluation.completed"],
                },
            )
            assert create_cross.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_mcp_adversarial_tenant_isolation(db_session) -> None:
    """Verifies that MCP tools strictly enforce workspace isolation and reject cross-tenant IDOR access."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "mcp-ws-a-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "mcp-ws-b-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    try:
        # 1. Tenant A creates Project A and an Evaluation Run
        app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
        app.dependency_overrides[get_optional_api_key] = lambda: key_tenant_a
        with TestClient(app) as client_a:
            res_proj_a = client_a.post("/api/v1/projects", json={"name": "MCP Project A"})
            assert res_proj_a.status_code == 201
            proj_a_id = res_proj_a.json()["data"]["id"]

            res_eval_a = client_a.post(
                "/api/v1/evaluations",
                json={
                    "project_id": proj_a_id,
                    "name": "Evaluation Config A",
                    "description": "Config for tests",
                },
            )
            assert res_eval_a.status_code == 201
            eval_a_id = res_eval_a.json()["data"]["id"]

        run_a = await EvaluationRepository.create_run(
            db_session,
            evaluation_id=eval_a_id,
            judge="geval",
            provider="openai",
            provider_model="gpt-4o",
            configuration={},
            total_cases=1,
        )
        await db_session.commit()
        run_a_id = str(run_a.id)

        with TestClient(app) as client_a:
            # Tenant A positive MCP tool checks
            mcp_res = client_a.post(
                "/api/v1/mcp/tools/call",
                json={"name": "get_evaluation_status", "arguments": {"run_id": run_a_id}},
            )
            assert mcp_res.status_code == 200
            assert mcp_res.json()["is_error"] is False

        # 2. Tenant B attempts cross-tenant MCP calls targeting Tenant A's project and run
        app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
        app.dependency_overrides[get_optional_api_key] = lambda: key_tenant_b
        with TestClient(app) as client_b:
            # List datasets for Project A -> is_error: True (Not found)
            call_data = client_b.post(
                "/api/v1/mcp/tools/call",
                json={"name": "list_datasets", "arguments": {"project_id": proj_a_id}},
            ).json()
            assert call_data["is_error"] is True
            assert "not found" in call_data["content"][0]["text"].lower()

            # Get status for Run A -> is_error: True (Not found)
            call_status = client_b.post(
                "/api/v1/mcp/tools/call",
                json={"name": "get_evaluation_status", "arguments": {"run_id": run_a_id}},
            ).json()
            assert call_status["is_error"] is True
            assert "not found" in call_status["content"][0]["text"].lower()

            # Get results for Run A -> is_error: True (Not found)
            call_results = client_b.post(
                "/api/v1/mcp/tools/call",
                json={"name": "get_evaluation_results", "arguments": {"run_id": run_a_id}},
            ).json()
            assert call_results["is_error"] is True
            assert "not found" in call_results["content"][0]["text"].lower()
    finally:
        app.dependency_overrides.clear()


def test_webhook_dispatcher_ssrf_blocking():
    """Verify that validate_webhook_destination blocks private CIDRs, loopbacks, and cloud metadata."""
    # Blocked URLs
    assert validate_webhook_destination("http://127.0.0.1:8000")[0] is False
    assert validate_webhook_destination("http://localhost:5000")[0] is False
    assert validate_webhook_destination("http://169.254.169.254/latest/meta-data")[0] is False
    assert validate_webhook_destination("http://10.0.0.1/webhook")[0] is False
    assert validate_webhook_destination("http://192.168.1.1/hook")[0] is False
    assert validate_webhook_destination("http://172.16.0.1/hook")[0] is False
    assert validate_webhook_destination("https://user:pass@example.com/hook")[0] is False
    assert validate_webhook_destination("ftp://example.com/hook")[0] is False
    assert validate_webhook_destination("http://[::1]:8080/hook")[0] is False

    # Permitted Public URLs
    is_safe, _ = validate_webhook_destination("https://httpbin.org/post", allow_http=True)
    assert is_safe is True


def test_plugin_workspace_scoping(db_session) -> None:
    """Verifies that custom plugin descriptors are scoped to tenant workspace."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "plugin-ws-a-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "plugin-ws-b-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    try:
        # Tenant A registers a custom plugin
        app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
        app.dependency_overrides[get_optional_api_key] = lambda: key_tenant_a
        with TestClient(app) as client_a:
            identifier_a = "com.tenant-a.custom-metric"
            reg_res = client_a.post(
                "/api/v1/plugins",
                json={
                    "name": "Tenant A Metric",
                    "identifier": identifier_a,
                    "version": "1.0.0",
                    "plugin_type": "metric",
                    "capabilities": ["metric:compute"],
                },
            )
            assert reg_res.status_code == 201

            # Tenant A can execute its own plugin
            exec_res = client_a.post(
                f"/api/v1/plugins/{identifier_a}/execute",
                json={"output": "Test Output", "reference": "Test Output"},
            )
            assert exec_res.status_code == 200

        # Tenant B attempts to execute Tenant A's plugin -> 400 Bad Request (Not found in scope)
        app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
        app.dependency_overrides[get_optional_api_key] = lambda: key_tenant_b
        with TestClient(app) as client_b:
            exec_cross = client_b.post(
                f"/api/v1/plugins/{identifier_a}/execute",
                json={"output": "Test Output", "reference": "Test Output"},
            )
            assert exec_cross.status_code == 400
    finally:
        app.dependency_overrides.clear()

