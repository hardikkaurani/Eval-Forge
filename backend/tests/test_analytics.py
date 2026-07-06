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
    run_id = batch_response.json()["data"]["id"]

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
        "filters": {}
    }
    report_response = client.post(
        f"/api/v1/reports/generate?project_id={project_id}", json=report_payload
    )
    assert report_response.status_code == 202
    report_data = report_response.json()
    assert report_data["success"] is True
    report_id = report_data["data"]["id"]
    assert report_data["data"]["name"] == "Quarterly Evaluation Report"
    assert report_data["data"]["status"] == "COMPLETED" # Completed synchronously in simulator
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
        "filters": {}
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
                {"id": "w2", "type": "time_series", "x": 4, "y": 0, "w": 8, "h": 4}
            ]
        }
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
