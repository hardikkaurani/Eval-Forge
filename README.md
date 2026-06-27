# EvalForge

<p align="center">
  <strong>Production-grade open-source LLM evaluation platform with G-Eval, LLM-as-a-Judge, and custom pipeline tooling.</strong>
</p>

<p align="center">
  <a href="#tech-stack"><strong>Tech Stack</strong></a> &bull;
  <a href="#getting-started"><strong>Getting Started</strong></a> &bull;
  <a href="#architecture"><strong>Architecture</strong></a> &bull;
  <a href="#roadmap"><strong>Roadmap</strong></a> &bull;
  <a href="#contributing"><strong>Contributing</strong></a>
</p>

---

## 🚀 Hero Section

EvalForge is built for developers, AI engineers, and product teams who need to benchmark and continuously evaluate LLM applications. Unlike complex, proprietary tools, EvalForge provides a transparent, developer-centric, and self-hosted environment to run evaluations locally or in production pipelines.

---

## ✨ Planned Features

- **G-Eval & LLM-as-a-Judge**: Implement state-of-the-art evaluation methodologies using custom rubrics.
- **RAG Evaluation**: Out-of-the-box support for assessing retrieval relevance, faithfulness, and answer correctness.
- **Customizable Evaluation Pipelines**: Graph-based and code-defined pipelines to model complex multi-step evaluations.
- **Real-Time Dashboards**: Interactive UI to compare test runs, inspect LLM outputs side-by-side, and track performance regressions.
- **CI/CD Integration**: Seamless integration with GitHub Actions, GitLab CI, and other tools to run evaluations on every PR.
- **Dataset Management**: Central repository to manage golden datasets, test sets, and system traces.

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast Python web framework.
- **SQLAlchemy (Async)**: SQL toolkit and Object Relational Mapper for Python.
- **Pydantic v2**: Data validation and settings management.
- **Structlog**: Asynchronous, structured logging.

### Frontend
- **React**: Declarative component library.
- **Vite**: Ultra-fast next-gen build tool.
- **TypeScript**: Static typing for robust interface design.
- **Vanilla CSS**: Clean, premium styling system without styling library overhead.

### Infrastructure
- **Docker & Docker Compose**: Unified local containerized environments.
- **PostgreSQL**: Production-grade relational database.
- **Redis**: Fast caching and task queue broker.

---

## 🏛️ Architecture Overview

EvalForge uses a decoupled monorepo layout:
- **Frontend** serves a single-page application built on React/TS that interacts with the backend.
- **Backend** acts as a stateless REST API, exposing endpoints, handling database connections asynchronously, and dispatching long-running evaluation tasks.
- **Database (PostgreSQL)** persists evaluation metadata, system metrics, pipelines, and dataset schemas.
- **Redis** manages ephemeral state, caching, and task broker queues.

---

## 📂 Folder Structure

```
eval-forge/
├── .github/             # GitHub workflow CI and templates
├── backend/             # Python FastAPI server
│   ├── app/             # Application source code
│   └── requirements.txt # Python package dependencies
├── datasets/            # Target folder for test datasets (golden sets)
├── docker/              # Multi-stage Dockerfiles
├── docs/                # Project documentation and specifications
├── examples/            # Example pipelines and code notebooks
├── frontend/            # React + Vite TypeScript web client
│   └── src/             # Frontend source code
├── scripts/             # Internal tooling and automation scripts
├── tests/               # Unit, integration, and E2E tests
├── docker-compose.yml   # Multi-container orchestration config
├── LICENSE              # License documentation
└── README.md            # You are here
```

---

## 🏁 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js v20+
- Python 3.11+

### Local Setup (Using Docker)
To bootstrap the entire stack including backend, frontend, PostgreSQL, and Redis:
```bash
docker compose up --build -d
```
The services will be available at:
- Frontend Client: `http://localhost`
- Backend API Docs: `http://localhost:8000/docs`

### Manual Development Setup

1. **Spin up Infrastructure**:
   Ensure Docker is running and run:
   ```bash
   docker compose up postgres redis -d
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   npm run dev
   ```

---

## 🗺️ Roadmap

Detailed plans can be viewed in the [ROADMAP.md](./ROADMAP.md) file.
- **Phase 1: Foundation (Current)**: Setup monorepo structure, engineering standards, CI workflows, and core architecture.
- **Phase 2: Database & Models**: Database schema migrations (Alembic), core database models (Runs, Datasets, Evaluations).
- **Phase 3: Core Evaluation Engine**: Implementation of G-Eval, RAG evaluations, and LLM judge callbacks.
- **Phase 4: Dashboard & Analytics**: Dynamic frontend pages to visualize run histories, side-by-side completions, and charts.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](./LICENSE) for more information.

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) to get started on how you can help.
