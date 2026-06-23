from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.settings import Settings

_engine = None
async_session_factory: Optional[async_sessionmaker] = None


def create_engine_and_session(settings: Settings):
    global _engine, async_session_factory

    db_url = settings.database_url
    if db_url.startswith("sqlite+aiosqlite"):
        _engine = create_async_engine(db_url, echo=False)
    else:
        _engine = create_async_engine(
            db_url,
            pool_size=settings.database_pool_size,
            max_overflow=10,
            echo=False,
        )

    async_session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return _engine, async_session_factory


def get_engine():
    return _engine
