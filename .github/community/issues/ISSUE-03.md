# ISSUE-03: Standardize Python Datetime UTC Usage across Enterprise Services

**Difficulty:** 🟢 Good First Issue  
**Component:** `backend/app/enterprise/`  
**Suggested Labels:** `good first issue`, `backend`, `refactor`  
**Priority:** Low

---

## Problem

Several enterprise SaaS service modules currently use `datetime.utcnow()`, which is deprecated in Python 3.12+ in favor of timezone-aware UTC objects.

## Why It Matters

`datetime.utcnow()` emits `DeprecationWarning` logs during pytest execution. Using `datetime.now(timezone.utc)` prevents future runtime deprecation breaks.

## Suggested Files

- `backend/app/enterprise/services/organization_service.py`
- `backend/app/enterprise/services/workspace_service.py`
- `backend/app/enterprise/services/billing_service.py`

## Definition of Done

- [ ] Replaced all instances of `datetime.utcnow()` with `datetime.now(timezone.utc)`.
- [ ] Pytest suite passes without datetime deprecation warnings.
