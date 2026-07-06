# EvalForge Roadmap

This document outlines the engineering milestones, historical build phases, and future goals for EvalForge.

---

## 🚀 Version 1.0.0: Core Build Phases (Completed)

### Phase 1: Foundation
- [x] Monorepo structure setup (`frontend`, `backend`, `docs`, `docker`)
- [x] FastAPI base app factory and React + Vite shell configuration
- [x] Linter and formatter tooling integration (`ruff`, `eslint`, `prettier`)
- [x] Docker Compose multi-service local environment

### Phase 2: Backend Core & Auth
- [x] Alembic migration engine with async PostgreSQL driver
- [x] ORM database entities (User, Org, Team, Project, Dataset, Run)
- [x] JWT authentication with refresh token rotation and BCrypt hashes
- [x] Role-Based Access Control (RBAC) middleware per route

### Phase 3: Evaluation Engine
- [x] Pluggable `JudgeBase` base architecture
- [x] Jinja2 templating system for metrics and judges
- [x] G-Eval evaluation runner with Chain-of-Thought scoring
- [x] DeepEval metric integration (Faithfulness, Relevancy, Recall)

### Phase 4: Dataset Management
- [x] Immutable version control for datasets
- [x] Column mapping parsing for CSV and JSON format uploads
- [x] File storage management and record preview APIs

### Phase 5: Developer Console UI
- [x] User registration, login, and profile administration pages
- [x] Project workspace list and run history table with sparklines
- [x] Side-by-side run difference highlighting and comparison inspector
- [x] Dataset upload wizards and record preview grids

### Phase 6: Asynchronous Jobs
- [x] Decoupled Celery worker architecture with Redis queues
- [x] Priority task queues (CI/CD high priority vs manual default)
- [x] Progress reporting over WebSockets and Server-Sent Events (SSE)
- [x] Partial completion handling and failed run retry engine

### Phase 7: Analytics & Reports
- [x] Interactive score distribution histograms (Recharts)
- [x] Multi-run metric radar charts
- [x] PDF summary reports generation
- [x] Paginated CSV/JSON data exporter

### Phase 8: Advanced Evaluations
- [x] Contextual precision and context recall metrics for RAG
- [x] Pairwise comparison engine (LLM winrate evaluation tournaments)
- [x] Custom metric builders using custom rubrics
- [x] Content safety/toxicity evaluation filters

### Phase 9: Production Engineering
- [x] Production Docker Compose with health probes and resource limits
- [x] Structlog structured JSON logging with request tracing
- [x] Prometheus metrics collector and custom Grafana dashboard templates
- [x] Rate limiter and secure request validation middleware

### Phase 10: API Platform & SDKs
- [x] Public API endpoint namespace `/api/v1/public/`
- [x] Scoped API key administration (Read/Write/Admin)
- [x] Fully typed SDK libraries for Python, TypeScript, Go, and Java
- [x] OpenAPI Swagger documentation generation

### Phase 11: Enterprise SaaS
- [x] Multi-tenant organization boundaries and project workspace scoping
- [x] Team invitation workflow via secure email tokens
- [x] Usage metering hooks and run limit controls
- [x] Feature plans configuration (Free, Pro, Enterprise tiers)

### Phase 12: Launch & Release (Current)
- [x] Repository audit and code quality cleanup
- [x] World-class documentation overhaul
- [x] Version 1.0.0 tagging and launch assets preparation

---

## 🔮 Version 2.0.0: Future Roadmap (Concepts only, not implemented)

### 1. Agentic Evaluations
- **Multi-Agent Red Teaming**: Deploy automated agent squads designed to actively search for vulnerabilities, edge cases, and jailbreaks in target model configurations.
- **Interactive Evaluation Loop**: Allow judges to ask follow-up questions to the model under test to probe depth of knowledge and confidence limits.

### 2. Closed-Loop Fine-Tuning Integration
- **Auto-SFT Pipeline Exports**: Automatically export evaluation runs that fall below threshold scores into structured Supervised Fine-Tuning (SFT) or DPO formats to retrain and improve candidate models.
- **Dataset Generation**: Use high-scoring evaluation outputs to expand ground-truth datasets synthetically.

### 3. Edge & Local Evaluation Support
- **Local Judge Runner**: Support offline running of light judges (e.g., Llama-3-8B-Instruct or specialized Qwen models) using local Ollama or llama.cpp setups, guaranteeing zero API costs and absolute data confidentiality.
- **WebGPU Judges**: Run client-side visual and linguistic checks directly in the browser console.

### 4. Git-Native Continuous Evaluation (GitOps)
- **Git Commit Hooks**: Block commits locally if evaluation checks on candidate prompts fail quality criteria.
- **Auto Pull Request Reports**: Automatically run evaluations on prompt changes and post comparison reports as comments inside GitHub Pull Requests.

### 5. Production Observability Loop
- **Gateway Evaluations**: Sample live traffic directly from API Gateways to run silent background evaluations on actual production query-response pairs.
- **Drift Alerting**: Trigger automated system Slack or PagerDuty alerts when production response alignment drifts from original golden datasets.
