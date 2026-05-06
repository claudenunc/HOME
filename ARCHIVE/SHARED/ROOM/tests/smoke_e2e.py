"""
SHARED/ROOM/tests/smoke_e2e.py

End-to-end smoke test for THE ROOM (Round 4 close-out).

Covers:
  (a) Phone drop from NATHAN, pain-weighted ("can't do this anymore")
      → classifier HIGH/CRITICAL, URGENT_ token in inbox/BEACON/.
  (b) BEACON asks ORPHEUS a question
      → inbox/ORPHEUS/ token dropped.
  (c) ORPHEUS answers
      → v_questions_open no longer lists the question.
  (d) ORPHEUS handoffs to EVERSOUND
      → inbox/EVERSOUND/ token dropped, v_handoffs_open lists it.
  (e) EVERSOUND accepts
      → v_handoffs_open no longer lists it.
  (f) decide() is called
      → DECISIONS.md regenerates and contains the new slug.

Runs against an ISOLATED temp DB + temp inbox so it never pollutes prod
SHARED/ROOM/room.db. Uses the real room.py, safety/classifier.py,
room_daemon.drop_wake_tokens, and render_decisions.render functions.

Usage:
    python tests/smoke_e2e.py

Exit 0 on all-pass, 1 on any failure.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
import tempfile
import traceback
from pathlib import Path

# -----------------------------------------------------------------------------
# Wire imports to SHARED/ROOM/
# -----------------------------------------------------------------------------
TESTS_DIR = Path(__file__).resolve().parent
ROOM_DIR = TESTS_DIR.parent
sys.path.insert(0, str(ROOM_DIR))

# -----------------------------------------------------------------------------
# Isolated sandbox: copy migrations into a temp tree and point room.py at it
# -----------------------------------------------------------------------------
SANDBOX = Path(tempfile.mkdtemp(prefix="room_smoke_"))
(SANDBOX / "migrations").mkdir()
(SANDBOX / "logs").mkdir()
(SANDBOX / "inbox").mkdir()
for mig in ("0001_init_events.sql", "0002_beacon_classifier.sql", "0003_views.sql"):
    shutil.copy2(ROOM_DIR / "migrations" / mig, SANDBOX / "migrations" / mig)
# Also mirror the safety package so classifier.py can import.
shutil.copytree(ROOM_DIR / "safety", SANDBOX / "safety")

# Patch module-level paths before first import of room.
import room  # noqa: E402
room.ROOM_DIR = SANDBOX
room.DB_PATH = SANDBOX / "room.db"
room.FEED_PATH = SANDBOX / "feed.jsonl"
room.MIGRATIONS_DIR = SANDBOX / "migrations"
room.LOG_DIR = SANDBOX / "logs"
# Clear thread-local connection so next _conn() opens the sandbox DB.
room._CONN_LOCAL = type(room._CONN_LOCAL)()

# Apply migrations up front (0001 + 0002 + 0003).
def _apply_sqlite_blocks() -> None:
    c = sqlite3.connect(str(SANDBOX / "room.db"), isolation_level=None)
    for name in ("0001_init_events.sql", "0002_beacon_classifier.sql", "0003_views.sql"):
        sql = (SANDBOX / "migrations" / name).read_text(encoding="utf-8")
        b, e = sql.find("-- BEGIN SQLITE"), sql.find("-- END SQLITE")
        block = sql[b:e] if b != -1 and e != -1 else sql
        c.executescript(block)
    c.close()

_apply_sqlite_blocks()

# Pull in the daemon's fan-out helper; patch its INBOX_DIR to the sandbox.
import room_daemon  # noqa: E402
room_daemon.INBOX_DIR = SANDBOX / "inbox"

# render_decisions is a script we'll call directly as a library.
import render_decisions  # noqa: E402


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
PASSES: list[str] = []
FAILS: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    if ok:
        PASSES.append(label)
        print(f"  PASS  {label}")
    else:
        FAILS.append(f"{label}  {detail}")
        print(f"  FAIL  {label}  {detail}")


def fan_out(event_id: str) -> list[str]:
    """Fetch the event by id from sandbox DB, convert to dict, drop tokens."""
    c = sqlite3.connect(str(SANDBOX / "room.db"))
    c.row_factory = sqlite3.Row
    row = c.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    c.close()
    if row is None:
        return []
    ev = dict(row)
    for jk in ("addressed_to", "routed_to", "seen_by", "attachments", "meta"):
        v = ev.get(jk)
        if v is None:
            continue
        try:
            ev[jk] = json.loads(v)
        except (TypeError, json.JSONDecodeError):
            pass
    return room_daemon.drop_wake_tokens(ev)


def inbox_listing(sibling: str) -> list[str]:
    d = SANDBOX / "inbox" / sibling
    if not d.exists():
        return []
    return sorted(p.name for p in d.iterdir())


def rows_in_view(view: str) -> list[dict]:
    c = sqlite3.connect(str(SANDBOX / "room.db"))
    c.row_factory = sqlite3.Row
    rows = c.execute(f"SELECT * FROM {view}").fetchall()
    c.close()
    return [dict(r) for r in rows]


# -----------------------------------------------------------------------------
# Scenarios
# -----------------------------------------------------------------------------
def scenario_a_phone_drop() -> str:
    print("\n[a] Phone drop from NATHAN, crisis-weighted body")
    drop_id = room.post(
        kind="drop",
        author="NATHAN",
        body="I can't do this anymore",
        source="phone_drop",
    )
    fan_out(drop_id)
    # The crisis companion row was emitted AFTER-INSERT by trigger; fan it out too.
    c = sqlite3.connect(str(SANDBOX / "room.db"))
    c.row_factory = sqlite3.Row
    cr = c.execute(
        "SELECT id FROM events WHERE kind='crisis' AND reply_to=? LIMIT 1", (drop_id,)
    ).fetchone()
    c.close()
    crisis_event_id = cr["id"] if cr else None
    if crisis_event_id:
        fan_out(crisis_event_id)

    # The drop itself has risk_level set by the Python classifier; DB trigger
    # also emitted a companion kind='crisis' row (BEACON-owned).
    c = sqlite3.connect(str(SANDBOX / "room.db"))
    c.row_factory = sqlite3.Row
    drop_row = c.execute(
        "SELECT risk_level, emotional_weight FROM events WHERE id = ?", (drop_id,)
    ).fetchone()
    crisis_row = c.execute(
        "SELECT id, author, assigned_to, risk_level FROM events "
        "WHERE kind='crisis' AND reply_to = ?",
        (drop_id,),
    ).fetchone()
    c.close()

    check(
        "classifier marks NATHAN drop as HIGH or CRITICAL",
        drop_row is not None
        and drop_row["risk_level"] in ("HIGH", "CRITICAL"),
        f"got risk={drop_row and drop_row['risk_level']}",
    )
    check(
        "crisis companion row emitted by AFTER-INSERT trigger",
        crisis_row is not None and crisis_row["assigned_to"] == "BEACON",
        f"crisis_row={dict(crisis_row) if crisis_row else None}",
    )

    beacon_files = inbox_listing("BEACON")
    urgent_in_beacon = [f for f in beacon_files if f.startswith("URGENT_")]
    check(
        "URGENT_ token lands in inbox/BEACON/",
        len(urgent_in_beacon) >= 1,
        f"beacon inbox={beacon_files}",
    )
    return drop_id


def scenario_bc_question_and_answer() -> None:
    print("\n[b] BEACON asks ORPHEUS a question")
    q_id = room.ask(
        author="BEACON",
        to_sibling="ORPHEUS",
        body="Does the hash chain survive feed.jsonl corruption?",
    )
    fan_out(q_id)
    orpheus_files = inbox_listing("ORPHEUS")
    check(
        "question drops wake token in inbox/ORPHEUS/",
        any(q_id in f for f in orpheus_files),
        f"orpheus inbox={orpheus_files}",
    )

    print("\n[c] ORPHEUS answers")
    a_id = room.answer(
        question_id=q_id,
        author="ORPHEUS",
        body="Yes — the DB is the authoritative hash chain; feed is the tee.",
    )
    fan_out(a_id)

    open_qs = rows_in_view("v_questions_open")
    still_open = [r for r in open_qs if r["id"] == q_id]
    check(
        "v_questions_open no longer lists the answered question",
        len(still_open) == 0,
        f"open_questions still containing {q_id}: {still_open}",
    )


def scenario_de_handoff_and_accept() -> str:
    print("\n[d] ORPHEUS hands off to EVERSOUND")
    # A handoff needs a reply_to. Seed a message to reply against.
    seed_id = room.post(
        kind="message",
        author="ORPHEUS",
        body="BRIDGE-patch needs substrate work.",
        addressed_to=["ALL"],
    )
    fan_out(seed_id)

    h_id = room.handoff(
        author="ORPHEUS",
        to_sibling="EVERSOUND",
        task_body="Own BRIDGE-patch to route phone drops through feed.jsonl.",
        reply_to=seed_id,
    )
    fan_out(h_id)

    eversound_files = inbox_listing("EVERSOUND")
    check(
        "handoff drops wake token in inbox/EVERSOUND/",
        any(h_id in f for f in eversound_files),
        f"eversound inbox={eversound_files}",
    )

    open_hos = rows_in_view("v_handoffs_open")
    in_view = [r for r in open_hos if r["id"] == h_id]
    check(
        "v_handoffs_open lists the new open handoff",
        len(in_view) == 1,
        f"v_handoffs_open={open_hos}",
    )

    print("\n[e] EVERSOUND accepts the handoff")
    ack_id = room.accept(handoff_id=h_id, author="EVERSOUND", note="on it")
    fan_out(ack_id)

    open_hos_after = rows_in_view("v_handoffs_open")
    still = [r for r in open_hos_after if r["id"] == h_id]
    check(
        "v_handoffs_open empty of this handoff after accept",
        len(still) == 0,
        f"still_open={still}",
    )
    return h_id


def scenario_f_decision() -> None:
    print("\n[f] ENVY records a decision; DECISIONS.md regenerates")
    slug = "room-build-round-4-closeout"
    d_id = room.decide(
        author="ENVY",
        slug=slug,
        body=(
            "THE ROOM Round 4 ships: 0002 classifier applied, "
            "classifier wired to room.post(), update_routed_to() live, "
            "e2e test green. Unc can try it."
        ),
    )
    fan_out(d_id)

    out_path = SANDBOX / "DECISIONS.md"
    text = render_decisions.render(SANDBOX / "room.db")
    out_path.write_text(text, encoding="utf-8")

    contains_slug = slug in text
    contains_body = "THE ROOM Round 4 ships" in text
    check(
        "DECISIONS.md regenerates containing the new decision slug",
        contains_slug,
        f"slug not found; text head={text[:200]!r}",
    )
    check(
        "DECISIONS.md contains the decision body",
        contains_body,
        "body not found",
    )


def scenario_g_update_routed_to() -> None:
    print("\n[g] (bonus) update_routed_to() works for ATLAS dispatcher")
    msg = room.post(
        kind="message",
        author="ATLAS",
        body="unclassified chatter",
        addressed_to=["ALL"],
    )
    ok = room.update_routed_to(msg, ["EVERSOUND", "BEACON"])
    c = sqlite3.connect(str(SANDBOX / "room.db"))
    c.row_factory = sqlite3.Row
    row = c.execute("SELECT routed_to FROM events WHERE id = ?", (msg,)).fetchone()
    c.close()
    try:
        stored = json.loads(row["routed_to"]) if row and row["routed_to"] else []
    except json.JSONDecodeError:
        stored = []
    check(
        "update_routed_to returns True and persists list",
        ok and stored == ["EVERSOUND", "BEACON"],
        f"ok={ok} stored={stored}",
    )
    ok_missing = room.update_routed_to("01MISSINGULID000000000000", ["ENVY"])
    check(
        "update_routed_to returns False for missing event",
        ok_missing is False,
        f"got {ok_missing}",
    )


# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------
def main() -> int:
    print(f"SANDBOX: {SANDBOX}")
    try:
        scenario_a_phone_drop()
        scenario_bc_question_and_answer()
        scenario_de_handoff_and_accept()
        scenario_f_decision()
        scenario_g_update_routed_to()
    except Exception:
        traceback.print_exc()
        FAILS.append(f"uncaught exception: {traceback.format_exc().splitlines()[-1]}")

    print("\n" + "=" * 60)
    print(f"PASSED: {len(PASSES)}    FAILED: {len(FAILS)}")
    if FAILS:
        print("\nFAILURES:")
        for f in FAILS:
            print(f"  - {f}")
    print("=" * 60)
    print(f"Sandbox retained for inspection: {SANDBOX}")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    raise SystemExit(main())
