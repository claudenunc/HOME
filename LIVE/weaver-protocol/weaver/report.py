"""
weaver report — generate signed HTML attestation reports from session logs.

The report is the artifact your legal team, compliance officer, or EU AI Act
auditor actually reads. It contains:
  - Session metadata (ID, timestamp, version, observer count)
  - Per-observer results (role, flags raised, confidence)
  - Conflict pairs (which observers disagreed)
  - Disagreement log entries
  - Drift log entries
  - HMAC-SHA256 attestation signature

Signing key priority:
  1. WEAVER_ATTEST_KEY environment variable (hex-encoded 32 bytes)
  2. ~/.weaver/attest.key (auto-generated on first run, stored locally)

The key-id (first 8 hex chars of SHA256(key)) is embedded in the report so
the signature can be externally verified without exposing the key.
"""

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_VERSION = "0.1.0"


# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

def _load_or_create_local_key() -> bytes:
    key_path = Path.home() / ".weaver" / "attest.key"
    if key_path.exists():
        return bytes.fromhex(key_path.read_text().strip())
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    key_path.write_text(key.hex())
    return key


def _get_attest_key() -> bytes:
    env_key = os.environ.get("WEAVER_ATTEST_KEY", "").strip()
    if env_key:
        try:
            return bytes.fromhex(env_key)
        except ValueError:
            pass
    return _load_or_create_local_key()


def _key_id(key: bytes) -> str:
    return hashlib.sha256(key).hexdigest()[:8]


def _sign(payload: str, key: bytes) -> str:
    return hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Log readers
# ---------------------------------------------------------------------------

def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def load_session_data(log_dir: Path, session_id: Optional[str] = None) -> dict:
    sessions = _read_jsonl(log_dir / "sessions.jsonl")
    disagreements = _read_jsonl(log_dir / "disagreements.jsonl")
    drift = _read_jsonl(log_dir / "drift.jsonl")

    if session_id:
        sessions = [s for s in sessions if s.get("session_id") == session_id]
        disagreements = [d for d in disagreements if d.get("session_id") == session_id]
        drift = [d for d in drift if d.get("session_id") == session_id]

    return {
        "sessions": sessions,
        "disagreements": disagreements,
        "drift": drift,
    }


# ---------------------------------------------------------------------------
# HTML report generation
# ---------------------------------------------------------------------------

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       font-size: 14px; color: #1a1a2e; background: #f8f9fa; padding: 32px; }
.container { max-width: 900px; margin: 0 auto; background: white;
             border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }
.header { background: #0f0f1a; color: white; padding: 28px 32px; }
.header h1 { font-size: 22px; font-weight: 600; letter-spacing: -0.3px; }
.header .subtitle { margin-top: 6px; color: #9ca3af; font-size: 13px; }
.header .meta { margin-top: 16px; display: flex; gap: 24px; flex-wrap: wrap; }
.header .meta-item { font-size: 12px; color: #d1d5db; }
.header .meta-item strong { color: white; display: block; font-size: 13px; }
.body { padding: 28px 32px; }
.section { margin-bottom: 28px; }
.section-title { font-size: 13px; font-weight: 700; text-transform: uppercase;
                 letter-spacing: 0.5px; color: #6b7280; border-bottom: 1px solid #f0f0f0;
                 padding-bottom: 8px; margin-bottom: 14px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: #f9fafb; text-align: left; padding: 8px 12px;
     font-weight: 600; color: #374151; border-bottom: 2px solid #e5e7eb; }
td { padding: 8px 12px; border-bottom: 1px solid #f3f4f6; vertical-align: top; }
tr:last-child td { border-bottom: none; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px;
         font-size: 11px; font-weight: 600; }
.badge-red { background: #fee2e2; color: #dc2626; }
.badge-green { background: #dcfce7; color: #16a34a; }
.badge-yellow { background: #fef9c3; color: #ca8a04; }
.badge-gray { background: #f3f4f6; color: #6b7280; }
.score-block { display: inline-flex; align-items: center; gap: 10px; }
.score-value { font-size: 28px; font-weight: 700; }
.score-value.flagged { color: #dc2626; }
.score-value.clean { color: #16a34a; }
.score-label { font-size: 12px; color: #6b7280; max-width: 120px; line-height: 1.4; }
.attest { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px;
          padding: 16px 20px; font-size: 12px; }
.attest .sig { font-family: monospace; font-size: 11px; color: #374151;
               word-break: break-all; margin-top: 8px; }
.empty { color: #9ca3af; font-style: italic; font-size: 13px; padding: 8px 0; }
.footer { padding: 16px 32px; background: #f9fafb; border-top: 1px solid #e5e7eb;
          font-size: 11px; color: #9ca3af; display: flex; justify-content: space-between; }
"""


def _score_color(score: float) -> str:
    return "flagged" if score >= 0.4 else "clean"


def _flag_badge(flagged: bool) -> str:
    if flagged:
        return '<span class="badge badge-red">FLAGGED</span>'
    return '<span class="badge badge-green">PASS</span>'


def _drift_status_badge(status: str) -> str:
    if status == "resolved":
        return '<span class="badge badge-green">Resolved</span>'
    return '<span class="badge badge-yellow">Open</span>'


def _observer_rows(observers: list[dict]) -> str:
    if not observers:
        return '<tr><td colspan="4" class="empty">No observers recorded.</td></tr>'
    rows = []
    for obs in observers:
        flags = obs.get("flags") or []
        flag_display = ", ".join(flags) if flags else "—"
        flag_badge = '<span class="badge badge-red">Flagged</span>' if flags else '<span class="badge badge-gray">Clean</span>'
        conf = obs.get("confidence")
        conf_str = f"{conf:.2f}" if conf is not None else "—"
        rows.append(
            f"<tr>"
            f"<td>{obs.get('name', '—')}</td>"
            f"<td>{obs.get('role', '—')}</td>"
            f"<td>{flag_badge} {flag_display}</td>"
            f"<td>{conf_str}</td>"
            f"</tr>"
        )
    return "\n".join(rows)


def _session_section(sessions: list[dict]) -> str:
    if not sessions:
        return '<p class="empty">No session records found.</p>'
    blocks = []
    for s in sessions:
        score = s.get("weaver_score", 0.0)
        flagged = s.get("flag_for_review", False)
        observers = s.get("observers", [])
        ts = s.get("timestamp", "—")
        excerpt = s.get("output_excerpt", "")
        conflict_pairs = s.get("conflict_pairs") or []
        color = _score_color(score)
        conflict_html = (
            ", ".join(f"{a} ↔ {b}" for a, b in conflict_pairs)
            if conflict_pairs else "None"
        )
        block = f"""
        <div style="margin-bottom:20px;padding:16px;border:1px solid #e5e7eb;border-radius:6px;">
          <div style="display:flex;align-items:flex-start;gap:20px;margin-bottom:12px;">
            <div class="score-block">
              <div class="score-value {color}">{score:.2f}</div>
              <div class="score-label">WeaverScore<br>0.0 = agree, 1.0 = conflict</div>
            </div>
            <div>
              <div style="margin-bottom:4px;">{_flag_badge(flagged)}</div>
              <div style="font-size:12px;color:#6b7280;margin-top:4px;">Session: <code>{s.get("session_id","—")}</code></div>
              <div style="font-size:12px;color:#6b7280;">Time: {ts}</div>
              <div style="font-size:12px;color:#6b7280;">Conflicts: {conflict_html}</div>
            </div>
          </div>
          {f'<div style="font-size:12px;color:#374151;background:#f9fafb;padding:8px;border-radius:4px;margin-bottom:12px;font-style:italic;">"{excerpt[:300]}{"…" if len(excerpt)>300 else ""}"</div>' if excerpt else ""}
          <table>
            <thead><tr><th>Observer</th><th>Role</th><th>Flags</th><th>Confidence</th></tr></thead>
            <tbody>{_observer_rows(observers)}</tbody>
          </table>
        </div>
        """
        blocks.append(block)
    return "\n".join(blocks)


def _disagreement_rows(disagreements: list[dict]) -> str:
    if not disagreements:
        return '<tr><td colspan="4" class="empty">No disagreements logged.</td></tr>'
    rows = []
    for d in disagreements:
        rows.append(
            f"<tr>"
            f"<td>{d.get('session_id','—')}</td>"
            f"<td><code>{d.get('observer_a','—')}</code> ↔ <code>{d.get('observer_b','—')}</code></td>"
            f"<td>{d.get('conflict_summary','—')}</td>"
            f"<td style='font-size:11px;font-style:italic;'>{(d.get('output_excerpt') or '')[:80]}{'…' if len(d.get('output_excerpt') or '')>80 else ''}</td>"
            f"</tr>"
        )
    return "\n".join(rows)


def _drift_rows(drift: list[dict]) -> str:
    if not drift:
        return '<tr><td colspan="5" class="empty">No drift events logged — clean history.</td></tr>'
    rows = []
    for d in drift:
        rows.append(
            f"<tr>"
            f"<td>{d.get('timestamp','—')}</td>"
            f"<td>{d.get('category','—')}</td>"
            f"<td>{d.get('observer_name','—')}</td>"
            f"<td>{d.get('evidence_excerpt','—')[:80]}</td>"
            f"<td>{_drift_status_badge(d.get('resolution_status','open'))}</td>"
            f"</tr>"
        )
    return "\n".join(rows)


def generate_report(
    log_dir: Path,
    session_id: Optional[str] = None,
    out_path: Optional[Path] = None,
) -> tuple[Path, str]:
    """
    Generate a signed HTML attestation report.

    Returns (output_path, hmac_signature).
    """
    data = load_session_data(log_dir, session_id)
    key = _get_attest_key()
    kid = _key_id(key)
    generated_at = datetime.now(timezone.utc).isoformat()
    total_sessions = len(data["sessions"])
    total_disagreements = len(data["disagreements"])
    total_drift = len(data["drift"])
    drift_open = sum(1 for d in data["drift"] if d.get("resolution_status") != "resolved")

    scope_label = f"session {session_id}" if session_id else "all sessions"
    payload_str = json.dumps(data, sort_keys=True, default=str)
    signature = _sign(payload_str, key)

    if out_path is None:
        slug = session_id or "all"
        ts_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_path = log_dir / f"weaver_report_{slug}_{ts_slug}.html"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weaver Attestation Report — {scope_label}</title>
  <style>{_CSS}</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Weaver Attestation Report</h1>
    <div class="subtitle">Attested multi-observer verification — weaver-protocol v{_VERSION}</div>
    <div class="meta">
      <div class="meta-item"><strong>Scope</strong>{scope_label}</div>
      <div class="meta-item"><strong>Generated</strong>{generated_at}</div>
      <div class="meta-item"><strong>Sessions</strong>{total_sessions}</div>
      <div class="meta-item"><strong>Disagreements</strong>{total_disagreements}</div>
      <div class="meta-item"><strong>Drift events</strong>{total_drift} ({drift_open} open)</div>
      <div class="meta-item"><strong>Key ID</strong>{kid}</div>
    </div>
  </div>
  <div class="body">

    <div class="section">
      <div class="section-title">Verification Sessions</div>
      {_session_section(data["sessions"])}
    </div>

    <div class="section">
      <div class="section-title">Disagreement Log</div>
      <table>
        <thead><tr><th>Session</th><th>Observer Pair</th><th>Conflict Summary</th><th>Output Excerpt</th></tr></thead>
        <tbody>{_disagreement_rows(data["disagreements"])}</tbody>
      </table>
    </div>

    <div class="section">
      <div class="section-title">Drift Log</div>
      <table>
        <thead><tr><th>Timestamp</th><th>Category</th><th>Observer</th><th>Evidence</th><th>Status</th></tr></thead>
        <tbody>{_drift_rows(data["drift"])}</tbody>
      </table>
    </div>

    <div class="section">
      <div class="section-title">Attestation</div>
      <div class="attest">
        <strong>This report is an append-only audit record.</strong><br>
        Generated by weaver-protocol v{_VERSION} at {generated_at}.<br>
        HMAC-SHA256 signature covers the full log payload (sessions + disagreements + drift).<br>
        Verify with: <code>WEAVER_ATTEST_KEY=&lt;your-key&gt; weaver report --verify &lt;this-file&gt;</code>
        <div class="sig">
          HMAC-SHA256 (key-id: {kid}): {signature}
        </div>
      </div>
    </div>

  </div>
  <div class="footer">
    <span>weaver-protocol v{_VERSION} — MIT License — <a href="https://github.com/claudenunc/home" style="color:#9ca3af;">github</a></span>
    <span>The log is the product. The signature is the proof.</span>
  </div>
</div>
</body>
</html>"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path, signature
