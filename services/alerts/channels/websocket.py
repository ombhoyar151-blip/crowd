import json
import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)


class WebSocketAlertChannel:
    """Publishes fired alerts to Redis Pub/Sub.

    When NullRedis is injected (no Redis configured), the publish is a no-op
    and alerts are still delivered via the in-process WebSocket manager
    through the backend_service broadcast path.
    """

    def __init__(self, redis_client):
        self._redis = redis_client

    async def publish(self, alert) -> None:
        try:
            channel = f"crowd:alerts:{alert.camera_id}"
            payload = json.dumps(asdict(alert))
            await self._redis.publish(channel, payload)
        except Exception as exc:
            logger.debug("WS alert channel publish skipped: %s", exc)
