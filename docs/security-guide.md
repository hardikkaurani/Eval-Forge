# Security Guide

This guide details the security configurations, policies, and authorization controls deployed inside EvalForge.

---

## 1. Network & Protocol Security

* **HTTPS Enforcement**: Strict Transport Security (HSTS) is enabled by default in production.
* **CORS Restrictions**: Configure `CORS_ORIGINS` to allow only specified organizational domains.
* **Trusted Hosts**: Set `ALLOWED_HOSTS` to filter HTTP requests targeting arbitrary host headers.

---

## 2. API Guardrails & Rate Limiting

* **Sliding Window Rate Limiter**: Configured at the middleware layer using Redis keys (`ratelimit:ip:...` or `ratelimit:api:...`).
* **Idempotency Protection**: Ensures duplicate POST/PUT operations with the same `X-Idempotency-Key` return cached execution responses without triggering redundant side effects.

---

## 3. Role-Based Access Control (RBAC)

EvalForge enforces 5 enterprise roles to control access:
1. **Owner**: Full system privileges, organization settings, and billing control.
2. **Admin**: Project administration, policy configuration, and deletion.
3. **Developer**: Evaluation runs, dataset modification, and basic analysis.
4. **Viewer**: Read-only visualization and metrics retrieval.
5. **Auditor**: Security and compliance evaluation audit trail reads.
