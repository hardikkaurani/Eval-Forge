from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_openapi_schema_generation_direct() -> None:
      """Tests that app.openapi() generates the OpenAPI schema dictionary cleanly without errors."""
      schema = app.openapi()
      assert isinstance(schema, dict)

    # Verify top-level required OpenAPI keys
      assert "openapi" in schema
      assert "info" in schema
      assert "paths" in schema
      assert "components" in schema

    # Verify API Info Metadata
      info = schema["info"]
      assert info["title"] == "EvalForge Core API"
      assert info["version"] == "1.0.0"

    # Verify key API endpoints are present in the schema paths
      paths = schema["paths"]
      assert "/api/v1/health" in paths
      assert "/api/v1/projects" in paths
      assert "/api/v1/evaluations" in paths

    # Ensure schema is cached on the FastAPI app instance
      assert app.openapi_schema == schema


def test_openapi_schema_endpoint_in_non_production(client: TestClient) -> None:
      """Tests the /openapi.json HTTP endpoint when openapi_url is configured."""
      if settings.APP_ENV != "production":
                response = client.get("/openapi.json")
                assert response.status_code == 200
                schema = response.json()
                assert schema["info"]["title"] == "EvalForge Core API"
else:
        # In production mode, openapi_url is disabled for security
          assert app.openapi_url is None
  
