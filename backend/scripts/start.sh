#!/usr/bin/env bash
set -e

echo "=========================================================="
echo " Starting EvalForge Production Backend"
echo " Environment: ${APP_ENV:-production}"
echo " Port: ${PORT:-8000}"
echo "=========================================================="

# Run database migrations (skip if DATABASE_URL is not set)
if [ -n "${DATABASE_URL}" ]; then
  echo "Executing database migrations via Alembic..."
  alembic upgrade head || echo "WARNING: Alembic migration failed, continuing startup..."
  echo "Database migration step completed."
else
  echo "DATABASE_URL not set, skipping Alembic migrations."
fi

# Start uvicorn server
echo "Starting Uvicorn web server..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
