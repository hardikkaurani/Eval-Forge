# Production Guide

This guide covers operational requirements, resource planning, and startup settings for running EvalForge in production.

---

## 1. Production Readiness Checklist

Before pushing to production, verify:
* [ ] Debug modes are disabled (`DEBUG=False`).
* [ ] API Swagger / OpenAPI documentation endpoint is disabled in production.
* [ ] Custom security headers are active and tested.
* [ ] Secrets are loaded from a secure vault (Vault, AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager).
* [ ] Database connection pool limits are configured based on available connections.
* [ ] CORS policies restrict access strictly to trusted client domains.

---

## 2. Resource Allocation Guidance

* **Backend API Nodes**: 1 vCPU, 2GB RAM per container (scale horizontally).
* **Workers**: 2 vCPU, 4GB RAM per container (adjust based on LLM eval load).
* **Database (PostgreSQL)**: Multi-AZ, minimum 2 vCPU, 8GB RAM with connection pooling set to `pool_size=20`, `max_overflow=10`.
* **Redis**: Persistent cache configuration (`maxmemory-policy volatile-lru`).
