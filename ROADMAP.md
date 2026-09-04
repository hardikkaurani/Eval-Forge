# EvalForge Product & Community Roadmap (v1.x – v2.0)

**Document Version:** 1.1.0  
**Status:** Active Roadmap  
**Target Community Goals:** 10,000+ Stars, 100+ Active Contributors, Global AI QA Standard

---

## 🗺️ Strategic Product Vision

EvalForge is building the definitive open-source platform for continuous LLM evaluation, prompt benchmarking, and AI application QA. Our roadmap balances feature velocity with open-source community growth.

```
       Phase 1 (v1.0)                 Phase 2 (v1.5)                 Phase 3 (v2.0)
┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────────┐
│   Core Monorepo & SPA    │   │  Extended Drivers & CLI  │   │ Enterprise Scale & Edge  │
│                          │   │                          │   │                          │
│ • FastAPI Backend        │──►│ • DeepSeek-V3 Driver     │──►│ • Distributed Workers    │
│ • React 18 UI Console    │   │ • EvalForge PyPI CLI     │   │ • Multi-Region Scaling   │
│ • PostgreSQL + Redis     │   │ • GitHub Actions Action  │   │ • Native Ollama Edge     │
│ • G-Eval & Custom Rubric │   │ • RAG Faithfulness Suite │   │ • Real-time Streaming    │
└──────────────────────────┘   └──────────────────────────┘   └──────────────────────────┘
```

---

## 🚀 Released Phases (v1.0.0 Baseline)

- [x] **Core Monorepo Setup:** FastAPI Gateway, SQLAlchemy Async Engine, React 18 SPA.
- [x] **Multi-Provider LLM Engine:** OpenAI, Anthropic Claude, Google Gemini, Ollama Local support.
- [x] **Evaluation Frameworks:** G-Eval (Chain-of-Thought), Custom Jinja2 Rubrics, Pairwise Comparisons.
- [x] **Immutable Versioning:** Snapshot-pinned dataset versioning and experiment execution history.
- [x] **Real-time Engine:** WebSocket progress streaming, Redis job queues, Periodic Cron Scheduler.
- [x] **Enterprise SaaS Hardening:** API key SHA-256 hashing, Security Headers, Rate Limiting middleware.
- [x] **Kalvium Concept Compliance:** 100% verified compliance across all 18 core software architecture concepts.

---

## 🎯 Upcoming Releases & Contributor Opportunities

### Q3 2026 — Release 1.2: Community & Developer Experience

- [ ] **EvalForge PyPI CLI Package (`evalforge-cli`):** Standalone Python CLI for triggering benchmark runs from local terminals.
- [ ] **GitHub Actions Custom Action (`evalforge/eval-action@v1`):** Drop-in GitHub Action for automated CI/CD PR regression checks.
- [ ] **DeepSeek-V3 & DeepSeek-R1 Driver:** First-class provider integration for DeepSeek models.
- [ ] **RAG Metric Suite Expansion:** Context Precision, Context Recall, and Faithfulness scoring engines.
- [ ] **OpenTelemetry Export:** Exporting evaluation metrics and judge traces to Jaeger, Zipkin, and Datadog.

### Q4 2026 — Release 1.5: Advanced Leaderboards & Fine-Tuning

- [ ] **AlpacaEval Pairwise Leaderboards:** Interactive side-by-side model comparison views.
- [ ] **Export to HuggingFace Datasets:** One-click export of red-team dataset versions to HuggingFace.
- [ ] **Automated Dataset Synthesizer:** Synthetic dataset record generation powered by LLMs.
- [ ] **Multi-Tenant SSO & SAML 2.0:** Enterprise Okta / Auth0 single sign-on integration.

### Q1 2027 — Release 2.0: Distributed Scale & Multi-Region Execution

- [ ] **Distributed Ray / Celery Cluster Scaling:** Support for 50,000+ concurrent judge evaluations.
- [ ] **On-Device Local Judge Execution:** Direct integration with vLLM and llama.cpp local inferencing.
- [ ] **Real-time Guardrails Middleware:** Sub-10ms response filtering proxy for production LLM calls.

---

## 🤝 How to Contribute to the Roadmap

Want to help us reach these milestones?

- Check out open tasks in [`docs/CONTRIBUTOR_ISSUES_CATALOG.md`](docs/CONTRIBUTOR_ISSUES_CATALOG.md).
- Search issues labeled [`good first issue`](https://github.com/hardikkaurani/Eval-Forge/issues?q=is%3Aissue+is%3Aopen+label%3A"good+first+issue").
- Submit an RFC in [GitHub Discussions](https://github.com/hardikkaurani/Eval-Forge/discussions) to propose a new feature on the roadmap!
