# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-07

### Added
- **Enterprise SaaS Module**: Integrated multi-tenant organization boundaries, workspace isolation, user roles (Admin, Team Admin, Member, Viewer), email-based invitation tokens, usage tracking, billing-ready API schemas, and feature-flagged plans (Free, Pro, Enterprise).
- **Developer Platform Features**: Implemented public versioned REST API, API key generation with bcrypt hashing, a command-line interface (CLI) for local/remote pipelines, native client SDKs (Python, TypeScript, Go, Java), custom metric rubrics via Jinja2 prompt layouts, and standard playground integrations.
- **RAG & Advanced Evaluation Pipeline**: Support for Contextual Precision, Contextual Recall, Faithfulness, Answer Relevancy, Hallucination checks, winrate-based pairwise tournaments, and custom judge configurations.
- **Asynchronous Task Architecture**: Fully decoupled FastAPI and Celery worker threads communicating via Redis queues with priority queues, dead-letter routing, and real-time WebSocket progress alerts.
- **Comprehensive Database Schema**: Stable migration schema with Alembic tracking users, orgs, teams, datasets, versions, evaluation runs, and individual test cases.
- **Enhanced Observability**: Structured JSON logs using `structlog`, Prometheus metrics exporter, and pre-packaged Grafana dashboards monitoring queue latency and API metrics.

### Changed
- Promoted all APIs from experimental status to stable `/api/v1` namespace.
- Improved frontend user dashboard UI with Recharts-based score distribution histograms, delta sparklines, and side-by-side run comparisons.

### Fixed
- Fixed concurrent connection leaks in async SQLAlchemy session sessions.
- Resolved type-checking errors for TrendItems and analytics route handlers.

## [0.1.0] - 2026-06-27

### Added
- Monorepo folder setup separating `frontend`, `backend`, `docs`, `examples`, `datasets`, `docker`, `scripts`, `tests`, and `.github` templates.
- FastAPI project shell with async database sessions (SQLAlchemy), CORS configuration, and structured logging setup.
- React, TypeScript, and Vite frontend workspace with customized vanilla styling, developer status monitor page, and ESLint/Prettier code quality integrations.
- GitHub Action CI workflows for automated linting, checking formatting, and builds on commits and pull requests.
- Configuration for dockerized deployments using `docker-compose.yml` supporting `postgres` and `redis` health checks.
- Professional markdown templates for issue reporting, security, pull requests, roadmap, and contributing standards.
