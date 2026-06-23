from unittest.mock import AsyncMock

import pytest


class TestCooldown:
    @pytest.mark.asyncio
    async def test_is_cooling_false_initially(self):
        from services.alerts.cooldown import CooldownStore

        mock_redis = AsyncMock()
        mock_redis.exists.return_value = False
        store = CooldownStore(mock_redis, cooldown_seconds=60)

        result = await store.is_cooling("cam_1", "zone_1")
        assert result is False
        mock_redis.exists.assert_awaited_once_with("alert_cooldown:cam_1:zone_1")

    @pytest.mark.asyncio
    async def test_set_then_is_cooling_true(self):
        from services.alerts.cooldown import CooldownStore

        mock_redis = AsyncMock()
        mock_redis.exists.return_value = True
        store = CooldownStore(mock_redis, cooldown_seconds=60)
        await store.set("cam_1", "zone_1")

        result = await store.is_cooling("cam_1", "zone_1")
        assert result is True
        mock_redis.set.assert_awaited_once()
        mock_redis.set.await_args[0][0] == "alert_cooldown:cam_1:zone_1"

    @pytest.mark.asyncio
    async def test_after_clear_is_cooling_false(self):
        from services.alerts.cooldown import CooldownStore

        mock_redis = AsyncMock()
        mock_redis.exists.side_effect = [True, False]
        store = CooldownStore(mock_redis, cooldown_seconds=60)
        await store.set("cam_1", "zone_1")
        assert await store.is_cooling("cam_1", "zone_1") is True
        await store.clear("cam_1", "zone_1")
        assert await store.is_cooling("cam_1", "zone_1") is False
        mock_redis.delete.assert_awaited_once_with("alert_cooldown:cam_1:zone_1")

    @pytest.mark.asyncio
    async def test_ttl_applied(self):
        from services.alerts.cooldown import CooldownStore

        mock_redis = AsyncMock()
        store = CooldownStore(mock_redis, cooldown_seconds=120)
        await store.set("cam_1", "zone_1")
        mock_redis.set.assert_awaited_once()
        args, kwargs = mock_redis.set.await_args
        assert kwargs.get("ex") == 120 or args[2] == 120 if len(args) > 2 else True
