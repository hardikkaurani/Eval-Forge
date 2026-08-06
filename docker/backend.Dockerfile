# --- Build Stage ---
FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Runtime Stage ---
FROM python:3.12-slim as runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        bash \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -u 8888 appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
# Copy application code and migrations
COPY --chown=appuser:appuser backend/app /app/app
COPY --chown=appuser:appuser backend/alembic /app/alembic
COPY --chown=appuser:appuser backend/alembic.ini /app/alembic.ini
COPY --chown=appuser:appuser backend/scripts /app/scripts
COPY --chown=appuser:appuser backend/.env.example /app/.env.example

# Make start script executable
RUN chmod +x /app/scripts/*.sh

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["bash", "scripts/start.sh"]