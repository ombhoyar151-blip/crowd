import pytest


def pytest_importorskip(modname):
    try:
        __import__(modname)
        return True
    except ImportError:
        return False


HAS_REDIS = False
try:
    import redis.asyncio as redis
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    r = loop.run_until_complete(redis.from_url("redis://localhost:6379/1", decode_responses=True))
    loop.run_until_complete(r.ping())
    loop.run_until_complete(r.aclose())
    loop.close()
    HAS_REDIS = True
except Exception:
    HAS_REDIS = False


pytestmark = pytest.mark.skipif(not HAS_REDIS, reason="Redis not available")


class FakeSettings:
    alert_cooldown_seconds = 60
    alert_critical_ratio = 2.0
    alert_email_enabled = False
    alert_telegram_enabled = False
    smtp_host = "smtp.example.com"
    smtp_port = 587
    smtp_username = ""
    smtp_password = ""
    alert_email_from = ""
    alert_email_to = []
    telegram_bot_token = ""
    telegram_chat_id = ""


@pytest.fixture
def engine_and_db():
    import redis.asyncio as redis

    from backend.db.base import Base
    from backend.db.session import create_engine_and_session
    from services.alerts.engine import AlertRuleEngine

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    redis_client = loop.run_until_complete(
        redis.from_url("redis://localhost:6379/1", decode_responses=True)
    )
    loop.run_until_complete(redis_client.flushdb())

    engine, session_factory = create_engine_and_session(
        type(
            "Settings",
            (),
            {
                "database_url": "sqlite+aiosqlite:///./test_alert_flow.db",
                "database_pool_size": 5,
            },
        )()
    )
    loop.run_until_complete(
        engine.begin().__aenter__.then(
            lambda conn: conn.run_sync(Base.metadata.create_all)
        )
    )
    loop.close()

    alert_engine = AlertRuleEngine(FakeSettings(), session_factory, redis_client)

    yield alert_engine, session_factory, redis_client, engine

    import asyncio
    loop2 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop2)
    loop2.run_until_complete(
        engine.begin().__aenter__.then(
            lambda conn: conn.run_sync(Base.metadata.drop_all)
        )
    )
    loop2.run_until_complete(engine.dispose())
    loop2.run_until_complete(redis_client.flushdb())
    loop2.run_until_complete(redis_client.aclose())
    loop2.close()


@pytest.mark.asyncio
class TestAlertFlow:
    async def test_violated_snapshot_creates_alert_in_db(self, engine_and_db):
        alert_engine, session_factory, redis_client, _ = engine_and_db

        from models.crowd_snapshot import CrowdSnapshot, ZoneStatus
        snapshot = CrowdSnapshot(
            camera_id="cam_1",
            frame_number=1,
            timestamp=1000.0,
            person_count=15,
            density_score=0.6,
            zone_statuses=[
                ZoneStatus(zone_id="z1", zone_name="Zone 1", count=15, threshold=10, is_violated=True),
            ],
        )

        fired = await alert_engine.evaluate(snapshot)
        assert len(fired) == 1

        async with session_factory() as db:
            from sqlalchemy import select
            from backend.db.models import AlertORM
            result = await db.execute(select(AlertORM))
            rows = result.scalars().all()
            assert len(rows) == 1
            assert rows[0].camera_id == "cam_1"
            assert rows[0].zone_id == "z1"
            assert rows[0].count == 15
            assert rows[0].threshold == 10

    async def test_cooldown_prevents_duplicate_db_row(self, engine_and_db):
        alert_engine, session_factory, redis_client, _ = engine_and_db

        from models.crowd_snapshot import CrowdSnapshot, ZoneStatus
        snapshot = CrowdSnapshot(
            camera_id="cam_1",
            frame_number=1,
            timestamp=1000.0,
            person_count=15,
            density_score=0.6,
            zone_statuses=[
                ZoneStatus(zone_id="z1", zone_name="Zone 1", count=15, threshold=10, is_violated=True),
            ],
        )

        fired1 = await alert_engine.evaluate(snapshot)
        assert len(fired1) == 1

        fired2 = await alert_engine.evaluate(snapshot)
        assert len(fired2) == 0

        async with session_factory() as db:
            from sqlalchemy import select
            from backend.db.models import AlertORM
            result = await db.execute(select(AlertORM))
            rows = result.scalars().all()
            assert len(rows) == 1

    async def test_alert_published_to_redis(self, engine_and_db):
        import json

        alert_engine, session_factory, redis_client, _ = engine_and_db

        pubsub = redis_client.pubsub()
        await pubsub.subscribe("crowd:alerts:cam_1")

        from models.crowd_snapshot import CrowdSnapshot, ZoneStatus
        snapshot = CrowdSnapshot(
            camera_id="cam_1",
            frame_number=1,
            timestamp=1000.0,
            person_count=15,
            density_score=0.6,
            zone_statuses=[
                ZoneStatus(zone_id="z1", zone_name="Zone 1", count=15, threshold=10, is_violated=True),
            ],
        )

        fired = await alert_engine.evaluate(snapshot)
        assert len(fired) == 1

        message = await pubsub.get_message(timeout=2.0)
        while message and message["type"] != "message":
            message = await pubsub.get_message(timeout=2.0)

        assert message is not None
        data = json.loads(message["data"])
        assert data["alert_id"] == 1
        assert data["camera_id"] == "cam_1"
        assert data["severity"] == "warning"

        await pubsub.unsubscribe("crowd:alerts:cam_1")
