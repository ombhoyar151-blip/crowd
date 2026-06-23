import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


class EmailAlertChannel:
    def __init__(self, settings):
        self._enabled = settings.alert_email_enabled
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._username = settings.smtp_username
        self._password = settings.smtp_password
        self._from_addr = settings.alert_email_from
        self._to_addrs = settings.alert_email_to

    async def send(self, alert) -> None:
        if not self._enabled:
            return

        subject = f"[{alert.severity.upper()}] Crowd Alert \u2014 {alert.zone_name} ({alert.camera_id})"

        body_html = f"""\
<html><body style="font-family:sans-serif;padding:20px">
<h2 style="color:{'#dc3545' if alert.severity == 'critical' else '#ffc107'}">
  {alert.severity.upper()} Crowd Alert
</h2>
<table style="border-collapse:collapse;width:100%;max-width:500px">
  <tr><td style="padding:8px;font-weight:bold">Zone</td><td>{alert.zone_name}</td></tr>
  <tr><td style="padding:8px;font-weight:bold">Camera</td><td>{alert.camera_id}</td></tr>
  <tr><td style="padding:8px;font-weight:bold">Count</td><td>{alert.count} / {alert.threshold} threshold</td></tr>
  <tr><td style="padding:8px;font-weight:bold">Severity</td><td>{alert.severity}</td></tr>
</table>
<p>{alert.message}</p>
</body></html>"""

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(self._to_addrs)
        msg.attach(MIMEText(alert.message, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        loop = asyncio.get_event_loop()

        def _send():
            try:
                with smtplib.SMTP(self._host, self._port, timeout=10) as server:
                    server.starttls()
                    if self._username:
                        server.login(self._username, self._password)
                    server.sendmail(self._from_addr, self._to_addrs, msg.as_string())
                logger.info("Email alert sent to %s", self._to_addrs)
            except Exception:
                logger.exception("Failed to send email alert")

        await loop.run_in_executor(None, _send)
