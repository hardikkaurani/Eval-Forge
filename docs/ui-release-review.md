# UI release review

## Scope

The existing React/TypeScript/Vite/Tailwind interface is rebuilt around neutral surfaces, blue actions, Geist, JetBrains Mono, a 240px sidebar and shared light/dark styles. The default follows the system theme. Navigation, forms, tables, native dialogs, errors and empty states use the same components throughout.

Authentication now validates an API key against the backend. The old fabricated email/password session and silent mock API fallbacks are removed. Keys use session storage and query caches are cleared on disconnect. Dataset import, evaluation configuration/execution, versioned records, results and job progress use actual backend contracts. Zero counts stay zero; unavailable data displays an error. Demo mode is explicit, read-only and excluded from production behavior.

## Supported interface

- Connect/disconnect; select and create projects; edit project settings.
- Create datasets, import CSV/JSON/JSONL, browse versions and records.
- Configure and execute an evaluation, inspect stored metrics and test-case results.
- Browse/create benchmark suites and policies; browse pipeline-supplied RAG/safety assessments.
- Generate/download reports; browse jobs and logs; inspect authenticated SSE progress with bounded polling fallback; confirm retry/cancel actions.
- Read the provider catalog, connection scope, system status and authorized organization records.

User-managed scheduling, email/password accounts, provider-key editing and SSO configuration are outside launch navigation. The scheduling route explains its availability. Registered providers are not labeled configured or healthy. RAG/safety pages show measurements supplied by the pipeline and do not claim to run an unimplemented assessment engine.

## Confirmed security repairs

| Finding | Repair and coverage |
| --- | --- |
| Workspace-scoped jobs could bypass isolation through unscoped keys; job pagination stopped after 1,000 records | Authorize against the project's workspace for every access; filter/count in SQL. Regression covers cross-workspace denial and 1,005 jobs. |
| API-key scope strings were not enforced; issuance could escape the parent workspace | Enforce read/write resource scopes, inherit workspace/organization, reject broader scopes and foreign revocation. Tests use real hashed keys. |
| Response idempotency keys were shared between callers and could replay after revocation | Hash credential, method, URL and body into the cache key; revalidate authorization before replay; exclude key-generation responses and file uploads. |
| Evaluation input could choose the Ollama network destination | Only the administrator-configured server URL is accepted; metadata-address override regression. |
| Webhook validation resolved DNS separately from delivery | Pin the HTTP connection to a validated public IP, retain Host/TLS SNI, disable redirects and environment proxies; tests cover DNS rebinding. |
| Workspace keys could control the global scheduler | Require explicit server-scheduler administration scope. |
| Provider credential errors could invalidate the UI's workspace session | Return a provider-service error rather than a workspace-authentication 401. |
| A mixed production CORS list could include a wildcard | Reject wildcard membership anywhere in the production list. |

React renders data as text. Nested secret fields and recognizable key strings are redacted in record/error displays. The production Nginx configuration prohibits inline/eval scripts and buffers neither SSE nor its proxy responses.

This is a source review with focused regression tests, not an independent penetration test or a Cloudflare account audit. No Cloudflare installation or production deployment was performed.

## Validation

Final command results and screenshots are added with the release-evidence commit. The browser suite uses real FastAPI authentication, routing, SQLite persistence, CSV import and evaluation execution with the explicit mock provider. It covers all 29 route variants at 375/768/1440 pixels in both themes, accessibility scans, keyboard dialog/drawer focus, invalidation, forbidden resources, malformed responses, network failures, project-switch races and job stream cleanup.

## Remaining environment-dependent launch gates

Docker is not installed on the local host. Production PostgreSQL migrations, Redis/Celery execution, Nginx container startup, HTTPS, deployed CORS and a real external-provider run must be validated in the intended deployment. Local browser tests use temporary SQLite and a mock LLM, and do not establish those production capabilities. CI status must be checked on the final PR head. These limits prevent an unconditional production-readiness claim.

No production data, credentials, deployment or merge is part of this change. See [setup](ui-setup.md) for required services and API-key provisioning.
