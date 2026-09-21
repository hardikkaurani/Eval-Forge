# Eval-Forge REST API Reference

Welcome to the official REST API reference for **Eval-Forge** — the production-grade, open-source AI evaluation and LLM observability platform.

---

## 1. Overview & Base URLs

All public API endpoints are versioned under `/api/v1`.

| Environment | Base URL | Interactive Docs |
|---|---|---|
| **Local Development** | `http://localhost:8000/api/v1` | [Swagger UI](http://localhost:8000/docs) · [ReDoc](http://localhost:8000/redoc) · [OpenAPI JSON](http://localhost:8000/openapi.json) |
| **Production (Self-Hosted)** | `https://your-domain.com/api/v1` | Configurable via `APP_ENV=production` |
| **Production Demo** | `https://evalforge.onrender.com/api/v1` | Health: `https://evalforge.onrender.com/health` |

---

## 2. Authentication

Eval-Forge supports two standard authentication mechanisms:

### Option A: API Key (Recommended for SDKs, CLI, and CI/CD)
Pass your API key in the `X-API-Key` request header:
```http
X-API-Key: ef_live_0123456789abcdef0123456789abcdef
```
Or via the standard `Authorization` header:
```http
Authorization: Bearer ef_live_0123456789abcdef0123456789abcdef
```

### Option B: JWT Bearer Token (Web UI & User Sessions)
Pass your session access token:
```http
Authorization: Bearer <jwt_access_token>
```

---

## 3. Standard Response Envelope

Every endpoint returns a predictable, structured response envelope:

```json
{
  "success": true,
  "message": "Evaluation job queued successfully.",
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "RAG Support Quality Run",
    "status": "QUEUED"
  },
  "timestamp": "2026-09-20T04:00:00.000Z",
  "request_id": "req-9a8b7c6d-5e4f"
}
```

### Error Envelope
When a request fails, the envelope returns `success: false` with actionable error diagnostics:
```json
{
  "success": false,
  "message": "Resource not found or outside your authorized workspace.",
  "data": null,
  "timestamp": "2026-09-20T04:00:00.000Z",
  "request_id": "req-11223344-5566"
}
```

---

## 4. End-to-End Developer Journey

Here is the complete workflow to authenticate, manage projects, run evaluations, and inspect results.

### Step 1 — Authenticate or Generate API Key

#### Create an Account
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SecurePassword123!",
    "full_name": "Jane Developer"
  }'
```

#### Log In
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SecurePassword123!"
  }'
```
*Returns JWT access token.*

#### Generate API Key
```bash
curl -X POST "http://localhost:8000/api/v1/keys" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI/CD Deployment Key",
    "expires_in_days": 90
  }'
```
*Returns an `ef_live_...` key. Store this key securely.*

---

### Step 2 — Create an Evaluation Project

```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "X-API-Key: ef_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support AI Benchmarks",
    "description": "Evaluates automated response accuracy, tone, and hallucination rates."
  }'
```

---

### Step 3 — Upload a Dataset

```bash
curl -X POST "http://localhost:8000/api/v1/datasets" \
  -H "X-API-Key: ef_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "YOUR_PROJECT_UUID",
    "name": "Support Q&A Benchmark v1",
    "description": "50 curated customer support golden test cases",
    "test_cases": [
      {
        "input": "How do I reset my password?",
        "expected_output": "Go to Settings > Security > Reset Password.",
        "context": "Knowledge base article #402: Password Management",
        "metadata": {"difficulty": "easy"}
      }
    ]
  }'
```

---

### Step 4 — Launch an Evaluation Run

```bash
curl -X POST "http://localhost:8000/api/v1/evaluations" \
  -H "X-API-Key: ef_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "YOUR_PROJECT_UUID",
    "dataset_id": "YOUR_DATASET_UUID",
    "name": "Sprint 24 Prompt Regression Test",
    "eval_type": "rag",
    "metrics": ["accuracy", "faithfulness", "context_recall", "hallucination"],
    "judge_model": "gpt-4o-mini",
    "threshold": 0.85
  }'
```
*Returns `run_id` and background `job_id`.*

---

### Step 5 — Track Job Progression

#### Poll Job Status
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/YOUR_JOB_UUID" \
  -H "X-API-Key: ef_live_your_key_here"
```

#### Real-Time Server-Sent Events (SSE) Stream
```bash
curl -N "http://localhost:8000/api/v1/jobs/YOUR_JOB_UUID/progress/sse" \
  -H "X-API-Key: ef_live_your_key_here"
```

---

### Step 6 — Inspect Results & Analytics

#### Get Evaluation Summary & Metrics
```bash
curl -X GET "http://localhost:8000/api/v1/evaluations/YOUR_RUN_UUID" \
  -H "X-API-Key: ef_live_your_key_here"
```

#### List Test Case Results
```bash
curl -X GET "http://localhost:8000/api/v1/results?run_id=YOUR_RUN_UUID&page=1&page_size=50" \
  -H "X-API-Key: ef_live_your_key_here"
```

---

## 5. Developer Platform

### Webhooks

Register a webhook endpoint to receive immediate event payloads when jobs finish or fail:

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks" \
  -H "X-API-Key: ef_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "YOUR_PROJECT_UUID",
    "target_url": "https://your-service.com/webhooks/evalforge",
    "events": ["evaluation.completed", "job.failed"]
  }'
```
*See [docs/webhooks.md](webhooks.md) for signature verification and event schemas.*

### Model Context Protocol (MCP)

Integrate Eval-Forge with AI agents (Claude Desktop, Cursor, LangChain):

```bash
# List available MCP tools
curl -X GET "http://localhost:8000/api/v1/mcp/tools" \
  -H "X-API-Key: ef_live_your_key_here"

# Execute tool call
curl -X POST "http://localhost:8000/api/v1/mcp/tools/call" \
  -H "X-API-Key: ef_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_projects",
    "arguments": {"page": 1, "page_size": 10}
  }'
```
*See [docs/mcp.md](mcp.md) for tool definitions and agent configuration.*

---

## 6. Health & System Telemetry

| Endpoint | Method | Purpose | Typical Response |
|---|---|---|---|
| `/health` | `GET` | Overall system health (API, DB, Redis) | `{"status": "healthy", "database": true, "redis": true}` |
| `/api/v1/live` | `GET` | Kubernetes / container liveness probe | `{"status": "alive"}` |
| `/api/v1/ready` | `GET` | Dependency readiness probe | `{"status": "ready"}` |
| `/metrics` | `GET` | Prometheus telemetry scrape endpoint | Plain text Prometheus exposition format |

---

## 7. Status Codes & Error Handling

| Code | Status | Meaning | Action |
|---|---|---|---|
| `200` | OK | Request succeeded. | Process `data` payload. |
| `201` | Created | Resource successfully created. | Retrieve newly assigned `id`. |
| `400` | Bad Request | Malformed request body or parameters. | Review error message and payload structure. |
| `401` | Unauthorized | Missing, invalid, or expired authentication token. | Provide a valid `X-API-Key` or Bearer token. |
| `403` | Forbidden | Insufficient permissions for requested action. | Ensure API key has appropriate workspace scope. |
| `404` | Not Found | Target resource does not exist or belongs to another tenant. | Verify UUID and workspace scoping. |
| `409` | Conflict | Resource conflict (e.g. duplicate key or state transition conflict). | Refresh state and retry. |
| `422` | Unprocessable Entity | Pydantic schema validation error. | Check field types, required properties, and constraints. |
| `429` | Too Many Requests | Rate limit exceeded (Default: 300 req/min). | Back off and inspect `Retry-After` header. |
| `500` | Internal Server Error | Unexpected server error. | Diagnostic ID is recorded in server logs; no secrets leaked. |
| `503` | Service Unavailable | Database or Redis dependencies temporarily unreachable. | Fast-fail retry with exponential backoff. |
