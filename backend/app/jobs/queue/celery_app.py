from celery import Celery

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
    # Run tasks synchronously in same process for test envs to avoid Redis requirement
    task_always_eager=(settings.APP_ENV == "testing"),
    task_eager_propagates=True,
)
