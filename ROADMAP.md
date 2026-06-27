# EvalForge Roadmap

This document outlines the milestones and release goals for EvalForge.

## Phase 1: Foundation (Current)
- [x] Initial monorepo layout setup
- [x] Backend FastAPI architecture base
- [x] Frontend React + TS client environment
- [x] Prettier, ESLint, Ruff, and Black configuration
- [x] Docker and Docker Compose orchestration
- [x] GitHub templates and CI actions

## Phase 2: Database Schema & Core Models (Upcoming)
- [ ] Alembic database migration system initialization
- [ ] Core DB entities definition (runs, datasets, configurations, users)
- [ ] Repository pattern layers for data access
- [ ] Pydantic request/response schema specifications
- [ ] Redis caching layers for metadata retrieval

## Phase 3: Core Evaluation Engine
- [ ] Implementation of G-Eval evaluation runner
- [ ] LLM-as-a-Judge API configurations
- [ ] RAG evaluation suite (faithfulness, answer relevance, context recall)
- [ ] Task runner integrations (Celery or custom async workers)
- [ ] SDK bindings for Python and Node clients to push metrics directly

## Phase 4: Developer Console & UI Dashboard
- [ ] Landing view for run comparisons
- [ ] Run inspector with side-by-side prompt output viewer
- [ ] Metric charting and regression tracking graphs
- [ ] Golden dataset uploads and editor interfaces
- [ ] Configuration manager for judges and evaluation criteria
