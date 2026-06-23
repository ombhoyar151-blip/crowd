from celery import Celery

from config.settings import Settings

settings = Settings()

# Use memory:// backend when no Redis is configured
_backend = settings.redis_url if not settings.redis_url.startswith("memory://") else None

celery_app = Celery(
    "crowd",
    broker=settings.redis_url,
    backend=_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    task_ignore_result=True,
    # Run tasks synchronously in the same process when using memory broker
    task_always_eager=settings.redis_url.startswith("memory://"),
    task_eager_propagates=True,
)

celery_app.autodiscover_tasks(["backend.worker"])
