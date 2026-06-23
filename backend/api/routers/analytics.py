from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user, get_db
from backend.db.models import CrowdSnapshotORM, UserORM
from backend.schemas.analytics import (
    SnapshotListResponse,
    SnapshotResponse,
    SummaryResponse,
)
from backend.services.analytics_service import get_current, get_history, get_summary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/current", response_model=SnapshotResponse)
async def current(
    camera_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
):
    snap = await get_current(db, camera_id)
    if not snap:
        raise HTTPException(status_code=404, detail="No snapshots found for this camera")
    return SnapshotResponse(
        id=snap.id,
        time=snap.time.isoformat(),
        camera_id=snap.camera_id,
        frame_number=snap.frame_number,
        person_count=snap.person_count,
        density_score=snap.density_score,
        heatmap_path=snap.heatmap_path,
    )


@router.get("/history", response_model=SnapshotListResponse)
async def history(
    camera_id: str = Query(...),
    from_: str | None = Query(None, alias="from"),
    to: str | None = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
):
    from_ts = datetime.fromisoformat(from_) if from_ else None
    to_ts = datetime.fromisoformat(to) if to else None

    items, total = await get_history(db, camera_id, from_ts, to_ts, limit, offset)
    return SnapshotListResponse(
        items=[
            SnapshotResponse(
                id=s.id,
                time=s.time.isoformat(),
                camera_id=s.camera_id,
                frame_number=s.frame_number,
                person_count=s.person_count,
                density_score=s.density_score,
                heatmap_path=s.heatmap_path,
            )
            for s in items
        ],
        total=total,
    )


@router.get("/summary", response_model=SummaryResponse)
async def summary(
    camera_id: str = Query(...),
    interval: str = Query("1 minute"),
    from_: str | None = Query(None, alias="from"),
    to: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
):
    from_ts = datetime.fromisoformat(from_) if from_ else None
    to_ts = datetime.fromisoformat(to) if to else None

    result = await get_summary(db, camera_id, interval, from_ts, to_ts)
    if not result:
        raise HTTPException(status_code=404, detail="No data found for this camera")
    return SummaryResponse(**result)
