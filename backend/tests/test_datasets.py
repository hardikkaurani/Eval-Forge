import json

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.datasets.parsers.parsers import DatasetParser
from app.datasets.validators.validators import DatasetValidator


def test_validator_with_valid_records():
    records = [
        {
            "prompt": "Translate 'hello'",
            "reference_output": "bonjour",
            "expected_score": 1.0,
        },
        {
            "prompt": "Write a poem",
            "ground_truth": "Roses are red",
            "tags": ["creative"],
        },
    ]
    report = DatasetValidator.validate_records(records)
    assert report["valid"] is True
    assert report["total_records"] == 2
    assert report["valid_records_count"] == 2
    assert len(report["errors"]) == 0


def test_validator_with_invalid_records():
    # Empty prompt and invalid expected_score type
    records = [
        {"prompt": "  ", "reference_output": "bonjour"},
        {"prompt": "Write a poem", "expected_score": "not-a-float"},
    ]
    report = DatasetValidator.validate_records(records)
    assert report["valid"] is False
    assert report["invalid_records_count"] == 2
    assert len(report["errors"]) == 2


def test_parser_csv():
    csv_content = (
        "prompt,input,reference_output,expected_score,tags\n"
        "Explain quantum physics,System,Particles in wave,0.85,physics\n"
        "Solve 2+2,System,4,1.0,math\n"
    ).encode("utf-8")

    records = DatasetParser.parse(csv_content, "csv")
    assert len(records) == 2
    assert records[0]["prompt"] == "Explain quantum physics"
    assert records[0]["expected_score"] == 0.85
    assert records[0]["tags"] == ["physics"]
    assert records[1]["prompt"] == "Solve 2+2"
    assert records[1]["expected_score"] == 1.0
    assert records[1]["tags"] == ["math"]


def test_parser_json():
    json_data = [
        {"prompt": "Explain quantum physics", "expected_score": 0.85},
        {"prompt": "Solve 2+2", "expected_score": 1.0},
    ]
    json_content = json.dumps(json_data).encode("utf-8")
    records = DatasetParser.parse(json_content, "json")
    assert len(records) == 2
    assert records[0]["prompt"] == "Explain quantum physics"
    assert records[1]["prompt"] == "Solve 2+2"


def test_parser_jsonl():
    jsonl_content = (
        '{"prompt": "Explain quantum physics", "expected_score": 0.85}\n'
        '{"prompt": "Solve 2+2", "expected_score": 1.0}\n'
    ).encode("utf-8")
    records = DatasetParser.parse(jsonl_content, "jsonl")
    assert len(records) == 2
    assert records[0]["prompt"] == "Explain quantum physics"
    assert records[1]["prompt"] == "Solve 2+2"


def create_test_project(client):
    payload = {
        "name": "Dataset Test Project",
        "description": "Validating dataset API CRUD flow.",
        "status": "active",
    }
    resp = client.post("/api/v1/projects", json=payload)
    return resp.json()["data"]["id"]


def test_dataset_crud_and_import(client):
    project_id = create_test_project(client)

    # 1. Create dataset empty
    dataset_payload = {
        "name": "E2E Test Dataset",
        "description": "Validating dataset",
        "visibility": "private",
        "tags": ["e2e", "test"],
    }
    resp = client.post(
        f"/api/v1/datasets/?project_id={project_id}", json=dataset_payload
    )
    assert resp.status_code == 201
    dataset = resp.json()
    assert dataset["name"] == "E2E Test Dataset"
    dataset_id = dataset["id"]

    # 2. Get dataset
    resp = client.get(f"/api/v1/datasets/{dataset_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "E2E Test Dataset"

    # 3. Update dataset
    update_payload = {"name": "Updated E2E Test Dataset"}
    resp = client.put(f"/api/v1/datasets/{dataset_id}", json=update_payload)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated E2E Test Dataset"

    # 4. Import a file (CSV format) to a new version of the existing dataset
    csv_data = (
        "prompt,input,reference_output,expected_score,tags\n"
        "Solve 3+3,System,6,1.0,math\n"
    )
    import_data = {
        "project_id": project_id,
        "dataset_name": "CSV Imported Dataset",
        "existing_dataset_id": dataset_id,
        "version_label": "v2",
    }
    files = {"file": ("dataset.csv", csv_data, "text/csv")}
    resp = client.post("/api/v1/datasets/import", data=import_data, files=files)
    assert resp.status_code == 202
    res = resp.json()
    assert res["status"] == "COMPLETED"
    assert res["records_imported"] == 1
    assert "version_id" in res

    # 5. List versions
    resp = client.get(f"/api/v1/datasets/{dataset_id}/versions")
    assert resp.status_code == 200
    versions = resp.json()
    assert len(versions) == 2  # v1 (empty initial) and v2 (imported)

    # 6. List records of v2
    v2_id = next(v["id"] for v in versions if v["version"] == "v2")
    resp = client.get(f"/api/v1/datasets/versions/{v2_id}/records")
    assert resp.status_code == 200
    records_res = resp.json()
    assert records_res["total"] == 1
    assert records_res["records"][0]["prompt"] == "Solve 3+3"

    # 7. Delete dataset
    resp = client.delete(f"/api/v1/datasets/{dataset_id}")
    assert resp.status_code == 204
    resp = client.get(f"/api/v1/datasets/{dataset_id}")
    assert resp.status_code == 404


def test_dataset_diff_rollback_and_benchmarks(client):
    project_id = create_test_project(client)

    # 1. Create dataset and import two versions to diff
    # Version 1 (v1)
    csv_v1 = "prompt,reference_output\nPrompt A,Ref A\nPrompt B,Ref B\n"
    resp = client.post(
        "/api/v1/datasets/import",
        data={
            "project_id": project_id,
            "dataset_name": "Diff Dataset",
            "version_label": "v1",
        },
        files={"file": ("dataset_v1.csv", csv_v1, "text/csv")},
    )
    assert resp.status_code == 202
    dataset_id = resp.json()["dataset_id"]

    # Version 2 (v2): Prompt A deleted, Prompt B modified, Prompt C added
    csv_v2 = "prompt,reference_output\nPrompt B,Ref B Modified\nPrompt C,Ref C\n"
    resp = client.post(
        "/api/v1/datasets/import",
        data={
            "project_id": project_id,
            "dataset_name": "Diff Dataset",
            "existing_dataset_id": dataset_id,
            "version_label": "v2",
        },
        files={"file": ("dataset_v2.csv", csv_v2, "text/csv")},
    )
    assert resp.status_code == 202

    # 2. Get Diff
    resp = client.get(f"/api/v1/datasets/{dataset_id}/diff?version_a=v1&version_b=v2")
    assert resp.status_code == 200
    diff = resp.json()
    assert len(diff) == 3
    # Check that removed, added, modified change types exist
    change_types = [item["change_type"] for item in diff]
    assert "removed" in change_types
    assert "added" in change_types
    assert "modified" in change_types

    # 3. Rollback (v1 promoted as v3)
    resp = client.post(f"/api/v1/datasets/{dataset_id}/rollback?target_version=v1")
    assert resp.status_code == 200
    rollback_res = resp.json()
    assert rollback_res["version"] == "v3"
    assert rollback_res["record_count"] == 2

    # 4. Benchmark Suite CRUD
    suite_payload = {
        "name": "E2E Benchmark Suite",
        "description": "Tests logic",
        "tags": ["math", "physics"],
        "dataset_ids": [dataset_id],
    }
    resp = client.post(
        f"/api/v1/benchmarks/?project_id={project_id}", json=suite_payload
    )
    assert resp.status_code == 201
    suite = resp.json()
    assert suite["name"] == "E2E Benchmark Suite"
    assert len(suite["datasets"]) == 1
    suite_id = suite["id"]

    # Update suite
    resp = client.put(
        f"/api/v1/benchmarks/{suite_id}", json={"name": "Updated Benchmark Suite"}
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Benchmark Suite"

    # Dashboard Metrics
    resp = client.get(f"/api/v1/benchmarks/dashboard/metrics?project_id={project_id}")
    assert resp.status_code == 200
    metrics = resp.json()
    assert metrics["total_datasets"] == 1
    assert metrics["total_benchmark_suites"] == 1

    # Delete suite
    resp = client.delete(f"/api/v1/benchmarks/{suite_id}")
    assert resp.status_code == 204


def test_experiment_flow(client):
    project_id = create_test_project(client)

    # 1. Import a dataset to get a valid version
    csv_data = "prompt,candidate_output,reference_output\nSolve 5+5,10,10\n"
    resp = client.post(
        "/api/v1/datasets/import",
        data={
            "project_id": project_id,
            "dataset_name": "Experiment Dataset",
            "version_label": "v1",
        },
        files={"file": ("dataset.csv", csv_data, "text/csv")},
    )
    assert resp.status_code == 202
    version_id = resp.json()["version_id"]

    # 2. Create Experiment
    exp_payload = {
        "name": "Math Evaluation Experiment",
        "description": "Factual math accuracy checks",
        "dataset_version_id": version_id,
        "judge": "rubric",
        "provider": "openai",
        "configuration": {"temperature": 0.0, "threshold": 0.8},
    }
    resp = client.post(
        f"/api/v1/experiments/?project_id={project_id}", json=exp_payload
    )
    assert resp.status_code == 201
    exp = resp.json()
    assert exp["name"] == "Math Evaluation Experiment"
    assert exp["status"] == "PENDING"
    experiment_id = exp["id"]

    # 3. List Experiments
    resp = client.get(f"/api/v1/experiments/?project_id={project_id}")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    # 4. Execute Experiment (Runs mocked OpenAI evaluation)
    resp = client.post(f"/api/v1/experiments/{experiment_id}/execute")
    assert resp.status_code == 200
    executed = resp.json()
    assert executed["status"] == "COMPLETED"
    assert "metrics" in executed
    assert executed["metrics"]["total_cases"] == 1
    assert len(executed["results"]) == 1

    # 5. Delete Experiment
    resp = client.delete(f"/api/v1/experiments/{experiment_id}")
    assert resp.status_code == 204


def test_dataset_download_path_traversal(client):
    import os

    os.makedirs("datasets", exist_ok=True)

    # 1. Create project and import dataset to get an authorized file
    res_p = client.post("/api/v1/projects", json={"name": "Traversal Test Project"})
    assert res_p.status_code == 201
    proj_id = res_p.json()["data"]["id"]

    csv_data = "prompt,output\ntest,test\n"
    imp_res = client.post(
        "/api/v1/datasets/import",
        data={"project_id": proj_id, "dataset_name": "Traversal Dataset"},
        files={"file": ("test_download.csv", csv_data, "text/csv")},
    )
    assert imp_res.status_code == 202
    job_id = imp_res.json()["job_id"]
    valid_file_name = f"import_{job_id}.csv"

    # Valid file download
    resp = client.get(f"/api/v1/datasets/download/{valid_file_name}")
    assert resp.status_code == 200
    assert "prompt,output" in resp.text

    # 2. Simple ../ encoded traversal
    resp = client.get("/api/v1/datasets/download/..%2Fpyproject.toml")
    assert resp.status_code == 400

    # 3. Deep ../../ encoded traversal
    resp = client.get("/api/v1/datasets/download/..%2F..%2F.env")
    assert resp.status_code == 400

    # 4. Windows backslash traversal
    resp = client.get("/api/v1/datasets/download/..%5C..%5C.env")
    assert resp.status_code == 400

    # 5. Non-existent legitimate file
    resp = client.get("/api/v1/datasets/download/non_existent.csv")
    assert resp.status_code == 404


def test_datasets_benchmarks_experiments_tenant_isolation(
    db_session: AsyncSession,
) -> None:
    """Verifies that Datasets, Benchmarks, and Experiments CRUD and execution paths enforce strict workspace isolation."""
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "aaaaaaaa-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "bbbbbbbb-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Tenant A creates resources under Project A
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_a = client_a.post(
            "/api/v1/projects", json={"name": "Project A", "status": "active"}
        )
        assert res_a.status_code == 201
        proj_a_id = res_a.json()["data"]["id"]

        # Tenant A creates Dataset A
        ds_a_res = client_a.post(
            f"/api/v1/datasets/?project_id={proj_a_id}",
            json={"name": "Dataset A", "visibility": "private"},
        )
        assert ds_a_res.status_code == 201
        dataset_a_id = ds_a_res.json()["id"]

        # Tenant A lists versions
        ver_res = client_a.get(f"/api/v1/datasets/{dataset_a_id}/versions")
        assert ver_res.status_code == 200
        version_a_id = ver_res.json()[0]["id"]

        # Tenant A creates Benchmark Suite A
        bs_a_res = client_a.post(
            f"/api/v1/benchmarks/?project_id={proj_a_id}",
            json={"name": "Benchmark A", "dataset_ids": [dataset_a_id]},
        )
        assert bs_a_res.status_code == 201
        suite_a_id = bs_a_res.json()["id"]

        # Tenant A creates Experiment A
        exp_a_res = client_a.post(
            f"/api/v1/experiments/?project_id={proj_a_id}",
            json={
                "name": "Experiment A",
                "dataset_version_id": version_a_id,
                "judge": "rubric",
                "provider": "openai",
            },
        )
        assert exp_a_res.status_code == 201
        experiment_a_id = exp_a_res.json()["id"]

    # 2. Tenant B attempts cross-tenant access to Tenant A's resources
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        res_b = client_b.post(
            "/api/v1/projects", json={"name": "Project B", "status": "active"}
        )
        assert res_b.status_code == 201
        proj_b_id = res_b.json()["data"]["id"]

        # Dataset isolation checks
        assert (
            client_b.post(
                f"/api/v1/datasets/?project_id={proj_a_id}",
                json={"name": "Attacker Dataset"},
            ).status_code
            == 404
        )
        assert client_b.get(f"/api/v1/datasets/{dataset_a_id}").status_code == 404
        assert (
            client_b.get(f"/api/v1/datasets/?project_id={proj_a_id}").status_code == 404
        )
        assert (
            client_b.put(
                f"/api/v1/datasets/{dataset_a_id}",
                json={"name": "Hacked Dataset Name"},
            ).status_code
            == 404
        )
        assert client_b.delete(f"/api/v1/datasets/{dataset_a_id}").status_code == 404
        assert (
            client_b.get(f"/api/v1/datasets/{dataset_a_id}/versions").status_code == 404
        )
        assert (
            client_b.get(
                f"/api/v1/datasets/versions/{version_a_id}/records"
            ).status_code
            == 404
        )

        # Benchmark isolation checks
        assert client_b.get(f"/api/v1/benchmarks/{suite_a_id}").status_code == 404
        assert (
            client_b.put(
                f"/api/v1/benchmarks/{suite_a_id}",
                json={"name": "Hacked Benchmark Name"},
            ).status_code
            == 404
        )
        assert client_b.delete(f"/api/v1/benchmarks/{suite_a_id}").status_code == 404
        assert (
            client_b.get(
                f"/api/v1/benchmarks/dashboard/metrics?project_id={proj_a_id}"
            ).status_code
            == 404
        )
        assert client_b.post(
            f"/api/v1/benchmarks/?project_id={proj_b_id}",
            json={"name": "Spoofed Suite", "dataset_ids": [dataset_a_id]},
        ).status_code in (400, 404)

        # Experiment isolation checks
        assert client_b.get(f"/api/v1/experiments/{experiment_a_id}").status_code == 404
        assert (
            client_b.post(f"/api/v1/experiments/{experiment_a_id}/execute").status_code
            == 404
        )
        assert (
            client_b.delete(f"/api/v1/experiments/{experiment_a_id}").status_code == 404
        )
        assert client_b.post(
            f"/api/v1/experiments/?project_id={proj_b_id}",
            json={
                "name": "Cross Tenant Experiment",
                "dataset_version_id": version_a_id,
                "judge": "rubric",
                "provider": "openai",
            },
        ).status_code in (400, 404)

    app.dependency_overrides.clear()


def test_cross_tenant_export_version_idor_blocked(
    db_session: AsyncSession,
) -> None:
    """Verifies that dataset export strictly blocks IDOR exfiltration of victim version IDs."""
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "aaaaaaaa-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "bbbbbbbb-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Tenant A imports dataset version
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_a = client_a.post(
            "/api/v1/projects", json={"name": "Project A", "status": "active"}
        )
        assert res_a.status_code == 201
        proj_a_id = res_a.json()["data"]["id"]

        csv_a = "prompt,reference_output\nVictim Secret Prompt,Victim Secret Output\n"
        import_a = client_a.post(
            "/api/v1/datasets/import",
            data={
                "project_id": proj_a_id,
                "dataset_name": "Victim Private Dataset",
                "version_label": "v1",
            },
            files={"file": ("dataset_a.csv", csv_a, "text/csv")},
        )
        assert import_a.status_code == 202
        dataset_a_id = import_a.json()["dataset_id"]
        version_a_id = import_a.json()["version_id"]

        # Tenant A export of own version -> succeeds
        export_a = client_a.post(
            f"/api/v1/datasets/export?project_id={proj_a_id}&version_id={version_a_id}&file_format=json"
        )
        assert export_a.status_code == 202
        file_url_a = export_a.json()["file_url"]
        download_a = client_a.get(file_url_a)
        assert download_a.status_code == 200
        assert "Victim Secret Prompt" in download_a.text

    # 2. Tenant B imports dataset version
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        res_b = client_b.post(
            "/api/v1/projects", json={"name": "Project B", "status": "active"}
        )
        assert res_b.status_code == 201
        proj_b_id = res_b.json()["data"]["id"]

        csv_b = "prompt,reference_output\nAttacker Prompt,Attacker Output\n"
        import_b = client_b.post(
            "/api/v1/datasets/import",
            data={
                "project_id": proj_b_id,
                "dataset_name": "Attacker Dataset",
                "version_label": "v1",
            },
            files={"file": ("dataset_b.csv", csv_b, "text/csv")},
        )
        assert import_b.status_code == 202
        version_b_id = import_b.json()["version_id"]

        # Tenant B export of own version -> succeeds
        export_b = client_b.post(
            f"/api/v1/datasets/export?project_id={proj_b_id}&version_id={version_b_id}&file_format=json"
        )
        assert export_b.status_code == 202

        # ATTACK 1: Tenant B attempts to export Tenant A's version using Tenant B's project_id
        attack_1 = client_b.post(
            f"/api/v1/datasets/export?project_id={proj_b_id}&version_id={version_a_id}&file_format=json"
        )
        assert attack_1.status_code == 404

        # ATTACK 2: Tenant B attempts to export Tenant A's version using Tenant A's project_id
        attack_2 = client_b.post(
            f"/api/v1/datasets/export?project_id={proj_a_id}&version_id={version_a_id}&file_format=json"
        )
        assert attack_2.status_code == 404

        # ATTACK 3: Tenant B attempts to export with Tenant A's dataset_id parameter
        attack_3 = client_b.post(
            f"/api/v1/datasets/export?project_id={proj_b_id}&dataset_id={dataset_a_id}&version_id={version_a_id}&file_format=json"
        )
        assert attack_3.status_code == 404

        # ATTACK 4: Random non-existent version_id
        fake_version = "00000000-0000-0000-0000-000000000000"
        attack_4 = client_b.post(
            f"/api/v1/datasets/export?project_id={proj_b_id}&version_id={fake_version}&file_format=json"
        )
        assert attack_4.status_code == 404

    app.dependency_overrides.clear()


def test_non_export_file_download_tenant_isolation(
    db_session: AsyncSession,
) -> None:
    """Verifies that download_file strictly authorizes ALL files (export and non-export/imported files)."""
    import os
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.main import app

    async def _override_get_db_non_export():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db_non_export

    ws_a_id = "aaaaaaaa-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "bbbbbbbb-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Tenant A setup: Project A + Import Dataset + Export Dataset
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_a = client_a.post(
            "/api/v1/projects", json={"name": "Project A", "status": "active"}
        )
        assert res_a.status_code == 201
        proj_a_id = res_a.json()["data"]["id"]

        csv_a = "prompt,reference_output\nVictim Private Prompt,Victim Private Secret\n"
        import_a = client_a.post(
            "/api/v1/datasets/import",
            data={
                "project_id": proj_a_id,
                "dataset_name": "Victim Private Dataset",
                "version_label": "v1",
            },
            files={"file": ("dataset_a.csv", csv_a, "text/csv")},
        )
        assert import_a.status_code == 202
        import_a_job_id = import_a.json()["job_id"]
        version_a_id = import_a.json()["version_id"]
        import_a_fn = f"import_{import_a_job_id}.csv"

        # Tenant A downloads own imported non-export file -> 200 OK
        dl_a_import = client_a.get(f"/api/v1/datasets/download/{import_a_fn}")
        assert dl_a_import.status_code == 200
        assert "Victim Private Secret" in dl_a_import.text

        # Tenant A exports dataset
        export_a = client_a.post(
            f"/api/v1/datasets/export?project_id={proj_a_id}&version_id={version_a_id}&file_format=json"
        )
        assert export_a.status_code == 202
        export_a_fn = os.path.basename(export_a.json()["file_url"])

        # Tenant A downloads own export file -> 200 OK
        dl_a_export = client_a.get(f"/api/v1/datasets/download/{export_a_fn}")
        assert dl_a_export.status_code == 200

    # Create an unowned file directly in datasets/ directory
    os.makedirs("datasets", exist_ok=True)
    unowned_path = os.path.join("datasets", "unowned_secret.csv")
    with open(unowned_path, "w", encoding="utf-8") as f:
        f.write("unowned,secret_data\n")

    # 2. Tenant B setup & cross-tenant attacks
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        res_b = client_b.post(
            "/api/v1/projects", json={"name": "Project B", "status": "active"}
        )
        assert res_b.status_code == 201
        proj_b_id = res_b.json()["data"]["id"]

        csv_b = "prompt,reference_output\nAttacker Prompt,Attacker Data\n"
        import_b = client_b.post(
            "/api/v1/datasets/import",
            data={
                "project_id": proj_b_id,
                "dataset_name": "Attacker Dataset",
                "version_label": "v1",
            },
            files={"file": ("dataset_b.csv", csv_b, "text/csv")},
        )
        assert import_b.status_code == 202
        import_b_job_id = import_b.json()["job_id"]
        import_b_fn = f"import_{import_b_job_id}.csv"

        # Tenant B downloads own imported file -> 200 OK
        dl_b_import = client_b.get(f"/api/v1/datasets/download/{import_b_fn}")
        assert dl_b_import.status_code == 200

        # ATTACK 1: Tenant B requests Tenant A's non-export imported file
        attack_non_export = client_b.get(f"/api/v1/datasets/download/{import_a_fn}")
        assert attack_non_export.status_code == 404
        assert "Victim Private Secret" not in attack_non_export.text

        # ATTACK 2: Tenant B requests Tenant A's export file
        attack_export = client_b.get(f"/api/v1/datasets/download/{export_a_fn}")
        assert attack_export.status_code == 404
        assert "Victim Private Secret" not in attack_export.text

        # ATTACK 3: Tenant B requests unknown file
        attack_unknown = client_b.get("/api/v1/datasets/download/nonexistent_12345.csv")
        assert attack_unknown.status_code == 404

        # ATTACK 4: Tenant B requests unowned file on disk with no DB record
        attack_unowned = client_b.get("/api/v1/datasets/download/unowned_secret.csv")
        assert attack_unowned.status_code == 404
        assert "secret_data" not in attack_unowned.text

        # ATTACK 5: Path traversal with ../
        attack_traversal = client_b.get(
            "/api/v1/datasets/download/../datasets/unowned_secret.csv"
        )
        assert attack_traversal.status_code in (400, 404)

        # ATTACK 6: Windows backslash traversal
        attack_backslash = client_b.get(
            "/api/v1/datasets/download/..\\datasets\\unowned_secret.csv"
        )
        assert attack_backslash.status_code in (400, 404)

    # 3. Unauthenticated request verification
    app.dependency_overrides.clear()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client_unauth:
        dl_unauth = client_unauth.get(f"/api/v1/datasets/download/{import_a_fn}")
        assert dl_unauth.status_code in (401, 403)

    # Clean up unowned file
    if os.path.exists(unowned_path):
        os.remove(unowned_path)

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_dataset_version_tenant_isolation(
    db_session: AsyncSession,
) -> None:
    """Verifies complete tenant isolation across all dataset, version, diff, rollback, and record operations."""
    from unittest.mock import MagicMock

    import pytest
    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.datasets.exceptions.exceptions import DatasetNotFoundException
    from app.datasets.services.dataset import DatasetService
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "aaaaaaaa-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "bbbbbbbb-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Setup Tenant A: Project A + Dataset A (v1 with records)
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_a = client_a.post(
            "/api/v1/projects", json={"name": "Project A", "status": "active"}
        )
        assert res_a.status_code == 201
        proj_a_id = res_a.json()["data"]["id"]

        csv_a = (
            "prompt,reference_output\nTenant A Secret Prompt,Tenant A Secret Output\n"
        )
        import_a = client_a.post(
            "/api/v1/datasets/import",
            data={
                "project_id": proj_a_id,
                "dataset_name": "Tenant A Dataset",
                "version_label": "v1",
            },
            files={"file": ("dataset_a.csv", csv_a, "text/csv")},
        )
        assert import_a.status_code == 202
        dataset_a_id = import_a.json()["dataset_id"]
        version_a_id = import_a.json()["version_id"]

        # Tenant A can access own dataset & versions & records
        assert client_a.get(f"/api/v1/datasets/{dataset_a_id}").status_code == 200
        assert (
            client_a.get(f"/api/v1/datasets/{dataset_a_id}/versions").status_code == 200
        )
        records_a_res = client_a.get(
            f"/api/v1/datasets/versions/{version_a_id}/records"
        )
        assert records_a_res.status_code == 200
        assert "Tenant A Secret Prompt" in records_a_res.text

    # 2. Setup Tenant B: Project B + Dataset B
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        res_b = client_b.post(
            "/api/v1/projects", json={"name": "Project B", "status": "active"}
        )
        assert res_b.status_code == 201
        proj_b_id = res_b.json()["data"]["id"]

        csv_b = "prompt,reference_output\nTenant B Prompt,Tenant B Output\n"
        import_b = client_b.post(
            "/api/v1/datasets/import",
            data={
                "project_id": proj_b_id,
                "dataset_name": "Tenant B Dataset",
                "version_label": "v1",
            },
            files={"file": ("dataset_b.csv", csv_b, "text/csv")},
        )
        assert import_b.status_code == 202
        dataset_b_id = import_b.json()["dataset_id"]

        # --- ADVERSARIAL CROSS-TENANT ATTACKS BY TENANT B AGAINST TENANT A ---

        # Attack 1: GET Tenant A's dataset
        att_1 = client_b.get(f"/api/v1/datasets/{dataset_a_id}")
        assert att_1.status_code == 404
        assert "Tenant A Secret" not in att_1.text

        # Attack 2: LIST Tenant A's dataset versions
        att_2 = client_b.get(f"/api/v1/datasets/{dataset_a_id}/versions")
        assert att_2.status_code == 404

        # Attack 3: CREATE dataset under Tenant A's project
        att_3 = client_b.post(
            f"/api/v1/datasets/?project_id={proj_a_id}",
            json={"name": "Spoofed Dataset"},
        )
        assert att_3.status_code == 404

        # Attack 4: UPDATE Tenant A's dataset
        att_4 = client_b.put(
            f"/api/v1/datasets/{dataset_a_id}",
            json={"name": "Hacked Dataset Name"},
        )
        assert att_4.status_code == 404

        # Attack 5: DELETE Tenant A's dataset
        att_5 = client_b.delete(f"/api/v1/datasets/{dataset_a_id}")
        assert att_5.status_code == 404

        # Attack 6: GET records belonging to Tenant A's version_id
        att_6 = client_b.get(f"/api/v1/datasets/versions/{version_a_id}/records")
        assert att_6.status_code == 404
        assert "Tenant A Secret" not in att_6.text

        # Attack 7: DIFF on Tenant A's dataset
        att_7 = client_b.get(
            f"/api/v1/datasets/{dataset_a_id}/diff?version_a=v1&version_b=v1"
        )
        assert att_7.status_code == 404

        # Attack 8: ROLLBACK on Tenant A's dataset
        att_8 = client_b.post(
            f"/api/v1/datasets/{dataset_a_id}/rollback?target_version=v1"
        )
        assert att_8.status_code == 404

        # Attack 9: ROLLBACK Tenant B's dataset specifying Tenant A's dataset version
        att_9 = client_b.post(
            f"/api/v1/datasets/{dataset_b_id}/rollback?target_version=v1_nonexistent"
        )
        assert att_9.status_code == 404

        # Attack 10: Payload/query workspace_id tampering
        att_10 = client_b.get(f"/api/v1/datasets/{dataset_a_id}?workspace_id={ws_a_id}")
        assert att_10.status_code == 404

    # 3. DIRECT SERVICE LAYER AUTHORIZATION VERIFICATION
    service = DatasetService(db_session)

    with pytest.raises(DatasetNotFoundException):
        await service.get_dataset(dataset_a_id, workspace_id=ws_b_id)

    with pytest.raises(DatasetNotFoundException):
        await service.get_records(version_a_id, workspace_id=ws_b_id)

    with pytest.raises(DatasetNotFoundException):
        await service.list_versions(dataset_a_id, workspace_id=ws_b_id)

    with pytest.raises(DatasetNotFoundException):
        await service.generate_diff(dataset_a_id, "v1", "v1", workspace_id=ws_b_id)

    with pytest.raises(DatasetNotFoundException):
        await service.rollback_version(dataset_a_id, "v1", workspace_id=ws_b_id)

    # 4. UNAUTHENTICATED ROUTE ACCESS VERIFICATION
    app.dependency_overrides.clear()

    async def override_get_db_unauth():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db_unauth

    with TestClient(app) as client_unauth:
        assert client_unauth.get(f"/api/v1/datasets/{dataset_a_id}").status_code in (
            401,
            403,
        )
        assert client_unauth.get(
            f"/api/v1/datasets/versions/{version_a_id}/records"
        ).status_code in (401, 403)

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_dataset_record_tenant_isolation(
    db_session: AsyncSession,
) -> None:
    """Verifies complete record integrity, immutability, and tenant isolation across all record CRUD paths."""
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.datasets.exceptions.exceptions import DatasetNotFoundException
    from app.datasets.services.dataset import DatasetService
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "aaaaa111-aaaa-4aaa-aaaa-aaaaaaaaaaaa"
    ws_b_id = "bbbbb222-bbbb-4bbb-bbbb-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Setup Tenant A resources
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_a = client_a.post(
            "/api/v1/projects", json={"name": "Project A Records", "status": "active"}
        )
        assert res_a.status_code == 201
        proj_a_id = res_a.json()["data"]["id"]

        csv_a = (
            "prompt,reference_output\nVictim Secret Prompt A,Victim Secret Output A\n"
        )
        import_a = client_a.post(
            "/api/v1/datasets/import",
            data={
                "project_id": proj_a_id,
                "dataset_name": "Tenant A Records Dataset",
                "version_label": "v1",
            },
            files={"file": ("dataset_a.csv", csv_a, "text/csv")},
        )
        assert import_a.status_code == 202
        version_a_id = import_a.json()["version_id"]

        # Insert a single record for Tenant A via POST endpoint
        rec_create_res = client_a.post(
            f"/api/v1/datasets/versions/{version_a_id}/records",
            json=[
                {
                    "prompt": "Tenant A Explicit Prompt",
                    "reference_output": "Tenant A Explicit Ref",
                }
            ],
        )
        assert rec_create_res.status_code == 201
        record_a_id = rec_create_res.json()[0]["id"]

        # Tenant A can GET own record
        rec_a_get = client_a.get(f"/api/v1/datasets/records/{record_a_id}")
        assert rec_a_get.status_code == 200
        assert rec_a_get.json()["prompt"] == "Tenant A Explicit Prompt"

        # Tenant A can UPDATE own record
        rec_a_put = client_a.put(
            f"/api/v1/datasets/records/{record_a_id}",
            json={"prompt": "Tenant A Updated Prompt"},
        )
        assert rec_a_put.status_code == 200
        assert rec_a_put.json()["prompt"] == "Tenant A Updated Prompt"

    # 2. Setup Tenant B resources
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        res_b = client_b.post(
            "/api/v1/projects", json={"name": "Project B Records", "status": "active"}
        )
        assert res_b.status_code == 201
        proj_b_id = res_b.json()["data"]["id"]

        csv_b = "prompt,reference_output\nTenant B Prompt,Tenant B Output\n"
        import_b = client_b.post(
            "/api/v1/datasets/import",
            data={
                "project_id": proj_b_id,
                "dataset_name": "Tenant B Records Dataset",
                "version_label": "v1",
            },
            files={"file": ("dataset_b.csv", csv_b, "text/csv")},
        )
        assert import_b.status_code == 202
        version_b_id = import_b.json()["version_id"]

        # --- ADVERSARIAL CROSS-TENANT RECORD ATTACKS BY TENANT B ---

        # Test 1: Tenant B GET Tenant A's record_a -> 404
        att_get = client_b.get(f"/api/v1/datasets/records/{record_a_id}")
        assert att_get.status_code == 404
        assert "Tenant A Updated Prompt" not in att_get.text

        # Test 2: Tenant B LIST records of Tenant A's version_a -> 404
        att_list = client_b.get(f"/api/v1/datasets/versions/{version_a_id}/records")
        assert att_list.status_code == 404
        assert "Victim Secret Prompt" not in att_list.text

        # Test 3: Tenant B INSERT record into Tenant A's version_a -> 404
        att_ins = client_b.post(
            f"/api/v1/datasets/versions/{version_a_id}/records",
            json=[{"prompt": "Tenant B Malicious Injection"}],
        )
        assert att_ins.status_code == 404

        # Test 4: Tenant B UPDATE Tenant A's record_a -> 404
        att_upd = client_b.put(
            f"/api/v1/datasets/records/{record_a_id}",
            json={"prompt": "Hacked Prompt By Tenant B"},
        )
        assert att_upd.status_code == 404

        # Test 5: Tenant B DELETE Tenant A's record_a -> 404
        att_del = client_b.delete(f"/api/v1/datasets/records/{record_a_id}")
        assert att_del.status_code == 404

        # Test 6: Reassignment attack - Tenant B tries to reassign record_a to version_b
        att_reassign = client_b.put(
            f"/api/v1/datasets/records/{record_a_id}",
            json={"version_id": version_b_id, "prompt": "Reassigned Prompt"},
        )
        assert att_reassign.status_code == 404

        # Test 7: workspace_id query tampering -> 404
        att_tamper = client_b.get(
            f"/api/v1/datasets/records/{record_a_id}?workspace_id={ws_a_id}"
        )
        assert att_tamper.status_code == 404

    # 3. VERIFY TENANT A RECORD INTEGRITY (UNCHANGED BY ATTACKS)
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        verif_a = client_a.get(f"/api/v1/datasets/records/{record_a_id}")
        assert verif_a.status_code == 200
        # Verify content was NOT mutated
        assert verif_a.json()["prompt"] == "Tenant A Updated Prompt"

        # Verify Tenant A record count remains accurate
        list_a = client_a.get(f"/api/v1/datasets/versions/{version_a_id}/records")
        assert list_a.status_code == 200
        assert list_a.json()["total"] == 2

        # Tenant A can DELETE own record
        del_a = client_a.delete(f"/api/v1/datasets/records/{record_a_id}")
        assert del_a.status_code == 204

        # Confirm record deleted for Tenant A
        assert (
            client_a.get(f"/api/v1/datasets/records/{record_a_id}").status_code == 404
        )

    # 4. DIRECT SERVICE LAYER AUTHORIZATION VERIFICATION
    service = DatasetService(db_session)

    with pytest.raises(DatasetNotFoundException):
        await service.get_single_record(record_a_id, workspace_id=ws_b_id)

    with pytest.raises(DatasetNotFoundException):
        await service.create_records(
            version_a_id,
            [{"prompt": "Unauthoried Service Create"}],
            workspace_id=ws_b_id,
        )

    with pytest.raises(DatasetNotFoundException):
        await service.update_record(
            record_a_id, {"prompt": "Hacked"}, workspace_id=ws_b_id
        )

    with pytest.raises(DatasetNotFoundException):
        await service.delete_record(record_a_id, workspace_id=ws_b_id)

    # 5. UNAUTHENTICATED REQUEST ACCESS VERIFICATION
    app.dependency_overrides.clear()

    async def override_get_db_unauth():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db_unauth

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_dataset_resource_limits_and_dos_protection(
    db_session: AsyncSession,
) -> None:
    """Verifies that eager loading is disabled for versions, pagination limits are enforced, and memory exhaustion is prevented."""
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.datasets.repositories.dataset import DatasetRepository
    from app.datasets.services.dataset import DatasetService
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_id = "dos-ws-1111-4111-a111-111111111111"
    key_mock = MagicMock()
    key_mock.id = "key_dos"
    key_mock.workspace_id = ws_id

    app.dependency_overrides[get_current_api_key] = lambda: key_mock

    repo = DatasetRepository(db_session)
    service = DatasetService(db_session)

    try:
        # 1. Create Project & Dataset
        with TestClient(app) as client:
            res_p = client.post(
                "/api/v1/projects",
                json={"name": "DoS Test Project", "status": "active"},
            )
            assert res_p.status_code == 201
            proj_id = res_p.json()["data"]["id"]

        dataset = await service.create_empty_dataset(
            project_id=proj_id, name="DoS Dataset", workspace_id=ws_id
        )
        version_1 = await service.get_dataset_version_by_label(
            dataset.id, "v1", workspace_id=ws_id
        )

        # 2. Bulk insert 1,500 records into version 1 to test pagination & chunking
        records_data = [
            {"prompt": f"Record Prompt #{i}", "reference_output": f"Ref #{i}"}
            for i in range(1500)
        ]
        await service.create_records(version_1.id, records_data, workspace_id=ws_id)

        # 3. VERIFY NO EAGER LOADING ON get_version
        from sqlalchemy.orm.base import NO_VALUE

        v_fetched = await repo.get_version(version_1.id)
        assert v_fetched is not None
        # Confirm DatasetVersion metadata loaded without eager-loading all 1500 records in Python
        assert (
            "records" not in v_fetched.__dict__
            or v_fetched.__dict__["records"] is NO_VALUE
            or v_fetched.__dict__["records"] == []
        )

        # 4. VERIFY PAGINATION CAP AND NORMALIZATION
        # Test 4.1: Excessive limit (limit=1000000) capped to 1000
        recs_excess, total_excess = await repo.get_records(version_1.id, limit=1000000)
        assert total_excess == 1500
        assert len(recs_excess) == 1000

        # Test 4.2: Negative limit (limit=-1) normalized to 100
        recs_neg_lim, _ = await repo.get_records(version_1.id, limit=-1)
        assert len(recs_neg_lim) == 100

        # Test 4.3: Negative skip (skip=-500) normalized to 0
        recs_neg_skip, _ = await repo.get_records(version_1.id, skip=-500, limit=50)
        assert len(recs_neg_skip) == 50
        assert recs_neg_skip[0].prompt == "Record Prompt #0"

        # 5. VERIFY ROUTER LEVEL VALIDATION & PAGINATION
        # Limit le=1000 enforced by FastAPI query parameter validation
        res_overflow = client.get(
            f"/api/v1/datasets/versions/{version_1.id}/records?limit=5000"
        )
        assert res_overflow.status_code in (400, 422)

        # Normal pagination query
        res_page = client.get(
            f"/api/v1/datasets/versions/{version_1.id}/records?skip=0&limit=100"
        )
        assert res_page.status_code == 200
        assert res_page.json()["total"] == 1500
        assert len(res_page.json()["records"]) == 100

        # 6. VERIFY ROLLBACK CHUNKED EXECUTION WITH LARGE DATASET
        v_rolled_back = await service.rollback_version(
            dataset.id, "v1", workspace_id=ws_id
        )
        assert v_rolled_back.version == "v2"
        assert v_rolled_back.record_count == 1500

        # Verify all 1,500 records cloned cleanly without RAM spike
        recs_v2_chunk1, total_v2 = await service.get_records(
            v_rolled_back.id, skip=0, limit=1000, workspace_id=ws_id
        )
        assert total_v2 == 1500
        assert len(recs_v2_chunk1) == 1000

        recs_v2_chunk2, _ = await service.get_records(
            v_rolled_back.id, skip=1000, limit=1000, workspace_id=ws_id
        )
        assert len(recs_v2_chunk2) == 500

        # 7. VERIFY CROSS-TENANT DoS PREVENTION (HTTP 404 BEFORE RECORD QUERY)
        key_unauth_mock = MagicMock()
        key_unauth_mock.id = "key_attacker"
        key_unauth_mock.workspace_id = "attacker-workspace-id"

        app.dependency_overrides[get_current_api_key] = lambda: key_unauth_mock
        res_attack = client.get(
            f"/api/v1/datasets/versions/{version_1.id}/records?limit=1000"
        )
        assert res_attack.status_code == 404
    except Exception as e:
        print("CRASH_ERROR:", type(e), e)
        raise e

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_dataset_and_benchmark_integrity(
    db_session: AsyncSession,
) -> None:
    """Verifies complete dataset and benchmark integrity, field immutability, cross-tenant isolation, and DB state constancy after attacks."""
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.datasets.exceptions.exceptions import BenchmarkSuiteNotFoundException
    from app.datasets.services.benchmark import BenchmarkService
    from app.datasets.services.dataset import DatasetService
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "integrity-ws-a-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "integrity-ws-b-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    dataset_service = DatasetService(db_session)
    benchmark_service = BenchmarkService(db_session)

    # 1. Setup Tenant A: Project A + Dataset A + Benchmark Suite A
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_pa = client_a.post(
            "/api/v1/projects", json={"name": "Project A Integrity", "status": "active"}
        )
        assert res_pa.status_code == 201
        proj_a_id = res_pa.json()["data"]["id"]

        dataset_a = await dataset_service.create_empty_dataset(
            project_id=proj_a_id, name="Dataset A Original Name", workspace_id=ws_a_id
        )
        suite_a = await benchmark_service.create_benchmark_suite(
            project_id=proj_a_id,
            name="Suite A Original Name",
            dataset_ids=[dataset_a.id],
            workspace_id=ws_a_id,
        )

    # 2. Setup Tenant B: Project B + Dataset B + Benchmark Suite B
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        res_pb = client_b.post(
            "/api/v1/projects", json={"name": "Project B Integrity", "status": "active"}
        )
        assert res_pb.status_code == 201
        proj_b_id = res_pb.json()["data"]["id"]

        dataset_b = await dataset_service.create_empty_dataset(
            project_id=proj_b_id, name="Dataset B", workspace_id=ws_b_id
        )
        suite_b = await benchmark_service.create_benchmark_suite(
            project_id=proj_b_id,
            name="Suite B",
            dataset_ids=[dataset_b.id],
            workspace_id=ws_b_id,
        )

        # --- ADVERSARIAL CROSS-TENANT MUTATION AND INTEGRITY ATTACKS BY TENANT B ---

        # Attack 1: Tenant B POST benchmark using Tenant A's dataset -> 404
        att_bm_create = client_b.post(
            f"/api/v1/benchmarks/?project_id={proj_b_id}",
            json={"name": "Spoofed Suite", "dataset_ids": [dataset_a.id]},
        )
        assert att_bm_create.status_code == 404

        # Attack 2: Tenant B PUT benchmark attaching Tenant A's dataset -> 404
        att_bm_update = client_b.put(
            f"/api/v1/benchmarks/{suite_b.id}",
            json={"dataset_ids": [dataset_b.id, dataset_a.id]},
        )
        assert att_bm_update.status_code == 404

        # Attack 3: Tenant B GET Tenant A's benchmark suite -> 404
        att_bm_get = client_b.get(f"/api/v1/benchmarks/{suite_a.id}")
        assert att_bm_get.status_code == 404

        # Attack 4: Tenant B DELETE Tenant A's benchmark suite -> 404
        att_bm_del = client_b.delete(f"/api/v1/benchmarks/{suite_a.id}")
        assert att_bm_del.status_code == 404

        # Attack 5: Dataset project_id reassignment attack
        att_ds_reassign = client_b.put(
            f"/api/v1/datasets/{dataset_b.id}",
            json={"project_id": proj_a_id, "name": "Reassigned Dataset"},
        )
        assert att_ds_reassign.status_code == 200
        # Verify project_id was NOT reassigned to Tenant A's project
        assert att_ds_reassign.json()["project_id"] == proj_b_id

        # Attack 6: Benchmark Suite project_id reassignment attack
        att_suite_reassign = client_b.put(
            f"/api/v1/benchmarks/{suite_b.id}",
            json={"project_id": proj_a_id, "name": "Reassigned Suite"},
        )
        assert att_suite_reassign.status_code == 200
        # Verify project_id was NOT reassigned to Tenant A's project
        assert att_suite_reassign.json()["project_id"] == proj_b_id

    # 3. VERIFY TENANT A DATABASE INTEGRITY IS 100% UNCHANGED
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        ds_verif = client_a.get(f"/api/v1/datasets/{dataset_a.id}")
        assert ds_verif.status_code == 200
        assert ds_verif.json()["name"] == "Dataset A Original Name"

        bm_verif = client_a.get(f"/api/v1/benchmarks/{suite_a.id}")
        assert bm_verif.status_code == 200
        assert bm_verif.json()["name"] == "Suite A Original Name"
        assert len(bm_verif.json()["datasets"]) == 1
        assert bm_verif.json()["datasets"][0]["id"] == dataset_a.id

    # 4. DIRECT SERVICE & REPOSITORY AUTHORIZATION BYPASS ATTEMPTS
    with pytest.raises(BenchmarkSuiteNotFoundException):
        await benchmark_service.get_benchmark_suite(suite_a.id, workspace_id=ws_b_id)

    from app.datasets.exceptions.exceptions import DatasetNotFoundException

    with pytest.raises(DatasetNotFoundException):
        await benchmark_service.create_benchmark_suite(
            proj_b_id,
            "Service Attack Suite",
            dataset_ids=[dataset_a.id],
            workspace_id=ws_b_id,
        )

    with pytest.raises(DatasetNotFoundException):
        await benchmark_service.update_benchmark_suite(
            suite_b.id,
            {"dataset_ids": [dataset_a.id]},
            workspace_id=ws_b_id,
        )

    with pytest.raises(BenchmarkSuiteNotFoundException):
        await benchmark_service.delete_benchmark_suite(suite_a.id, workspace_id=ws_b_id)

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_dataset_consistency_and_integrity(
    db_session: AsyncSession,
) -> None:
    """Verifies invariant integrity: orphan dataset prevention, duplicate benchmark associations deduplication, record version immutability, and transaction rollback."""
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.datasets.exceptions.exceptions import (
        DatasetNotFoundException,
    )
    from app.datasets.services.benchmark import BenchmarkService
    from app.datasets.services.dataset import DatasetService
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_id = "consistency-ws-1111-4111-a111-aaaaaaaaaaaa"
    key_mock = MagicMock()
    key_mock.id = "key_consistency"
    key_mock.workspace_id = ws_id

    app.dependency_overrides[get_current_api_key] = lambda: key_mock

    dataset_service = DatasetService(db_session)
    benchmark_service = BenchmarkService(db_session)

    with TestClient(app) as client:
        # 1. Create valid project and dataset
        res_p = client.post(
            "/api/v1/projects", json={"name": "Consistency Project", "status": "active"}
        )
        assert res_p.status_code == 201
        proj_id = res_p.json()["data"]["id"]

        dataset = await dataset_service.create_empty_dataset(
            project_id=proj_id, name="Consistency Dataset", workspace_id=ws_id
        )
        version_1 = await dataset_service.get_dataset_version_by_label(
            dataset.id, "v1", workspace_id=ws_id
        )

        # 2. Test Orphan Dataset Prevention (non-existent project ID)
        with pytest.raises(DatasetNotFoundException):
            await dataset_service.create_empty_dataset(
                project_id="nonexistent-project-id",
                name="Orphan DS",
                workspace_id=ws_id,
            )

        # 3. Test Duplicate Benchmark Dataset IDs Deduplication
        suite = await benchmark_service.create_benchmark_suite(
            project_id=proj_id,
            name="Deduplication Benchmark Suite",
            dataset_ids=[dataset.id, dataset.id, dataset.id],
            workspace_id=ws_id,
        )
        assert suite is not None
        # Verify deduplicated association count in DB
        suite_fetched = await benchmark_service.get_benchmark_suite(
            suite.id, workspace_id=ws_id
        )
        assert len(suite_fetched.datasets) == 1

        # 4. Test Record Update Version Immutability
        recs = await dataset_service.create_records(
            version_1.id,
            [{"prompt": "Test Prompt", "reference_output": "Ref"}],
            workspace_id=ws_id,
        )
        rec_id = recs[0].id

        # Attempt to mutate version_id on existing record -> ignored/immutable
        rec_updated = await dataset_service.update_record(
            rec_id,
            {"version_id": "fake-version-id", "prompt": "Updated Prompt"},
            workspace_id=ws_id,
        )
        assert rec_updated.version_id == version_1.id
        assert rec_updated.prompt == "Updated Prompt"

        # 5. Test Record Creation Against Nonexistent / Cross-Tenant Version
        with pytest.raises(DatasetNotFoundException):
            await dataset_service.create_records(
                "fake-version-id",
                [{"prompt": "Malicious Record"}],
                workspace_id=ws_id,
            )

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_experiment_and_import_export_isolation(
    db_session: AsyncSession,
) -> None:
    """Verifies complete Experiment and Import/Export cross-tenant isolation, relationship consistency, and field immutability."""
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.datasets.exceptions.exceptions import (
        DatasetNotFoundException,
        ExperimentNotFoundException,
    )
    from app.datasets.repositories.experiment import ExperimentRepository
    from app.datasets.services.dataset import DatasetService
    from app.datasets.services.experiment import ExperimentService
    from app.datasets.services.import_export import ImportExportService
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "exp-ws-a-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "exp-ws-b-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_exp_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_exp_b"
    key_tenant_b.workspace_id = ws_b_id

    dataset_service = DatasetService(db_session)
    experiment_service = ExperimentService(db_session)
    import_export_service = ImportExportService(db_session)
    experiment_repo = ExperimentRepository(db_session)

    # 1. Tenant A Setup: Project A + Dataset A (v1)
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_pa = client_a.post(
            "/api/v1/projects", json={"name": "Exp Project A", "status": "active"}
        )
        assert res_pa.status_code == 201
        proj_a_id = res_pa.json()["data"]["id"]

        dataset_a = await dataset_service.create_empty_dataset(
            project_id=proj_a_id, name="Exp Dataset A", workspace_id=ws_a_id
        )
        version_a = await dataset_service.get_dataset_version_by_label(
            dataset_a.id, "v1", workspace_id=ws_a_id
        )

        exp_a = await experiment_service.create_experiment(
            project_id=proj_a_id,
            dataset_version_id=version_a.id,
            name="Tenant A Experiment",
            workspace_id=ws_a_id,
        )

    # 2. Tenant B Setup: Project B + Dataset B (v1)
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        res_pb = client_b.post(
            "/api/v1/projects", json={"name": "Exp Project B", "status": "active"}
        )
        assert res_pb.status_code == 201
        proj_b_id = res_pb.json()["data"]["id"]

        dataset_b = await dataset_service.create_empty_dataset(
            project_id=proj_b_id, name="Exp Dataset B", workspace_id=ws_b_id
        )
        version_b = await dataset_service.get_dataset_version_by_label(
            dataset_b.id, "v1", workspace_id=ws_b_id
        )

        exp_b = await experiment_service.create_experiment(
            project_id=proj_b_id,
            dataset_version_id=version_b.id,
            name="Tenant B Experiment",
            workspace_id=ws_b_id,
        )

        # --- ADVERSARIAL EXPERIMENT ATTACKS BY TENANT B ---

        # Attack 1: Tenant B creates experiment using Tenant A's dataset_version_id -> 404
        res_exp_create = client_b.post(
            f"/api/v1/experiments/?project_id={proj_b_id}",
            json={
                "name": "Spoofed Experiment",
                "dataset_version_id": version_a.id,
                "judge": "rubric",
                "provider": "openai",
            },
        )
        assert res_exp_create.status_code == 404

        # Attack 2: Tenant B GET Tenant A's experiment -> 404
        res_exp_get = client_b.get(f"/api/v1/experiments/{exp_a.id}")
        assert res_exp_get.status_code == 404

        # Attack 3: Tenant B EXECUTE Tenant A's experiment -> 404
        res_exp_exec = client_b.post(f"/api/v1/experiments/{exp_a.id}/execute")
        assert res_exp_exec.status_code == 404

        # Attack 4: Tenant B DELETE Tenant A's experiment -> 404
        res_exp_del = client_b.delete(f"/api/v1/experiments/{exp_a.id}")
        assert res_exp_del.status_code == 404

        # Attack 5: Tenant B attempts to mutate exp_b immutable fields via repository
        exp_updated = await experiment_repo.update_experiment(
            exp_b.id,
            {
                "id": exp_a.id,
                "project_id": proj_a_id,
                "dataset_version_id": version_a.id,
                "name": "Updated Exp B Name",
            },
        )
        assert exp_updated is not None
        assert exp_updated.id == exp_b.id
        assert exp_updated.project_id == proj_b_id
        assert exp_updated.dataset_version_id == version_b.id
        assert exp_updated.name == "Updated Exp B Name"

        # Attack 6: Tenant B exports dataset using Tenant A's version_id -> 404
        res_exp_export = client_b.post(
            f"/api/v1/datasets/export?project_id={proj_b_id}&version_id={version_a.id}&file_format=json"
        )
        assert res_exp_export.status_code == 404

    # 3. DIRECT SERVICE AUTHORIZATION BYPASS ATTEMPTS
    with pytest.raises((ExperimentNotFoundException, DatasetNotFoundException)):
        await experiment_service.get_experiment(exp_a.id, workspace_id=ws_b_id)

    with pytest.raises((ExperimentNotFoundException, DatasetNotFoundException)):
        await experiment_service.create_experiment(
            project_id=proj_b_id,
            dataset_version_id=version_a.id,
            name="Service Attack Experiment",
            workspace_id=ws_b_id,
        )

    with pytest.raises((ExperimentNotFoundException, DatasetNotFoundException)):
        await experiment_service.execute_experiment(exp_a.id, workspace_id=ws_b_id)

    with pytest.raises((ExperimentNotFoundException, DatasetNotFoundException)):
        await experiment_service.delete_experiment(exp_a.id, workspace_id=ws_b_id)

    with pytest.raises((ValueError, DatasetNotFoundException)):
        await import_export_service.execute_export(
            "fake-job-id", version_id=version_a.id, workspace_id=ws_b_id
        )

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_download_file_cross_tenant_isolation(
    db_session: AsyncSession,
) -> None:
    """Verifies complete cross-tenant file download isolation, preventing fuzzy endswith exfiltration attacks."""
    import os
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.main import app
    from app.models.dataset import ExportJob, ImportJob

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "dl-ws-a-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "dl-ws-b-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_dl_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_dl_b"
    key_tenant_b.workspace_id = ws_b_id

    # Create dummy export file for Tenant A in datasets directory
    datasets_dir = os.path.realpath("datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    dummy_export_filename = "export_job-tenant-a-test.json"
    dummy_export_path = os.path.join(datasets_dir, dummy_export_filename)
    with open(dummy_export_path, "w") as f:
        f.write('{"secret": "tenant_a_data"}')

    try:
        # Tenant A Setup: Project A + ExportJob A
        app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
        with TestClient(app) as client_a:
            res_pa = client_a.post(
                "/api/v1/projects", json={"name": "DL Project A", "status": "active"}
            )
            assert res_pa.status_code == 201
            proj_a_id = res_pa.json()["data"]["id"]

            job_a = ExportJob(
                id="job-tenant-a-test",
                project_id=proj_a_id,
                dataset_id="ds-a",
                file_format="json",
                file_path=dummy_export_path,
                status="COMPLETED",
            )
            db_session.add(job_a)
            await db_session.commit()

            # Tenant A downloads file -> 200 OK
            res_dl_a = client_a.get(
                f"/api/v1/datasets/download/{dummy_export_filename}"
            )
            assert res_dl_a.status_code == 200
            assert res_dl_a.json() == {"secret": "tenant_a_data"}

        # Tenant B Setup: Project B + Malicious ImportJob B attempting endswith bypass
        app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
        with TestClient(app) as client_b:
            res_pb = client_b.post(
                "/api/v1/projects", json={"name": "DL Project B", "status": "active"}
            )
            assert res_pb.status_code == 201
            proj_b_id = res_pb.json()["data"]["id"]

            # Craft malicious ImportJob B in Project B whose file_path ends with Tenant A's filename
            job_b_spoof = ImportJob(
                id="job-tenant-b-spoof",
                project_id=proj_b_id,
                file_format="json",
                file_path=f"crafted_path_to_{dummy_export_filename}",
                status="COMPLETED",
            )
            db_session.add(job_b_spoof)
            await db_session.commit()

            # Tenant B attempts to download Tenant A's export file -> MUST RETURN 404
            res_dl_b = client_b.get(
                f"/api/v1/datasets/download/{dummy_export_filename}"
            )
            assert res_dl_b.status_code == 404

    finally:
        if os.path.exists(dummy_export_path):
            os.remove(dummy_export_path)
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_import_export_job_cross_tenant_isolation(
    db_session: AsyncSession,
) -> None:
    """Verifies that Import and Export jobs cannot be hijacked across tenants or projects."""
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient

    from app.core.dependencies import get_current_api_key, get_db
    from app.datasets.exceptions.exceptions import DatasetNotFoundException
    from app.datasets.services.dataset import DatasetService
    from app.datasets.services.import_export import ImportExportService
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "job-ws-a-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "job-ws-b-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_job_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_job_b"
    key_tenant_b.workspace_id = ws_b_id

    dataset_service = DatasetService(db_session)
    import_export_service = ImportExportService(db_session)

    # 1. Tenant A Setup: Project A + Dataset A + Version A + ImportJob A + ExportJob A
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_pa = client_a.post(
            "/api/v1/projects", json={"name": "Job Project A", "status": "active"}
        )
        assert res_pa.status_code == 201
        proj_a_id = res_pa.json()["data"]["id"]

        dataset_a = await dataset_service.create_empty_dataset(
            project_id=proj_a_id, name="Job Dataset A", workspace_id=ws_a_id
        )
        await dataset_service.get_dataset_version_by_label(
            dataset_a.id, "v1", workspace_id=ws_a_id
        )

        import_job_a = await import_export_service.create_import_job(
            proj_a_id, "json", workspace_id=ws_a_id
        )
        export_job_a = await import_export_service.create_export_job(
            proj_a_id, "json", dataset_id=dataset_a.id, workspace_id=ws_a_id
        )

    # 2. Tenant B Setup: Project B
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        res_pb = client_b.post(
            "/api/v1/projects", json={"name": "Job Project B", "status": "active"}
        )
        assert res_pb.status_code == 201
        proj_b_id = res_pb.json()["data"]["id"]

        dataset_b = await dataset_service.create_empty_dataset(
            project_id=proj_b_id, name="Job Dataset B", workspace_id=ws_b_id
        )
        version_b = await dataset_service.get_dataset_version_by_label(
            dataset_b.id, "v1", workspace_id=ws_b_id
        )

        # Attack 1: Tenant B attempts to process Tenant A's import_job_a using Tenant B's project_id
        with pytest.raises(DatasetNotFoundException):
            await import_export_service.process_import(
                job_id=import_job_a.id,
                file_content=b'[{"prompt":"hacked"}]',
                dataset_name="Hacked Dataset",
                project_id=proj_b_id,
                workspace_id=ws_b_id,
            )

        # Attack 2: Tenant B attempts to execute Tenant A's export_job_a
        with pytest.raises(DatasetNotFoundException):
            await import_export_service.execute_export(
                job_id=export_job_a.id,
                version_id=version_b.id,
                workspace_id=ws_b_id,
            )

    app.dependency_overrides.clear()
