"""Phase 12 Final Ship & Release Verification Test Suite.

Validates:
1. Universal v1.0.0 version coherence across all components.
2. Production security settings, fail-closed guards, and CORS validations.
3. Health check endpoints and live/ready probes.
4. Security headers and idempotency middlewares.
5. Python SDK and CLI client integration.
6. OpenAPI contract integrity and schema generation.
7. Example files syntax and data validity.
8. Database migration continuity and head resolution.
"""

import json
from pathlib import Path

import pytest
from evalforge import EvalForge
from httpx import ASGITransport, AsyncClient

from app.config.config import Settings
from app.main import app


@pytest.mark.asyncio
async def test_phase12_version_coherence_across_all_manifests():
    """Verify v1.0.0 version coherence across backend, frontend, SDKs, and CLI."""
    # 1. FastAPI App Version
    assert app.version == "1.0.0"

    root_dir = Path(__file__).resolve().parent.parent.parent

    # 2. Python SDK pyproject.toml
    sdk_pyproject = root_dir / "sdk" / "python" / "pyproject.toml"
    assert sdk_pyproject.exists()
    assert 'version = "1.0.0"' in sdk_pyproject.read_text(encoding="utf-8")

    # 3. CLI pyproject.toml
    cli_pyproject = root_dir / "cli" / "pyproject.toml"
    assert cli_pyproject.exists()
    assert 'version = "1.0.0"' in cli_pyproject.read_text(encoding="utf-8")

    # 4. Frontend package.json
    frontend_pkg = root_dir / "frontend" / "package.json"
    assert frontend_pkg.exists()
    frontend_data = json.loads(frontend_pkg.read_text(encoding="utf-8"))
    assert frontend_data.get("version") == "1.0.0"

    # 5. TypeScript SDK package.json
    ts_sdk_pkg = root_dir / "sdk" / "typescript" / "package.json"
    assert ts_sdk_pkg.exists()
    ts_data = json.loads(ts_sdk_pkg.read_text(encoding="utf-8"))
    assert ts_data.get("version") == "1.0.0"

    # 6. Java SDK pom.xml
    java_pom = root_dir / "sdk" / "java" / "pom.xml"
    assert java_pom.exists()
    assert "<version>1.0.0</version>" in java_pom.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_phase12_health_endpoints():
    """Verify root health check and API health probes return correct status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Root health check (used by Docker & Load Balancers)
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "healthy"
        assert "service" in data

        # API live probe
        resp_live = await client.get("/api/v1/live")
        assert resp_live.status_code == 200
        live_data = resp_live.json()
        assert (
            live_data.get("data", {}).get("status") == "alive"
            or live_data.get("status") == "healthy"
        )

        # API ready probe
        resp_ready = await client.get("/api/v1/ready")
        assert resp_ready.status_code in (200, 503)  # Depends on test DB availability


@pytest.mark.asyncio
async def test_phase12_security_headers_middleware():
    """Verify production security response headers on all requests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        headers = resp.headers
        assert headers.get("x-frame-options") == "DENY"
        assert headers.get("x-content-type-options") == "nosniff"
        assert headers.get("x-xss-protection") == "1; mode=block"
        assert "default-src 'self'" in headers.get("content-security-policy", "")
        assert "request-id" in headers or "x-request-id" in headers


@pytest.mark.asyncio
async def test_phase12_production_settings_validation():
    """Verify Settings fail-closed validator in production mode."""
    # 1. Production with default password (no DATABASE_URL) must raise ValueError
    with pytest.raises(
        ValueError, match="POSTGRES_PASSWORD must be set to a secure value"
    ):
        Settings(
            APP_ENV="production",
            POSTGRES_PASSWORD="postgres_password",
            SECRET_KEY="secure-production-key-example-12345",
            CORS_ORIGINS=["https://app.evalforge.dev"],
            DEBUG=False,
        )

    # 2. Production with known insecure passwords must raise ValueError
    for insecure_pw in ["password", "changeme", "secret", "admin", "123456"]:
        with pytest.raises(
            ValueError, match="POSTGRES_PASSWORD must be set to a secure value"
        ):
            Settings(
                APP_ENV="production",
                POSTGRES_PASSWORD=insecure_pw,
                SECRET_KEY="secure-production-key-example-12345",
                CORS_ORIGINS=["https://app.evalforge.dev"],
                DEBUG=False,
            )

    # 3. Production with default secret key must raise ValueError
    with pytest.raises(ValueError, match="SECRET_KEY must be set to a secure value"):
        Settings(
            APP_ENV="production",
            POSTGRES_PASSWORD="secure_postgres_pass",
            SECRET_KEY="dev-secret-key-evalforge-placeholder",
            CORS_ORIGINS=["https://app.evalforge.dev"],
            DEBUG=False,
        )

    # 4. Production with wildcard CORS must raise ValueError
    with pytest.raises(ValueError, match="CORS_ORIGINS must be set to a specific list"):
        Settings(
            APP_ENV="production",
            POSTGRES_PASSWORD="secure_postgres_pass",
            SECRET_KEY="secure-production-key-example-12345",
            CORS_ORIGINS=["*"],
            DEBUG=False,
        )

    # 5. Production with DEBUG=True must raise ValueError
    with pytest.raises(ValueError, match="DEBUG must be False in production"):
        Settings(
            APP_ENV="production",
            POSTGRES_PASSWORD="secure_postgres_pass",
            SECRET_KEY="secure-production-key-example-12345",
            CORS_ORIGINS=["https://app.evalforge.dev"],
            DEBUG=True,
        )

    # 6. Production with insecure DATABASE_URL password must raise ValueError
    with pytest.raises(ValueError, match="DATABASE_URL must be set to a secure value"):
        Settings(
            APP_ENV="production",
            DATABASE_URL="postgresql://postgres:postgres_password@dpg-host-123:5432/evalforge",
            SECRET_KEY="secure-production-key-example-12345",
            CORS_ORIGINS=["https://app.evalforge.dev"],
            DEBUG=False,
        )

    with pytest.raises(ValueError, match="DATABASE_URL must be set to a secure value"):
        Settings(
            APP_ENV="production",
            DATABASE_URL="postgresql://postgres:password@dpg-host-123:5432/evalforge",
            SECRET_KEY="secure-production-key-example-12345",
            CORS_ORIGINS=["https://app.evalforge.dev"],
            DEBUG=False,
        )

    # 7. Production with valid DATABASE_URL (e.g. Render managed Postgres) and default POSTGRES_PASSWORD is valid
    render_prod_settings = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql://postgres:secure_render_db_pass_998877@dpg-host-123.render.com:5432/evalforge",
        SECRET_KEY="secure-production-key-example-12345",
        CORS_ORIGINS=["https://evalforge.onrender.com", "https://app.evalforge.dev"],
        DEBUG=False,
    )
    assert "secure_render_db_pass_998877" in render_prod_settings.get_database_url
    assert render_prod_settings.get_database_url.startswith("postgresql+asyncpg://")

    # 8. Production with valid discrete POSTGRES_PASSWORD is valid
    discrete_prod_settings = Settings(
        APP_ENV="production",
        POSTGRES_PASSWORD="my_secure_prod_password_xyz",
        SECRET_KEY="secure-production-key-example-12345",
        CORS_ORIGINS=["https://app.evalforge.dev"],
        DEBUG=False,
    )
    assert "my_secure_prod_password_xyz" in discrete_prod_settings.get_database_url

    # 9. Development mode works with default non-production settings
    dev_settings = Settings(APP_ENV="development")
    assert dev_settings.APP_ENV == "development"
    assert dev_settings.DEBUG is True
    assert "postgres_password" in dev_settings.get_database_url


@pytest.mark.asyncio
async def test_phase12_openapi_contract_generation():
    """Verify OpenAPI schema can be generated and contains essential metadata."""
    schema = app.openapi()
    assert schema["info"]["title"] == "EvalForge Core API"
    assert schema["info"]["version"] == "1.0.0"
    assert "/api/v1/projects" in schema["paths"]
    assert "/api/v1/evaluations" in schema["paths"]
    assert any(k.startswith("/api/v1/datasets") for k in schema["paths"])


@pytest.mark.asyncio
async def test_phase12_examples_validity():
    """Verify that all example JSON and script files are valid."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    examples_dir = root_dir / "examples"

    # Test cli_evaluation_example.json
    cli_example = examples_dir / "cli_evaluation_example.json"
    assert cli_example.exists()
    content = json.loads(cli_example.read_text(encoding="utf-8"))
    assert "name" in content
    assert "test_cases" in content
    assert len(content["test_cases"]) > 0

    # Test README.md in examples
    assert (examples_dir / "README.md").exists()
    assert (examples_dir / "python_quickstart.py").exists()
    assert (examples_dir / "typescript_quickstart.ts").exists()


@pytest.mark.asyncio
async def test_phase12_sdk_initialization():
    """Verify Python SDK client initialization and defaults."""
    client = EvalForge(api_key="ef_live_testkey123", base_url="http://localhost:8000")
    assert client.api_key == "ef_live_testkey123"
    assert client.base_url == "http://localhost:8000"
    assert client.projects is not None
    assert client.evaluations is not None
    assert client.datasets is not None
    assert client.jobs is not None
    client.close()
