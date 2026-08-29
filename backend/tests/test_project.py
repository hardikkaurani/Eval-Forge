import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


def test_project_crud_flow(client: TestClient) -> None:
    """Verifies the complete CRUD flow of the Project resource."""
    # 1. Create a Project
    payload = {
        "name": "E2E Test Project",
        "description": "Validating production Project API CRUD flow.",
        "status": "active",
    }
    create_response = client.post("/api/v1/projects", json=payload)
    assert create_response.status_code == 201
    create_res = create_response.json()
    assert create_res["success"] is True
    assert create_res["message"] == "Project created successfully."

    project = create_res["data"]
    project_id = project["id"]
    assert project["name"] == payload["name"]
    assert project["description"] == payload["description"]
    assert project["status"] == "active"
    assert project["deleted_at"] is None
    assert "created_at" in project
    assert "updated_at" in project

    # 2. Get Project by ID
    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 200
    get_res = get_response.json()
    assert get_res["success"] is True
    assert get_res["data"]["id"] == project_id

    # 3. List Projects (Verify presence and pagination metadata)
    list_response = client.get("/api/v1/projects?page=1&page_size=5")
    assert list_response.status_code == 200
    list_res = list_response.json()
    assert list_res["success"] is True
    assert len(list_res["data"]["items"]) >= 1
    assert list_res["data"]["meta"]["page"] == 1
    assert list_res["data"]["meta"]["page_size"] == 5
    assert list_res["data"]["meta"]["total_items"] >= 1

    # 4. Search and Filter Projects
    search_response = client.get("/api/v1/projects?search=E2E&status=active")
    assert search_response.status_code == 200
    search_res = search_response.json()
    assert len(search_res["data"]["items"]) >= 1
    assert search_res["data"]["items"][0]["id"] == project_id

    # 5. Update Project (Sparse Update)
    update_payload = {"name": "Updated E2E Test Name", "status": "inactive"}
    update_response = client.patch(
        f"/api/v1/projects/{project_id}", json=update_payload
    )
    assert update_response.status_code == 200
    update_res = update_response.json()
    assert update_res["success"] is True
    assert update_res["data"]["name"] == "Updated E2E Test Name"
    assert update_res["data"]["status"] == "inactive"

    # 6. Soft Delete Project
    delete_response = client.delete(f"/api/v1/projects/{project_id}")
    assert delete_response.status_code == 200
    delete_res = delete_response.json()
    assert delete_res["success"] is True
    assert delete_res["data"]["deleted_at"] is not None

    # 7. Verify Soft Deleted Project is filtered out from active routes
    get_deleted_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_deleted_response.status_code == 404
    get_deleted_res = get_deleted_response.json()
    assert get_deleted_res["success"] is False
    assert get_deleted_res["data"]["code"] == "NotFoundException"


def test_project_validation_errors(client: TestClient) -> None:
    """Verifies that invalid requests raise appropriate validation exceptions."""
    # 1. Invalid status value on creation
    invalid_payload = {
        "name": "Invalid Project",
        "status": "some-nonexistent-status",
    }
    response = client.post("/api/v1/projects", json=invalid_payload)
    assert response.status_code == 400
    res_data = response.json()
    assert res_data["success"] is False
    assert res_data["data"]["code"] == "RequestValidationError"

    # 2. Retrieve project with invalid UUID format
    response = client.get("/api/v1/projects/invalid-uuid-format")
    assert response.status_code == 400
    res_data = response.json()
    assert res_data["success"] is False
    assert res_data["data"]["code"] == "ValidationException"


def test_tenant_workspace_isolation(db_session: AsyncSession) -> None:
    """Verifies that project access, listing, updating, and soft deletion are strictly scoped to the authenticated workspace context."""
    from unittest.mock import MagicMock

    from app.core.dependencies import get_current_api_key, get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Define workspace identities
    ws_a_id = "11111111-1111-4111-a111-111111111111"
    ws_b_id = "22222222-2222-4222-b222-222222222222"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Create Tenant A Project
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        payload_a = {"name": "Tenant A Confidential Project", "status": "active"}
        res_a = client_a.post("/api/v1/projects", json=payload_a)
        assert res_a.status_code == 201
        proj_a = res_a.json()["data"]
        proj_a_id = proj_a["id"]
        assert proj_a["workspace_id"] == ws_a_id

        # Tenant A can access Tenant A's project
        get_a = client_a.get(f"/api/v1/projects/{proj_a_id}")
        assert get_a.status_code == 200

    # 2. Create Tenant B Project
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        payload_b = {"name": "Tenant B Proprietary Project", "status": "active"}
        res_b = client_b.post("/api/v1/projects", json=payload_b)
        assert res_b.status_code == 201
        proj_b = res_b.json()["data"]
        proj_b_id = proj_b["id"]
        assert proj_b["workspace_id"] == ws_b_id

        # Tenant B can access Tenant B's project
        get_b = client_b.get(f"/api/v1/projects/{proj_b_id}")
        assert get_b.status_code == 200

        # Tenant B CANNOT access Tenant A's project (GET DENIED -> 404)
        get_cross = client_b.get(f"/api/v1/projects/{proj_a_id}")
        assert get_cross.status_code == 404
        assert get_cross.json()["success"] is False

        # Tenant B CANNOT update Tenant A's project (UPDATE DENIED -> 404)
        patch_cross = client_b.patch(
            f"/api/v1/projects/{proj_a_id}",
            json={"name": "Hacked Tenant A Name"},
        )
        assert patch_cross.status_code == 404

        # Tenant B CANNOT delete Tenant A's project (DELETE DENIED -> 404)
        del_cross = client_b.delete(f"/api/v1/projects/{proj_a_id}")
        assert del_cross.status_code == 404

        # Tenant B LIST projects returns ONLY Tenant B resources
        list_b = client_b.get("/api/v1/projects")
        assert list_b.status_code == 200
        items_b = list_b.json()["data"]["items"]
        b_ids = [item["id"] for item in items_b]
        assert proj_b_id in b_ids
        assert proj_a_id not in b_ids

        # Attempting client payload workspace_id manipulation cannot override server boundary
        spoof_payload = {
            "name": "Spoofed Workspace Project",
            "status": "active",
            "workspace_id": ws_a_id,  # Attempting to assign Tenant A workspace_id
        }
        res_spoof = client_b.post("/api/v1/projects", json=spoof_payload)
        assert res_spoof.status_code == 201
        # Created project must be bound to Tenant B's server-derived workspace_id
        assert res_spoof.json()["data"]["workspace_id"] == ws_b_id

    app.dependency_overrides.clear()


def test_adversarial_tenant_isolation_scenarios(db_session: AsyncSession) -> None:
    """Adversarial regression test verifying null workspace isolation, ownership mutation prevention, and direct repository/service boundary enforcement."""
    import asyncio
    from unittest.mock import MagicMock

    from app.core.dependencies import get_current_api_key, get_db
    from app.core.exceptions import NotFoundException
    from app.database.repository import ProjectRepository
    from app.main import app
    from app.services.project import ProjectService

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "33333333-3333-4333-a333-333333333333"
    ws_b_id = "44444444-4444-4444-b444-444444444444"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_unscoped = MagicMock()
    key_unscoped.id = "key_unscoped"
    key_unscoped.workspace_id = None

    # 1. Create a project under Tenant A
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_a = client_a.post(
            "/api/v1/projects",
            json={"name": "Tenant A Secret Base", "status": "active"},
        )
        assert res_a.status_code == 201
        proj_a_id = res_a.json()["data"]["id"]

        # Attempt to mutate ownership via UPDATE payload
        res_patch_tamper = client_a.patch(
            f"/api/v1/projects/{proj_a_id}",
            json={"name": "Renamed", "workspace_id": ws_b_id},
        )
        assert res_patch_tamper.status_code == 200
        # Workspace ID remains ws_a_id despite update payload tampering
        assert res_patch_tamper.json()["data"]["workspace_id"] == ws_a_id

    # 2. Verify Unscoped API key (workspace_id = None) CANNOT access Tenant A project
    app.dependency_overrides[get_current_api_key] = lambda: key_unscoped
    with TestClient(app) as client_unscoped:
        res_unscoped_get = client_unscoped.get(f"/api/v1/projects/{proj_a_id}")
        assert res_unscoped_get.status_code == 404

        res_unscoped_patch = client_unscoped.patch(
            f"/api/v1/projects/{proj_a_id}", json={"name": "Hacked"}
        )
        assert res_unscoped_patch.status_code == 404

        res_unscoped_delete = client_unscoped.delete(f"/api/v1/projects/{proj_a_id}")
        assert res_unscoped_delete.status_code == 404

    # 3. Verify Direct Repository / Service enforcement
    async def run_direct_checks():
        repo = ProjectRepository(db_session)
        service = ProjectService(db_session, workspace_id=ws_b_id)

        # Direct repo get with wrong workspace_id returns None
        repo_res = await repo.get_by_id(proj_a_id, workspace_id=ws_b_id)
        assert repo_res is None

        # Direct repo get with null workspace_id returns None for Tenant A project
        repo_null_res = await repo.get_by_id(proj_a_id, workspace_id=None)
        assert repo_null_res is None

        # Direct service get with wrong workspace_id raises NotFoundException
        with pytest.raises(NotFoundException):
            await service.get_project(proj_a_id)

    asyncio.run(run_direct_checks())

    app.dependency_overrides.clear()


def test_evaluation_flow_cross_tenant_isolation_red_team(
    db_session: AsyncSession,
) -> None:
    """Verifies that Tenant B cannot create evaluations, list evaluations, or run batch evaluations on Tenant A's project."""
    from unittest.mock import MagicMock

    from app.core.dependencies import get_current_api_key, get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "55555555-5555-4555-a555-555555555555"
    ws_b_id = "66666666-6666-4666-b666-666666666666"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Tenant A creates Project A
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_a = client_a.post(
            "/api/v1/projects",
            json={"name": "Tenant A Evaluation Target", "status": "active"},
        )
        assert res_a.status_code == 201
        proj_a_id = res_a.json()["data"]["id"]

    # 2. Tenant B attempts to manipulate Tenant A's Project via Evaluation Endpoints
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        # 2a. Tenant B POST /api/v1/evaluations for Tenant A's project -> DENIED (404)
        eval_payload = {
            "project_id": proj_a_id,
            "name": "Hostile Cross-Tenant Evaluation",
            "description": "Attacker attempting to attach evaluation to Victim Project",
        }
        res_create_eval = client_b.post("/api/v1/evaluations", json=eval_payload)
        assert res_create_eval.status_code == 404
        assert res_create_eval.json()["success"] is False

        # 2b. Tenant B GET /api/v1/evaluations?project_id=... for Tenant A's project -> DENIED (404)
        res_list_eval = client_b.get(f"/api/v1/evaluations?project_id={proj_a_id}")
        assert res_list_eval.status_code == 404
        assert res_list_eval.json()["success"] is False

        # 2c. Tenant B POST /api/v1/evaluations/batch for Tenant A's project -> DENIED (404)
        batch_payload = {
            "project_id": proj_a_id,
            "evaluation_name": "Hostile Batch Evaluation Run",
            "judge": "rubric",
            "provider": "openai",
            "test_cases": [
                {"input_prompt": "Prompt text", "model_output": "Output text"}
            ],
        }
        res_batch_eval = client_b.post("/api/v1/evaluations/batch", json=batch_payload)
        assert res_batch_eval.status_code == 404
        assert res_batch_eval.json()["success"] is False

    app.dependency_overrides.clear()
