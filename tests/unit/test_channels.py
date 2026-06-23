from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.alerts.channels.email import EmailAlertChannel
from services.alerts.channels.telegram import TelegramAlertChannel
from services.alerts.channels.websocket import WebSocketAlertChannel
from services.alerts.engine import FiredAlert


@pytest.fixture
def fired_alert():
    return FiredAlert(
        alert_id=1,
        camera_id="cam_1",
        zone_id="zone_1",
        zone_name="Main Entrance",
        count=20,
        threshold=10,
        severity="critical",
        message="[CRITICAL] Zone ...",
        timestamp=1718000000.0,
    )


class FakeSettings:
    alert_email_enabled = True
    smtp_host = "smtp.example.com"
    smtp_port = 587
    smtp_username = "user"
    smtp_password = "pass"
    alert_email_from = "from@test.com"
    alert_email_to = ["to@test.com"]
    alert_telegram_enabled = True
    telegram_bot_token = "123:ABC"
    telegram_chat_id = "-100123"


class FakeSettingsDisabled:
    alert_email_enabled = False
    smtp_host = "smtp.example.com"
    smtp_port = 587
    smtp_username = "user"
    smtp_password = "pass"
    alert_email_from = "from@test.com"
    alert_email_to = ["to@test.com"]
    alert_telegram_enabled = False
    telegram_bot_token = "123:ABC"
    telegram_chat_id = "-100123"


class TestWebSocketChannel:
    @pytest.mark.asyncio
    async def test_publishes_to_redis(self, fired_alert):
        mock_redis = AsyncMock()
        channel = WebSocketAlertChannel(mock_redis)
        await channel.publish(fired_alert)

        mock_redis.publish.assert_awaited_once()
        args = mock_redis.publish.await_args
        assert args[0][0] == "crowd:alerts:cam_1"
        assert "Main Entrance" in args[0][1]


class TestEmailChannel:
    @pytest.mark.asyncio
    async def test_sends_smtp(self, fired_alert):
        settings = FakeSettings()
        channel = EmailAlertChannel(settings)

        with patch("services.alerts.channels.email.smtplib.SMTP") as mock_smtp:
            instance = mock_smtp.return_value.__enter__.return_value
            await channel.send(fired_alert)

            instance.sendmail.assert_called_once()
            call_args = instance.sendmail.call_args[0]
            assert call_args[0] == "from@test.com"
            assert "to@test.com" in call_args[1]

    @pytest.mark.asyncio
    async def test_disabled_skips(self, fired_alert):
        settings = FakeSettingsDisabled()
        channel = EmailAlertChannel(settings)

        with patch("services.alerts.channels.email.smtplib.SMTP") as mock_smtp:
            await channel.send(fired_alert)
            mock_smtp.assert_not_called()

    @pytest.mark.asyncio
    async def test_smtp_failure_no_raise(self, fired_alert):
        settings = FakeSettings()
        channel = EmailAlertChannel(settings)

        with patch("services.alerts.channels.email.smtplib.SMTP", side_effect=Exception("SMTP down")):
            await channel.send(fired_alert)


class TestTelegramChannel:
    @pytest.mark.asyncio
    async def test_posts_http(self, fired_alert):
        settings = FakeSettings()
        channel = TelegramAlertChannel(settings)

        with patch("httpx.AsyncClient") as mock_client:
            instance = mock_client.return_value.__aenter__.return_value
            instance.post = AsyncMock()
            instance.post.return_value.raise_for_status = MagicMock()

            await channel.send(fired_alert)

            instance.post.assert_awaited_once()
            url = instance.post.await_args[0][0]
            assert "api.telegram.org" in url

    @pytest.mark.asyncio
    async def test_disabled_skips(self, fired_alert):
        settings = FakeSettingsDisabled()
        channel = TelegramAlertChannel(settings)

        with patch("httpx.AsyncClient") as mock_client:
            await channel.send(fired_alert)
            mock_client.assert_not_called()

    @pytest.mark.asyncio
    async def test_network_failure_no_raise(self, fired_alert):
        settings = FakeSettings()
        channel = TelegramAlertChannel(settings)

        with patch("httpx.AsyncClient") as mock_client:
            instance = mock_client.return_value.__aenter__.return_value
            instance.post = AsyncMock(side_effect=Exception("Network error"))

            await channel.send(fired_alert)
