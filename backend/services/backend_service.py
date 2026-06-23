import asyncio
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.analytics_service import save_snapshot
from backend.services.websocket_manager import ws_manager
from models.crowd_snapshot import CrowdSnapshot

logger = logging.getLogger(__name__)


class BackendService:
    def __init__(self):
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._session_factory = None
        self._celery_app = None

    def setup(
        self,
        loop: asyncio.AbstractEventLoop,
        session_factory,
        celery_app=None,
    ):
        self._loop = loop
        self._session_factory = session_factory
        self._celery_app = celery_app

    def ingest_snapshot(self, snapshot: CrowdSnapshot):
        if not self._loop or not self._session_factory:
            return

        asyncio.run_coroutine_threadsafe(
            self._do_ingest(snapshot),
            self._loop,
        )

    async def _do_ingest(self, snapshot: CrowdSnapshot):
        async with self._session_factory() as db:
            try:
                snapshot_id = await save_snapshot(db, snapshot)
                logger.debug("Saved snapshot %d (frame=%d)", snapshot_id, snapshot.frame_number)
            except Exception:
                logger.exception("Failed to save snapshot")

        try:
            await ws_manager.broadcast(
                snapshot.camera_id,
                snapshot.model_dump(),
            )
        except Exception:
            logger.exception("Failed to broadcast snapshot")

        if self._celery_app:
            try:
                self._celery_app.send_task(
                    "backend.worker.tasks.evaluate_alerts",
                    args=[snapshot.model_dump()],
                )
            except Exception:
                logger.exception("Failed to enqueue alert evaluation")


backend_service = BackendService()
