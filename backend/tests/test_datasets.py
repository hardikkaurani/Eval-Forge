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
