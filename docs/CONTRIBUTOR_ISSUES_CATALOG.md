# EvalForge Master Contributor Issues Catalog (30 Real Issues)

This catalog contains **30 real, repository-specific engineering tasks** derived directly from the EvalForge codebase. These issues are categorized by difficulty and component area to provide an exceptional first-time and ongoing contributor experience.

---

## 📊 Issues Summary by Difficulty

| Difficulty Level | Count | Recommended For |
|---|---|---|
| **🟢 Good First Issue** | 10 Issues | First-time open-source contributors, students, new community members |
| **🟡 Intermediate** | 15 Issues | Developers familiar with FastAPI, React 18, PostgreSQL, or Celery |
| **🔴 Advanced** | 5 Issues | Experienced software engineers, system architects, and maintainers |

---

## 🟢 Good First Issues (10 Issues)

### ISSUE-01: Add Strict Pydantic Response Model for Dataset Import Route
- **Component:** `backend/app/datasets/routers/`
- **Labels:** `good first issue`, `backend`, `api`
- **Summary:** Define an explicit Pydantic v2 response schema (`DatasetImportResponse`) for `/api/v1/datasets/import` instead of returning raw dict objects.
- **Suggested Files:** [`backend/app/schemas/dataset.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/schemas/dataset.py), `backend/app/datasets/routers/`

### ISSUE-02: Add Request Cancellation (AbortController) to React Query Hooks
- **Component:** `frontend/src/services/api.ts`
- **Labels:** `good first issue`, `frontend`, `ux`
- **Summary:** Pass Axios `signal` to `apiClient.get()` calls so that navigating away from Datasets or Evaluations pages cancels pending HTTP requests cleanly.
- **Suggested Files:** [`frontend/src/services/api.ts`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/services/api.ts)

### ISSUE-03: Standardize Python Datetime UTC Usage across Enterprise Services
- **Component:** `backend/app/enterprise/`
- **Labels:** `good first issue`, `backend`, `refactor`
- **Summary:** Replace deprecated `datetime.utcnow()` calls with timezone-aware `datetime.now(timezone.utc)` across enterprise service modules.
- **Suggested Files:** `backend/app/enterprise/services/organization_service.py`, `workspace_service.py`, `billing_service.py`

### ISSUE-04: Create Pytest Fixture for Redis Connection Mocking in Offline Runs
- **Component:** `backend/tests/`
- **Labels:** `good first issue`, `testing`, `backend`
- **Summary:** Create a reusable `@pytest.fixture` in `conftest.py` that mocks Redis ping and set/get operations when Redis is not running locally.
- **Suggested Files:** [`backend/tests/conftest.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/tests/conftest.py)

### ISSUE-05: Add Structured JSON Error Schema Validation to Exception Handler
- **Component:** `backend/app/core/exceptions.py`
- **Labels:** `good first issue`, `api`, `backend`
- **Summary:** Ensure global exception handler returns RFC 7807 problem details JSON schema (`type`, `title`, `status`, `detail`, `instance`).
- **Suggested Files:** [`backend/app/core/exceptions.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/core/exceptions.py)

### ISSUE-06: Implement Automated Pre-Commit Configuration
- **Component:** Repository Root
- **Labels:** `good first issue`, `dev-ex`, `devops`
- **Summary:** Add `.pre-commit-config.yaml` running `ruff`, `black`, and `prettier` pre-commit hooks locally.
- **Suggested Files:** `.pre-commit-config.yaml`, `README.md`

### ISSUE-07: Add OpenAPI Parameter Descriptions and Tags to Benchmark Router
- **Component:** `backend/app/datasets/routers/benchmark.py`
- **Labels:** `good first issue`, `documentation`, `api`
- **Summary:** Add rich OpenAPI docstrings and parameter descriptions (`summary`, `description`, `response_description`) to benchmark suite endpoints.
- **Suggested Files:** `backend/app/datasets/routers/benchmark.py`

### ISSUE-08: Add Dark Mode / High Contrast Visual Adjustments to Scheduled Jobs Page
- **Component:** `frontend/src/pages/ScheduledJobs.tsx`
- **Labels:** `good first issue`, `frontend`, `ui`
- **Summary:** Update tailwind border and opacity classes on cron history cards to ensure AAA contrast ratio compliance.
- **Suggested Files:** [`frontend/src/pages/ScheduledJobs.tsx`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/pages/ScheduledJobs.tsx)

### ISSUE-09: Add Strict TypeScript Discriminator Types for WebSocket Progress Events
- **Component:** `frontend/src/hooks/useJobWebSocket.ts`
- **Labels:** `good first issue`, `frontend`, `typing`
- **Summary:** Use discriminated union types for `WebSocketProgressEvent` based on `event` field (`started`, `progress`, `completed`, `failed`).
- **Suggested Files:** [`frontend/src/hooks/useJobWebSocket.ts`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/hooks/useJobWebSocket.ts)

### ISSUE-10: Add Docker Image Vulnerability Scanning Step to GitHub Actions CI
- **Component:** `.github/workflows/ci.yml`
- **Labels:** `good first issue`, `devops`, `security`
- **Summary:** Add Trivy / Grype vulnerability scanner step to `.github/workflows/ci.yml` docker build job.
- **Suggested Files:** [`.github/workflows/ci.yml`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/.github/workflows/ci.yml)

---

## 🟡 Intermediate Issues (15 Issues)

### ISSUE-11: Implement Sliding Window Rate Limit Header Exposure (`X-RateLimit-Remaining`)
- **Component:** `backend/app/core/production_security.py`
- **Labels:** `intermediate`, `backend`, `api`
- **Summary:** Update `RateLimitingMiddleware` to calculate and attach `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers to responses.
- **Suggested Files:** [`backend/app/core/production_security.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/core/production_security.py)

### ISSUE-12: Implement RAG Context Precision Metric Calculator in G-Eval Engine
- **Component:** `backend/app/evaluation/`
- **Labels:** `intermediate`, `backend`, `evaluation`
- **Summary:** Add `ContextPrecisionCalculator` evaluating whether retrieved context chunks are relevant to the user query prompt.
- **Suggested Files:** [`backend/app/evaluation/prompts/geval.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/evaluation/prompts/geval.py)

### ISSUE-13: Add Virtualized Table Rendering for Dataset Records List
- **Component:** `frontend/src/pages/Datasets.tsx`
- **Labels:** `intermediate`, `frontend`, `performance`
- **Summary:** Integrate `react-window` or `@tanstack/react-virtual` to render dataset record lists with 10,000+ rows smoothly without DOM lagging.
- **Suggested Files:** [`frontend/src/pages/Datasets.tsx`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/pages/Datasets.tsx)

### ISSUE-14: Add Prometheus Metrics Exporter Endpoint (`/metrics`) for Worker Queues
- **Component:** `backend/app/main.py`
- **Labels:** `intermediate`, `devops`, `infra`
- **Summary:** Integrate `prometheus-fastapi-instrumentator` exposing API request counts, latencies, and active Celery task counts at `/metrics`.
- **Suggested Files:** [`backend/app/main.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/main.py), `pyproject.toml`

### ISSUE-15: Implement DeepSeek-V3 LLM Provider Driver
- **Component:** `backend/app/evaluation/providers/`
- **Labels:** `intermediate`, `backend`, `evaluation`
- **Summary:** Create `DeepSeekLLMProvider` inheriting from `BaseLLMProvider` to support DeepSeek-V3 and DeepSeek-R1 API inferencing.
- **Suggested Files:** [`backend/app/evaluation/providers/base.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/evaluation/providers/base.py), `deepseek_provider.py`

### ISSUE-16: Implement Automatic Exponential Backoff Retry for WebSocket Hook
- **Component:** `frontend/src/hooks/useJobWebSocket.ts`
- **Labels:** `intermediate`, `frontend`, `web-sockets`
- **Summary:** Add configurable reconnection attempts with exponential backoff (1s, 2s, 4s, 8s max 30s) when WebSocket connection drops.
- **Suggested Files:** [`frontend/src/hooks/useJobWebSocket.ts`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/hooks/useJobWebSocket.ts)

### ISSUE-17: Add JSON Schema Validation Check to Dataset Bulk Import Router
- **Component:** `backend/app/datasets/`
- **Labels:** `intermediate`, `backend`, `api`
- **Summary:** Validate imported JSONL and CSV dataset rows against a target dataset version JSON schema prior to database insertion.
- **Suggested Files:** `backend/app/datasets/services/import_service.py`

### ISSUE-18: Add Jinja2 Template Syntax Error Validator Before Prompt Execution
- **Component:** `backend/app/evaluation/prompts/`
- **Labels:** `intermediate`, `backend`, `validation`
- **Summary:** Catch Jinja2 `TemplateSyntaxError` when compiling custom judge prompt templates and return structured HTTP 422 error details.
- **Suggested Files:** `backend/app/evaluation/prompts/templates.py`

### ISSUE-19: Implement Database Query Index Optimizations for Evaluation Runs
- **Component:** `backend/app/models/`
- **Labels:** `intermediate`, `performance`, `database`
- **Summary:** Add composite SQLAlchemy indexes on `(project_id, status, created_at)` for `evaluations` and `experiments` tables.
- **Suggested Files:** [`backend/app/models/evaluation.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/models/evaluation.py)

### ISSUE-20: Implement Side-by-Side Pairwise LLM Response Diff Viewer Component
- **Component:** `frontend/src/pages/Evaluations.tsx`
- **Labels:** `intermediate`, `frontend`, `ui`
- **Summary:** Create a side-by-side diff viewer component highlighting textual token differences between Candidate Output and Reference Ground Truth.
- **Suggested Files:** [`frontend/src/pages/Evaluations.tsx`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/pages/Evaluations.tsx)

### ISSUE-21: Implement Local CSV / JSONL Dataset Exporter Utility
- **Component:** `backend/app/datasets/`
- **Labels:** `intermediate`, `backend`, `feature`
- **Summary:** Add export endpoint `/api/v1/datasets/versions/{id}/export?format=jsonl` streaming dataset records as formatted JSONL/CSV downloads.
- **Suggested Files:** `backend/app/datasets/routers/dataset.py`

### ISSUE-22: Add Automated OpenAPI Schema Generation Test in CI Workflow
- **Component:** `backend/tests/`
- **Labels:** `intermediate`, `testing`, `ci`
- **Summary:** Add pytest test verifying that `app.openapi()` generates a valid OpenAPI 3.1 schema without throwing schema generation errors.
- **Suggested Files:** `backend/tests/test_openapi_schema.py`

### ISSUE-23: Implement Request Correlation ID Tracing to Celery Async Worker Logs
- **Component:** `backend/app/jobs/`
- **Labels:** `intermediate`, `backend`, `logging`
- **Summary:** Propagate HTTP `X-Request-ID` header into Celery task contextvars so worker logs include matching `request_id` context.
- **Suggested Files:** `backend/app/jobs/queue/tasks.py`, `backend/app/core/logging.py`

### ISSUE-24: Implement Red-Team Jailbreak Prompt Benchmark Dataset Template
- **Component:** `datasets/`
- **Labels:** `intermediate`, `datasets`, `security`
- **Summary:** Add a curated 50-item JSONL benchmark dataset containing gold-standard adversarial jailbreak prompts for LLM red-teaming.
- **Suggested Files:** `datasets/safety_redteam_v1.jsonl`

### ISSUE-25: Implement Audit Log Exporter Endpoint for Enterprise Compliance
- **Component:** `backend/app/enterprise/`
- **Labels:** `intermediate`, `enterprise`, `api`
- **Summary:** Add route allowing tenant admins to list and export security audit logs (API key usage, role changes, dataset deletions).
- **Suggested Files:** `backend/app/enterprise/routes/audit_logs.py`

---

## 🔴 Advanced Issues (5 Issues)

### ISSUE-26: Create Standalone Python CLI Tool (`evalforge-cli`)
- **Component:** `packages/evalforge-cli/`
- **Labels:** `advanced`, `cli`, `sdk`
- **Summary:** Build a standalone Click/Typer CLI client allowing developers to run `evalforge run --dataset safety_v1.jsonl --model gpt-4o` from terminal.
- **Suggested Files:** `pyproject.toml`, `packages/evalforge-cli/`

### ISSUE-27: Implement Health Check Probe for Redis Sentinel / Cluster Fallback
- **Component:** `backend/app/core/redis.py`
- **Labels:** `advanced`, `infra`, `redis`
- **Summary:** Upgrade `RedisManager` to support Redis Sentinel failover clusters and automatic reconnection retry strategies.
- **Suggested Files:** [`backend/app/core/redis.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/core/redis.py)

### ISSUE-28: Create Standalone Python SDK Client Wrapper (`evalforge-python`)
- **Component:** `packages/evalforge-python/`
- **Labels:** `advanced`, `sdk`, `python`
- **Summary:** Publish a PyPI-ready Python SDK providing programmatic access to project creation, dataset uploads, and evaluation tracking.
- **Suggested Files:** `packages/evalforge-python/`

### ISSUE-29: Add Automated Visual Regression Tests for Dashboard using Playwright
- **Component:** `frontend/tests/`
- **Labels:** `advanced`, `testing`, `frontend`
- **Summary:** Set up Playwright E2E test suite running headless browser visual snapshot regression checks on Dashboard and Evaluations pages.
- **Suggested Files:** `frontend/tests/e2e/dashboard.spec.ts`

### ISSUE-30: Implement Real-time Guardrail Filtering Proxy Middleware
- **Component:** `backend/app/evaluation/`
- **Labels:** `advanced`, `architecture`, `security`
- **Summary:** Build a high-throughput proxy middleware evaluating LLM prompt inputs and model outputs against safety rubrics with sub-15ms latency.
- **Suggested Files:** `backend/app/evaluation/guardrails/proxy.py`
