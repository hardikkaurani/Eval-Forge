# ISSUE-02: Add Request Cancellation (AbortController) to React Query Hooks

**Difficulty:** 🟢 Good First Issue  
**Component:** `frontend/src/services/api.ts`  
**Suggested Labels:** `good first issue`, `frontend`, `ux`  
**Priority:** Medium

---

## Problem

When navigating rapidly between Dashboard, Datasets, and Evaluations pages in the SPA, background HTTP requests continue executing in transit without cancellation.

## Why It Matters

Passing an `AbortController` signal to Axios requests avoids memory leaks and unnecessary network bandwidth consumption when users switch views before data finishes loading.

## Suggested Files

- [`frontend/src/services/api.ts`](file:///c:/Users/hardi/OneDrive/Desktop/Eval-Forge/frontend/src/services/api.ts)

## Step-by-Step Guidance

1. Update API client methods in `frontend/src/services/api.ts` to accept an optional `{ signal?: AbortSignal }` parameter.
2. Forward the `signal` to `apiClient.get('/...', { signal })`.
3. Verify that `npm run typecheck` and `npm run lint` pass with zero errors.

## Definition of Done

- [ ] API methods accept `signal?: AbortSignal`.
- [ ] React Query hooks pass signal parameter.
- [ ] Frontend typecheck and lint pass cleanly.
