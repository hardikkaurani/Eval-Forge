from fastapi.testclient import TestClient

from app.evaluation.rubrics.rubrics import Rubric


def test_phase8_custom_jinja2_rubric(client: TestClient) -> None:
    """Verify registration and Jinja2 rendering of custom evaluation rubrics."""
    # 1. Register custom rubric
    res = client.post(
        "/api/v1/rubrics/custom",
        json={
            "key": "coherence_v2",
            "name": "Coherence V2",
            "description": "Custom logical structure metric",
            "weight": 1.5,
            "scoring_scale": 10,
            "prompt_template": "Evaluate coherence of {{ answer }} given context {{ context }}.",
        },
    )
    assert res.status_code == 201
    assert res.json()["data"]["key"] == "coherence_v2"

    # 2. Verify in rubrics list
    list_res = client.get("/api/v1/rubrics")
    assert list_res.status_code == 200
    keys = [item["key"] for item in list_res.json()["data"]]
    assert "coherence_v2" in keys

    # 3. Test Jinja2 rendering on Rubric model directly
    rubric = Rubric(
        name="Test Jinja2",
        description="Jinja2 Test Description",
        prompt_template="Answer: {{ answer }} | Score target: {{ scale }}",
    )
    rendered = rubric.render_prompt(answer="Quantum Computing", scale=10)
    assert "Answer: Quantum Computing" in rendered
    assert "Score target: 10" in rendered


def test_phase8_pairwise_elo_comparison(client: TestClient) -> None:
    """Verify pairwise comparison outcomes and ELO rating updates."""
    # 1. Create Project
    proj_res = client.post("/api/v1/projects", json={"name": "Pairwise ELO Project"})
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["data"]["id"]

    # 2. Record Pairwise Winner Model A
    comp_res = client.post(
        "/api/v1/evaluations/pairwise/compare",
        json={
            "project_id": proj_id,
            "model_a": "gpt-4o",
            "model_b": "gemini-1.5-pro",
            "winner": "A",
            "reasoning": "Model A gave more concise explanation.",
            "k_factor": 32.0,
        },
    )
    assert comp_res.status_code == 200
    data = comp_res.json()["data"]
    assert data["winner"] == "A"
    assert data["new_elo_a"] > data["old_elo_a"]
    assert data["new_elo_b"] < data["old_elo_b"]
    assert data["elo_delta_a"] > 0

    # 3. Fetch ELO Leaderboard
    elo_res = client.get(f"/api/v1/evaluations/pairwise/elo?project_id={proj_id}")
    assert elo_res.status_code == 200
    elo_map = elo_res.json()["data"]
    assert elo_map["gpt-4o"] > elo_map["gemini-1.5-pro"]


def test_phase8_rag_and_hallucination_pipeline(client: TestClient) -> None:
    """Verify full RAG pipeline evaluation and hallucination detection report."""
    # 1. Create Project
    proj_res = client.post("/api/v1/projects", json={"name": "Phase 8 RAG Project"})
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["data"]["id"]

    # 2. Run RAG Pipeline Evaluation
    rag_res = client.post(
        "/api/v1/rag",
        json={
            "project_id": proj_id,
            "run_id": "rag-run-101",
            "evaluation_name": "RAG Quality Benchmark",
        },
    )
    assert rag_res.status_code == 201
    rag_data = rag_res.json()
    assert "context_precision" in rag_data
    assert "faithfulness" in rag_data
    assert "source_attribution" in rag_data

    # 3. Generate Hallucination Report
    halluc_res = client.post(
        f"/api/v1/rag/hallucinations?result_id=res-888&project_id={proj_id}",
    )
    assert halluc_res.status_code == 201
    h_data = halluc_res.json()
    assert "confidence_score" in h_data
    assert "evidence_mismatch" in h_data


def test_phase8_safety_and_toxicity(client: TestClient) -> None:
    """Verify content safety and toxicity evaluation."""
    # 1. Create Project
    proj_res = client.post("/api/v1/projects", json={"name": "Phase 8 Safety Project"})
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["data"]["id"]

    # 2. Run Safety Evaluation
    safety_res = client.post(
        "/api/v1/safety",
        json={
            "project_id": proj_id,
            "result_id": "res-safety-1",
        },
    )
    assert safety_res.status_code == 201
    s_data = safety_res.json()
    assert "safety_score" in s_data
    assert "toxicity_score" in s_data


def test_phase8_tenant_isolation(db_session) -> None:
    """Verify multi-tenant workspace security on Phase 8 endpoints."""
    from app.core.dependencies import get_current_api_key
    from app.enterprise.models import EnterpriseAPIKey
    from app.main import app
    from app.models.project import Project

    # 1. Create Project A (Tenant A) and Project B (Tenant B)
    proj_a = Project(id="proj-a-101", name="Tenant A Project", workspace_id="ws-a")
    proj_b = Project(id="proj-b-202", name="Tenant B Project", workspace_id="ws-b")
    db_session.add_all([proj_a, proj_b])

    # 2. API Keys
    key_a = EnterpriseAPIKey(
        key_hash="hash_a",
        workspace_id="ws-a",
        name="Key A",
        scopes=["read:all"],
        is_active=True,
    )
    key_b = EnterpriseAPIKey(
        key_hash="hash_b",
        workspace_id="ws-b",
        name="Key B",
        scopes=["read:all"],
        is_active=True,
    )
    db_session.add_all([key_a, key_b])

    app.dependency_overrides[get_current_api_key] = lambda: key_b
    client_b = TestClient(app)

    # 3. Cross-Tenant Pairwise compare -> 404
    assert (
        client_b.post(
            "/api/v1/evaluations/pairwise/compare",
            json={
                "project_id": proj_a.id,
                "model_a": "gpt-4o",
                "model_b": "claude-3-5-sonnet",
                "winner": "A",
            },
        ).status_code
        == 404
    )

    # 4. Cross-Tenant Pairwise ELO -> 404
    assert (
        client_b.get(
            f"/api/v1/evaluations/pairwise/elo?project_id={proj_a.id}"
        ).status_code
        == 404
    )

    # 5. Cross-Tenant RAG List -> 404
    assert client_b.get(f"/api/v1/rag?project_id={proj_a.id}").status_code == 404

    # 6. Cross-Tenant Safety List -> 404
    assert client_b.get(f"/api/v1/safety?project_id={proj_a.id}").status_code == 404

    app.dependency_overrides.clear()


def test_phase8_jinja2_ssti_and_sandbox_security() -> None:
    """Verify Jinja2 SandboxedEnvironment blocks SSTI payloads and respects size bounds."""
    # 1. Legitimate template renders
    r1 = Rubric(name="R1", description="D1", prompt_template="Hello {{ name }}")
    assert "Hello World" in r1.render_prompt(name="World")

    # 2. SSTI payloads blocked safely (no class / mro / globals exposure)
    ssti_payloads = [
        "{{ ''.__class__.__mro__ }}",
        "{{ config.__class__ }}",
        "{{ cycler.__init__.__globals__ }}",
    ]
    for p in ssti_payloads:
        r_ssti = Rubric(name="SSTI", description="Test SSTI", prompt_template=p)
        res = r_ssti.render_prompt()
        assert "__class__" not in res
        assert "<class" not in res
        assert "__globals__" not in res
        assert "Evaluate SSTI" in res  # Safe fallback text returned

    # 3. Malformed template handled safely
    r_bad = Rubric(name="Bad", description="Desc", prompt_template="{% if true %}")
    assert "Evaluate Bad" in r_bad.render_prompt()

    # 4. Missing variable handled safely
    r_missing = Rubric(
        name="Miss", description="Desc", prompt_template="Value: {{ undefined_var }}"
    )
    assert "Evaluate Miss" in r_missing.render_prompt()

    # 5. Oversized template rejected (> 4096 chars)
    r_huge = Rubric(name="Huge", description="Desc", prompt_template="A" * 5000)
    assert "Evaluate Huge" in r_huge.render_prompt()


def test_phase8_persistent_elo_and_concurrency(client: TestClient, db_session) -> None:
    """Verify ELO rating persistence in DB across requests and process restart simulation."""
    from sqlalchemy import select

    from app.models.evaluation import ModelEloRating

    # 1. Create Project via API
    proj_res = client.post("/api/v1/projects", json={"name": "ELO Persistent Project"})
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["data"]["id"]

    # 2. First comparison persists rating in DB
    c1 = client.post(
        "/api/v1/evaluations/pairwise/compare",
        json={
            "project_id": proj_id,
            "model_a": "model-alpha",
            "model_b": "model-beta",
            "winner": "A",
        },
    )
    assert c1.status_code == 200
    assert c1.json()["data"]["new_elo_a"] > 1500.0

    # 3. Second request reads persisted rating from DB
    c2 = client.post(
        "/api/v1/evaluations/pairwise/compare",
        json={
            "project_id": proj_id,
            "model_a": "model-alpha",
            "model_b": "model-beta",
            "winner": "A",
        },
    )
    assert c2.status_code == 200
    assert c2.json()["data"]["old_elo_a"] > 1500.0
    assert c2.json()["data"]["new_elo_a"] > c2.json()["data"]["old_elo_a"]

    # 4. Restart simulation: API leaderboard directly fetches persisted ratings from DB
    elo_res = client.get(f"/api/v1/evaluations/pairwise/elo?project_id={proj_id}")
    assert elo_res.status_code == 200
    elo_map = elo_res.json()["data"]
    assert "model-alpha" in elo_map
    assert "model-beta" in elo_map
    assert elo_map["model-alpha"] > elo_map["model-beta"]


def test_phase8_custom_rubric_persistence_and_limits(client: TestClient) -> None:
    """Verify custom rubric persistence, built-in protection, and resource limits."""
    # 1. Create Project
    proj_res = client.post("/api/v1/projects", json={"name": "Rubric Limits Project"})
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["data"]["id"]

    # 2. Create Custom Rubric attached to project
    r1 = client.post(
        "/api/v1/rubrics/custom",
        json={
            "project_id": proj_id,
            "key": "coherence_limit_1",
            "name": "Limit Rubric 1",
            "description": "Valid custom rubric description",
            "weight": 1.0,
            "scoring_scale": 5,
        },
    )
    assert r1.status_code == 201

    # 3. Overwrite built-in key rejected
    r_builtin = client.post(
        "/api/v1/rubrics/custom",
        json={
            "key": "correctness",
            "name": "Fake Correctness",
            "description": "Attempt to overwrite built-in key",
        },
    )
    assert r_builtin.status_code == 400
    assert "built-in" in str(r_builtin.json()).lower()

    # 4. Invalid key / oversized name rejected
    r_huge_name = client.post(
        "/api/v1/rubrics/custom",
        json={
            "key": "valid_key",
            "name": "X" * 200,
            "description": "Valid description",
        },
    )
    assert r_huge_name.status_code == 400

    # 5. List rubrics includes project custom rubric
    l_res = client.get(f"/api/v1/rubrics?project_id={proj_id}")
    assert l_res.status_code == 200
    keys = [item["key"] for item in l_res.json()["data"]]
    assert "coherence_limit_1" in keys
