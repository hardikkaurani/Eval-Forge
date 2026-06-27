from fastapi.testclient import TestClient


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
