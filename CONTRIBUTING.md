# Contributing to EvalForge 🚀

Welcome to the **EvalForge** contributor community! We are thrilled to have you here. EvalForge is an open-source, production-grade evaluation platform designed to automate LLM testing, benchmarking, and quality assurance for AI engineering teams worldwide.

Whether you are fixing a typo, adding a new LLM judge metric, writing tests, or improving UI components, your contributions are invaluable to shaping the future of AI engineering tools.

---

## Table of Contents

1. [Welcome Message](#1-welcome-message)
2. [Project Vision](#2-project-vision)
3. [Repository Architecture](#3-repository-architecture)
4. [Local Development Setup](#4-local-development-setup)
5. [Environment Variables](#5-environment-variables)
6. [Installation](#6-installation)
7. [Running Locally](#7-running-locally)
8. [Running Tests](#8-running-tests)
9. [Linting](#9-linting)
10. [Formatting](#10-formatting)
11. [Branch Naming Convention](#11-branch-naming-convention)
12. [Conventional Commit Guide](#12-conventional-commit-guide)
13. [Pull Request Process](#13-pull-request-process)
14. [Coding Standards](#14-coding-standards)
15. [Folder Organization](#15-folder-organization)
16. [Testing Expectations](#16-testing-expectations)
17. [Documentation Expectations](#17-documentation-expectations)
18. [Issue Workflow](#18-issue-workflow)
19. [Review Process](#19-review-process)
20. [Communication Channels](#20-communication-channels)
21. [First Contribution Guide](#21-first-contribution-guide)
22. [Good First PR Walkthrough](#22-good-first-pr-walkthrough)
23. [Contributor Recognition](#23-contributor-recognition)

---

## 1. Welcome Message

EvalForge is maintained by developers, for developers. We foster an inclusive, welcoming, and collaborative environment. No contribution is too small! If this is your first time contributing to open source, we are here to support you step-by-step.

---

## 2. Project Vision

Our vision is to build the definitive open-source infrastructure for LLM quality assurance:
- **100% Data Privacy & Self-Hostable:** Developers should be able to run benchmarks locally without sending data to third-party SaaS vendors.
- **Framework Agnostic:** First-class support for G-Eval, DeepEval, RAG metrics, and custom Jinja2 rubrics.
- **Reproducible Evaluation:** Immutable dataset versioning and snapshot-pinned evaluation runs.
- **CI/CD Native:** Seamless integration with GitHub Actions, GitLab CI, and automated deployment checks.

---

## 3. Repository Architecture

EvalForge is structured as a high-performance monorepo:

```
Eval-Forge/
├── backend/                  # FastAPI 0.115+ Python backend gateway & services
│   ├── app/
│   │   ├── api/v1/          # RESTful routing endpoints & controllers
│   │   ├── config/          # Pydantic BaseSettings & env validation
│   │   ├── core/            # Middleware, Security, DB session, Redis manager
│   │   ├── evaluation/      # LLM judge engine, G-Eval, multi-provider drivers
│   │   ├── jobs/            # Celery async worker tasks & Cron scheduler
│   │   └── models/          # SQLAlchemy 2.0 async database models
│   └── tests/               # Pytest suite (40+ unit & integration tests)
├── frontend/                 # React 18 + Vite + TypeScript + Tailwind CSS SPA
│   ├── src/
│   │   ├── components/      # UI components & status badges
│   │   ├── hooks/           # Custom React hooks (useJobWebSocket, etc.)
│   │   ├── pages/           # Dashboard, Datasets, Evaluations, Benchmarks
│   │   ├── services/        # Axios API client & mock storage fallbacks
│   │   └── utils/           # Closures, Event Loop schedulers, Hoisting helpers
├── docker/                   # Production multi-stage Dockerfiles & Nginx configs
├── docs/                     # Architecture, HLD, LLD, PRD, and Contributor Guides
└── .github/                  # CI/CD workflows, issue templates, PR template
```

---

## 4. Local Development Setup

### Prerequisites
- **Python 3.12+**
- **Node.js 20+ & npm 10+**
- **Docker & Docker Compose** (optional but recommended for full stack container testing)
- **Git 2.40+**

### Automated Setup Script
Run our developer onboarding script to configure your environment automatically:

```bash
# macOS / Linux
chmod +x scripts/setup-dev-env.sh
./scripts/setup-dev-env.sh

# Windows (PowerShell)
.\scripts\setup-dev-env.ps1
```

---

## 5. Environment Variables

EvalForge uses strict environment variable validation via Pydantic (`BaseSettings`) and Vite `import.meta.env`.

Copy the sample environment files:
```bash
# Root & Backend
cp .env.example .env
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

Key environment variables:
| Variable | Default Value | Description |
|---|---|---|
| `APP_ENV` | `development` | Application runtime environment (`development`, `production`, `testing`) |
| `DATABASE_URL` | `postgresql+asyncpg://evalforge:evalforge_pass@localhost:5432/evalforge_db` | Async SQLAlchemy PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis caching & Celery message broker URL |
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Frontend API gateway base endpoint |
| `OPENAI_API_KEY` | `sk-placeholder` | Optional OpenAI API key for LLM judge evaluation |

---

## 6. Installation

### Backend Dependencies
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
npm install --legacy-peer-deps
```

---

## 7. Running Locally

### Option A: Docker Compose (Full Stack)
To launch all services (FastAPI, React UI, PostgreSQL, Redis, Celery Worker, Cron Scheduler):
```bash
docker compose up --build
```
- **Web UI:** `http://localhost:5173` (or `http://localhost:3000`)
- **API Swagger Docs:** `http://localhost:8000/docs`
- **API Health Probe:** `http://localhost:8000/health`

### Option B: Local Microservices (Manual)

1. **Start FastAPI Backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start React Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

---

## 8. Running Tests

We require test coverage for all bug fixes and new features.

### Backend Pytest Suite
```bash
cd backend
pytest
```
To run tests with verbosity and print statements:
```bash
pytest -v -s
```

### Frontend Typecheck & Build Validation
```bash
cd frontend
npm run typecheck
npm run build
```

---

## 9. Linting

We enforce strict static analysis to maintain production quality.

### Backend Linting (Ruff)
```bash
cd backend
ruff check .
```

### Frontend Linting (ESLint)
```bash
cd frontend
npm run lint
```

---

## 10. Formatting

### Python Formatting (Black & Ruff)
```bash
cd backend
black --check .
ruff check --fix .
```
To auto-format python code:
```bash
black .
```

### Frontend Formatting (Prettier)
```bash
cd frontend
npx prettier --check "src/**/*.{ts,tsx,css,json,md}"
```
To auto-format frontend code:
```bash
npx prettier --write "src/**/*.{ts,tsx,css,json,md}"
```

---

## 11. Branch Naming Convention

We use descriptive, prefix-based branch names:

- `feature/<short-description>`: New functionality
- `fix/<short-description>`: Bug fixes
- `docs/<short-description>`: Documentation changes
- `refactor/<short-description>`: Code refactoring
- `test/<short-description>`: Adding or modifying test suites

### Real Examples:
- `feature/api-auth`
- `feature/g-eval-engine`
- `fix/windows-path`
- `docs/update-readme`
- `refactor/evaluation-engine`

---

## 12. Conventional Commit Guide

Commits must follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification:

Format: `<type>(<scope>): <description>`

### Standard Types:
- `feat`: A new feature for the user or system
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect code logic (white-space, formatting)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Updating build tasks, package manager configs, or dependencies

### Examples:
- `feat(eval): add DeepSeek-V3 LLM judge provider`
- `fix(ws): resolve WebSocket reconnection exponential backoff memory leak`
- `docs(api): add OpenAPI parameter descriptions for dataset version upload`
- `test(redis): add integration tests for sliding window rate limiter`

---

## 13. Pull Request Process

1. **Fork & Branch:** Fork the repository and create your feature branch from `main`.
2. **Implement & Test:** Write your changes and add corresponding unit/integration tests.
3. **Verify Locally:** Run linting, typechecking, tests, and formatting checks locally.
4. **Submit PR:** Open a Pull Request against `main` using our [Pull Request Template](.github/pull_request_template.md).
5. **Link Issues:** Include `Closes #123` or `Fixes #456` in your PR description.
6. **Code Review:** Address any comments or requested revisions from maintainers.
7. **Merge:** Once approved and CI checks pass, a maintainer will merge your PR via squash-and-merge.

---

## 14. Coding Standards

- **Python (Backend):**
  - Use Python 3.12+ type hints (`str | None`, `list[dict]`).
  - Use SQLAlchemy 2.0 async syntax (`select(Model).where(...)`).
  - Prefer `structlog` structured logging over standard `print()`.
  - Handle exceptions gracefully using custom app exception classes in `app.core.exceptions`.

- **TypeScript / React (Frontend):**
  - Use functional components with hooks (`useState`, `useEffect`, `useCallback`, `useMemo`).
  - Do NOT use `any`. Always define explicit TypeScript interfaces/types.
  - Follow modular Tailwind CSS styling patterns; avoid inline static style hacks.
  - Ensure zero console errors or unhandled promise rejections.

---

## 15. Folder Organization

```
backend/app/
├── api/v1/endpoints/   # Single-responsibility route handlers
├── config/             # Environment & app configurations
├── core/               # Cross-cutting concerns (auth, caching, middleware)
├── evaluation/         # LLM evaluation engine & provider drivers
├── jobs/               # Background task queues & cron managers
├── models/             # SQLAlchemy ORM models
└── schemas/            # Pydantic request/response schemas
```

---

## 16. Testing Expectations

- **Coverage Goal:** Every new route, service function, or utility should include test coverage.
- **Backend Tests:** Located in `backend/tests/`. Use `pytest` fixtures provided in `conftest.py`.
- **Determinism:** Tests must be idempotent and pass cleanly without relying on external network connectivity (mock external LLM APIs using `unittest.mock` or `requests-mock`).

---

## 17. Documentation Expectations

- If your PR introduces a new API endpoint, update `docs/` and add docstrings to the route function.
- If your PR adds a new feature or environment variable, update `README.md` and `.env.example`.
- Keep architectural diagrams in `ARCHITECTURE.md`, `HLD.md`, and `LLD.md` up to date when changing core abstractions.

---

## 18. Issue Workflow

1. Search existing issues before creating a new one to avoid duplicates.
2. Use the structured issue templates in `.github/ISSUE_TEMPLATE/`.
3. If you'd like to work on an unassigned issue, comment `I'd like to work on this!` so a maintainer can assign it to you.
4. Issues tagged with `good first issue` are reserved for first-time contributors.

---

## 19. Review Process

- PRs are reviewed within **24–48 hours** by core maintainers.
- Reviews evaluate: architectural fit, test coverage, static analysis, performance impact, and security.
- Maintainers may leave inline suggestions or request changes. Please respond to feedback politely and constructively.

---

## 20. Communication Channels

Stay connected with the EvalForge core team and community:
- **GitHub Discussions:** Ask questions, share ideas, and present RFC proposals in [GitHub Discussions](https://github.com/hardikkaurani/Eval-Forge/discussions).
- **Issue Tracker:** Report verified bugs or suggest features via [GitHub Issues](https://github.com/hardikkaurani/Eval-Forge/issues).
- **Security Inquiries:** Contact security maintainers privately via `security@evalforge.dev`.

---

## 21. First Contribution Guide

Looking for a place to start? Follow these steps:

1. Browse issues tagged [`good first issue`](https://github.com/hardikkaurani/Eval-Forge/issues?q=is%3Aissue+is%3Aopen+label%3A"good+first+issue").
2. Check out our catalog of 30 curated contributor tasks in [`docs/CONTRIBUTOR_ISSUES_CATALOG.md`](docs/CONTRIBUTOR_ISSUES_CATALOG.md).
3. Comment on the issue to request assignment.
4. Clone the repository and run `./scripts/setup-dev-env.sh` (or `.\scripts\setup-dev-env.ps1`).
5. Complete the task, run tests, and open your PR!

---

## 22. Good First PR Walkthrough

Here is an example of creating a clean fix for a "good first issue":

```bash
# 1. Update your local main branch
git checkout main
git pull origin main

# 2. Create a dedicated topic branch
git checkout -b fix/websocket-reconnect-badge

# 3. Make your changes in code
# (e.g. edit frontend/src/components/common/WebSocketStatusBadge.tsx)

# 4. Verify formatting, linting, and tests
cd frontend
npm run lint
npm run typecheck
npx prettier --check "src/**/*.{ts,tsx,css,json,md}"

cd ../backend
pytest

# 5. Commit with conventional commit syntax
git add .
git commit -m "fix(ui): resolve status badge icon alignment on reconnection failure"

# 6. Push to your fork and create PR
git push origin fix/websocket-reconnect-badge
```

---

## 23. Contributor Recognition

We believe in celebrating our community! All contributors are recognized in:
- The **EvalForge Leaderboard & README** section.
- GitHub's native contributor graph.
- Our quarterly **Release Notes** (`docs/RELEASE_NOTES_v1.0.0.md`).

Thank you for helping us make LLM application testing reliable, accessible, and production-grade for everyone! 🚀
