# Workspace UI setup

The UI connects to the existing API with an EvalForge API key. Email/password sign-in, registration, password recovery, SSO setup and provider-key editing are not supported by this UI. Provider credentials belong on the server.

## Requirements

- Node.js 22.12 or newer; Python 3.12 or newer.
- PostgreSQL and Redis for the normal backend. Celery workers are required for queued background jobs.
- At least one configured LLM provider for live evaluations. The provider catalog describes registered capabilities; it does not confirm that credentials are configured.

## Development

From the repository root, install Python dependencies into a virtual environment and start local services:

```sh
python -m venv .venv
# Activate .venv using the command for your shell.
pip install -r backend/requirements.txt -e ./sdk/python -e ./cli
docker compose up -d postgres redis
cd backend
alembic upgrade head
python scripts/bootstrap_workspace.py --name "My workspace"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The bootstrap command creates an organization, workspace, owner membership and a key scoped to that workspace. It requires database access and prints the new key once. Save it securely. Keys expire after 30 days by default; `--expires-days` accepts 1–365. Each invocation creates a separate workspace. This is an administrator command, not a public registration endpoint.

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173` and connect with the workspace key. Vite proxies `/api` to port 8000. For a separate backend origin, set `VITE_API_URL=https://your-api.example/api/v1` before building and allow the frontend origin in backend CORS. This is public configuration; never put a provider key or workspace key into a `VITE_` variable.

Create a project, import CSV/JSON/JSONL with `prompt`, `candidate_output` and `reference_output` fields, then create an evaluation. Select its dataset version, judge, registered provider and model. Execution stores results in the backend. The UI preserves a created evaluation after execution errors so that a failed connection is not presented as success.

Workspace keys require `read:all` for the full UI and `write:all` for mutations. Narrow scopes use `read:<resource>` or `write:<resource>`; experiment endpoints use the `evaluations` resource. Generated child keys inherit their parent workspace/organization and cannot gain broader scopes. Organization administration also requires the backend's membership permissions.

Keys stay in session storage and are removed on disconnect or authentication failure. Project data is cleared at the same time. Theme selection is the only persistent UI preference. Jobs use authenticated SSE with a bounded polling fallback; credentials are never placed in stream URLs.

## Isolated browser validation

This test server uses the actual FastAPI routes, hashed API-key authentication and a temporary SQLite database. It disables Redis connectivity and uses the explicit mock LLM provider. It is not a production deployment or evidence of a live external LLM call.

```sh
python backend/tests/ui_server.py
# Another terminal, from frontend:
npm run dev
# Another terminal, from frontend:
npx playwright install chrome
npm run test:e2e
```

Restart the test server before rerunning the complete suite: the core journey verifies an initially empty fixture and creates records. Its public test-only connection key is `ef_browser_test_only`. Never run `ui_server.py` as your real backend.

```sh
# Set APP_ENV=testing for this command (PowerShell: $env:APP_ENV='testing').
pytest backend/tests sdk/python/tests cli/tests
ruff check backend/
black --check backend/
# From frontend:
npm run typecheck
npm run lint
npm test
npx prettier --check "src/**/*.{ts,tsx,css,json,md}"
npm run build
```

`VITE_ENABLE_MOCKS=true` enables an explicitly labeled, read-only development preview. `import.meta.env.DEV` prevents demo behavior in production builds. Live request failures never switch into demo mode.

## Production configuration

Use the production Compose configuration and the deployment documentation for infrastructure. Set `APP_ENV=production`, `DEBUG=false`, a strong `SECRET_KEY`, database/Redis credentials, explicit `CORS_ORIGINS`, trusted hosts/proxies and server-side provider credentials. Do not deploy the default development Compose passwords. Apply migrations before provisioning a workspace.

The frontend image builds with Node 22 and serves through Nginx. It uses same-origin `/api` requests; Nginx has SPA fallback for direct route reloads, disables SSE buffering, and disallows inline/eval scripts in its CSP. If you host the build elsewhere, reproduce the route fallback and configure the API origin and CSP together. Serve browser connections over HTTPS.

Release evidence and environment-dependent limitations are recorded in [the UI release review](ui-release-review.md). Production PostgreSQL/Redis/Celery, real-provider evaluation, TLS and deployment-specific CORS must be checked in the target environment before launch.
