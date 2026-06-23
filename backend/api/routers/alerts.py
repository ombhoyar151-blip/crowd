from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user, get_db
from backend.db.models import UserORM
from backend.schemas.alert import AlertListResponse, AlertResponse
from backend.services.alert_service import get_alerts, resolve_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    camera_id: str | None = Query(None),
    from_: str | None = Query(None, alias="from"),
    to: str | None = Query(None),
    unresolved_only: bool = Query(False),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
):
    from_ts = datetime.fromisoformat(from_) if from_ else None
    to_ts = datetime.fromisoformat(to) if to else None

    items, total = await get_alerts(db, camera_id, from_ts, to_ts, unresolved_only, limit, offset)
    return AlertListResponse(
        items=[
            AlertResponse(
                id=a.id,
                time=a.time.isoformat(),
                camera_id=a.camera_id,
                zone_id=a.zone_id,
                zone_name=a.zone_name,
                count=a.count,
                threshold=a.threshold,
                severity=a.severity,
                message=a.message,
                resolved_at=a.resolved_at.isoformat() if a.resolved_at else None,
            )
            for a in items
        ],
        total=total,
    )


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    alert = await resolve_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertResponse(
        id=alert.id,
        time=alert.time.isoformat(),
        camera_id=alert.camera_id,
        zone_id=alert.zone_id,
        zone_name=alert.zone_name,
        count=alert.count,
        threshold=alert.threshold,
        severity=alert.severity,
        message=alert.message,
        resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
    )
