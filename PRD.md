# Product Requirements Document (PRD)

## Project Name: EvalForge

**Document Version:** 1.0.0  
**Status:** Released / Active  
**Author:** AI Engineering & Product Team  
**Target Audience:** AI/ML Engineers, Product Managers, QA/Testing Engineers, Enterprise DevOps Teams

---

## 1. Executive Summary & Problem Statement

### 1.1 Background

The rapid adoption of Large Language Models (LLMs) in production applications has transformed software development. However, evaluating LLM outputs—measuring accuracy, hallucination rates, relevance, toxicity, and domain-specific quality—remains one of the biggest bottlenecks in AI product lifecycles.

### 1.2 Problem Statement

- **Ad-hoc & Unstructured Testing:** Most engineering teams rely on manual spot-checks, spreadsheets, or non-reproducible local scripts to evaluate prompt changes or model updates.
- **Lack of Versioning & Reproducibility:** Prompts, datasets, and benchmark results are rarely pinned to immutable dataset versions, leading to evaluation drift over time.
- **Vendor Lock-in & Privacy Risks:** Proprietary evaluation SaaS platforms force teams to send sensitive enterprise data to external third parties.
- **Disconnected from CI/CD:** Unlike traditional unit testing, LLM evaluation is rarely integrated into continuous integration pipelines, allowing regression bugs to reach production.
- **Rigid Evaluation Frameworks:** Existing tools lock developers into a single scoring methodology (e.g., only ROUGE/BLEU or only a specific vendor metric) rather than supporting flexible LLM-as-a-Judge paradigms.

### 1.3 Solution Statement

**EvalForge** is a self-hostable, developer-first, production-grade LLM evaluation platform. It treats LLM evaluation like modern software testing: automated, versioned, reproducible, multi-tenant, and seamlessly integrated into developer CI/CD workflows.

---

## 2. Product Vision & Goals

### 2.1 Vision

To become the standard open-source evaluation platform for AI application teams, enabling continuous, automated benchmarking of LLM applications with full data privacy and framework flexibility.

### 2.2 Key Product Objectives

1. **100% Self-Hostable Data Privacy:** Zero required outbound network calls; full local execution capabilities via Docker.
2. **Framework-Agnostic Judge Engine:** Unified interface supporting G-Eval (Chain-of-Thought), DeepEval metrics, AlpacaEval, and custom Jinja2 prompt rubrics.
3. **Immutable Versioning:** Every dataset upload and evaluation run is immutably snapshot-pinned for full auditability and reproducibility.
4. **CI/CD Native:** Provide first-class REST API and CLI capabilities for embedding evaluation checks into GitHub Actions / GitLab CI workflows.
5. **Enterprise Multi-Tenancy:** Provide organization-level and workspace-level isolation with fine-grained Role-Based Access Control (RBAC).

### 2.3 Key Performance Indicators (KPIs)

- **API Response Latency:** Sub-200ms latency for non-eval API operations.
- **Job Execution Reliability:** 99.9% successful completion rate for queued evaluation tasks.
- **Scale:** Ability to execute 1,000+ concurrent LLM judge calls per dataset run via horizontal Celery worker scaling.
- **Integration Setup Time:** < 5 minutes for developers to run locally using Docker Compose.

---

## 3. User Personas & Use Cases

### 3.1 User Personas

| Persona                             | Role                            | Primary Goal                                                              | Key Pain Point                                                    |
| ----------------------------------- | ------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **P1: Alex (AI/ML Engineer)**       | Builds LLM pipelines & prompts  | Benchmark prompt variants & fine-tuned models automatically               | Manual testing consumes hours; lack of automated regression tests |
| **P2: Sarah (AI Product Lead)**     | Manages AI product roadmap & QA | Track model response quality, hallucination rate, and cost over time      | No centralized dashboard or leaderboard to compare model releases |
| **P3: Michael (Enterprise SecOps)** | System Administrator & Security | Ensure customer data and prompt inputs never leave private infrastructure | Cloud eval tools violate strict enterprise compliance rules       |

### 3.2 Key Use Cases

1. **Prompt Engineering Regression Testing:** Evaluate Prompt A vs. Prompt B against a 500-sample benchmark dataset prior to releasing to production.
2. **Model Upgrades (e.g., GPT-4o vs. Claude 3.5 Sonnet):** Run comparative pairwise evaluations to verify model switch quality.
3. **RAG Pipeline Optimization:** Measure context recall, faithfulness, and answer relevancy across retrieval strategies.
4. **Automated CI/CD Quality Gates:** Block pull requests if an evaluation score drops below defined thresholds.

---

## 4. Functional Requirements

### 4.1 Feature Breakdown

#### FR-1: Dataset Management & Immutable Versioning

- **FR-1.1:** Support CSV, JSON, and JSONL format dataset uploads up to 100MB per file.
- **FR-1.2:** Automatic schema validation verifying required columns (e.g., `input`, `expected_output`, `context`).
- **FR-1.3:** Create immutable `DatasetVersion` snapshots on every dataset update.
- **FR-1.4:** Provide dataset version comparison and diffing capabilities.

#### FR-2: Flexible Judge & Evaluation Engine

- **FR-2.1 G-Eval Engine:** Support G-Eval Chain-of-Thought auto-generation of scoring criteria and weighted evaluation.
- **FR-2.2 DeepEval & RAG Metrics:** Support Faithfulness, Answer Relevancy, Context Precision, and Context Recall metrics.
- **FR-2.3 Custom Rubric Judge:** Allow users to define custom judge prompts using Jinja2 templates and configurable scoring scales (1–5, 1–10, Pass/Fail).
- **FR-2.4 Pairwise LLM-as-a-Judge:** Support side-by-side model comparison with position bias mitigation (swap position scoring).

#### FR-3: Asynchronous Task Execution Pipeline

- **FR-3.1:** Asynchronous job dispatching using FastAPI, Celery, and Redis.
- **FR-3.2:** Priority queue routing (e.g., `high` priority for CI/CD runs, `default` for background batches).
- **FR-3.3:** Progress tracking with streaming updates over WebSockets / Server-Sent Events (SSE).
- **FR-3.4:** Configurable retry loops with exponential backoff for handling LLM provider rate limits (429s).

#### FR-4: Analytics, Visualizations & Leaderboards

- **FR-4.1:** Interactive evaluation run dashboard displaying overall score, pass/fail ratios, and metric distribution charts.
- **FR-4.2:** Side-by-side test case breakdown with response inspection and metric sub-scores.
- **FR-4.3:** Project leaderboard tracking model release quality over time.
- **FR-4.4:** CSV and JSON export of full run results and detailed judge explanations.

#### FR-5: SaaS Multi-Tenancy & Access Control

- **FR-5.1:** Organization and Workspace hierarchy for project grouping.
- **FR-5.2:** Role-Based Access Control (RBAC) supporting `Viewer`, `Member`, `Team Admin`, and `Org Admin` roles.
- **FR-5.3:** JWT authentication with bcrypt password hashing and token refresh mechanisms.
- **FR-5.4:** Team API key generation and management with usage metering hooks.

#### FR-6: Integrations & API Layer

- **FR-6.1:** Open API v3 spec compliant REST API endpoints.
- **FR-6.2:** Python SDK wrapper for programmatic evaluation triggers.
- **FR-6.3:** GitHub Actions integration example for workflow pipelines.

---

## 5. Non-Functional Requirements (NFRs)

### 5.1 Performance & Scalability

- **NFR-1.1:** Non-blocking async API handling using FastAPI and SQLAlchemy Async Engine.
- **NFR-1.2:** Horizontal worker scaling: worker nodes must scale independently based on Redis queue depth.
- **NFR-1.3:** PostgreSQL query response time < 50ms for page requests via indexed queries on `org_id`, `project_id`, and `run_id`.

### 5.2 Security & Data Privacy

- **NFR-2.1:** Zero telemetry requirement; full operation within air-gapped networks.
- **NFR-2.2:** Tenant isolation: Automatic database-level query scoping by `org_id` on all endpoints.
- **NFR-2.3:** API key hashing in database using SHA-256; plain-text keys shown only once upon creation.

### 5.3 Reliability & Availability

- **NFR-3.1:** Job recovery: Worker crash recovery via Redis task acknowledgment and dead-letter queues.
- **NFR-3.2:** Database transaction boundaries ensuring atomic updates to run status and metrics.

### 5.4 Observability & Maintainability

- **NFR-4.1:** Structured JSON logging using `structlog` with correlation `request_id` propagation.
- **NFR-4.2:** Prometheus metrics exporter for API request counts, worker queue lag, and LLM latency.

---

## 6. Release & Build Roadmap

| Phase        | Target Deliverable                                                                                                   | Status    |
| ------------ | -------------------------------------------------------------------------------------------------------------------- | --------- |
| **Phase 1**  | Core Monorepo Setup, FastAPI Gateway, PostgreSQL Schemas                                                             | Completed |
| **Phase 2**  | React 18 + Vite SPA, UI Component System, Auth Flow                                                                  | Completed |
| **Phase 3**  | Dataset Storage, Validation, Immutable Versioning                                                                    | Completed |
| **Phase 4**  | `JudgeBase` Abstract Engine & Provider System                                                                        | Completed |
| **Phase 5**  | G-Eval Chain-of-Thought & Custom Rubrics                                                                             | Completed |
| **Phase 6**  | Celery Async Task Execution, Priority Queues, Redis Broker                                                           | Completed |
| **Phase 7**  | RAG Metric Suite (Faithfulness, Relevancy, Recall)                                                                   | Completed |
| **Phase 8**  | Real-time Dashboard, WebSocket Progress, Recharts                                                                    | Completed |
| **Phase 9**  | Leaderboards & Side-by-side Comparative Viewers                                                                      | Completed |
| **Phase 10** | REST API Key System, CLI Tool, GitHub Actions CI/CD                                                                  | Completed |
| **Phase 11** | Organization Multi-Tenancy & RBAC Enforcement                                                                        | Completed |
| **Phase 12** | Observability (Prometheus + Grafana), Security Hardening                                                             | Completed |
| **Phase 16** | Kalvium Concept Coverage: Docker Containerization, Redis Caching, WebSocket Real-time Updates, Scheduled Jobs / Cron | Completed |

---

## 7. Assumptions & Dependencies

- Docker and Docker Compose (v2.20+) available on target execution environment.
- Access to OpenAI, Anthropic, or local Ollama endpoints for LLM judge calls.
- PostgreSQL 16+ and Redis 7+ services.

---

## 8. Kalvium Mandatory Concept Compliance Matrix

The following table maps every mandatory Kalvium concept to its specification and implementation within EvalForge:

| #   | Mandatory Concept              | Architectural Scope           | Primary Implementation Location                                                                                                                                | Compliance Status |
| --- | ------------------------------ | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| 1   | **LLM API Integration**        | Backend Multi-Provider Engine | [`backend/app/evaluation/providers/`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/evaluation/providers)                                     | ✅ Implemented    |
| 2   | **Prompt Engineering**         | System Prompts & Rubrics      | [`backend/app/evaluation/prompts/`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/evaluation/prompts)                                         | ✅ Implemented    |
| 3   | **Structured Outputs**         | Pydantic JSON Schemas         | [`backend/app/schemas/`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/schemas)                                                               | ✅ Implemented    |
| 4   | **HTTP Status Codes**          | REST API Endpoints            | [`backend/app/api/v1/endpoints/`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/api/v1/endpoints)                                             | ✅ Implemented    |
| 5   | **Middleware**                 | Gateway Pipelines             | [`backend/app/main.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/main.py)                                                                | ✅ Implemented    |
| 6   | **Problem Modeling**           | DB Domain Entities            | [`backend/app/models/`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/models)                                                                 | ✅ Implemented    |
| 7   | **RESTful Endpoint Design**    | Gateway Routing               | [`backend/app/api/v1/router.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/api/v1/router.py)                                              | ✅ Implemented    |
| 8   | **Server-side Error Handling** | Global Handlers               | [`backend/app/core/exceptions.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/core/exceptions.py)                                          | ✅ Implemented    |
| 9   | **System Design**              | Full-stack Architecture       | [`ARCHITECTURE.md`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/ARCHITECTURE.md), [`HLD.md`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/HLD.md) | ✅ Implemented    |
| 10  | **Environment Variables**      | Configuration Engine          | [`backend/app/config/config.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/config/config.py)                                              | ✅ Implemented    |
| 11  | **Secrets Management**         | Security Layer                | [`backend/app/core/security.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/core/security.py)                                              | ✅ Implemented    |
| 12  | **Git Workflow**               | Repo Governance               | [`CONTRIBUTING.md`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/CONTRIBUTING.md)                                                                        | ✅ Implemented    |
| 13  | **Async Data Fetching**        | React Query SPA               | [`frontend/src/services/api.ts`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/services/api.ts)                                              | ✅ Implemented    |
| 14  | **Client-side Routing**        | React Router v6               | [`frontend/src/App.tsx`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/App.tsx)                                                              | ✅ Implemented    |
| 15  | **JavaScript async/await**     | Frontend Async Layer          | [`frontend/src/services/api.ts`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/services/api.ts)                                              | ✅ Implemented    |
| 16  | **JavaScript Closures**        | Stateful Factories            | [`frontend/src/utils/closures.ts`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/utils/closures.ts)                                          | ✅ Implemented    |
| 17  | **JavaScript Event Loop**      | Micro/Macrotask Queue         | [`frontend/src/utils/eventLoop.ts`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/utils/eventLoop.ts)                                        | ✅ Implemented    |
| 18  | **JavaScript Hoisting**        | Compilation Scoping           | [`frontend/src/utils/hoisting.ts`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/utils/hoisting.ts)                                          | ✅ Implemented    |
