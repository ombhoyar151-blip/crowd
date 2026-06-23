import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import AlertORM

logger = logging.getLogger(__name__)


async def save_alert(
    db: AsyncSession,
    camera_id: str,
    zone_id: str,
    zone_name: str,
    count: int,
    threshold: int,
    severity: str,
    message: str,
) -> int:
    orm = AlertORM(
        time=datetime.now(timezone.utc),
        camera_id=camera_id,
        zone_id=zone_id,
        zone_name=zone_name,
        count=count,
        threshold=threshold,
        severity=severity,
        message=message,
    )
    db.add(orm)
    await db.commit()
    await db.refresh(orm)
    return orm.id


async def get_alerts(
    db: AsyncSession,
    camera_id: str | None = None,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    unresolved_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AlertORM], int]:
    stmt = select(AlertORM)

    if camera_id:
        stmt = stmt.where(AlertORM.camera_id == camera_id)
    if from_ts:
        stmt = stmt.where(AlertORM.time >= from_ts)
    if to_ts:
        stmt = stmt.where(AlertORM.time <= to_ts)
    if unresolved_only:
        stmt = stmt.where(AlertORM.resolved_at.is_(None))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0

    stmt = stmt.order_by(AlertORM.time.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def resolve_alert(db: AsyncSession, alert_id: int) -> AlertORM | None:
    stmt = select(AlertORM).where(AlertORM.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if alert:
        alert.resolved_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(alert)
    return alert
