# EvalForge Community & Style Guide

This document establishes the developer standards, review policies, and community guidelines to ensure high-quality, readable, and consistent contributions to the EvalForge project.

---

## 1. Community Guidelines

### 1.1 Communication Channels
- **GitHub Issues**: Reserved for verified bug reports and concrete feature proposals.
- **GitHub Discussions**: The primary channel for Q&A, brainstorming, setup questions, and community support.
- **Pull Requests (PR)**: Used to propose actual code additions or documentation edits.

### 1.2 Behavior Expectations
We strictly enforce our [Code of Conduct](../CODE_OF_CONDUCT.md). Please treat all contributors with respect, empathy, and professionalism.

---

## 2. Python Backend Style Guide

All backend code must align with standard Python conventions enforced by our lint configurations.

### 2.1 Typing & Signatures
- Proactively write type hints for all function arguments and return signatures:
  ```python
  async def fetch_evaluation_run(run_id: str, db: AsyncSession) -> RunResponse:
  ```
- Use the standard `dict[str, Any]` type syntax rather than `Dict` from `typing` when writing python 3.10+ compatible code.

### 2.2 Async/Await Principles
- Never call blocking functions (e.g., synchronous requests, file system access) directly in async functions. Wrap them using thread pools or execute them via Celery.
- Always use the async connection drivers (e.g., `asyncpg`) for database sessions.

### 2.3 Exception Handling
- Throw domain-specific exceptions (e.g., `DatasetValidationException`) rather than generic `ValueError` or `Exception` classes.
- Allow HTTP-specific router middlewares to serialize errors into unified JSON structures rather than catching and returning custom response envelopes inside controllers.

---

## 3. TypeScript/React Frontend Style Guide

### 3.1 Functional Components
- Define React components using standard function syntax:
  ```tsx
  export function RunSummaryCard({ run }: RunSummaryProps) {
      return (
          <div className="bg-slate-900 p-4 rounded-lg">
              ...
          </div>
      );
  }
  ```
- Keep components small and specialized. Extract rendering helper cards or tables into isolated sub-components.

### 3.2 State Management
- Utilize `@tanstack/react-query` for API query states. Avoid mirroring server data in local React component states.
- Encapsulate custom state logic inside React hooks (e.g., `useWorkspace`).

### 3.3 CSS & Tailwind Guidelines
- Avoid inline styles. Rely exclusively on utility classes.
- Use curated CSS variable mappings (e.g., `text-primary`, `bg-dark`) to support theme consistency.
