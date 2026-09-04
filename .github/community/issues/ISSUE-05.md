# ISSUE-05: Add Structured JSON Error Schema Validation to Global Exception Handler

**Difficulty:** 🟢 Good First Issue  
**Component:** `backend/app/core/exceptions.py`  
**Suggested Labels:** `good first issue`, `api`, `backend`  
**Priority:** Medium

---

## Problem

Uncaught application exceptions currently return error messages without enforcing strict RFC 7807 problem details fields (`type`, `title`, `status`, `detail`, `instance`).

## Why It Matters

Enforcing a consistent RFC 7807 JSON error schema allows frontend clients and API integrations to parse error payloads deterministically.

## Suggested Files

- [`backend/app/core/exceptions.py`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/backend/app/core/exceptions.py)

## Definition of Done

- [ ] Exception handler updated to emit RFC 7807 structured JSON.
- [ ] Pytest suite verifies 404, 422, and 500 error structure.
