from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from models.crowd_snapshot import CrowdSnapshot, ZoneStatus


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


@pytest_asyncio.fixture
async def engine():
    from services.alerts.engine import AlertRuleEngine

    mock_redis = AsyncMock()
    mock_redis.exists.return_value = False
    mock_session_factory = MagicMock()

    eng = AlertRuleEngine(FakeSettings(), mock_session_factory, mock_redis)

    from backend.services.alert_service import save_alert
    save_alert_orig = __import__("backend.services.alert_service", fromlist=["save_alert"]).save_alert

    yield eng, mock_redis, mock_session_factory

    if "backend.services.alert_service" in __import__("sys").modules:
        __import__("backend.services.alert_service", fromlist=["save_alert"]).save_alert = save_alert_orig


@pytest.mark.asyncio
class TestAlertEngine:
    async def test_no_violation_no_alert(self, engine, monkeypatch):
        eng, mock_redis, mock_sf = engine
        snapshot = CrowdSnapshot(
            camera_id="cam_1",
            frame_number=1,
            timestamp=1000.0,
            person_count=5,
            density_score=0.3,
            zone_statuses=[
                ZoneStatus(zone_id="z1", zone_name="Zone 1", count=5, threshold=10, is_violated=False),
            ],
        )

        fired = await eng.evaluate(snapshot)
        assert fired == []

    async def test_violation_fires_alert(self, engine, monkeypatch):
        eng, mock_redis, mock_sf = engine

        mock_db = AsyncMock()
        mock_db.__aenter__.return_value = mock_db
        mock_sf.return_value = mock_db

        save_called = False

        async def fake_save_alert(**kwargs):
            nonlocal save_called


            save_called = True
            return 42

        monkeypatch.setattr("backend.services.alert_service.save_alert", fake_save_alert)

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

        fired = await eng.evaluate(snapshot)
        assert len(fired) == 1
        assert fired[0].alert_id == 42
        assert fired[0].camera_id == "cam_1"
        assert fired[0].severity == "warning"

    async def test_cooldown_suppresses_second_alert(self, engine, monkeypatch):
        eng, mock_redis, mock_sf = engine

        mock_db = AsyncMock()
        mock_db.__aenter__.return_value = mock_db
        mock_sf.return_value = mock_db

        call_count = 0

        async def fake_save_alert(**kwargs):
            nonlocal call_count
            call_count += 1
            return call_count

        monkeypatch.setattr("backend.services.alert_service.save_alert", fake_save_alert)

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

        fired1 = await eng.evaluate(snapshot)
        assert len(fired1) == 1

        mock_redis.exists.return_value = True

        fired2 = await eng.evaluate(snapshot)
        assert len(fired2) == 0

        assert call_count == 1

    async def test_cooldown_expires_fires_again(self, engine, monkeypatch):
        eng, mock_redis, mock_sf = engine

        mock_db = AsyncMock()
        mock_db.__aenter__.return_value = mock_db
        mock_sf.return_value = mock_db

        call_count = 0

        async def fake_save_alert(**kwargs):
            nonlocal call_count
            call_count += 1
            return call_count

        monkeypatch.setattr("backend.services.alert_service.save_alert", fake_save_alert)

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

        fired1 = await eng.evaluate(snapshot)
        assert len(fired1) == 1

        mock_redis.exists.return_value = False

        fired2 = await eng.evaluate(snapshot)
        assert len(fired2) == 1
        assert call_count == 2

    async def test_severity_warning(self, engine, monkeypatch):
        eng, mock_redis, mock_sf = engine
        eng._settings.alert_critical_ratio = 2.0

        mock_db = AsyncMock()
        mock_db.__aenter__.return_value = mock_db
        mock_sf.return_value = mock_db

        async def fake_save_alert(**kwargs):
            return 1

        monkeypatch.setattr("backend.services.alert_service.save_alert", fake_save_alert)

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

        fired = await eng.evaluate(snapshot)
        assert fired[0].severity == "warning"

    async def test_severity_critical(self, engine, monkeypatch):
        eng, mock_redis, mock_sf = engine
        eng._settings.alert_critical_ratio = 2.0

        mock_db = AsyncMock()
        mock_db.__aenter__.return_value = mock_db
        mock_sf.return_value = mock_db

        async def fake_save_alert(**kwargs):
            return 1

        monkeypatch.setattr("backend.services.alert_service.save_alert", fake_save_alert)

        snapshot = CrowdSnapshot(
            camera_id="cam_1",
            frame_number=1,
            timestamp=1000.0,
            person_count=25,
            density_score=0.9,
            zone_statuses=[
                ZoneStatus(zone_id="z1", zone_name="Zone 1", count=25, threshold=10, is_violated=True),
            ],
        )

        fired = await eng.evaluate(snapshot)
        assert fired[0].severity == "critical"

    async def test_multiple_zones_violated(self, engine, monkeypatch):
        eng, mock_redis, mock_sf = engine

        mock_db = AsyncMock()
        mock_db.__aenter__.return_value = mock_db
        mock_sf.return_value = mock_db

        call_count = 0

        async def fake_save_alert(**kwargs):
            nonlocal call_count
            call_count += 1
            return call_count

        monkeypatch.setattr("backend.services.alert_service.save_alert", fake_save_alert)

        snapshot = CrowdSnapshot(
            camera_id="cam_1",
            frame_number=1,
            timestamp=1000.0,
            person_count=20,
            density_score=0.7,
            zone_statuses=[
                ZoneStatus(zone_id="z1", zone_name="Zone 1", count=15, threshold=10, is_violated=True),
                ZoneStatus(zone_id="z2", zone_name="Zone 2", count=8, threshold=10, is_violated=False),
                ZoneStatus(zone_id="z3", zone_name="Zone 3", count=30, threshold=10, is_violated=True),
            ],
        )

        fired = await eng.evaluate(snapshot)
        assert len(fired) == 2
        assert call_count == 2
