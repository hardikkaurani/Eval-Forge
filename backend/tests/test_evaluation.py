from fastapi.testclient import TestClient


def test_evaluation_metadata_endpoints(client: TestClient) -> None:
    """Verifies retrieval of registered providers, judges, and built-in rubrics metadata."""
    # 1. Retrieve Providers list
    response = client.get("/api/v1/evaluations/metadata/providers")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert len(res_data["data"]) >= 6
    provider_keys = [p["key"] for p in res_data["data"]]
    assert "openai" in provider_keys
    assert "gemini" in provider_keys
    assert "claude" in provider_keys

    # 2. Retrieve Judges list
    response = client.get("/api/v1/evaluations/metadata/judges")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert len(res_data["data"]) >= 4
    judge_keys = [j["key"] for j in res_data["data"]]
    assert "geval" in judge_keys
    assert "pairwise" in judge_keys
    assert "rubric" in judge_keys
    assert "reference" in judge_keys

    # 3. Retrieve Rubrics list
    response = client.get("/api/v1/evaluations/metadata/rubrics")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert len(res_data["data"]) >= 10
    rubric_keys = [r["key"] for r in res_data["data"]]
    assert "correctness" in rubric_keys
    assert "faithfulness" in rubric_keys
    assert "coherence" in rubric_keys


def test_evaluation_crud_flow(client: TestClient) -> None:
    """Verifies creation, listing, retrieval, and deletion of evaluation configurations."""
    # 1. Create a Project first
    project_payload = {
        "name": "Evaluation Flow Project",
        "description": "Project supporting evaluation crud flow tests.",
    }
    project_response = client.post("/api/v1/projects", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 2. Create Evaluation Configuration
    eval_payload = {
        "name": "LLM Response Correctness Eval",
        "description": "Runs factual checks against gold standard answers.",
        "project_id": project_id,
    }
    create_response = client.post("/api/v1/evaluations", json=eval_payload)
    assert create_response.status_code == 201
    create_res = create_response.json()
    assert create_res["success"] is True

    evaluation = create_res["data"]
    evaluation_id = evaluation["id"]
    assert evaluation["name"] == eval_payload["name"]
    assert evaluation["description"] == eval_payload["description"]
    assert evaluation["project_id"] == project_id

    # 3. List Evaluations for the Project
    list_response = client.get(
        f"/api/v1/evaluations?project_id={project_id}&page=1&page_size=10"
    )
    assert list_response.status_code == 200
    list_res = list_response.json()
    assert list_res["success"] is True
    assert len(list_res["data"]["items"]) >= 1
    assert list_res["data"]["items"][0]["id"] == evaluation_id
    assert list_res["data"]["meta"]["total_items"] == 1

    # 4. Get Evaluation Details
    get_response = client.get(f"/api/v1/evaluations/{evaluation_id}")
    assert get_response.status_code == 200
    get_res = get_response.json()
    assert get_res["success"] is True
    assert get_res["data"]["id"] == evaluation_id

    # 5. Delete Evaluation (Soft Delete)
    delete_response = client.delete(f"/api/v1/evaluations/{evaluation_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["success"] is True

    # 6. Verify soft-deleted item is not found
    get_deleted = client.get(f"/api/v1/evaluations/{evaluation_id}")
    assert get_deleted.status_code == 404


def test_batch_evaluation_execution(client: TestClient) -> None:
    """Verifies batch execution runs through validation, prompt construction, mock generation, and DB logs."""
    # 1. Create a Project
    project_payload = {
        "name": "Batch Eval Project",
        "description": "Project for batch evaluation runs.",
    }
    project_response = client.post("/api/v1/projects", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 2. Trigger Batch Rubric-scoring evaluation (Mocked provider keys auto-trigger test output generation)
    batch_payload = {
        "project_id": project_id,
        "evaluation_name": "Test Batch Run",
        "evaluation_description": "Validates single rubric scoring flow.",
        "judge": "rubric",
        "provider": "openai",
        "test_cases": [
            {
                "input_prompt": "What is the capital of France?",
                "model_output": "The capital is Paris.",
                "reference": "Paris",
            },
            {
                "input_prompt": "Who wrote Romeo and Juliet?",
                "model_output": "It was written by William Shakespeare.",
                "reference": "William Shakespeare",
            },
        ],
        "configuration": {"temperature": 0.0, "threshold": 0.8, "timeout": 15.0},
    }

    response = client.post("/api/v1/evaluations/batch", json=batch_payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True

    run = res_data["data"]
    assert run["status"] == "COMPLETED"
    assert run["judge"] == "rubric"
    assert run["provider"] == "openai"
    assert run["total_cases"] == 2
    assert run["completed_cases"] == 2
    assert run["aggregate_score"] is not None
    assert run["started_at"] is not None
    assert run["completed_at"] is not None


def test_batch_evaluation_validation_errors(client: TestClient) -> None:
    """Verifies that invalid batch evaluation requests are caught by validators and raise proper exceptions."""
    # Create a valid project first
    project_payload = {
        "name": "Validation Errors Project",
        "description": "Project for checking validation errors.",
    }
    project_response = client.post("/api/v1/projects", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 1. Invalid provider
    payload = {
        "project_id": project_id,
        "evaluation_name": "Invalid Provider Run",
        "judge": "rubric",
        "provider": "unsupported-fake-provider",
        "test_cases": [{"input_prompt": "A", "model_output": "B"}],
    }
    response = client.post("/api/v1/evaluations/batch", json=payload)
    assert response.status_code == 400
    assert response.json()["data"]["code"] == "UnsupportedProviderException"

    # 2. Invalid judge
    payload = {
        "project_id": project_id,
        "evaluation_name": "Invalid Judge Run",
        "judge": "unsupported-fake-judge",
        "provider": "openai",
        "test_cases": [{"input_prompt": "A", "model_output": "B"}],
    }
    response = client.post("/api/v1/evaluations/batch", json=payload)
    assert response.status_code == 400
    assert response.json()["data"]["code"] == "UnsupportedJudgeException"

    # 3. Invalid Configuration (temperature too high)
    payload = {
        "project_id": project_id,
        "evaluation_name": "Invalid Config Run",
        "judge": "rubric",
        "provider": "openai",
        "test_cases": [{"input_prompt": "A", "model_output": "B"}],
        "configuration": {"temperature": 3.0},  # Invalid range (> 2.0)
    }
    response = client.post("/api/v1/evaluations/batch", json=payload)
    assert response.status_code == 400
    assert response.json()["data"]["code"] == "InvalidConfigException"
