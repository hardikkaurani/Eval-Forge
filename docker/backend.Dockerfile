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
RUN pip install --no-cache-dir -t /install -r requirements.txt

# --- Runtime Stage ---
FROM python:3.12-slim as runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -u 8888 appuser

# Copy installed packages from builder
COPY --from=builder --chown=appuser:appuser /install /usr/local
# Copy application code
COPY --chown=appuser:appuser backend/app /app/app
# Copy example env file (optional)
COPY --chown=appuser:appuser backend/.env.example /app/.env.example

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]