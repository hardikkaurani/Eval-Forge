# Eval-Forge Python SDK (`evalforge`)

Official Python client SDK for the [Eval-Forge](https://github.com/hardikkaurani/Eval-Forge) AI evaluation and LLM observability platform.

---

## Installation

```bash
pip install evalforge
```

Or for development / editable mode:

```bash
pip install -e sdk/python
```

---

## Authentication

Set your API key via environment variable:

```bash
export EVALFORGE_API_KEY="ef_live_your_api_key_here"
export EVALFORGE_BASE_URL="http://localhost:8000"  # Optional, defaults to http://localhost:8000
```

Or provide it directly to the client constructor:

```python
from evalforge import EvalForge

client = EvalForge(api_key="ef_live_your_api_key_here")
```

---

## Quickstart

### Synchronous Usage

```python
from evalforge import EvalForge

client = EvalForge()

# 1. List Projects
projects = client.projects.list()
for p in projects:
    print(f"Project: {p.name} ({p.id})")

# 2. Create an Evaluation Run
eval_run = client.evaluations.create(
    project_id="your-project-uuid",
    name="RAG Quality Benchmark",
    test_cases=[
        {
            "input_prompt": "What is the capital of France?",
            "model_output": "Paris is the capital of France.",
            "reference": "Paris",
        }
    ],
    metrics=["accuracy", "semantic_similarity"],
)
print(f"Evaluation Run ID: {eval_run.id}")

# 3. Retrieve Results
results = client.evaluations.list_results(run_id=eval_run.id)
for r in results:
    print(f"Passed: {r.passed}, Latency: {r.latency_ms}ms")
```

### Asynchronous Usage (`AsyncEvalForge`)

```python
import asyncio
from evalforge import AsyncEvalForge

async def main():
    async with AsyncEvalForge() as client:
        projects = await client.projects.list()
        print(f"Found {len(projects)} projects.")

asyncio.run(main())
```

---

## Error Handling

All client errors inherit from `EvalForgeError`:

```python
from evalforge import EvalForge
from evalforge.exceptions import AuthenticationError, NotFoundError, RateLimitError

client = EvalForge()

try:
    project = client.projects.get("invalid-uuid")
except NotFoundError as e:
    print(f"Resource not found (Request ID: {e.request_id})")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
```

---

## License

Apache 2.0 / MIT
