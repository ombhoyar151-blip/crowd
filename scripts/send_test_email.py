#!/usr/bin/env python3
"""Send a single test email using the project's SMTP settings (reads .env via Settings).

Usage: python scripts/send_test_email.py
"""
import sys
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Ensure project root is on sys.path so imports like `config.settings` work
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import Settings


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

    host = settings.smtp_host
    port = int(settings.smtp_port)
    username = settings.smtp_username
    password = settings.smtp_password
    from_addr = settings.alert_email_from or username
    to_addrs = _ensure_list(settings.alert_email_to) or ["ombhoyar151@gmail.com"]

    subject = "[TEST] CrowdSense SMTP Test"
    body = "This is a test email sent by the CrowdSense test script. If you received this, SMTP is configured correctly."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    msg.attach(MIMEText(body, "plain"))

    print(f"Connecting to SMTP {host}:{port} as {username}...")

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.ehlo()
            server.starttls()
            if username:
                server.login(username, password)
            server.sendmail(from_addr, to_addrs, msg.as_string())

        print("Email sent to:", to_addrs)
        sys.exit(0)
    except Exception as exc:
        print("Failed to send email:", exc)
        sys.exit(2)


if __name__ == "__main__":
    main()
