# EvalForge v1.0.0 Release & Launch Assets

This document contains pre-packaged marketing copy, release notes, and social media launch assets.

---

## 1. Launch & Release Checklists

### 1.1 Pre-Release Checklist
- [x] All unit and integration tests passing (`pytest` / linting check).
- [x] Hardcoded secrets removed; verify correct handling of `.env` configurations.
- [x] Documentation review complete (README, ARCHITECTURE, CONTRIBUTING).
- [x] Version numbers bumped across monorepo package files.
- [x] Create v1.0.0 tag and push.

### 1.2 Product Hunt Checklist
- [ ] Upload Product Hunt logo (800x800) and promotional screenshots.
- [ ] Prepare YouTube demo walkthrough video.
- [ ] Draft hunter invitation copy.
- [ ] Launch on scheduled launch date (Tuesday, 12:01 AM PST).

---

## 2. Social Media Threads

### 2.1 Twitter/X Launch Thread
```text
1/ 🚀 Introducing EvalForge v1.0.0 — the open-source, developer-first LLM evaluation platform!

Unify G-Eval, DeepEval, RAG metrics, and custom LLM-as-a-Judge rubrics under a single, high-performance UI.

100% self-hosted. 100% private. 

Let's dive in 👇

[Link to Repo]

2/ Standard software engineering relies on automated tests on every commit. Why is LLM app development any different?

EvalForge makes evaluations a first-class citizen in your CI/CD. Trigger dataset evaluation runs on every commit, prompt, or model change.

3/ Under the hood:
⚡ FastAPI backend with async SQLAlchemy 2.0 & PostgreSQL
⚙️ Decoupled judge adapter pattern (G-Eval, DeepEval, rubrics)
📦 Celery workers for async queue management
📊 Recharts metrics dashboard, compare UI, and PDF report generator

4/ Getting started takes 1 command:
$ docker compose up -d --build

Zero external dependencies. Runs PostgreSQL, Redis, Celery, and the web console immediately.

5/ We've also shipped typed SDKs for Python, TypeScript, Go, and Java, alongside a clean CLI.

Trigger evals directly from your Python terminal:
from evalforge import Client
client = Client(api_key="...")
run = client.run_evaluation(dataset_id="...", judge="g-eval")

6/ Whether you are building RAG apps, agents, or structured extractors, EvalForge brings rigorous, reproducible benchmarking to your stack.

Give us a star on GitHub 🌟, read our guides, and join the community!

[Link to Repo]
```

### 2.2 LinkedIn Announcement
```text
🚀 Exciting News! Today we are officially launching EvalForge v1.0.0, an open-source, production-grade LLM evaluation platform designed for AI engineers and developers!

EvalForge replaces spreadsheets and fragile, custom scripts with a unified, self-hosted console. Bring G-Eval, RAG triaging (context recall, precision, faithfulness), and custom LLM-as-a-Judge prompt templates under a single developer interface.

Key Features:
- Asynchronous task management using Celery and Redis to handle large dataset runs.
- Multi-tenant Organization scoping, RBAC roles, and invitation token workflows.
- Developer SDKs in Python, TS, Go, and Java to easily integrate evaluations into CI/CD.
- Interactive visualization console showing score histograms, comparisons, and leaderboard rankings.

Setup is completely self-contained with a single docker-compose command.

A massive thank you to everyone who contributed to our early beta phases. Check out the project on GitHub, star the repository, and let us know what you think! 🌟

#OpenSource #LLM #FastAPI #React #GenerativeAI #AIPlatform #SoftwareEngineering
```

---

## 3. Product Walkthrough & Demo Script

### 3.1 Setup Section
1. Run `docker compose up -d` in the terminal.
2. Show the startup logs highlighting PostgreSQL database migrations completing and Celery workers connecting to Redis.

### 3.2 UI Demo Flow
1. Open `http://localhost:5173` and register a developer account.
2. Show the dashboard, highlighting the default workspace and the Projects section.
3. Upload a golden dataset (CSV format) and review the column mapping UI.
4. Launch a new evaluation run, choosing G-Eval as the judge.
5. Navigate to the Run Detail page, showing the live progress bar (WebSockets) as cases are scored.
6. Open the Radar chart and score histogram to analyze output metrics.
7. Show the side-by-side model output compare view highlighting score deltas.
