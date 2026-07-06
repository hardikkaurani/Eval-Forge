# Deployment Guide

This guide details the procedures for deploying EvalForge to a production-grade infrastructure, focusing on Docker, Kubernetes, and Helm.

---

## 1. Production Docker Builds

For production environments, use the optimized multi-stage build.

```bash
docker build --target production -t evalforge-backend:latest -f docker/Dockerfile .
```

---

## 2. Environment Variables configuration

Configure secrets and environment variables securely:

| Key | Description | Example |
|-----|-------------|---------|
| `APP_ENV` | Target environment mode | `production` |
| `SECRET_KEY` | JWT signing security key | `[ENCRYPTED_JWT_SECRET]` |
| `SECRET_PROVIDER` | Vault or cloud provider type | `vault` |
| `DATABASE_URL` | Postgres pooled connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `REDIS_URL` | Redis URL for caching/jobs | `redis://:pass@host:6379/0` |

---

## 3. High Availability Clustering

* Run at least 3 instances of the FastAPI API backend behind a layer-7 load balancer (e.g. NGINX, Traefik, AWS ALB).
* Deploy Redis in Sentinel or Cluster mode with high-availability replication.
* Run multiple background worker containers (`worker-eval`, `worker-jobs`) to scale task processing.
