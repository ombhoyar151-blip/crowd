#!/usr/bin/env python3
"""Send a sample crowd alert using the project's EmailAlertChannel.

Usage: python scripts/send_sample_alert.py
"""
import os
import sys
import asyncio
import json
from types import SimpleNamespace

# Ensure project root is on sys.path so imports like `config.settings` work
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import Settings
from services.alerts.channels.email import EmailAlertChannel


def _ensure_list(val):
    if val is None:
        return []
    if isinstance(val, (list, tuple)):
        return list(val)
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [val]
    return [str(val)]


def main():
    settings = Settings()

    if not settings.alert_email_enabled:
        print("Email alerts are disabled in settings (ALERT_EMAIL_ENABLED=false)")
        sys.exit(1)

    channel = EmailAlertChannel(settings)

    # Ensure we have at least one recipient
    to_addrs = _ensure_list(settings.alert_email_to)
    if not to_addrs:
        fallback = [settings.alert_email_from or "ombhoyar151@gmail.com"]
        channel._to_addrs = fallback

    threshold = int(getattr(settings, "alert_scene_threshold", 10))
    count = threshold + 2
    severity = "critical" if (count / threshold) >= settings.alert_critical_ratio else "warning"
    message = (
        f"[{severity.upper()}] Whole Scene: {count} people detected (threshold: {threshold}). "
        "This is a sample alert sent for testing purposes."
    )

    alert = SimpleNamespace(
        alert_id=0,
        camera_id="sample-camera",
        zone_id="scene",
        zone_name="Whole Scene",
        count=count,
        threshold=threshold,
        severity=severity,
        message=message,
        timestamp=None,
    )

    print("Sending sample alert:", message)
    try:
        asyncio.run(channel.send(alert))
        print("Sample alert send complete.")
    except Exception as exc:
        print("Failed to send sample alert:", exc)
        sys.exit(2)


if __name__ == "__main__":
    main()
