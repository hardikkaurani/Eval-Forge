# ISSUE-01: Add Strict Pydantic Response Model for Dataset Import Route

**Difficulty:** 🟢 Good First Issue  
**Component:** `backend/app/datasets/routers/`  
**Suggested Labels:** `good first issue`, `backend`, `api`  
**Priority:** Low  

---

## Problem
The dataset import router endpoint (`POST /api/v1/datasets/import`) currently returns a raw dictionary response payload (`{"job_id": ..., "status": ...}`) without using a dedicated Pydantic response schema.

## Why It Matters
Using an explicit Pydantic model (`DatasetImportResponse`) ensures strict response validation, enables automatic OpenAPI schema doc generation, and prevents unexpected payload keys from reaching API consumers.

## Suggested Files
- [`backend/app/schemas/dataset.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/schemas/dataset.py)
- `backend/app/datasets/routers/dataset.py`

## Step-by-Step Guidance
1. Open `backend/app/schemas/dataset.py` and define `DatasetImportResponse(BaseModel)` with fields `job_id`, `status`, `version_id`, `records_imported`.
2. Update the route in `backend/app/datasets/routers/dataset.py` to specify `response_model=DatasetImportResponse`.
3. Run `pytest backend/tests/test_datasets.py` to verify all tests pass.

## Definition of Done
- [ ] `DatasetImportResponse` schema defined in `schemas/dataset.py`.
- [ ] Route updated with `response_model=DatasetImportResponse`.
- [ ] Pytest suite passes cleanly.
