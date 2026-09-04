# EvalForge v1.0.0 Release Notes

**Release Date:** August 5, 2026  
**Status:** General Availability (GA) — Production Ready

EvalForge v1.0.0 is the inaugural public release of the enterprise-grade, production-ready LLM evaluation platform. This landmark release brings full self-hosting capabilities, single-click deployment configurations for Vercel and Railway, multi-provider evaluation pipelines, and complete organizational multi-tenancy.

---

## 🌟 What's New in v1.0.0

### 1. Cloud & One-Command Production Deployment

- **Vercel Frontend Integration**: Full SPA client routing support with `vercel.json` rewrites and `VITE_API_URL` environment binding.
- **Railway Backend & Database Integration**: Native support for Railway PostgreSQL and Railway Redis, dynamic `$PORT` binding, and automatic DB scheme normalization (`postgres://` to `postgresql+asyncpg://`).
- **Production Docker Compose**: Optimized multi-stage Dockerfiles for backend and frontend with non-root security defaults and SPA Nginx routing.

### 2. Multi-Provider LLM & Judge Abstraction Engine

- Unified judge interface (`JudgeBase`) supporting:
  - **G-Eval**: Multi-criteria weighted scoring with structured reasoning.
  - **Pairwise Judge**: Comparative win/loss ELO rating.
  - **Rubric-based Judge**: Schema-enforced custom rubric evaluation.
  - **Reference-based Judge**: Lexical, semantic, and exact-match reference benchmarks.
- Support for OpenAI, Anthropic Claude, Google Gemini, OpenRouter, DeepSeek, Cohere, NVIDIA NIM, and local Ollama instances.

### 3. Versioned Immutable Datasets & Benchmarks

- Upload datasets via CSV/JSON with automatic schema validation.
- Every dataset mutation creates an immutable version snapshot.
- Benchmarks group multiple dataset versions for standardized evaluation runs.

### 4. Enterprise SaaS & Multi-Tenancy Engine

- Organizations, Workspaces, and RBAC permissions (Owner, Admin, Member, Viewer).
- Scoped API key management with usage quota tracking and audit logs.
- Stripe subscription integration and plan enforcement hooks.

### 5. High-Performance Asynchronous Architecture

- Async SQLAlchemy 2.0 connection pooling with pre-ping health checks.
- Structured JSON logging with request correlation IDs (`X-Request-ID`).
- Comprehensive health probes (`/health`, `/api/v1/health`, `/api/v1/ready`, `/api/v1/live`).

---

## 🚀 Deployment Instructions

- **Deployment Guide**: [docs/deployment_guide.md](file:///docs/deployment_guide.md)
- **Environment Template**: [.env.example](file:///.env.example)

---

## 📋 Production Readiness Verification Checklist

| Area     | Component          | Status      | Notes                                                  |
| -------- | ------------------ | ----------- | ------------------------------------------------------ |
| Frontend | Vercel Deployment  | ✅ Verified | SPA routes fallback to `index.html` via `vercel.json`  |
| Backend  | Railway FastAPI    | ✅ Verified | Dynamic `$PORT` binding & automatic Alembic migrations |
| Database | Railway PostgreSQL | ✅ Verified | `postgresql+asyncpg://` scheme normalization active    |
| Redis    | Railway Redis      | ✅ Verified | Connection pool pinging & graceful reconnect logic     |
| Security | Headers & CORS     | ✅ Verified | Restricted `CORS_ORIGINS` & production secret checks   |
| Docker   | Multi-stage        | ✅ Verified | Non-root `appuser` (8888) & non-root `nginx` users     |
| Tests    | Unit & Integration | ✅ Verified | 37/37 backend tests passed, zero type errors           |

---

## 👥 Contributors & Maintainers

Special thanks to all early contributors, maintainers, and community testers who helped shape EvalForge v1.0.0.

- **Repository**: [https://github.com/hardikkaurani/Eval-Forge](https://github.com/hardikkaurani/Eval-Forge)
- **License**: MIT
