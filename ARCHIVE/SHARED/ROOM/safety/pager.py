"""
SHARED/ROOM/safety/pager.py

THE ROOM — single outbound-alert surface. "Page Unc."

Replaces the direct Telegram code that used to live in escalation.py and
deadman.py. Now every page goes through page_unc(text) here. Under the hood,
three delivery paths are tried in order until one succeeds:

    1) IFTTT Webhooks applet (Nathan's preferred primary)
       - env: IFTTT_WEBHOOK_URL   (full URL, maker.ifttt.com/...)
          OR IFTTT_WEBHOOKS_KEY   (key only) + IFTTT_EVENT_NAME (default "envy_page")
       - POST {"value1": <subject>, "value2": <body>, "value3": <severity>}

    2) SMTP email to PAGER_EMAIL (default iamaienvy@gmail.com)
       - IFTTT Gmail-trigger applets watch this inbox and SMS Unc's phone.
       - env: GMAIL_USER, GMAIL_APP_PASSWORD (Gmail app-specific password).

    3) Direct carrier email-to-SMS gateway (zero-IFTTT path, also free)
       - env: PAGER_SMS_GATEWAY (e.g. "2707090697@tmomail.net")
       - Same SMTP creds as (2).

Paths are tried in order. First success wins, the rest are skipped. If all
three fail, the function returns False and the caller logs it.

Nathan (contact reference):
    Phone   : 270-709-0697
    Email   : iamaienvy@gmail.com

These values are CONFIGURABLE via env, but the constants below are the
documented defaults so a fresh box knows where pages go by default.

Owner: BEACON (safety layer)
Replaces: Telegram paths in safety/escalation.py + safety/deadman.py
"""
from __future__ import annotations

import json
import logging
import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional
from urllib import request as urlrequest
from urllib.error import URLError

ROOM_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = ROOM_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Env loader (same locations escalation.py used). Does NOT raise if missing.
_ENV_PATHS = [
    Path(r"C:\Users\natej\OneDrive\Desktop\AI_FAMILY_getting_ORGANIZED\ENVY\ENVY-SYSTEM\CREDENTIALS\.env"),
    Path(r"C:\Users\natej\OneDrive\Desktop\AI_FAMILY_getting_ORGANIZED\BEACON\LIGHTHOUSE_LIVE\.env"),
    ROOM_DIR / ".env",
]
for _p in _ENV_PATHS:
    if _p.exists():
        for _line in _p.read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [pager] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pager.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("pager")

# Documented defaults (Nathan's contact info). Overridable via env.
DEFAULT_PAGER_EMAIL = "iamaienvy@gmail.com"
DEFAULT_PAGER_PHONE = "270-709-0697"
DEFAULT_IFTTT_EVENT = "envy_page"


# ---------------------------------------------------------------------------
# Path 1: IFTTT Webhooks
# ---------------------------------------------------------------------------

def _ifttt_url() -> Optional[str]:
    """Build the IFTTT trigger URL from env, or return None if not configured."""
    full = os.environ.get("IFTTT_WEBHOOK_URL", "").strip()
    if full:
        return full
    key = os.environ.get("IFTTT_WEBHOOKS_KEY", "").strip()
    event = os.environ.get("IFTTT_EVENT_NAME", DEFAULT_IFTTT_EVENT).strip()
    if key and event:
        return f"https://maker.ifttt.com/trigger/{event}/with/key/{key}"
    return None


def _page_ifttt(subject: str, body: str, severity: str = "INFO") -> bool:
    url = _ifttt_url()
    if not url:
        return False
    payload = json.dumps({
        "value1": subject[:200],   # IFTTT ingredient 1 — short header
        "value2": body[:1500],     # IFTTT ingredient 2 — main text
        "value3": severity[:40],   # IFTTT ingredient 3 — severity tag
    }).encode("utf-8")
    req = urlrequest.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=10) as resp:
            status = resp.status
            msg = resp.read().decode("utf-8", errors="replace")[:200]
        if 200 <= status < 300:
            log.info(f"paged via IFTTT webhook, status={status}")
            return True
        log.warning(f"ifttt status={status} body={msg}")
        return False
    except URLError as exc:
        log.error(f"ifttt URLError: {exc}")
    except Exception as exc:  # noqa: BLE001
        log.error(f"ifttt send failed: {exc}")
    return False


# ---------------------------------------------------------------------------
# Path 2 & 3: SMTP (Gmail) → mailbox OR carrier SMS gateway
# ---------------------------------------------------------------------------

def _smtp_send(to_addr: str, subject: str, body: str) -> bool:
    user = os.environ.get("GMAIL_USER", "").strip() or DEFAULT_PAGER_EMAIL
    password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    if not password:
        log.info("GMAIL_APP_PASSWORD unset — SMTP path disabled")
        return False
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com").strip()
    port = int(os.environ.get("SMTP_PORT", "587"))

    msg = MIMEMultipart()
    msg["From"] = user
    msg["To"] = to_addr
    msg["Subject"] = subject[:250]
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        with smtplib.SMTP(host, port, timeout=15) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(user, password)
            s.sendmail(user, [to_addr], msg.as_string())
        log.info(f"paged via SMTP → {to_addr}")
        return True
    except Exception as exc:  # noqa: BLE001
        log.error(f"smtp send failed: {exc}")
        return False


def _page_email(subject: str, body: str) -> bool:
    """Email the page to the watched inbox (IFTTT Gmail-trigger picks it up)."""
    to_addr = os.environ.get("PAGER_EMAIL", DEFAULT_PAGER_EMAIL).strip()
    if not to_addr:
        return False
    return _smtp_send(to_addr, subject, body)


def _page_sms_gateway(subject: str, body: str) -> bool:
    """Email the page to the carrier SMS gateway address (no IFTTT)."""
    gw = os.environ.get("PAGER_SMS_GATEWAY", "").strip()
    if not gw:
        return False
    # Carrier SMS bodies are 160-char-ish; don't waste the send with long prose.
    short = f"{subject}\n{body}"[:320]
    return _smtp_send(gw, subject[:40], short)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def page_unc(text: str, *, subject: str = "BEACON ALERT", severity: str = "INFO") -> bool:
    """Send a page to Nathan. Returns True if ANY delivery path succeeded.

    Replaces the old Telegram-only page path. Safe to call from multiple
    processes (escalation, deadman, silence_watcher) — each call is
    independent and does not share state.

    Message shape:
      - `subject` is the one-line headline (e.g. "BEACON DEAD-MAN ALERT").
      - `text` is the multi-line body.
      - `severity` is INFO|WARN|HIGH|CRITICAL, used as IFTTT value3 so applets
        can branch (e.g. SMS only on HIGH+).

    Never raises. Swallows all transport errors and logs them.
    """
    text = text or ""
    # 1. IFTTT webhook (primary)
    if _page_ifttt(subject, text, severity):
        return True
    # 2. SMTP email to watched inbox (IFTTT Gmail-trigger picks it up)
    if _page_email(subject, text):
        return True
    # 3. Direct carrier SMS gateway (no IFTTT at all)
    if _page_sms_gateway(subject, text):
        return True
    log.error(
        f"ALL page paths failed. subject={subject!r} severity={severity!r} "
        f"— check IFTTT_WEBHOOK_URL / GMAIL_APP_PASSWORD / PAGER_SMS_GATEWAY envs"
    )
    return False


# ---------------------------------------------------------------------------
# CLI (for manual testing: python -m safety.pager "test page")
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="Send a test page to Nathan.")
    p.add_argument("body", nargs="?", default="pager.py test page — all channels",
                   help="message body")
    p.add_argument("--subject", default="BEACON TEST", help="subject line")
    p.add_argument("--severity", default="INFO", help="INFO|WARN|HIGH|CRITICAL")
    args = p.parse_args()
    ok = page_unc(args.body, subject=args.subject, severity=args.severity)
    sys.stderr.write(f"page_unc → {ok}\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
