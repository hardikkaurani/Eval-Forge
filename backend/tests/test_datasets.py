import json
import pytest
from app.datasets.parsers.parsers import DatasetParser
from app.datasets.validators.validators import DatasetValidator
from app.datasets.exceptions.exceptions import DatasetValidationException, InvalidDatasetFormatException


def test_validator_with_valid_records():
    records = [
        {"prompt": "Translate 'hello'", "reference_output": "bonjour", "expected_score": 1.0},
        {"prompt": "Write a poem", "ground_truth": "Roses are red", "tags": ["creative"]},
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
    resp = client.post(f"/api/v1/datasets/?project_id={project_id}", json=dataset_payload)
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
        data={"project_id": project_id, "dataset_name": "Diff Dataset", "version_label": "v1"},
        files={"file": ("dataset_v1.csv", csv_v1, "text/csv")}
    )
    assert resp.status_code == 202
    dataset_id = resp.json()["dataset_id"]

    # Version 2 (v2): Prompt A deleted, Prompt B modified, Prompt C added
    csv_v2 = "prompt,reference_output\nPrompt B,Ref B Modified\nPrompt C,Ref C\n"
    resp = client.post(
        "/api/v1/datasets/import",
        data={"project_id": project_id, "dataset_name": "Diff Dataset", "existing_dataset_id": dataset_id, "version_label": "v2"},
        files={"file": ("dataset_v2.csv", csv_v2, "text/csv")}
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
    resp = client.post(f"/api/v1/benchmarks/?project_id={project_id}", json=suite_payload)
    assert resp.status_code == 201
    suite = resp.json()
    assert suite["name"] == "E2E Benchmark Suite"
    assert len(suite["datasets"]) == 1
    suite_id = suite["id"]

    # Update suite
    resp = client.put(f"/api/v1/benchmarks/{suite_id}", json={"name": "Updated Benchmark Suite"})
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
        data={"project_id": project_id, "dataset_name": "Experiment Dataset", "version_label": "v1"},
        files={"file": ("dataset.csv", csv_data, "text/csv")}
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
    resp = client.post(f"/api/v1/experiments/?project_id={project_id}", json=exp_payload)
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
