# ISSUE-04: Create Pytest Fixture for Redis Connection Mocking in Offline Runs

**Difficulty:** 🟢 Good First Issue  
**Component:** `backend/tests/`  
**Suggested Labels:** `good first issue`, `testing`, `backend`  
**Priority:** Medium  

---

## Problem
Running `pytest` without a local Redis server running causes warnings or connection attempts in certain integration tests.

## Why It Matters
A reliable offline mock fixture ensures developers can run the entire backend test suite on air-gapped environments or local machines without spinning up Docker services.

## Suggested Files
- [`backend/tests/conftest.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/tests/conftest.py)

## Definition of Done
- [ ] Added `mock_redis` fixture to `conftest.py`.
- [ ] All 40+ pytest backend tests pass cleanly in offline mode.
