import json
import logging

logger = logging.getLogger(__name__)


class AlertBroadcaster:
    def __init__(self, redis_client, ws_manager):
        self._redis = redis_client
        self._ws_manager = ws_manager

    async def run(self):
        pubsub = self._redis.pubsub()
        await pubsub.psubscribe("crowd:alerts:*")

        logger.info("Alert broadcaster subscribed to crowd:alerts:*")

        async for message in pubsub.listen():
            if message["type"] != "pmessage":
                continue

            try:
                data = json.loads(message["data"])
                camera_id = data.get("camera_id")
                if not camera_id:
                    continue

                data["type"] = "alert"
                await self._ws_manager.broadcast(camera_id, data)
            except Exception:
                logger.exception("Error broadcasting alert to WebSocket clients")
