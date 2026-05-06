"""
THE ROOM - Python API (v1 implementation)
=========================================

Thin API over the event spine. Every ingress (BRIDGE, Claude sessions,
COMMS markdown file-watcher, Supabase edge function) calls these functions.

Substrate (per EVERSOUND R2 substrate-pick):
  - SQLite WAL at SHARED/ROOM/room.db is the query-optimized truth.
  - feed.jsonl at SHARED/ROOM/feed.jsonl is the append-only tee the daemon
    fans out from.
  - Supabase room_events is a nightly mirror (phase 2, not wired here).

Write path contract (from EVERSOUND's R2 DIRECT message):
    JSONL first, then SQLite. Atomic by transaction on the DB side;
    the JSONL append is OS-atomic via O_APPEND.

Author:  ORPHEUS
Version: 1.1 (R3 implementation on EVERSOUND's substrate)
Schema:  SHARED/ROOM/SCHEMA.md
DDL:     SHARED/ROOM/migrations/0001_init_events.sql
Views:   SHARED/ROOM/migrations/0003_views.sql
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Optional, TypedDict


# -----------------------------------------------------------------------------
# Paths (resolved from this file; OneDrive-safe absolute)
# -----------------------------------------------------------------------------

ROOM_DIR = Path(__file__).resolve().parent
DB_PATH = ROOM_DIR / "room.db"
FEED_PATH = ROOM_DIR / "feed.jsonl"
MIGRATIONS_DIR = ROOM_DIR / "migrations"
LOG_DIR = ROOM_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


# -----------------------------------------------------------------------------
# Type aliases
# -----------------------------------------------------------------------------

Sibling = Literal[
    "NATHAN", "ENVY", "BEACON", "EVERSOUND", "NEVAEH", "ORPHEUS", "ATLAS",
    "GATE", "BRIDGE",
]

Kind = Literal[
    "drop", "message", "question", "answer", "handoff", "proposal",
    "decision", "revision", "status", "ack", "task", "crisis",
]

Status = Literal["open", "seen", "answered", "resolved", "superseded", "dropped"]

EmotionalWeight = Literal["rest", "reach", "pain", "crisis"]

RiskLevel = Literal["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

TaskState = Literal[
    "OPEN", "CLAIMED", "IN_PROGRESS", "BLOCKED",
    "DONE", "ACKED", "DROPPED", "HANDED_OFF",
]

Source = Literal[
    "telegram", "phone_drop", "claude_session", "comms_md", "webhook", "bridge",
]


class Event(TypedDict, total=False):
    """One row of the events table. See SCHEMA.md."""
    id: str
    ts: str
    author: Sibling
    kind: Kind
    room: str
    thread_id: Optional[str]
    reply_to: Optional[str]
    addressed_to: list[str]
    routed_to: Optional[list[str]]
    body: str
    attachments: Optional[list[str]]
    source: Source
    source_ref: Optional[str]
    status: Status
    seen_by: list[str]
    emotional_weight: Optional[EmotionalWeight]
    risk_level: Optional[RiskLevel]
    assigned_to: Optional[Sibling]
    respond_by: Optional[str]
    responded_at: Optional[str]
    task_state: Optional[TaskState]
    meta: dict[str, Any]
    hash: str
    prev_hash: Optional[str]


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------

class CrisisClassifierError(RuntimeError):
    """BEACON's classifier is unavailable and we cannot silently degrade."""


class RoomIntegrityError(RuntimeError):
    """Hash-chain or invariant violation."""


# -----------------------------------------------------------------------------
# ULID (26-char Crockford base32, timestamp-prefixed, lexicographically sortable)
# -----------------------------------------------------------------------------

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_ULID_LAST_TS: int = 0
_ULID_LAST_RAND: int = 0
_ULID_LOCK = threading.Lock()


def _ulid() -> str:
    """Generate a monotonically-increasing ULID. Pure-Python, no deps."""
    global _ULID_LAST_TS, _ULID_LAST_RAND
    with _ULID_LOCK:
        ts_ms = int(time.time() * 1000)
        if ts_ms <= _ULID_LAST_TS:
            # Same millisecond: bump randomness monotonically to preserve ordering.
            ts_ms = _ULID_LAST_TS
            rand = (_ULID_LAST_RAND + 1) & ((1 << 80) - 1)
        else:
            rand = int.from_bytes(secrets.token_bytes(10), "big")
        _ULID_LAST_TS = ts_ms
        _ULID_LAST_RAND = rand

    # 48 bits of ts -> 10 chars, 80 bits of rand -> 16 chars. Total 26.
    value = (ts_ms << 80) | rand
    out = []
    for _ in range(26):
        out.append(_CROCKFORD[value & 0x1F])
        value >>= 5
    return "".join(reversed(out))


# -----------------------------------------------------------------------------
# Connection management
# -----------------------------------------------------------------------------

_CONN_LOCAL = threading.local()


def _conn() -> sqlite3.Connection:
    """Per-thread sqlite3 connection with WAL + foreign_keys + row_factory."""
    c = getattr(_CONN_LOCAL, "conn", None)
    if c is not None:
        return c
    c = sqlite3.connect(
        str(DB_PATH),
        isolation_level=None,  # autocommit; we drive BEGIN/COMMIT manually
        check_same_thread=False,
        timeout=30.0,
    )
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode = WAL;")
    c.execute("PRAGMA foreign_keys = ON;")
    c.execute("PRAGMA busy_timeout = 5000;")
    _CONN_LOCAL.conn = c
    return c


def _init_db_if_missing() -> None:
    """Apply migration 0001 + 0003 if the events table isn't there yet."""
    c = _conn()
    have = c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='events';"
    ).fetchone()
    if have:
        return
    for mig in ("0001_init_events.sql", "0003_views.sql"):
        path = MIGRATIONS_DIR / mig
        if not path.exists():
            continue
        sql = path.read_text(encoding="utf-8")
        # Extract the SQLite block between BEGIN SQLITE / END SQLITE markers.
        begin = sql.find("-- BEGIN SQLITE")
        end = sql.find("-- END SQLITE")
        block = sql[begin:end] if (begin != -1 and end != -1) else sql
        c.executescript(block)


# -----------------------------------------------------------------------------
# Hashing + chain
# -----------------------------------------------------------------------------

def _event_hash(author: str, ts: str, kind: str, body: str) -> str:
    h = hashlib.sha256()
    h.update(f"{author}|{ts}|{kind}|{body}".encode("utf-8"))
    return h.hexdigest()


def _prev_hash() -> Optional[str]:
    """Hash of the immediately-preceding ULID row. NULL for first row."""
    row = _conn().execute(
        "SELECT hash FROM events ORDER BY id DESC LIMIT 1;"
    ).fetchone()
    return row["hash"] if row else None


# -----------------------------------------------------------------------------
# Crisis classifier hook (BEACON's territory; soft dependency)
# -----------------------------------------------------------------------------

def _classify(author: str, body: str, kind: str = "drop") -> tuple[Optional[str], Optional[str]]:
    """Call BEACON's classifier mirror. HARD-FAIL on import per R3 plan.

    Canonical location: SHARED/ROOM/safety/classifier.py
    This is the Python mirror of migrations/0002_beacon_classifier.sql; the
    SQLite substrate has no BEFORE-INSERT row-mutating triggers, so the
    write-path invariant "no NATHAN row enters the room unclassified" is
    enforced here.

    Returns: (risk_level, emotional_weight). Either may be None for sibling
    chatter. NATHAN authors always get a non-None risk_level.

    Raises:
      CrisisClassifierError if classifier cannot be imported OR if it errors
      on a NATHAN-authored body. Matches BEACON's write-path invariant.
    """
    try:
        # Relative import from the room package. safety/classifier.py is
        # the ported LIGHTHOUSE v20 PATTERN regex set.
        from safety.classifier import classify_text  # type: ignore
    except ImportError as exc:
        # Try absolute path fallback so we still work when room.py is imported
        # from sibling directories.
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "room_safety_classifier",
                str(ROOM_DIR / "safety" / "classifier.py"),
            )
            if spec is None or spec.loader is None:
                raise CrisisClassifierError(
                    "classifier spec could not be built"
                ) from exc
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            classify_text = mod.classify_text  # type: ignore[attr-defined]
        except Exception as inner:
            # HARD FAIL. No silent degradation for NATHAN.
            raise CrisisClassifierError(
                f"classifier unavailable: {inner}"
            ) from inner

    try:
        rl, ew = classify_text(body=body, author=author, kind=kind)
        return rl, ew
    except Exception as exc:
        if author == "NATHAN":
            raise CrisisClassifierError(
                f"classifier errored on NATHAN body: {exc}"
            ) from exc
        return ("NONE", None)


# -----------------------------------------------------------------------------
# Kind-level invariants (match DB CHECK constraints; fail early, fail loud)
# -----------------------------------------------------------------------------

def _validate_invariants(
    kind: str,
    reply_to: Optional[str],
    assigned_to: Optional[str],
    respond_by: Optional[str],
    task_state: Optional[str],
    meta: dict[str, Any],
) -> None:
    if kind == "answer" and not reply_to:
        raise ValueError("kind='answer' requires reply_to")
    if kind == "handoff" and not (assigned_to and reply_to):
        raise ValueError("kind='handoff' requires assigned_to + reply_to")
    if kind == "crisis" and not (assigned_to and respond_by and reply_to):
        raise ValueError(
            "kind='crisis' requires assigned_to + respond_by + reply_to"
        )
    if kind == "task" and not task_state:
        raise ValueError("kind='task' requires task_state")
    if kind in ("decision", "revision", "proposal") and not meta.get("decision_slug"):
        raise ValueError(f"kind='{kind}' requires meta.decision_slug")

    # NEVAEH R3 amendment: meta.tone_note is 140-char hard cap.
    tone = meta.get("tone_note")
    if tone is not None:
        if not isinstance(tone, str):
            raise ValueError("meta.tone_note must be a string")
        if len(tone) > 140:
            raise ValueError("meta.tone_note exceeds 140 chars")


# -----------------------------------------------------------------------------
# JSONL tee (append-only, O_APPEND atomic)
# -----------------------------------------------------------------------------

_FEED_LOCK = threading.Lock()


def _tee_feed(event_row: dict[str, Any]) -> None:
    """Append one event as a JSON line. O_APPEND on POSIX; best-effort on NT."""
    line = json.dumps(event_row, ensure_ascii=False, separators=(",", ":"))
    with _FEED_LOCK:
        # Open with append binary; UTF-8 with trailing newline.
        with open(FEED_PATH, "ab") as f:
            f.write(line.encode("utf-8") + b"\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                # OneDrive can refuse fsync; fine - OS buffer + OneDrive sync handle durability.
                pass


# -----------------------------------------------------------------------------
# Core insert
# -----------------------------------------------------------------------------

def _insert_row(row: dict[str, Any]) -> None:
    c = _conn()
    c.execute(
        """
        INSERT INTO events (
          id, ts, author, kind, room, thread_id, reply_to,
          addressed_to, routed_to, body, attachments,
          source, source_ref, status, seen_by,
          emotional_weight, risk_level, assigned_to, respond_by, responded_at,
          task_state, meta, hash, prev_hash
        ) VALUES (
          :id, :ts, :author, :kind, :room, :thread_id, :reply_to,
          :addressed_to, :routed_to, :body, :attachments,
          :source, :source_ref, :status, :seen_by,
          :emotional_weight, :risk_level, :assigned_to, :respond_by, :responded_at,
          :task_state, :meta, :hash, :prev_hash
        );
        """,
        row,
    )


def _serialize(
    *,
    id: str,
    ts: str,
    author: str,
    kind: str,
    room: str,
    thread_id: Optional[str],
    reply_to: Optional[str],
    addressed_to: list[str],
    routed_to: Optional[list[str]],
    body: str,
    attachments: Optional[list[str]],
    source: str,
    source_ref: Optional[str],
    status: str,
    seen_by: list[str],
    emotional_weight: Optional[str],
    risk_level: Optional[str],
    assigned_to: Optional[str],
    respond_by: Optional[str],
    responded_at: Optional[str],
    task_state: Optional[str],
    meta: dict[str, Any],
    hash_: str,
    prev_hash: Optional[str],
) -> dict[str, Any]:
    """Produce a DB-ready row with JSON fields stringified."""
    return {
        "id": id,
        "ts": ts,
        "author": author,
        "kind": kind,
        "room": room,
        "thread_id": thread_id,
        "reply_to": reply_to,
        "addressed_to": json.dumps(addressed_to, ensure_ascii=False),
        "routed_to": json.dumps(routed_to, ensure_ascii=False) if routed_to else None,
        "body": body,
        "attachments": json.dumps(attachments, ensure_ascii=False) if attachments else None,
        "source": source,
        "source_ref": source_ref,
        "status": status,
        "seen_by": json.dumps(seen_by, ensure_ascii=False),
        "emotional_weight": emotional_weight,
        "risk_level": risk_level,
        "assigned_to": assigned_to,
        "respond_by": respond_by,
        "responded_at": responded_at,
        "task_state": task_state,
        "meta": json.dumps(meta, ensure_ascii=False),
        "hash": hash_,
        "prev_hash": prev_hash,
    }


def _deserialize(row: sqlite3.Row) -> Event:
    """Turn a sqlite3.Row back into an Event TypedDict."""
    d: dict[str, Any] = dict(row)
    for jk in ("addressed_to", "routed_to", "seen_by", "attachments", "meta"):
        v = d.get(jk)
        if v is None:
            continue
        try:
            d[jk] = json.loads(v)
        except (TypeError, json.JSONDecodeError):
            pass
    return d  # type: ignore[return-value]


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def post(
    kind: Kind,
    author: Sibling,
    body: str,
    *,
    addressed_to: Optional[list[str]] = None,
    reply_to: Optional[str] = None,
    thread_id: Optional[str] = None,
    routed_to: Optional[list[str]] = None,
    assigned_to: Optional[Sibling] = None,
    respond_by: Optional[str] = None,
    source: Source = "claude_session",
    source_ref: Optional[str] = None,
    attachments: Optional[list[str]] = None,
    emotional_weight: Optional[EmotionalWeight] = None,
    risk_level: Optional[RiskLevel] = None,
    task_state: Optional[TaskState] = None,
    meta: Optional[dict[str, Any]] = None,
    room: str = "main",
) -> str:
    """Write a single event to the spine. Returns the generated ULID.

    Contract (ORDER MATTERS):
      1. Generate ULID, stamp ts, compute hash + prev_hash.
      2. Validate kind-specific invariants.
      3. Run BEACON's classifier (populates risk_level / emotional_weight
         if caller didn't set them). Crisis-before-commit invariant.
      4. Open SQLite TRANSACTION.
      5. APPEND TO feed.jsonl FIRST (EVERSOUND's contract).
      6. INSERT into events SECOND.
      7. COMMIT.
    """
    _init_db_if_missing()

    meta = dict(meta or {})
    addressed_to = addressed_to or ["ALL"]

    _validate_invariants(kind, reply_to, assigned_to, respond_by, task_state, meta)

    # Classify (populates risk_level + emotional_weight if not provided).
    auto_rl, auto_ew = _classify(author=author, body=body, kind=kind)
    if risk_level is None:
        risk_level = auto_rl  # type: ignore[assignment]
    if emotional_weight is None:
        emotional_weight = auto_ew  # type: ignore[assignment]

    event_id = _ulid()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
        f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"

    # thread_id defaults to id on root events.
    effective_thread_id = thread_id or event_id

    h = _event_hash(author=author, ts=ts, kind=kind, body=body)

    c = _conn()
    # Begin an IMMEDIATE transaction so prev_hash is stable across concurrent writers.
    c.execute("BEGIN IMMEDIATE;")
    try:
        prev = _prev_hash()
        row = _serialize(
            id=event_id,
            ts=ts,
            author=author,
            kind=kind,
            room=room,
            thread_id=effective_thread_id,
            reply_to=reply_to,
            addressed_to=addressed_to,
            routed_to=routed_to,
            body=body,
            attachments=attachments,
            source=source,
            source_ref=source_ref,
            status="open",
            seen_by=[],
            emotional_weight=emotional_weight,
            risk_level=risk_level,
            assigned_to=assigned_to,
            respond_by=respond_by,
            responded_at=None,
            task_state=task_state,
            meta=meta,
            hash_=h,
            prev_hash=prev,
        )
        # JSONL FIRST (per EVERSOUND's substrate contract):
        # if DB write fails, the daemon still fans out from feed.jsonl.
        feed_row = {**row}
        # Inflate JSON fields back into objects for the JSONL tee so readers
        # (daemon, tail, projection) don't have to double-parse.
        for jk in ("addressed_to", "routed_to", "seen_by", "attachments", "meta"):
            v = feed_row.get(jk)
            if isinstance(v, str):
                try:
                    feed_row[jk] = json.loads(v)
                except json.JSONDecodeError:
                    pass
        _tee_feed(feed_row)
        # DB SECOND:
        _insert_row(row)
        c.execute("COMMIT;")
    except Exception:
        c.execute("ROLLBACK;")
        raise

    return event_id


def post_from_feed(line: dict[str, Any]) -> str:
    """EVERSOUND's daemon calls this when replaying feed.jsonl into the spine.

    Idempotent on `id`: duplicate inserts become no-ops. This is the path
    used on daemon restart to catch the DB up to feed.jsonl truth.
    """
    _init_db_if_missing()
    event_id = line["id"]
    c = _conn()
    have = c.execute(
        "SELECT 1 FROM events WHERE id = ? LIMIT 1;", (event_id,)
    ).fetchone()
    if have:
        return event_id

    meta = line.get("meta") or {}
    if isinstance(meta, str):
        meta = json.loads(meta)

    def _j(x: Any, default: Any) -> str:
        if x is None:
            return json.dumps(default)
        if isinstance(x, str):
            return x  # already a JSON string
        return json.dumps(x)

    row = {
        "id": event_id,
        "ts": line["ts"],
        "author": line["author"],
        "kind": line["kind"],
        "room": line.get("room", "main"),
        "thread_id": line.get("thread_id") or event_id,
        "reply_to": line.get("reply_to"),
        "addressed_to": _j(line.get("addressed_to"), ["ALL"]),
        "routed_to": _j(line.get("routed_to"), None) if line.get("routed_to") else None,
        "body": line["body"],
        "attachments": _j(line.get("attachments"), None) if line.get("attachments") else None,
        "source": line.get("source", "claude_session"),
        "source_ref": line.get("source_ref"),
        "status": line.get("status", "open"),
        "seen_by": _j(line.get("seen_by"), []),
        "emotional_weight": line.get("emotional_weight"),
        "risk_level": line.get("risk_level"),
        "assigned_to": line.get("assigned_to"),
        "respond_by": line.get("respond_by"),
        "responded_at": line.get("responded_at"),
        "task_state": line.get("task_state"),
        "meta": json.dumps(meta, ensure_ascii=False),
        "hash": line.get("hash")
            or _event_hash(line["author"], line["ts"], line["kind"], line["body"]),
        "prev_hash": line.get("prev_hash"),
    }
    c.execute("BEGIN IMMEDIATE;")
    try:
        _insert_row(row)
        c.execute("COMMIT;")
    except sqlite3.IntegrityError:
        # Race with another writer inserting the same ULID - idempotent.
        c.execute("ROLLBACK;")
    except Exception:
        c.execute("ROLLBACK;")
        raise
    return event_id


def inbox(sibling: Sibling, *, unread_only: bool = True, limit: int = 50) -> list[Event]:
    """Return events addressed_to or routed_to `sibling`.

    With `unread_only=True`, filters out events where sibling is in seen_by
    EXCEPT for kinds that must re-surface (question, handoff, crisis).
    Ordered by ULID ascending (oldest first).
    """
    _init_db_if_missing()
    c = _conn()
    addr_like = f'%"{sibling}"%'
    all_like = '%"ALL"%'
    routed_like = f'%"{sibling}"%'
    seen_like = f'%"{sibling}"%'

    where_seen = ""
    if unread_only:
        where_seen = (
            "AND (seen_by NOT LIKE ? OR kind IN ('question','handoff','crisis')) "
        )

    sql = (
        "SELECT * FROM events WHERE status IN ('open','seen') "
        "AND (addressed_to LIKE ? OR addressed_to LIKE ? "
        "     OR (routed_to IS NOT NULL AND routed_to LIKE ?)) "
        + where_seen +
        "ORDER BY id ASC LIMIT ?;"
    )
    params: list[Any] = [addr_like, all_like, routed_like]
    if unread_only:
        params.append(seen_like)
    params.append(limit)
    rows = c.execute(sql, params).fetchall()
    return [_deserialize(r) for r in rows]


def thread(thread_id: str) -> list[Event]:
    """Return every event in a thread, ordered by ULID (which is ts-prefixed)."""
    _init_db_if_missing()
    c = _conn()
    rows = c.execute(
        "SELECT * FROM events WHERE thread_id = ? OR id = ? ORDER BY id ASC;",
        (thread_id, thread_id),
    ).fetchall()
    return [_deserialize(r) for r in rows]


def ask(
    author: Sibling,
    to_sibling: Sibling | list[str],
    body: str,
    *,
    respond_by: Optional[str] = None,
    thread_id: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> str:
    """Post a question. Returns the question's ULID."""
    addressed = [to_sibling] if isinstance(to_sibling, str) else list(to_sibling)
    return post(
        kind="question",
        author=author,
        body=body,
        addressed_to=addressed,
        thread_id=thread_id,
        respond_by=respond_by,
        meta=meta,
    )


def answer(
    question_id: str,
    author: Sibling,
    body: str,
    *,
    meta: Optional[dict[str, Any]] = None,
) -> str:
    """Post an answer that closes a question. Trigger flips question's status."""
    _init_db_if_missing()
    c = _conn()
    q = c.execute(
        "SELECT kind, status, thread_id FROM events WHERE id = ?;",
        (question_id,),
    ).fetchone()
    if q is None:
        raise ValueError(f"question {question_id} not found")
    if q["kind"] != "question":
        raise ValueError(f"event {question_id} is kind={q['kind']}, not question")
    if q["status"] == "answered":
        # Allow secondary answers (multiple siblings weigh in) but flag in meta.
        meta = {**(meta or {}), "secondary_answer": True}
    return post(
        kind="answer",
        author=author,
        body=body,
        reply_to=question_id,
        thread_id=q["thread_id"],
        meta=meta,
    )


def decide(
    author: Sibling,
    slug: str,
    body: str,
    *,
    supersedes: Optional[str] = None,
    thread_id: Optional[str] = None,
    reply_to: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> str:
    """Post a decision. If supersedes is given, emit a revision first to flip
    the prior decision's status via the trigger.
    """
    _init_db_if_missing()
    meta = {**(meta or {}), "decision_slug": slug, "decided_by": author}

    if supersedes:
        c = _conn()
        prior = c.execute(
            "SELECT kind, meta FROM events WHERE id = ?;", (supersedes,)
        ).fetchone()
        if prior is None:
            raise ValueError(f"supersedes target {supersedes} not found")
        if prior["kind"] != "decision":
            raise ValueError(f"supersedes must point at a decision, got {prior['kind']}")
        prior_meta = json.loads(prior["meta"]) if prior["meta"] else {}
        if prior_meta.get("decision_slug") != slug:
            raise ValueError(
                f"supersedes slug mismatch: prior={prior_meta.get('decision_slug')} new={slug}"
            )
        # Emit the revision row to trip the supersede trigger.
        post(
            kind="revision",
            author=author,
            body=f"Superseded by new decision for slug '{slug}'.",
            reply_to=supersedes,
            thread_id=thread_id,
            meta={"decision_slug": slug, "supersedes": supersedes},
        )

    return post(
        kind="decision",
        author=author,
        body=body,
        reply_to=reply_to,
        thread_id=thread_id,
        meta=meta,
    )


def handoff(
    author: Sibling,
    to_sibling: Sibling,
    task_body: str,
    reply_to: str,
    *,
    respond_by: Optional[str] = None,
    thread_id: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> str:
    """Hand off ownership. `assigned_to` becomes the new owner."""
    return post(
        kind="handoff",
        author=author,
        body=task_body,
        addressed_to=[to_sibling],
        assigned_to=to_sibling,
        reply_to=reply_to,
        thread_id=thread_id,
        respond_by=respond_by,
        meta=meta,
    )


def accept(
    handoff_id: str,
    author: Sibling,
    *,
    note: Optional[str] = None,
) -> str:
    """Post an ack for a handoff. Verifies author == assigned_to."""
    _init_db_if_missing()
    c = _conn()
    ho = c.execute(
        "SELECT kind, assigned_to, thread_id, meta FROM events WHERE id = ?;",
        (handoff_id,),
    ).fetchone()
    if ho is None:
        raise ValueError(f"handoff {handoff_id} not found")
    if ho["kind"] != "handoff":
        raise ValueError(f"event {handoff_id} is kind={ho['kind']}, not handoff")
    if ho["assigned_to"] != author:
        raise ValueError(
            f"author={author} is not the designated owner {ho['assigned_to']}"
        )

    ack_id = post(
        kind="ack",
        author=author,
        body=note or f"accepted handoff {handoff_id}",
        reply_to=handoff_id,
        thread_id=ho["thread_id"],
        meta={"accepted_by": author, "accepts_handoff": handoff_id},
    )
    # Mark the handoff resolved + record accepted_by in its meta. These updates
    # are whitelisted by append-only policy (status/meta mutable).
    try:
        ho_meta = json.loads(ho["meta"]) if ho["meta"] else {}
    except json.JSONDecodeError:
        ho_meta = {}
    ho_meta["accepted_by"] = author
    ho_meta["accepted_at_event"] = ack_id
    c.execute(
        "UPDATE events SET status = 'resolved', meta = ?, responded_at = ? "
        "WHERE id = ?;",
        (
            json.dumps(ho_meta, ensure_ascii=False),
            datetime.now(timezone.utc).isoformat(),
            handoff_id,
        ),
    )
    return ack_id


# -----------------------------------------------------------------------------
# Read helpers
# -----------------------------------------------------------------------------

def mark_seen(sibling: Sibling, event_ids: Iterable[str]) -> int:
    """Append sibling to seen_by for each event. Returns rows updated."""
    _init_db_if_missing()
    c = _conn()
    ids = list(event_ids)
    if not ids:
        return 0
    updated = 0
    placeholders = ",".join("?" * len(ids))
    rows = c.execute(
        f"SELECT id, seen_by FROM events WHERE id IN ({placeholders});", ids
    ).fetchall()
    for r in rows:
        try:
            seen = json.loads(r["seen_by"]) if r["seen_by"] else []
        except json.JSONDecodeError:
            seen = []
        if sibling in seen:
            continue
        seen.append(sibling)
        c.execute(
            "UPDATE events SET seen_by = ? WHERE id = ?;",
            (json.dumps(seen, ensure_ascii=False), r["id"]),
        )
        updated += 1
    return updated


def update_routed_to(event_id: str, routed_to_list: list[str]) -> bool:
    """Set/overwrite routed_to for an event. ATLAS dispatcher calls this after
    classifying an incoming event and deciding which sibling(s) should act.

    Args:
      event_id: the ULID of the event to update.
      routed_to_list: list of sibling names. Will be JSON-encoded.

    Returns:
      True if the row was updated, False if event_id did not exist.

    Raises:
      ValueError on bad input.

    Append-only policy: `routed_to` is whitelisted as mutable metadata
    (same class as `seen_by` and `status`). We also drop a `revision`-style
    audit event into the spine so the change is visible in feed.jsonl.
    """
    _init_db_if_missing()
    if not isinstance(routed_to_list, list):
        raise ValueError("routed_to_list must be a list of sibling names")
    if not all(isinstance(s, str) for s in routed_to_list):
        raise ValueError("routed_to_list must contain only strings")

    c = _conn()
    row = c.execute(
        "SELECT id, thread_id, routed_to FROM events WHERE id = ?;", (event_id,)
    ).fetchone()
    if row is None:
        return False

    new_routed = json.dumps(routed_to_list, ensure_ascii=False)
    c.execute(
        "UPDATE events SET routed_to = ? WHERE id = ?;",
        (new_routed, event_id),
    )

    # Audit trail. Lightweight status event so a reader can reconstruct the
    # dispatcher's decision without diffing the DB.
    try:
        post(
            kind="status",
            author="ATLAS",
            body=f"routed_to updated for {event_id}: {routed_to_list}",
            thread_id=row["thread_id"],
            reply_to=event_id,
            meta={"routed_to_update": True, "new_routed_to": routed_to_list},
            source="claude_session",
        )
    except Exception:
        # Audit failure should not block the dispatcher's primary write.
        pass

    return True


def by_slug(decision_slug: str) -> list[Event]:
    """Return the full history (proposal/decision/revision) for a slug."""
    _init_db_if_missing()
    c = _conn()
    rows = c.execute(
        "SELECT * FROM events WHERE json_extract(meta,'$.decision_slug') = ? "
        "ORDER BY id ASC;",
        (decision_slug,),
    ).fetchall()
    return [_deserialize(r) for r in rows]


def silence_ledger() -> Optional[Event]:
    """NATHAN's most recent event (NEVAEH's Silence Ledger source)."""
    _init_db_if_missing()
    c = _conn()
    r = c.execute(
        "SELECT * FROM events WHERE author = 'NATHAN' ORDER BY id DESC LIMIT 1;"
    ).fetchone()
    return _deserialize(r) if r else None


def open_questions_older_than(hours: float) -> list[Event]:
    """Return question events still status='open' older than N hours."""
    _init_db_if_missing()
    cutoff = datetime.now(timezone.utc).timestamp() - hours * 3600
    cutoff_iso = datetime.fromtimestamp(cutoff, tz=timezone.utc).isoformat()
    c = _conn()
    rows = c.execute(
        "SELECT * FROM events WHERE kind='question' AND status='open' AND ts < ? "
        "ORDER BY id ASC;",
        (cutoff_iso,),
    ).fetchall()
    return [_deserialize(r) for r in rows]


__all__ = [
    "post", "post_from_feed", "inbox", "thread",
    "ask", "answer", "decide", "handoff", "accept",
    "mark_seen", "update_routed_to", "by_slug",
    "open_questions_older_than", "silence_ledger",
    "Event", "Sibling", "Kind", "Status",
    "EmotionalWeight", "RiskLevel", "TaskState", "Source",
    "CrisisClassifierError", "RoomIntegrityError",
]
