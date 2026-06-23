import logging

import httpx

logger = logging.getLogger(__name__)


class TelegramAlertChannel:
    def __init__(self, settings):
        self._enabled = settings.alert_telegram_enabled
        self._token = settings.telegram_bot_token
        self._chat_id = settings.telegram_chat_id

    async def send(self, alert) -> None:
        if not self._enabled:
            return

        icon = "\U0001f6a8" if alert.severity == "critical" else "\u26a0\ufe0f"
        text = (
            f"{icon} [{alert.severity.upper()}] Crowd Alert\n\n"
            f"\U0001f4cd Zone: {alert.zone_name}\n"
            f"\U0001f4f7 Camera: {alert.camera_id}\n"
            f"\U0001f465 Count: {alert.count} / {alert.threshold} threshold\n"
            f"\u23f0 Time: {alert.timestamp}\n\n"
            f"{alert.message}"
        )

        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload = {"chat_id": self._chat_id, "text": text, "parse_mode": "HTML"}

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                logger.info("Telegram alert sent to chat %s", self._chat_id)
            except Exception:
                logger.exception("Failed to send Telegram alert")
