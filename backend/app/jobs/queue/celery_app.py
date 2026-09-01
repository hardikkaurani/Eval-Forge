from celery import Celery
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
