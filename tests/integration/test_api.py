import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.api.routers.auth import create_access_token, hash_password
from backend.db.base import Base
from backend.db.models import UserORM
from backend.db.session import create_engine_and_session
from backend.main import app


@pytest_asyncio.fixture
async def test_db():
    settings = type("Settings", (), {
        "database_url": "sqlite+aiosqlite:///./test.db",
        "database_pool_size": 5,
        "redis_url": "redis://localhost:6379/0",
        "jwt_secret_key": "test_secret",
        "jwt_algorithm": "HS256",
        "cors_origins": ["*"],
        "api_prefix": "/api/v1",
        "backend_port": 8000,
        "log_level": "INFO",
        "output_dir": "output",
    })()

    engine, session_factory = create_engine_and_session(settings)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as db:
        db.add(UserORM(
            username="admin",
            hashed_password=hash_password("changeme"),
            is_active=True,
            role="admin",
        ))
        await db.commit()

    from backend.dependencies import get_db

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield engine, session_factory, settings

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
class TestAPI:
    async def test_login_success(self, test_db):
        engine, sf, settings = test_db
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.post("/api/v1/auth/token", json={"username": "admin", "password": "changeme"})
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, test_db):
        engine, sf, settings = test_db
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.post("/api/v1/auth/token", json={"username": "admin", "password": "wrong"})
            assert resp.status_code == 401

    async def test_protected_without_token(self, test_db):
        engine, sf, settings = test_db
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get("/api/v1/analytics/current?camera_id=cam_1")
            assert resp.status_code == 401

    async def test_get_current_no_data(self, test_db):
        engine, sf, settings = test_db
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            token = create_access_token("admin")
            resp = await client.get(
                "/api/v1/analytics/current?camera_id=cam_1",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 404

    async def test_get_history_empty(self, test_db):
        engine, sf, settings = test_db
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            token = create_access_token("admin")
            resp = await client.get(
                "/api/v1/analytics/history?camera_id=cam_1",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["items"] == []
            assert data["total"] == 0

    async def test_get_alerts_empty(self, test_db):
        engine, sf, settings = test_db
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            token = create_access_token("admin")
            resp = await client.get(
                "/api/v1/alerts",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["items"] == []

    async def test_health(self, test_db):
        engine, sf, settings = test_db
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"
