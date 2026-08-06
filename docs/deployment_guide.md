# EvalForge v1.0.0 Production Deployment Guide

This document provides step-by-step instructions for deploying EvalForge to production infrastructure, targeting **Vercel** (Frontend), **Railway** (Backend, PostgreSQL, and Redis), or **Docker Compose** (Self-Hosted).

---

## 1. Cloud Architecture Overview

```
+---------------------------------------+
|            Vercel (CDN)               |
|      React / Vite Frontend App        |
|     (https://evalforge.vercel.app)    |
+-------------------+-------------------+
                    |
                    | API Requests (HTTPS)
                    v
+---------------------------------------+
|           Railway (PaaS)              |
|        FastAPI Backend Engine         |
|  (https://backend.up.railway.app)     |
+---------+-------------------+---------+
          |                   |
          v                   v
+-------------------+ +-----------------+
| Railway Postgres  | |  Railway Redis  |
|  (PostgreSQL 16)  | |   (Redis 7)     |
+-------------------+ +-----------------+
```

---

## 2. Environment Variables Specification

Before deploying, configure your production environment variables. Refer to [.env.example](file:///.env.example) at the project root.

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `APP_ENV` | Yes | `production` | Enables production security checks & disables public docs |
| `DEBUG` | Yes | `False` | Disables verbose debug logging |
| `PORT` | Auto | `8000` | Dynamic port provided by Railway / cloud host |
| `DATABASE_URL` | Yes | Auto-provided | PostgreSQL connection string (`postgresql://` or `postgres://` auto-converts to `postgresql+asyncpg://`) |
| `REDIS_URL` | Yes | Auto-provided | Redis connection string (`redis://...`) |
| `SECRET_KEY` | Yes | Secure Hex | 64-character random string for cryptography |
| `CORS_ORIGINS` | Yes | `["https://..."]` | JSON array of trusted frontend domains allowed by CORS |
| `ALLOWED_HOSTS` | Yes | `["*"]` | Trusted host headers allowed by proxy middleware |
| `VITE_API_URL` | Yes | `https://...` | Base API URL configured on Vercel frontend |

---

## 3. Deployment Steps

### Option A: Cloud Deployment (Vercel & Railway)

#### Step A1: Backend & Database Deployment on Railway
1. Sign in to [Railway.app](https://railway.app).
2. Create a **New Project** and add a **PostgreSQL** database service and a **Redis** database service.
3. Add a **GitHub Repository Service** pointing to `hardikkaurani/Eval-Forge`.
4. Set the service root directory to `/backend` (or leave as root and use `railway.json`).
5. Configure environment variables in Railway:
   - `APP_ENV=production`
   - `DEBUG=False`
   - `SECRET_KEY=<your-64-character-secret>`
   - `CORS_ORIGINS=["https://evalforge.vercel.app"]`
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
   - `REDIS_URL=${{Redis.REDIS_URL}}`
6. Railway will automatically execute `bash scripts/start.sh` (running Alembic migrations and starting Uvicorn).
7. Copy your deployed Railway backend URL (e.g. `https://evalforge-production.up.railway.app`).

#### Step A2: Frontend Deployment on Vercel
1. Sign in to [Vercel.com](https://vercel.com).
2. Click **Add New Project** and import `hardikkaurani/Eval-Forge`.
3. Set **Framework Preset** to **Vite**.
4. Set **Root Directory** to `frontend`.
5. Configure Environment Variables:
   - `VITE_API_URL=https://evalforge-production.up.railway.app/api/v1`
6. Click **Deploy**. Vercel will build the frontend using `npm run build` and route all SPA paths correctly via `vercel.json`.

---

### Option B: Docker Production Deployment (Self-Hosted)

For self-hosted virtual machines or on-premise servers:

1. Clone the repository and navigate to root:
   ```bash
   git clone https://github.com/hardikkaurani/Eval-Forge.git
   cd Eval-Forge
   ```

2. Copy `.env.example` to `.env` and fill in production secrets:
   ```bash
   cp .env.example .env
   ```

3. Build and launch services using the production compose stack:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

4. Verify health status of all containers:
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```

5. Access your deployment:
   - Frontend SPA: `http://localhost:80`
   - Backend API Health: `http://localhost:8000/api/v1/health`

---

## 4. Post-Deployment Verification Checklist

After deploying EvalForge, run through this verification checklist:

- [ ] **Liveness Probe**: `GET /health` returns HTTP 200 `{"status": "healthy"}`
- [ ] **Readiness Probe**: `GET /api/v1/ready` returns HTTP 200 with DB & Redis healthy
- [ ] **SPA Routing**: Directly opening sub-routes (e.g. `/projects`, `/datasets`) in browser reloads cleanly without 404
- [ ] **Database Connection**: Alembic migrations applied tables (`projects`, `datasets`, `evaluations`, `users`, etc.)
- [ ] **Redis Connection**: Redis ping passes on container startup
- [ ] **CORS Preflight**: Browser cross-origin OPTIONS requests succeed without CORS block
- [ ] **API Documentation**: Docs disabled or locked in production (`APP_ENV=production`)

---

## 5. Rollback Procedure

If a deployment fails:
1. Revert to the previous git release tag:
   ```bash
   git checkout tags/v0.9.0
   ```
2. Re-trigger Vercel deployment or Railway build.
3. For Docker deployments, execute:
   ```bash
   docker compose -f docker-compose.prod.yml down
   docker compose -f docker-compose.prod.yml up -d --build
   ```
