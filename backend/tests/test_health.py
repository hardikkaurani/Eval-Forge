from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Tests the /health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "System health check completed."
    assert "data" in json_data
    assert json_data["data"]["status"] == "healthy"
    assert json_data["data"]["services"]["api"] == "healthy"
    assert json_data["data"]["services"]["database"] == "healthy"
    assert json_data["data"]["services"]["redis"] == "healthy"
    assert "request_id" in json_data
    assert "timestamp" in json_data


def test_readiness_check(client: TestClient) -> None:
    """Tests the /ready check endpoint when backend services are active."""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["ready"] is True
    assert json_data["data"]["services"]["database"] == "healthy"
    assert json_data["data"]["services"]["redis"] == "healthy"


def test_liveness_check(client: TestClient) -> None:
    """Tests the /live check endpoint."""
    response = client.get("/api/v1/live")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "alive"


def test_version_check(client: TestClient) -> None:
    """Tests the /version check endpoint."""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["version"] == "0.1.0"
    assert "environment" in json_data["data"]
