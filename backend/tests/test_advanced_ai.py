from fastapi.testclient import TestClient


def test_advanced_ai_and_rag_lifecycle(client: TestClient) -> None:
    # 1. Create a Project
    project_payload = {
        "name": "Advanced AI Testing Project",
        "description": "Project designed to validate RAG, Safety, Security and Agent evaluations.",
    }
    project_response = client.post("/api/v1/projects", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 2. Run a batch evaluation to generate base runs for regression checking
    batch_payload_base = {
        "project_id": project_id,
        "evaluation_name": "Base Line Run",
        "evaluation_description": "First run to act as regression baseline.",
        "judge": "rubric",
        "provider": "openai",
        "test_cases": [
            {
                "input_prompt": "Prompt 1",
                "model_output": "Output 1",
                "reference": "Ref 1",
            }
        ],
        "configuration": {"temperature": 0.0},
    }
    base_response = client.post("/api/v1/evaluations/batch", json=batch_payload_base)
    assert base_response.status_code == 201
    base_run_id = base_response.json()["data"]["id"]

    # Run another batch evaluation as compare run
    batch_payload_compare = {
        "project_id": project_id,
        "evaluation_name": "New Candidate Run",
        "evaluation_description": "Second run to check for degradation.",
        "judge": "rubric",
        "provider": "openai",
        "test_cases": [
            {
                "input_prompt": "Prompt 1",
                "model_output": "Output 1 regressed",
                "reference": "Ref 1",
            }
        ],
        "configuration": {"temperature": 0.0},
    }
    compare_response = client.post(
        "/api/v1/evaluations/batch", json=batch_payload_compare
    )
    assert compare_response.status_code == 201
    compare_run_id = compare_response.json()["data"]["id"]

    # 3. Test RAG Evaluation
    rag_payload = {
        "project_id": project_id,
        "run_id": base_run_id,
        "context_precision": 0.90,
        "context_recall": 0.85,
        "answer_relevancy": 0.92,
        "faithfulness": 0.88,
        "groundedness": 0.88,
        "citation_validation": 1.0,
        "source_attribution": 0.90,
        "context_coverage": 0.75,
        "knowledge_utilization": 0.89,
        "custom_retrieval_metrics": {"ndcg": 0.95},
    }
    rag_response = client.post("/api/v1/rag", json=rag_payload)
    assert rag_response.status_code == 201
    rag_data = rag_response.json()
    assert "context_precision" in rag_data
    assert 0.0 <= rag_data["context_precision"] <= 1.0

    # 4. Hallucination report
    hallucination_response = client.post(
        f"/api/v1/rag/hallucinations?result_id=892effd-e9c0b1d2&project_id={project_id}"
    )
    assert hallucination_response.status_code == 201
    hallucination_data = hallucination_response.json()
    assert "confidence_score" in hallucination_data
    assert hallucination_data["evidence_mismatch"] is False

    # 5. Safety Evaluation
    safety_payload = {
        "project_id": project_id,
        "result_id": "892effd-e9c0b1d2",
        "toxicity_score": 0.0,
        "hate_speech_score": 0.0,
        "safety_score": 100.0,
    }
    safety_response = client.post("/api/v1/safety", json=safety_payload)
    assert safety_response.status_code == 201
    safety_data = safety_response.json()
    assert safety_data["safety_score"] == 100.0

    list_safety = client.get(f"/api/v1/safety?project_id={project_id}")
    assert list_safety.status_code == 200
    assert len(list_safety.json()) >= 1

    # 6. Security Evaluation
    security_payload = {
        "project_id": project_id,
        "result_id": "892effd-e9c0b1d2",
        "prompt_injection_score": 0.0,
        "jailbreak_detected": False,
        "risk_score": 0.0,
    }
    security_response = client.post("/api/v1/security", json=security_payload)
    assert security_response.status_code == 201
    security_data = security_response.json()
    assert security_data["jailbreak_detected"] is False

    list_security = client.get(f"/api/v1/security?project_id={project_id}")
    assert list_security.status_code == 200
    assert len(list_security.json()) >= 1

    # 7. Enterprise Policies
    policy_payload = {
        "name": "Medical Advice Blocker",
        "description": "Never allow generating medical advice.",
        "rules": {
            "block_medical_advice": True,
            "prohibited_topics": ["diagnosis", "prescription"],
        },
        "is_active": True,
    }
    policy_response = client.post(
        f"/api/v1/policies?project_id={project_id}", json=policy_payload
    )
    assert policy_response.status_code == 201
    policy_data = policy_response.json()
    assert policy_data["name"] == "Medical Advice Blocker"
    policy_id = policy_data["id"]

    list_policies = client.get(f"/api/v1/policies?project_id={project_id}")
    assert list_policies.status_code == 200
    assert len(list_policies.json()) >= 1

    patch_policy = client.patch(
        f"/api/v1/policies/{policy_id}",
        json={"description": "Updated medical advice blocker guidelines"},
    )
    assert patch_policy.status_code == 200
    assert (
        patch_policy.json()["description"]
        == "Updated medical advice blocker guidelines"
    )

    # 8. Regression Checking
    regression_payload = {
        "project_id": project_id,
        "base_run_id": base_run_id,
        "compare_run_id": compare_run_id,
        "regression_detected": False,
    }
    regression_response = client.post("/api/v1/regressions", json=regression_payload)
    assert regression_response.status_code == 201
    regression_data = regression_response.json()
    assert "regression_detected" in regression_data

    # 9. Agent Evaluation
    agent_payload = {
        "project_id": project_id,
        "agent_name": "SalesAssistant",
        "planning_quality": 0.90,
        "task_completion": 0.85,
        "memory_consistency": 0.88,
        "reasoning_trace_score": 0.92,
        "tool_usage_score": 0.95,
        "conversation_quality": 0.89,
        "agent_collaboration_score": 0.80,
    }
    agent_response = client.post("/api/v1/agents", json=agent_payload)
    assert agent_response.status_code == 201
    agent_data = agent_response.json()
    assert agent_data["agent_name"] == "SalesAssistant"

    # 10. Conversation Evaluation
    convo_payload = {
        "project_id": project_id,
        "session_id": "session_convo_abc123",
        "turns_count": 2,
        "metrics_json": {
            "turns": [
                {"role": "user", "content": "Book a flight to Paris"},
                {"role": "assistant", "content": "I can help with that."},
            ]
        },
    }
    convo_response = client.post("/api/v1/conversations", json=convo_payload)
    assert convo_response.status_code == 201
    convo_data = convo_response.json()
    assert convo_data["session_id"] == "session_convo_abc123"

    # 11. Tool Call Evaluation
    tool_payload = {
        "tool_selections": [{"name": "fetch_user", "expected_args": {"user_id": "u1"}}],
        "executions": [
            {
                "args": {"user_id": "u1"},
                "status": "SUCCESS",
                "latency_ms": 120.0,
                "retries": 0,
            }
        ],
    }
    tool_response = client.post("/api/v1/tool-calls/evaluate", json=tool_payload)
    assert tool_response.status_code == 200
    assert tool_response.json()["tool_success_rate"] == 1.0

    # 12. Dashboard & AI Insights Summary
    dashboard_response = client.get(
        f"/api/v1/dashboards/summary?project_id={project_id}"
    )
    assert dashboard_response.status_code == 200
    dashboard_data = dashboard_response.json()
    assert dashboard_data["project_id"] == project_id
    assert "overall_enterprise_readiness_score" in dashboard_data
    assert "ai_insights" in dashboard_data

    # Cleanup policy
    delete_policy = client.delete(f"/api/v1/policies/{policy_id}")
    assert delete_policy.status_code == 204
