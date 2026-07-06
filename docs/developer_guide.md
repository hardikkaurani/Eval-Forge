# EvalForge v1.0.0 Developer Guide

This guide is designed to help developers understand, extend, and contribute to the EvalForge codebase.

---

## 1. Codebase Structure

EvalForge is structured as a monorepo containing:
- **`backend/`**: A FastAPI-based asynchronous application serving the REST APIs, evaluation engine, and Celery tasks.
- **`frontend/`**: A React 19 single-page application built with TypeScript, Vite, Recharts, and Framer Motion.
- **`docker/`**: Deployment and local development Docker configuration files.
- **`docs/`**: Platform documentation and architectural decisions.
- **`examples/`**: Code snippets demonstrating integrations.

---

## 2. Extending the Evaluation Engine

To add a new LLM judge or evaluation metric, follow the pluggable repository pattern:

### 2.1 Implementing a Custom Judge
All judges inherit from the abstract base class `JudgeBase` located at `backend/app/evaluation/prompts/engine.py`.

Example of creating a custom judge class:
```python
from typing import Dict, Any
from app.evaluation.prompts.engine import JudgeBase, EvalResult

class CustomHumorJudge(JudgeBase):
    """Evaluates how humorous or engaging an LLM output is based on a structured rubric."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: str = None):
        super().__init__(model_name=model_name, api_key=api_key)
        
    async def evaluate(self, output: str, reference: str = None, config: Dict[str, Any] = None) -> EvalResult:
        # 1. Compile prompt using Jinja templates
        prompt = self.compile_template("humor_rubric.j2", output=output, reference=reference)
        
        # 2. Call external LLM client
        raw_response = await self.llm_client.generate(prompt)
        
        # 3. Parse and calibrate score
        score, reasoning = self.parse_json_result(raw_response)
        normalized_score = self.calibrate_score(score, scale=(1, 5))
        
        return EvalResult(
            score=normalized_score,
            reasoning=reasoning,
            raw_output=raw_response
        )
```

### 2.2 Registering the Metric
Add your new judge implementation to the `MetricRegistry` class in `backend/app/evaluation/pipelines/pipeline.py`:
```python
self.registry.register("humor", CustomHumorJudge)
```

---

## 3. Developing APIs

EvalForge follows a strict **Repository-Service-Controller** layered architecture:

1. **Schemas (`app/schemas/`)**: Define the Pydantic v2 validation classes.
2. **Repositories (`app/evaluation/repositories/`)**: Encapsulate SQL queries and database operations.
3. **Services (`app/services/` or `app/evaluation/services/`)**: Orchestrate transactions, validate quotas, and trigger async workers.
4. **Routers (`app/api/v1/`)**: Define HTTP verbs, parameters, and inject services.

---

## 4. Running Tests & Linters

Ensure your code is clean before committing:

### 4.1 Backend Checks
```bash
cd backend
.venv/Scripts/ruff check app
.venv/Scripts/ruff format --check app
.venv/Scripts/pytest
```

### 4.2 Frontend Checks
```bash
cd frontend
npm run lint
npm run build
```
