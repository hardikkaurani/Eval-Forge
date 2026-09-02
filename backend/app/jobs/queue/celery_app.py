import uuid

import structlog
from celery import Celery
from celery.signals import task_postrun, task_prerun
from kombu import Queue

from app.config.config import settings

# Initialize Celery app instance pointing to Redis
celery_app = Celery(
    "evalforge_jobs",
    broker=settings.get_redis_url,
    backend=settings.get_redis_url,
)

# Load configuration options
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_default_queue="default",
    task_queues=(
        Queue("high", routing_key="high.#"),
        Queue("default", routing_key="default.#"),
        Queue("low", routing_key="low.#"),
    ),
    task_routes={
        "app.jobs.tasks.run_evaluation_job": {"queue": "high"},
        "app.jobs.tasks.run_background_job": {"queue": "default"},
    },
    # Run tasks synchronously in same process for test envs to avoid Redis requirement
    task_always_eager=(settings.APP_ENV == "testing"),
    task_eager_propagates=True,
)


@task_prerun.connect
def setup_task_logging_context(
    sender=None, task_id=None, task=None, args=None, kwargs=None, **kw
):
    """Binds task correlation context and IDs to structlog contextvars before task execution."""
    structlog.contextvars.clear_contextvars()

    corr_ctx = (kwargs or {}).get("correlation_context") or {}
    req_id = corr_ctx.get("request_id") or task_id or str(uuid.uuid4())
    trace_id = corr_ctx.get("trace_id") or str(uuid.uuid4())

    bind_dict = {
        "request_id": req_id,
        "trace_id": trace_id,
        "celery_task_id": task_id,
    }
    for field in ("user_id", "org_id", "workspace_id"):
        if corr_ctx.get(field):
            bind_dict[field] = corr_ctx[field]

    structlog.contextvars.bind_contextvars(**bind_dict)


@task_postrun.connect
def cleanup_task_logging_context(
    sender=None,
    task_id=None,
    task=None,
    args=None,
    kwargs=None,
    retval=None,
    state=None,
    **kw,
):
    """Clears structlog contextvars after task execution to prevent worker state leakage."""
    structlog.contextvars.clear_contextvars()
