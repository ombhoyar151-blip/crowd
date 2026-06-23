import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from services.alerts.channels import (
    EmailAlertChannel,
    TelegramAlertChannel,
    WebSocketAlertChannel,
)
from services.alerts.cooldown import CooldownStore

logger = logging.getLogger(__name__)


@dataclass
class FiredAlert:
    alert_id: int
    camera_id: str
    zone_id: str
    zone_name: str
    count: int
    threshold: int
    severity: str
    message: str
    timestamp: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())


class AlertRuleEngine:
    def __init__(self, settings, session_factory, redis_client):
        self._settings = settings
        self._session_factory = session_factory
        self._cooldown = CooldownStore(redis_client, settings.alert_cooldown_seconds)
        self._ws_channel = WebSocketAlertChannel(redis_client)
        self._email_channel = EmailAlertChannel(settings)
        self._telegram_channel = TelegramAlertChannel(settings)

    async def evaluate(self, snapshot) -> list[FiredAlert]:
        fired: list[FiredAlert] = []

        for zone in snapshot.zone_statuses:
            if not zone.is_violated:
                continue

            if await self._cooldown.is_cooling(snapshot.camera_id, zone.zone_id):
                logger.debug("Cooldown active for %s/%s, skipping", snapshot.camera_id, zone.zone_id)
                continue

            severity = self._classify(zone.count, zone.threshold)
            message = self._build_message(severity, zone)

            from backend.services.alert_service import save_alert

            async with self._session_factory() as db:
                try:
                    alert_id = await save_alert(
                        db=db,
                        camera_id=snapshot.camera_id,
                        zone_id=zone.zone_id,
                        zone_name=zone.zone_name,
                        count=zone.count,
                        threshold=zone.threshold,
                        severity=severity,
                        message=message,
                    )
                except Exception:
                    logger.exception("Failed to save alert to DB")
                    continue

            await self._cooldown.set(snapshot.camera_id, zone.zone_id)

            fired_alert = FiredAlert(
                alert_id=alert_id,
                camera_id=snapshot.camera_id,
                zone_id=zone.zone_id,
                zone_name=zone.zone_name,
                count=zone.count,
                threshold=zone.threshold,
                severity=severity,
                message=message,
                timestamp=snapshot.timestamp,
            )

            await self._ws_channel.publish(fired_alert)
            await self._email_channel.send(fired_alert)
            await self._telegram_channel.send(fired_alert)

            fired.append(fired_alert)

        return fired

    def _classify(self, count: int, threshold: int) -> str:
        ratio = count / threshold if threshold else 0
        if ratio >= self._settings.alert_critical_ratio:
            return "critical"
        return "warning"

    @staticmethod
    def _build_message(severity: str, zone) -> str:
        if severity == "critical":
            return (
                f"[CRITICAL] Zone \"{zone.zone_name}\": {zone.count} people detected "
                f"(threshold: {zone.threshold}). Severe overcrowding \u2014 immediate action required."
            )
        return (
            f"[WARNING] Zone \"{zone.zone_name}\": {zone.count} people detected "
            f"(threshold: {zone.threshold}). Mild overcrowding."
        )
