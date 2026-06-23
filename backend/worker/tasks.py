import asyncio
import logging

from backend.worker.celery_app import celery_app
from config.settings import Settings
from models.crowd_snapshot import CrowdSnapshot

logger = logging.getLogger(__name__)

_settings = None
_engine = None


def _make_redis_client(settings):
    if settings.redis_url.startswith("memory://") or not settings.redis_url.startswith(
        ("redis://", "rediss://", "unix://")
    ):
        from services.alerts.null_redis import NullRedis
        return NullRedis()

    import asyncio as _asyncio
    import redis.asyncio as redis
    loop = asyncio.new_event_loop()
    client = loop.run_until_complete(
        redis.from_url(settings.redis_url, decode_responses=True)
    )
    loop.close()
    return client


def _get_alert_engine():
    global _engine, _settings
    if _engine is not None:
        return _engine

    _settings = Settings()

    from backend.db.session import create_engine_and_session
    from services.alerts.engine import AlertRuleEngine

    redis_client = _make_redis_client(_settings)
    _, session_factory = create_engine_and_session(_settings)
    _engine = AlertRuleEngine(_settings, session_factory, redis_client)
    return _engine


@celery_app.task(name="backend.worker.tasks.evaluate_alerts")
def evaluate_alerts(snapshot_data: dict):
    logger.info("Evaluating alerts for frame %s", snapshot_data.get("frame_number"))
    snapshot = CrowdSnapshot(**snapshot_data)
    asyncio.run(_run_evaluation(snapshot))
    return {"status": "evaluated"}


async def _run_evaluation(snapshot: CrowdSnapshot):
    engine = _get_alert_engine()
    await engine.evaluate(snapshot)


@celery_app.task(name="backend.worker.tasks.send_email_alert")
def send_email_alert(alert_data: dict):
    logger.info("Email alert stub: %s", alert_data.get("message"))
    return {"status": "logged"}


@celery_app.task(name="backend.worker.tasks.send_telegram_alert")
def send_telegram_alert(alert_data: dict):
    logger.info("Telegram alert stub: %s", alert_data.get("message"))
    return {"status": "logged"}
