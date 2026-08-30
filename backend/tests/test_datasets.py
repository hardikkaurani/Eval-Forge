import json

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

    # 1. Valid file download
    test_file_path = os.path.join("datasets", "test_download.csv")
    with open(test_file_path, "w") as f:
        f.write("prompt,output\ntest,test\n")

    try:
        resp = client.get("/api/v1/datasets/download/test_download.csv")
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
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


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
