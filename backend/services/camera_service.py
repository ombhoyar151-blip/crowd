from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import CameraORM


async def get_cameras(db: AsyncSession) -> list[CameraORM]:
    stmt = select(CameraORM).order_by(CameraORM.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_camera(db: AsyncSession, camera_id: str) -> CameraORM | None:
    stmt = select(CameraORM).where(CameraORM.id == camera_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
