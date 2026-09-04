import json
import pytest
from unittest.mock import patch, MagicMock
from evalforge_cli.main import main, print_output
from evalforge_cli.config import load_config, save_config, get_api_key, get_base_url
from evalforge_cli.client import CLIClient


def test_cli_config_management(tmp_path, monkeypatch):
    test_config_file = tmp_path / "config.json"
    monkeypatch.setattr("evalforge_cli.config.CONFIG_FILE", test_config_file)
    monkeypatch.setattr("evalforge_cli.config.CONFIG_DIR", tmp_path)

    # Initial state empty
    assert load_config() == {}

    # Save config
    save_config({"api_key": "test-key-123", "base_url": "http://test:8000"})
    loaded = load_config()
    assert loaded["api_key"] == "test-key-123"
    assert loaded["base_url"] == "http://test:8000"

    # get_api_key & get_base_url
    monkeypatch.delenv("EVALFORGE_API_KEY", raising=False)
    monkeypatch.delenv("EVALFORGE_BASE_URL", raising=False)
    assert get_api_key() == "test-key-123"
    assert get_base_url() == "http://test:8000"


def test_cli_auth_login_and_status(tmp_path, monkeypatch, capsys):
    test_config_file = tmp_path / "config.json"
    monkeypatch.setattr("evalforge_cli.config.CONFIG_FILE", test_config_file)
    monkeypatch.setattr("evalforge_cli.config.CONFIG_DIR", tmp_path)
    monkeypatch.delenv("EVALFORGE_API_KEY", raising=False)

    # Run login
    main(["auth", "login", "--key", "ef_live_testsecretkey123456"])
    captured = capsys.readouterr()
    assert "Authentication successful" in captured.out

    # Run status
    main(["auth", "status"])
    captured = capsys.readouterr()
    assert "Authenticated with API key: ef_liv...3456" in captured.out


def test_cli_projects_list_and_create(monkeypatch, capsys):
    mock_request = MagicMock(return_value={"data": [{"id": "p1", "name": "Test Project"}]})
    monkeypatch.setattr(CLIClient, "request", mock_request)

    main(["projects", "list", "--page", "1", "--page-size", "10", "--json"])
    captured = capsys.readouterr()
    assert "Test Project" in captured.out
    mock_request.assert_called_with("GET", "/api/v1/projects", params={"page": 1, "page_size": 10})

    main(["projects", "create", "--name", "New Project", "--description", "Desc", "--json"])
    captured = capsys.readouterr()
    mock_request.assert_called_with(
        "POST", "/api/v1/projects", json_data={"name": "New Project", "description": "Desc"}
    )


def test_cli_evaluations_run(tmp_path, monkeypatch, capsys):
    mock_request = MagicMock(return_value={"data": {"id": "eval-1", "status": "pending"}})
    monkeypatch.setattr(CLIClient, "request", mock_request)

    config_file = tmp_path / "eval_config.json"
    config_file.write_text(
        json.dumps({
            "name": "Test Run",
            "test_cases": [{"input": "hi", "actual_output": "hello"}],
            "metrics": ["accuracy"]
        }),
        encoding="utf-8",
    )

    main(["evaluations", "run", "--project-id", "p1", "--config", str(config_file), "--json"])
    captured = capsys.readouterr()
    assert "eval-1" in captured.out


def test_cli_print_output_variations(capsys):
    # Dict
    print_output({"k1": "v1", "k2": "v2"})
    captured = capsys.readouterr()
    assert "k1: v1" in captured.out

    # List of dicts
    print_output([{"id": "1", "name": "Item 1"}])
    captured = capsys.readouterr()
    assert "ID | NAME" in captured.out
    assert "1 | Item 1" in captured.out

    # Empty list
    print_output([])
    captured = capsys.readouterr()
    assert "No items found." in captured.out
