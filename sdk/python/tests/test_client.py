from unittest.mock import MagicMock, patch
import pytest

from evalforge import AsyncEvalForge, AuthenticationError, EvalForge, NotFoundError


def test_python_sdk_initialization():
    # 1. Missing API key raises AuthenticationError
    with pytest.raises(AuthenticationError):
        EvalForge(api_key="")

    # 2. Valid key initializes client
    client = EvalForge(api_key="ef_test_key_123", base_url="http://localhost:8000")
    assert client.api_key == "ef_test_key_123"
    assert client.base_url == "http://localhost:8000"


def test_python_sdk_project_operations():
    client = EvalForge(api_key="ef_test_key_123", base_url="http://localhost:8000")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"X-Request-ID": "req-1"}
    mock_resp.json.return_value = {
        "success": True,
        "data": {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "SDK Project",
            "description": "Created via Python SDK",
        },
    }

    with patch.object(client._http, "request", return_value=mock_resp):
        project = client.projects.create("SDK Project", "Created via Python SDK")
        assert str(project.id) == "11111111-1111-1111-1111-111111111111"
        assert project.name == "SDK Project"


def test_python_sdk_not_found_handling():
    client = EvalForge(api_key="ef_test_key_123", base_url="http://localhost:8000")

    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.headers = {"X-Request-ID": "req-404"}
    mock_resp.text = "Not Found"

    with patch.object(client._http, "request", return_value=mock_resp):
        with pytest.raises(NotFoundError):
            client.projects.get("11111111-1111-1111-1111-111111111111")


@pytest.mark.asyncio
async def test_async_python_sdk_operations():
    client = AsyncEvalForge(api_key="ef_test_key_123", base_url="http://localhost:8000")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"X-Request-ID": "async-req-1"}
    mock_resp.json.return_value = {
        "success": True,
        "data": {
            "id": "22222222-2222-2222-2222-222222222222",
            "name": "Async SDK Project",
            "description": "Created via Async Python SDK",
        },
    }

    with patch.object(client._http, "request", return_value=mock_resp):
        project = await client.projects.create("Async SDK Project", "Created via Async Python SDK")
        assert str(project.id) == "22222222-2222-2222-2222-222222222222"
        assert project.name == "Async SDK Project"

    await client.aclose()


@pytest.mark.asyncio
async def test_async_python_sdk_context_manager():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"X-Request-ID": "async-ctx-1"}
    mock_resp.json.return_value = {
        "success": True,
        "data": [
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "name": "Async Project List",
                "description": "Listed via Async Context Manager",
            }
        ],
    }

    async with AsyncEvalForge(api_key="ef_test_key_123", base_url="http://localhost:8000") as client:
        with patch.object(client._http, "request", return_value=mock_resp):
            projects = await client.projects.list()
            assert len(projects) == 1
            assert projects[0].name == "Async Project List"
