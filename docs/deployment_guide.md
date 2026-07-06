# EvalForge v1.0.0 Production Deployment Guide

This document outlines the requirements and procedures for deploying EvalForge to production infrastructure.

---

## 1. System Architecture & Requirements

A standard production deployment of EvalForge consists of:
- **Load Balancer / Reverse Proxy**: Nginx, Traefik, or Caddy terminating SSL (HTTPS) and routing traffic.
- **FastAPI Core Service**: Stateless API instances handling REST requests.
- **React Frontend**: Bundled static files served by the reverse proxy.
- **PostgreSQL Database**: Relational database (v15+) for state persistence.
- **Redis Cache & Broker**: In-memory broker for Celery queues and query cache.
- **Celery Workers**: Execution nodes running LLM evaluations.

---

## 2. Configuration & Environment Variables

Create a secure `.env` file in your production environment. Never commit this file to source control.

| Variable Name | Description | Example / Recommended Value |
|---|---|---|
| `APP_ENV` | Application environment mode | `production` |
| `DEBUG` | Enable debug logs and Swagger | `False` |
| `SECRET_KEY` | JWT signing security key (64-char hex) | `8f2a...` |
| `POSTGRES_SERVER` | PostgreSQL server hostname | `db.evalforge.internal` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | PostgreSQL user | `evalforge_admin` |
| `POSTGRES_PASSWORD` | PostgreSQL database password | `[SECURE_PASSWORD]` |
| `POSTGRES_DB` | Database name | `evalforge_prod` |
| `REDIS_HOST` | Redis server hostname | `redis.evalforge.internal` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database index | `0` |
| `LOG_LEVEL` | Minimum log level output | `warning` |
| `JSON_LOGS` | Format logs as structured JSON | `True` |
| `OPENAI_API_KEY` | OpenAI API credentials | `sk-proj-...` |
| `ANTHROPIC_API_KEY` | Anthropic API credentials | `sk-ant-...` |

---

## 3. Docker Compose Production Deployment

The fastest way to deploy the entire stack is using our optimized production Docker Compose configuration.

### 3.1 Build Production Images
```bash
docker compose -f docker-compose.prod.yml build
```

### 3.2 Start Services in Detached Mode
```bash
docker compose -f docker-compose.prod.yml up -d
```

### 3.3 Verify Container Statuses
```bash
docker compose -f docker-compose.prod.yml ps
```
Ensure healthcheck statuses are `healthy` for PostgreSQL, Redis, and FastAPI.

---

## 4. HTTPS and Reverse Proxy (Caddy Example)

Use Caddy to automatically provision SSL certs via Let's Encrypt.

Create a `Caddyfile`:
```caddy
evalforge.yourdomain.com {
    # Serve static frontend files
    root * /var/www/evalforge/frontend/dist
    file_server
    
    # Route API requests to the FastAPI backend
    handle /api/* {
        reverse_proxy localhost:8000
    }

    # Route WebSockets progress channels
    handle /ws/* {
        reverse_proxy localhost:8000
    }

    # Fallback to frontend router index.html for SPA
    try_files {path} /index.html
}
```

---

## 5. Monitoring, Health Checks, & Rollback

### 5.1 Health Check Endpoints
- **Liveness Probe**: `GET /api/v1/health/liveness` (returns 200 if server is running)
- **Readiness Probe**: `GET /api/v1/health/readiness` (returns 200 if DB and Redis are connected)

### 5.2 Rollback Strategy
If an update fails:
1. Stop running containers:
   ```bash
   docker compose -f docker-compose.prod.yml down
   ```
2. Revert git tags/images to the previous stable release version (e.g. `v0.9.5`).
3. Restore database snapshots if migrations were run and fail to downgrade automatically.
4. Restart services:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```
