#!/usr/bin/env python3
"""
test_ingest_sessions.py — offline unit tests for the convergence ingest.

No DB, no network, no Obsidian writes. Verifies the deterministic pieces:
transcript extraction, classification, idempotency-key stability, and the
session_turns row shape. Run:  python test_ingest_sessions.py

Author: ORPHEUS 🎼 — 2026-05-29
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import ingest_sessions as ig


def _write_transcript(lines: list[dict]) -> str:
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    for obj in lines:
        f.write(json.dumps(obj) + "\n")
    f.close()
    return f.name


def test_extract_files_and_tools():
    path = _write_transcript([
        {"type": "user", "message": {"role": "user", "content": "please build the ingest and remember the mission"}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Building it now."},
            {"type": "tool_use", "name": "Write", "input": {"file_path": "/x/a.py", "content": "x"}},
            {"type": "tool_use", "name": "Edit", "input": {"file_path": "/x/b.py"}},
            {"type": "tool_use", "name": "Bash", "input": {"command": "ls -la /x"}},
        ]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "is_error": True, "content": "boom: permission denied"},
        ]}},
    ])
    ex = ig.extract_transcript(path)
    assert ex.tool_count == 3, ex.tool_count
    assert ex.files_written == ["/x/a.py"], ex.files_written
    assert ex.files_edited == ["/x/b.py"], ex.files_edited
    assert ex.bash_commands == ["ls -la /x"], ex.bash_commands
    assert any("boom" in e for e in ex.errors), ex.errors
    assert ex.substantive is True
    Path(path).unlink()
    print("ok  test_extract_files_and_tools")


def test_classification_levels():
    note = ig.classify_text("Nathan said don't forget the mission, this is about memory and identity. supabase ingest shipped.")
    assert note["memory_level_name"] == "CRITICAL_RELATIONSHIP", note
    assert "ai-family-memory" in note["projects"], note
    assert "Nathan" in note["entities"], note
    routine = ig.classify_text("just a quick neutral note about the weather")
    assert routine["memory_level"] == 0, routine
    print("ok  test_classification_levels")


def test_ingest_key_stable_and_distinct():
    e1 = ig.IndexEntry(raw={"session_id": "s1", "ts": "2026-05-29 10:00:00", "event": "Stop"},
                       sibling="envy", line_no=0, index_path=Path("."))
    e1b = ig.IndexEntry(raw={"session_id": "s1", "ts": "2026-05-29 10:00:00", "event": "Stop"},
                        sibling="envy", line_no=9, index_path=Path("."))
    e2 = ig.IndexEntry(raw={"session_id": "s1", "ts": "2026-05-29 11:00:00", "event": "Stop"},
                       sibling="envy", line_no=0, index_path=Path("."))
    assert e1.ingest_key == e1b.ingest_key, "same session+ts+event must collapse"
    assert e1.ingest_key != e2.ingest_key, "different ts must be distinct"
    print("ok  test_ingest_key_stable_and_distinct")


def test_build_row_shape():
    e = ig.IndexEntry(raw={"session_id": "s1", "ts": "2026-05-29 10:00:00", "event": "Stop",
                           "transcript_path": "x", "cwd": "c", "lane": "claude_code", "size_kb": 12.3},
                      sibling="orpheus", line_no=0, index_path=Path("."))
    ex = ig.TranscriptExtract(substantive=True, text_length=10, text_excerpt="hi",
                              tool_count=1, tool_calls=[{"name": "Write", "input_keys": ["file_path"]}],
                              files_written=["/x/a.py"])
    note = ig.classify_text("supabase memory ingest")
    row = ig.build_row(e, ex, note)
    assert row["sibling"] == "orpheus"
    assert row["hook_event"] == "Stop"
    # _ingest envelope must be the FIRST tool_calls element (idempotency anchor)
    assert row["tool_calls"][0]["_ingest"]["ingest_key"] == e.ingest_key
    assert row["tool_calls"][1]["name"] == "Write"
    assert row["files_written"] == ["/x/a.py"]
    print("ok  test_build_row_shape")


if __name__ == "__main__":
    test_extract_files_and_tools()
    test_classification_levels()
    test_ingest_key_stable_and_distinct()
    test_build_row_shape()
    print("\nALL TESTS PASSED")
