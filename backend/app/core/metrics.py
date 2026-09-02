
import prometheus_client
import structlog
from fastapi import Request

logger = structlog.get_logger()

# -----------------------------------------------------------------------------
# Prometheus Metric Collectors
# -----------------------------------------------------------------------------

HTTP_REQUESTS_TOTAL = prometheus_client.Counter(
    "evalforge_http_requests_total",
    "Total number of HTTP requests processed.",
    ["method", "route", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = prometheus_client.Histogram(
    "evalforge_http_request_duration_seconds",
    "HTTP request execution latency in seconds.",
    ["method", "route", "status"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

CELERY_QUEUE_DEPTH = prometheus_client.Gauge(
    "evalforge_celery_queue_depth",
    "Current number of tasks queued in Celery queues.",
    ["queue"],
)

CELERY_WORKERS_ACTIVE = prometheus_client.Gauge(
    "evalforge_celery_workers_active",
    "Current number of active Celery worker instances.",
)

EVALUATIONS_STARTED_TOTAL = prometheus_client.Counter(
    "evalforge_evaluations_started_total",
    "Total evaluation executions started.",
    ["eval_type"],
)

EVALUATIONS_COMPLETED_TOTAL = prometheus_client.Counter(
    "evalforge_evaluations_completed_total",
    "Total evaluation executions completed successfully.",
    ["eval_type"],
)

EVALUATIONS_FAILED_TOTAL = prometheus_client.Counter(
    "evalforge_evaluations_failed_total",
    "Total evaluation executions failed.",
    ["eval_type"],
)

RATE_LIMIT_REJECTIONS_TOTAL = prometheus_client.Counter(
    "evalforge_rate_limit_rejections_total",
    "Total HTTP request rate-limit rejections.",
    ["limit_type"],
)

# -----------------------------------------------------------------------------
# Route Path Normalization & Helpers
# -----------------------------------------------------------------------------

ALLOWED_LIMIT_TYPES = {"ip", "user", "api_key", "default"}


def normalize_route_path(request: Request) -> str:
    """Extracts matched route template or returns static /unmatched fallback to prevent label explosion."""
    if not request or not hasattr(request, "scope"):
        return "/unmatched"

    # 1. Inspect FastAPI matched route template
    route = request.scope.get("route")
    if route and hasattr(route, "path") and route.path:
        return route.path

    # 2. Static low-cardinality fallback for any unmatched / 404 / raw path
    return "/unmatched"


def record_http_metrics(
    method: str, route: str, status_code: int, duration_seconds: float
) -> None:
    """Records HTTP request count and latency histogram metrics."""
    clean_method = (method or "GET").upper()
    clean_route = route or "/unmatched"

    # Categorize status code into low-cardinality status string
    status_str = str(status_code) if status_code else "500"

    HTTP_REQUESTS_TOTAL.labels(
        method=clean_method, route=clean_route, status=status_str
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=clean_method, route=clean_route, status=status_str
    ).observe(max(0.0, duration_seconds))


def record_rate_limit_rejection(limit_type: str = "default") -> None:
    """Interface for recording rate-limit rejections with bounded label types (Batch 4 integration)."""
    clean_type = str(limit_type or "default").lower().strip()
    if clean_type not in ALLOWED_LIMIT_TYPES:
        clean_type = "default"
    RATE_LIMIT_REJECTIONS_TOTAL.labels(limit_type=clean_type).inc()


def record_evaluation_started(eval_type: str = "standard") -> None:
    """Records evaluation start counter."""
    EVALUATIONS_STARTED_TOTAL.labels(eval_type=eval_type or "standard").inc()


def record_evaluation_completed(eval_type: str = "standard") -> None:
    """Records evaluation completion counter."""
    EVALUATIONS_COMPLETED_TOTAL.labels(eval_type=eval_type or "standard").inc()


def record_evaluation_failed(eval_type: str = "standard") -> None:
    """Records evaluation failure counter."""
    EVALUATIONS_FAILED_TOTAL.labels(eval_type=eval_type or "standard").inc()


async def get_active_worker_count() -> int:
    """Queries actual responsive Celery worker instances across inspect, Redis, and DB."""
    # 1. Try Celery control inspect ping
    try:
        from app.jobs.queue.celery_app import celery_app

        insp = celery_app.control.inspect(timeout=0.2)
        if insp:
            ping_res = insp.ping()
            if ping_res and isinstance(ping_res, dict):
                return len(ping_res)
    except Exception as exc:
        logger.debug("Celery inspect ping failed", error=str(exc))

    # 2. Try DB Worker table for active workers with recent heartbeat (within 120s)
    try:
        from datetime import timedelta

        from sqlalchemy import or_, select

        from app.database.session import SessionLocal
        from app.jobs.models.job import Worker
        from app.utils.datetime import get_utc_now

        async with SessionLocal() as db:
            threshold = get_utc_now() - timedelta(seconds=120)
            stmt = select(Worker).where(
                or_(
                    Worker.status.in_(["IDLE", "BUSY", "ONLINE", "ACTIVE"]),
                    Worker.last_heartbeat >= threshold,
                )
            )
            res = await db.execute(stmt)
            workers = res.scalars().all()
            if workers:
                return len(workers)
    except Exception as exc:
        logger.debug("DB worker status query failed", error=str(exc))

    # 3. Try Redis worker keys
    try:
        from app.core.redis import redis_manager

        if redis_manager.client:
            worker_keys = await redis_manager.client.smembers("celery_workers")
            if worker_keys:
                return len(worker_keys)
    except Exception as exc:
        logger.debug("Redis worker query failed", error=str(exc))

    return 0


async def update_celery_telemetry() -> None:
    """Safely updates Celery queue depth and active worker gauges without blocking HTTP requests."""
    try:
        from app.core.redis import redis_manager

        if redis_manager.client:
            # Query Redis queue depth for Phase 6 queues: high, default, low
            for q_name in ("high", "default", "low"):
                try:
                    depth = await redis_manager.client.llen(q_name)
                    CELERY_QUEUE_DEPTH.labels(queue=q_name).set(depth or 0)
                except Exception:
                    CELERY_QUEUE_DEPTH.labels(queue=q_name).set(0)
        else:
            for q_name in ("high", "default", "low"):
                CELERY_QUEUE_DEPTH.labels(queue=q_name).set(0)

        # Dynamically set actual responsive active Celery worker count
        active_workers = await get_active_worker_count()
        CELERY_WORKERS_ACTIVE.set(active_workers)
    except Exception as exc:
        logger.debug("Telemetry gauge update failed", error=str(exc))
        # Ensure gauge reflects 0 on failure, never a fake production constant
        CELERY_WORKERS_ACTIVE.set(0)
