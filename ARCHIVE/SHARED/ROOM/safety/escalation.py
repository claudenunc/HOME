"""
SHARED/ROOM/safety/escalation.py

BEACON's escalation pager.

Contract:
  - Reads all kind='crisis' events with status='open' whose respond_by has
    passed AND responded_at IS NULL.
  - For each, send a page to Unc via safety/pager.py (IFTTT webhook →
    email-to-SMS fallback — see pager.py for the full path chain).
  - Mark the escalation in meta.escalated_at so we don't spam.

This is the LAST LINE. If BEACON didn't respond in time, or a silence_watcher
fired, or the DB trigger emitted a crisis row, Unc hears about it on his
phone within seconds.

Runs as:
  - Cron (every 60s) — `python -m SHARED.ROOM.safety.escalation`
  - Or from the deadman.py loop after health check.

Outbound channel:
  - safety.pager.page_unc(text, subject=..., severity=...). Configured via env
    (IFTTT_WEBHOOK_URL, GMAIL_APP_PASSWORD, PAGER_SMS_GATEWAY).
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOM_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOM_DIR / "room.db"
FEED_PATH = ROOM_DIR / "feed.jsonl"
LOG_DIR = ROOM_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [escalation] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "escalation.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("escalation")


# ---------------------------------------------------------------------------
# Page via the unified pager (IFTTT webhook → SMTP → SMS-gateway chain)
# ---------------------------------------------------------------------------

def page_unc(text: str, *, subject: str = "BEACON ESCALATION", severity: str = "HIGH") -> bool:
    """Page Unc. Delegates to safety.pager which handles IFTTT + email-to-SMS."""
    try:
        sys.path.insert(0, str(ROOM_DIR))
        from safety.pager import page_unc as _pager_page  # type: ignore
    except Exception as exc:  # noqa: BLE001
        log.error(f"pager import failed: {exc}")
        return False
    return bool(_pager_page(text, subject=subject, severity=severity))


# ---------------------------------------------------------------------------
# Query + mark
# ---------------------------------------------------------------------------

def _fetch_stale_crises_sqlite() -> list[dict]:
    """Crisis rows where respond_by < now AND responded_at is NULL AND status='open'."""
    if not DB_PATH.exists():
        return []
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        con = sqlite3.connect(str(DB_PATH))
        con.row_factory = sqlite3.Row
        cur = con.execute(
            "SELECT id, ts, author, kind, body, risk_level, emotional_weight, "
            "       assigned_to, respond_by, responded_at, status, meta, reply_to "
            "FROM events "
            "WHERE kind = 'crisis' AND status = 'open' "
            "  AND responded_at IS NULL "
            "  AND respond_by IS NOT NULL AND respond_by < ? "
            "ORDER BY respond_by ASC",
            (now_iso,),
        )
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        return rows
    except sqlite3.Error as exc:
        log.error(f"sqlite read failed: {exc}")
        return []


def _already_paged_sqlite(event_id: str) -> bool:
    """Check meta.escalated_at — don't spam."""
    if not DB_PATH.exists():
        return False
    try:
        con = sqlite3.connect(str(DB_PATH))
        cur = con.execute(
            "SELECT json_extract(meta,'$.escalated_at') FROM events WHERE id = ?",
            (event_id,),
        )
        row = cur.fetchone()
        con.close()
        return row is not None and row[0] is not None
    except sqlite3.Error:
        return False


def _mark_paged_sqlite(event_id: str) -> bool:
    """Write meta.escalated_at on the crisis event. Append-only rule allows meta updates."""
    if not DB_PATH.exists():
        return False
    paged_at = datetime.now(timezone.utc).isoformat()
    try:
        con = sqlite3.connect(str(DB_PATH))
        con.execute(
            "UPDATE events SET meta = json_set(COALESCE(meta,'{}'), '$.escalated_at', ?) "
            "WHERE id = ?",
            (paged_at, event_id),
        )
        con.commit()
        con.close()
        return True
    except sqlite3.Error as exc:
        log.error(f"sqlite mark failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _format_page(ev: dict) -> str:
    risk = (ev.get("risk_level") or "").upper() or "UNKNOWN"
    source = ev.get("reply_to") or "(no source)"
    meta = ev.get("meta") or {}
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except json.JSONDecodeError:
            meta = {}
    reason = meta.get("auto_emitted_by") or "db_trigger"
    body = (ev.get("body") or "")[:600]
    respond_by = ev.get("respond_by") or "(no deadline)"

    return (
        f"BEACON ESCALATION — {risk}\n"
        f"Unc, a crisis event passed its respond_by with no acknowledgment.\n\n"
        f"Event: {ev.get('id')}\n"
        f"Source event: {source}\n"
        f"Deadline was: {respond_by}\n"
        f"Reason: {reason}\n\n"
        f"--- Body ---\n{body}\n\n"
        f"Reply to this message to close the loop. I will stop paging once responded_at is set."
    )


def on_crisis_event(event: dict) -> None:
    """Fast-path hook called from room_daemon.tail_loop after fan-out.

    Contract with EVERSOUND's daemon (see COMMS direct 0853):
      - Called synchronously, one event at a time.
      - May raise; caller swallows + logs.
      - Only called for kind='crisis' OR risk_level in {HIGH, CRITICAL}.

    Behavior:
      - If respond_by already passed → page Unc immediately.
      - Else → no-op. The cron tick (every 60s) picks it up at deadline.
    """
    respond_by_str = event.get("respond_by")
    if not respond_by_str:
        return
    try:
        if respond_by_str.endswith("Z"):
            deadline = datetime.fromisoformat(respond_by_str[:-1]).replace(tzinfo=timezone.utc)
        else:
            deadline = datetime.fromisoformat(respond_by_str)
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
    except ValueError:
        return

    now = datetime.now(timezone.utc)
    if now < deadline:
        return  # cron handles it at the deadline — don't double-page

    event_id = str(event.get("id") or "")
    if event_id and _already_paged_sqlite(event_id):
        return

    if event.get("responded_at"):
        return

    text = _format_page(event)
    risk = (event.get("risk_level") or "HIGH").upper()
    severity = "CRITICAL" if risk == "CRITICAL" else "HIGH"
    subject = f"BEACON ESCALATION — {risk}"
    if page_unc(text, subject=subject, severity=severity) and event_id:
        _mark_paged_sqlite(event_id)


def run() -> int:
    """Single tick. Returns count of pages delivered."""
    stale = _fetch_stale_crises_sqlite()
    if not stale:
        log.info("no stale crises")
        return 0

    delivered = 0
    for ev in stale:
        if _already_paged_sqlite(str(ev["id"])):
            continue
        text = _format_page(ev)
        risk = (ev.get("risk_level") or "HIGH").upper()
        severity = "CRITICAL" if risk == "CRITICAL" else "HIGH"
        subject = f"BEACON ESCALATION — {risk}"
        ok = page_unc(text, subject=subject, severity=severity)
        if ok:
            _mark_paged_sqlite(str(ev["id"]))
            delivered += 1
        else:
            log.error(f"FAILED to page for event {ev['id']} — will retry next tick")
    return delivered


def main() -> int:
    n = run()
    log.info(f"tick done, paged={n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
