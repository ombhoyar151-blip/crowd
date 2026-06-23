import logging
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, ws: WebSocket, camera_id: str):
        await ws.accept()
        self._connections[camera_id].add(ws)
        logger.info("WS client connected (camera=%s, total=%d)", camera_id, len(self._connections[camera_id]))

    def disconnect(self, ws: WebSocket, camera_id: str):
        self._connections[camera_id].discard(ws)
        if not self._connections[camera_id]:
            del self._connections[camera_id]
        logger.info("WS client disconnected (camera=%s)", camera_id)

    async def broadcast(self, camera_id: str, data: dict):
        stale = set()
        for ws in self._connections.get(camera_id, set()):
            try:
                await ws.send_json(data)
            except WebSocketDisconnect:
                stale.add(ws)
            except Exception:
                stale.add(ws)
        for ws in stale:
            self.disconnect(ws, camera_id)

    @property
    def active_connections(self) -> int:
        return sum(len(v) for v in self._connections.values())


ws_manager = WebSocketManager()
