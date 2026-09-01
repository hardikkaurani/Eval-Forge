import os

from fastapi.testclient import TestClient


def test_analytics_and_reporting_lifecycle(client: TestClient) -> None:
    # 1. Create a Project
    project_payload = {
        "name": "Analytics Testing Project",
        "description": "Project designed to validate analytics, trends, and reports.",
    }
    project_response = client.post("/api/v1/projects", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 2. Run a batch evaluation to generate raw evaluation data
    batch_payload = {
        "project_id": project_id,
        "evaluation_name": "Test Run for Analytics",
        "evaluation_description": "Generates data for statistics aggregation.",
        "judge": "rubric",
        "provider": "openai",
        "test_cases": [
            {
                "input_prompt": "Prompt 1",
                "model_output": "Output 1",
                "reference": "Ref 1",
            },
            {
                "input_prompt": "Prompt 2",
                "model_output": "Output 2",
                "reference": "Ref 2",
            },
        ],
        "configuration": {"temperature": 0.0},
    }
    batch_response = client.post("/api/v1/evaluations/batch", json=batch_payload)
    assert batch_response.status_code == 201
    assert batch_response.json()["data"]["id"] is not None

    # 3. Manually trigger snapshot aggregation
    snapshot_response = client.post(
        f"/api/v1/analytics/snapshots?project_id={project_id}&scope=project"
    )
    assert snapshot_response.status_code == 201
    snap_data = snapshot_response.json()
    assert snap_data["success"] is True
    assert "snapshot_id" in snap_data["data"]

    # 4. Fetch Project Analytics Overview
    overview_response = client.get(f"/api/v1/analytics?project_id={project_id}")
    assert overview_response.status_code == 200
    overview_data = overview_response.json()
    assert overview_data["success"] is True
    data = overview_data["data"]
    assert data["total_evaluations"] == 2
    assert "avg_score" in data
    assert "success_rate" in data
    assert "avg_latency_ms" in data
    assert len(data["daily_eval_volume"]) == 7

    # 5. Fetch Trends
    trends_response = client.get(
        f"/api/v1/trends?project_id={project_id}&metric_name=avg_score&granularity=daily"
    )
    assert trends_response.status_code == 200
    trends_data = trends_response.json()
    assert trends_data["success"] is True
    assert trends_data["data"]["metric_name"] == "avg_score"
    assert "trends" in trends_data["data"]

    # 6. Fetch Leaderboard
    leaderboard_response = client.get(
        f"/api/v1/leaderboards?project_id={project_id}&entity_type=model"
    )
    assert leaderboard_response.status_code == 200
    leaderboard_data = leaderboard_response.json()
    assert leaderboard_data["success"] is True
    assert leaderboard_data["data"]["entity_type"] == "model"

    # 7. Fetch Auto-generated Insights
    insights_response = client.get(f"/api/v1/insights?project_id={project_id}")
    assert insights_response.status_code == 200
    insights_data = insights_response.json()
    assert insights_data["success"] is True
    assert isinstance(insights_data["data"], list)

    # 8. Generate PDF Report
    report_payload = {
        "name": "Quarterly Evaluation Report",
        "type": "PDF",
        "filters": {},
    }
    report_response = client.post(
        f"/api/v1/reports/generate?project_id={project_id}", json=report_payload
    )
    assert report_response.status_code == 202
    report_data = report_response.json()
    assert report_data["success"] is True
    report_id = report_data["data"]["id"]
    assert report_data["data"]["name"] == "Quarterly Evaluation Report"
    assert (
        report_data["data"]["status"] == "COMPLETED"
    )  # Completed synchronously in simulator
    assert report_data["data"]["file_path"] is not None

    # Verify report PDF actually got generated on disk
    file_path = report_data["data"]["file_path"]
    assert os.path.exists(file_path)

    # 9. Download Compiled Report
    download_response = client.get(f"/api/v1/reports/{report_id}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"

    # Clean up generated test report file
    if os.path.exists(file_path):
        os.remove(file_path)

    # 10. Generate CSV Report
    report_payload_csv = {
        "name": "Evaluations Export CSV",
        "type": "CSV",
        "filters": {},
    }
    csv_response = client.post(
        f"/api/v1/reports/generate?project_id={project_id}", json=report_payload_csv
    )
    assert csv_response.status_code == 202
    csv_data = csv_response.json()
    assert csv_data["success"] is True
    csv_report_id = csv_data["data"]["id"]
    csv_file_path = csv_data["data"]["file_path"]
    assert os.path.exists(csv_file_path)

    # Download CSV Report
    download_csv_response = client.get(f"/api/v1/reports/{csv_report_id}/download")
    assert download_csv_response.status_code == 200
    assert "text/csv" in download_csv_response.headers["content-type"]

    # Clean up generated CSV file
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)

    # 11. Save and list dashboard layout snapshots
    dashboard_payload = {
        "name": "Executive QA Dashboard",
        "layout": {
            "cols": 12,
            "widgets": [
                {"id": "w1", "type": "metric_card", "x": 0, "y": 0, "w": 4, "h": 2},
                {"id": "w2", "type": "time_series", "x": 4, "y": 0, "w": 8, "h": 4},
            ],
        },
    }
    dash_response = client.post(
        f"/api/v1/analytics/dashboards?project_id={project_id}", json=dashboard_payload
    )
    assert dash_response.status_code == 201
    dash_data = dash_response.json()
    assert dash_data["success"] is True
    assert dash_data["data"]["name"] == "Executive QA Dashboard"

    list_dash = client.get(f"/api/v1/analytics/dashboards?project_id={project_id}")
    assert list_dash.status_code == 200
    list_dash_data = list_dash.json()
    assert list_dash_data["success"] is True
    assert len(list_dash_data["data"]) == 1
    assert list_dash_data["data"][0]["name"] == "Executive QA Dashboard"

    # 12. Fetch System Observability metrics
    system_response = client.get("/api/v1/system/metrics")
    assert system_response.status_code == 200
    system_data = system_response.json()
    assert system_data["success"] is True
    assert "cpu_usage_percent" in system_data["data"]
    assert "memory_usage_bytes" in system_data["data"]
    assert "redis_health" in system_data["data"]


def test_analytics_tenant_isolation(db_session) -> None:
    """Verifies that Analytics, Reports, Dashboards, Leaderboards, and Trends enforce strict workspace isolation."""
    from unittest.mock import MagicMock

    from app.core.dependencies import get_current_api_key, get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    ws_a_id = "ana-ws-a-1111-4111-a111-aaaaaaaaaaaa"
    ws_b_id = "ana-ws-b-2222-4222-b222-bbbbbbbbbbbb"

    key_tenant_a = MagicMock()
    key_tenant_a.id = "key_tenant_a"
    key_tenant_a.workspace_id = ws_a_id

    key_tenant_b = MagicMock()
    key_tenant_b.id = "key_tenant_b"
    key_tenant_b.workspace_id = ws_b_id

    # 1. Tenant A creates Project A and Report A
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_a
    with TestClient(app) as client_a:
        res_proj_a = client_a.post(
            "/api/v1/projects", json={"name": "Analytics Project A"}
        )
        assert res_proj_a.status_code == 201
        proj_a_id = res_proj_a.json()["data"]["id"]

        report_res = client_a.post(
            f"/api/v1/reports/generate?project_id={proj_a_id}",
            json={"name": "Secret Report A", "type": "PDF", "filters": {}},
        )
        assert report_res.status_code == 202
        report_a_id = report_res.json()["data"]["id"]

        # Tenant A can view overview
        overview_a = client_a.get(f"/api/v1/analytics?project_id={proj_a_id}")
        assert overview_a.status_code == 200

    # 2. Tenant B attempts cross-tenant analytics access
    app.dependency_overrides[get_current_api_key] = lambda: key_tenant_b
    with TestClient(app) as client_b:
        # Overview -> 404
        assert (
            client_b.get(f"/api/v1/analytics?project_id={proj_a_id}").status_code == 404
        )

        # Reports list -> 404
        assert (
            client_b.get(f"/api/v1/reports?project_id={proj_a_id}").status_code == 404
        )

        # Download report -> 404
        assert (
            client_b.get(f"/api/v1/reports/{report_a_id}/download").status_code == 404
        )

        # Trends -> 404
        assert client_b.get(f"/api/v1/trends?project_id={proj_a_id}").status_code == 404

        # Leaderboards -> 404
        assert (
            client_b.get(f"/api/v1/leaderboards?project_id={proj_a_id}").status_code
            == 404
        )

        # Insights -> 404
        assert (
            client_b.get(f"/api/v1/insights?project_id={proj_a_id}").status_code == 404
        )

        # Snapshots -> 404
        assert (
            client_b.post(
                f"/api/v1/analytics/snapshots?project_id={proj_a_id}"
            ).status_code
            == 404
        )

        # Distribution -> 404
        assert (
            client_b.get(
                f"/api/v1/analytics/distribution?project_id={proj_a_id}"
            ).status_code
            == 404
        )

        # Comparison -> 404
        assert (
            client_b.get(
                f"/api/v1/analytics/comparison?project_id={proj_a_id}"
            ).status_code
            == 404
        )

        # Radar -> 404
        assert (
            client_b.get(f"/api/v1/analytics/radar?project_id={proj_a_id}").status_code
            == 404
        )

        # Exports CSV -> 404
        assert (
            client_b.get(
                f"/api/v1/analytics/exports/csv?project_id={proj_a_id}"
            ).status_code
            == 404
        )

        # Exports JSON -> 404
        assert (
            client_b.get(
                f"/api/v1/analytics/exports/json?project_id={proj_a_id}"
            ).status_code
            == 404
        )

    app.dependency_overrides.clear()


def test_phase7_analytics_and_export_features(client: TestClient) -> None:
    # 1. Create Project
    res = client.post("/api/v1/projects", json={"name": "Phase 7 Analytics Project"})
    assert res.status_code == 201
    proj_id = res.json()["data"]["id"]

    # 2. Run Batch Evaluation
    batch_res = client.post(
        "/api/v1/evaluations/batch",
        json={
            "project_id": proj_id,
            "evaluation_name": "Phase 7 Eval Run",
            "judge": "rubric",
            "provider": "openai",
            "test_cases": [
                {
                    "input_prompt": "Explain Quantum Computing",
                    "model_output": "Quantum computing uses qubits...",
                    "reference": "Qubits allow superposition",
                }
            ],
        },
    )
    assert batch_res.status_code == 201

    # 3. Test Score Distribution
    dist_res = client.get(f"/api/v1/analytics/distribution?project_id={proj_id}")
    assert dist_res.status_code == 200
    assert len(dist_res.json()["data"]) == 5

    # 4. Test Run Comparison
    comp_res = client.get(f"/api/v1/analytics/comparison?project_id={proj_id}")
    assert comp_res.status_code == 200
    assert len(comp_res.json()["data"]) >= 1

    # 5. Test Radar Metrics
    radar_res = client.get(f"/api/v1/analytics/radar?project_id={proj_id}")
    assert radar_res.status_code == 200
    assert "accuracy" in radar_res.json()["data"]

    # 6. Test Export CSV
    csv_res = client.get(f"/api/v1/analytics/exports/csv?project_id={proj_id}")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]

    # 7. Test Export JSON
    json_res = client.get(f"/api/v1/analytics/exports/json?project_id={proj_id}")
    assert json_res.status_code == 200
    assert isinstance(json_res.json()["data"], list)
