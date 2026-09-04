import unittest
from unittest.mock import MagicMock, patch

from evalforge import AsyncEvalForge, AuthenticationError, EvalForge, NotFoundError


class TestEvalForgeSDK(unittest.TestCase):
    def test_python_sdk_initialization(self):
        # 1. Missing API key raises AuthenticationError
        with self.assertRaises(AuthenticationError):
            EvalForge(api_key="")

        # 2. Valid key initializes client
        client = EvalForge(api_key="ef_test_key_123", base_url="http://localhost:8000")
        self.assertEqual(client.api_key, "ef_test_key_123")
        self.assertEqual(client.base_url, "http://localhost:8000")

    def test_python_sdk_project_operations(self):
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
            self.assertEqual(str(project.id), "11111111-1111-1111-1111-111111111111")
            self.assertEqual(project.name, "SDK Project")

    def test_python_sdk_not_found_handling(self):
        client = EvalForge(api_key="ef_test_key_123", base_url="http://localhost:8000")

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.headers = {"X-Request-ID": "req-404"}
        mock_resp.text = "Not Found"

        with patch.object(client._http, "request", return_value=mock_resp):
            with self.assertRaises(NotFoundError):
                client.projects.get("11111111-1111-1111-1111-111111111111")


class TestAsyncEvalForgeSDK(unittest.IsolatedAsyncioTestCase):
    async def test_async_python_sdk_operations(self):
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
            project = await client.projects.create(
                "Async SDK Project", "Created via Async Python SDK"
            )
            self.assertEqual(str(project.id), "22222222-2222-2222-2222-222222222222")
            self.assertEqual(project.name, "Async SDK Project")

        await client.aclose()

    async def test_async_python_sdk_context_manager(self):
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

        async with AsyncEvalForge(
            api_key="ef_test_key_123", base_url="http://localhost:8000"
        ) as client:
            with patch.object(client._http, "request", return_value=mock_resp):
                projects = await client.projects.list()
                self.assertEqual(len(projects), 1)
                self.assertEqual(projects[0].name, "Async Project List")
