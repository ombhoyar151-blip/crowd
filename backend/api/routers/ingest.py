from fastapi import APIRouter

from models.crowd_snapshot import CrowdSnapshot

from backend.services.backend_service import backend_service

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", status_code=202)
async def ingest_snapshot(snapshot: CrowdSnapshot):
    """Accept a snapshot JSON payload and forward it to the backend service.

    This endpoint is intentionally unauthenticated to allow local pipeline
    processes to POST snapshots. In production you should protect it.
    """
    try:
        backend_service.ingest_snapshot(snapshot)
    except Exception:
        # swallow exceptions — backend_service runs async tasks and logs errors
        pass
    return {"status": "accepted"}
