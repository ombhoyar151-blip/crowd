import asyncio
import logging

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.base import Base
from backend.db.models import CameraORM, UserORM
from backend.db.session import create_engine_and_session
from config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    settings = Settings()
    engine, session_factory = create_engine_and_session(settings)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as db:
        result = await db.execute(select(UserORM).where(UserORM.username == "admin"))
        if not result.scalar_one_or_none():
            admin = UserORM(
                username="admin",
                hashed_password=pwd_context.hash("changeme"),
                is_active=True,
                role="admin",
            )
            db.add(admin)
            await db.commit()
            logger.info("Created admin user (username=admin, password=changeme)")
        else:
            logger.info("Admin user already exists")

    async with session_factory() as db:
        for cam_data in [
            {"id": "cam_1", "name": "Main Entrance", "source_type": "file", "source_url": "sample.mp4"},
            {"id": "cam_2", "name": "Parking Lot", "source_type": "rtsp", "source_url": "rtsp://admin:password@192.168.1.100:554/stream1"},
            {"id": "cam_3", "name": "Lobby Camera", "source_type": "webcam", "source_url": "0"},
        ]:
            result = await db.execute(select(CameraORM).where(CameraORM.id == cam_data["id"]))
            if not result.scalar_one_or_none():
                db.add(CameraORM(**cam_data))

        await db.commit()
        logger.info("Camera definitions seeded")

    await engine.dispose()
    logger.info("Database seeding complete")


if __name__ == "__main__":
    asyncio.run(seed())
