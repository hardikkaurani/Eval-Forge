# Developer Documentation

## Local development

- Backend: FastAPI + SQLAlchemy + SQLite test harness
- Frontend: React + Vite + TypeScript
- Containers: Docker Compose for the full stack

## Testing

- Unit and integration tests live under `backend/tests/`
- Evaluation coverage focuses on metadata endpoints, CRUD flow, batch execution, and validation errors

## Implementation standards

- Keep API routes thin
- Put business logic in services and pipelines
- Use registries for extensibility
- Avoid hardcoded provider or judge branching
- Prefer explicit validation before model execution

## Phase 3 highlights

- modular evaluation pipeline
- provider abstraction
- judge abstraction
- prompt versioning
- rubric catalog
- batch progress tracking
- partial failure isolation
