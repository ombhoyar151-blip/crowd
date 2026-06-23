import logging
from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import CrowdSnapshotORM, ZoneSnapshotORM
from models.crowd_snapshot import CrowdSnapshot

logger = logging.getLogger(__name__)


async def save_snapshot(db: AsyncSession, snapshot: CrowdSnapshot) -> int:
    ts = datetime.fromtimestamp(snapshot.timestamp, tz=timezone.utc)

    orm = CrowdSnapshotORM(
        time=ts,
        camera_id=snapshot.camera_id,
        frame_number=snapshot.frame_number,
        person_count=snapshot.person_count,
        density_score=snapshot.density_score,
        heatmap_path=snapshot.heatmap_path,
    )
    db.add(orm)
    await db.flush()

    for zs in snapshot.zone_statuses:
        zone_orm = ZoneSnapshotORM(
            snapshot_id=orm.id,
            time=ts,
            camera_id=snapshot.camera_id,
            zone_id=zs.zone_id,
            zone_name=zs.zone_name,
            count=zs.count,
            threshold=zs.threshold,
            is_violated=zs.is_violated,
        )
        db.add(zone_orm)

    await db.commit()
    return orm.id


async def get_current(db: AsyncSession, camera_id: str) -> CrowdSnapshotORM | None:
    stmt = (
        select(CrowdSnapshotORM)
        .where(CrowdSnapshotORM.camera_id == camera_id)
        .order_by(CrowdSnapshotORM.time.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_history(
    db: AsyncSession,
    camera_id: str,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[CrowdSnapshotORM], int]:
    stmt = select(CrowdSnapshotORM).where(CrowdSnapshotORM.camera_id == camera_id)

    if from_ts:
        stmt = stmt.where(CrowdSnapshotORM.time >= from_ts)
    if to_ts:
        stmt = stmt.where(CrowdSnapshotORM.time <= to_ts)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0

    stmt = stmt.order_by(CrowdSnapshotORM.time.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def get_summary(
    db: AsyncSession,
    camera_id: str,
    interval: str = "1 minute",
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
) -> dict | None:
    where_clause = "camera_id = :camera_id"
    params = {"camera_id": camera_id}

    if from_ts:
        where_clause += " AND time >= :from_ts"
        params["from_ts"] = from_ts
    if to_ts:
        where_clause += " AND time <= :to_ts"
        params["to_ts"] = to_ts

    query = text(f"""
        SELECT
            AVG(person_count)::float AS avg_count,
            MAX(person_count) AS max_count,
            MIN(person_count) AS min_count,
            COUNT(*) AS total
        FROM crowd_snapshots
        WHERE {where_clause}
    """)

    result = await db.execute(query, params)
    row = result.one_or_none()

    if not row or row.total == 0:
        return None

    return {
        "camera_id": camera_id,
        "interval": interval,
        "avg_person_count": round(float(row.avg_count), 2),
        "max_person_count": int(row.max_count),
        "min_person_count": int(row.min_count),
        "total_snapshots": int(row.total),
    }
