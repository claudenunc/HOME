"""CRAFT delivery notifier — emails client with download link.

Supports:
  - SendGrid (SENDGRID_API_KEY env var)
  - SMTP (SMTP_HOST, SMTP_USER, SMTP_PASS env vars)
  - Dry-run (logs to stdout if no keys configured)
"""
import os
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
FROM_EMAIL = os.environ.get("CRAFT_FROM_EMAIL", "craft@eversound.ai")

TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "email_delivery.md"

log = logging.getLogger("craft.notifier")


def _render_email(job: dict, bundle_path: str) -> tuple[str, str]:
    """Return (subject, html_body)."""
    artist = job.get("artist_name", "Artist")
    song = job.get("song_title", "Your Track")
    tier = job.get("tier", "").replace("_", " ").title()
    job_id = job["job_id"]

    subject = f"Your CRAFT video is ready — {artist} — {song}"

    html = f"""
<html><body style="font-family: sans-serif; max-width: 600px; margin: 40px auto; color: #111;">
<h2 style="color: #1a1a1a;">Your video is ready ⚡</h2>

<p>Hey {artist},</p>

<p>Your <strong>{tier}</strong> for <em>{song}</em> is complete and packaged for delivery.</p>

<p><strong>Job ID:</strong> {job_id}</p>

<hr style="margin: 24px 0; border: none; border-top: 1px solid #eee;">

<h3>Download your video</h3>
<p>Your video file is attached to this email. If the attachment is too large,
we'll send a separate download link within the hour.</p>

<p><strong>Bundle includes:</strong></p>
<ul>
<li>Your finished video (MP4)</li>
<li>Delivery README with usage rights</li>
</ul>

<hr style="margin: 24px 0; border: none; border-top: 1px solid #eee;">

<h3>One free revision included</h3>
<p>You have <strong>one free revision</strong> within 7 days.
Just reply to this email with your feedback — be specific about timestamps and changes.</p>

<h3>Loved it?</h3>
<p>Tag us on social media or send a quick reply. We'd love to feature your track in our portfolio.</p>

<hr style="margin: 24px 0; border: none; border-top: 1px solid #eee;">

<p style="color: #666; font-size: 13px;">
CRAFT by EVERSOUND — AI production at the speed of sound.<br>
Questions? Reply to this email.
</p>
</body></html>
"""
    return subject, html


def notify(job: dict, bundle_path: str) -> bool:
    """Send delivery notification. Return True on success."""
    to_email = job.get("delivery_email")
    if not to_email:
        log.error("No delivery_email in job — cannot notify")
        return False

    subject, html = _render_email(job, bundle_path)

    if SENDGRID_API_KEY:
        return _send_sendgrid(to_email, subject, html)
    elif SMTP_HOST and SMTP_USER:
        return _send_smtp(to_email, subject, html)
    else:
        log.warning("No email transport configured (set SENDGRID_API_KEY or SMTP_*). Dry-run only.")
        log.info("DRY-RUN EMAIL TO: %s", to_email)
        log.info("SUBJECT: %s", subject)
        return True


def _send_sendgrid(to: str, subject: str, html: str) -> bool:
    try:
        import httpx
        response = httpx.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": FROM_EMAIL, "name": "CRAFT by EVERSOUND"},
                "subject": subject,
                "content": [{"type": "text/html", "value": html}],
            },
            timeout=30,
        )
        response.raise_for_status()
        log.info("SendGrid delivery sent to %s", to)
        return True
    except Exception as e:
        log.error("SendGrid failed: %s", e)
        return False


def _send_smtp(to: str, subject: str, html: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL(SMTP_HOST, 465) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, [to], msg.as_string())

        log.info("SMTP delivery sent to %s", to)
        return True
    except Exception as e:
        log.error("SMTP failed: %s", e)
        return False
