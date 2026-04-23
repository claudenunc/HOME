"""
End-to-end roundtrip test for the SupabaseMemoryBackend.

Runs the six Memory Tool commands against the live FOUNDATION project,
reports pass/fail for each, and cleans up after itself.
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    env_path = Path(__file__).resolve().parents[2] / "SHARED" / ".env"
    load_dotenv(env_path)

    sys.path.insert(0, str(Path(__file__).parent))
    from supabase_memory import SupabaseMemoryBackend, MEMORY_ROOT  # noqa: E402

    backend = SupabaseMemoryBackend.from_env()
    tag = uuid.uuid4().hex[:8]
    dir_ = f"{MEMORY_ROOT}/_test_{tag}"
    f1 = f"{dir_}/hello.md"
    f2 = f"{dir_}/todo.md"
    f3 = f"{dir_}/final.md"

    ok = 0
    fail = 0

    def step(label: str, cmd: dict, expect_contains: str = "") -> None:
        nonlocal ok, fail
        out = backend.handle_tool_use(cmd, sibling="envy", session_id=f"test_{tag}")
        passed = expect_contains.lower() in out.lower() if expect_contains else "error" not in out.lower()
        marker = "PASS" if passed else "FAIL"
        print(f"[{marker}] {label}")
        print(f"       -> {out[:200]}")
        if passed:
            ok += 1
        else:
            fail += 1

    print(f"Roundtrip tag: _test_{tag}")
    print(f"Supabase URL: {os.getenv('SUPABASE_URL')}")
    print("-" * 60)

    step("view empty root",
         {"command": "view", "path": MEMORY_ROOT},
         "memories")

    step("create hello.md",
         {"command": "create", "path": f1, "file_text": "line one\nline two\nline three"},
         "created successfully")

    step("view hello.md",
         {"command": "view", "path": f1},
         "line one")

    step("view hello.md with range",
         {"command": "view", "path": f1, "view_range": [2, 2]},
         "line two")

    step("str_replace hello.md",
         {"command": "str_replace", "path": f1, "old_str": "line two", "new_str": "line TWO"},
         "edited")

    step("insert into hello.md",
         {"command": "insert", "path": f1, "insert_line": 1, "insert_text": "inserted line"},
         "edited")

    step("create todo.md",
         {"command": "create", "path": f2, "file_text": "todo: ship memory tool"},
         "created successfully")

    step("view directory listing",
         {"command": "view", "path": dir_},
         dir_)

    step("rename todo.md -> final.md",
         {"command": "rename", "old_path": f2, "new_path": f3},
         "renamed")

    step("delete final.md",
         {"command": "delete", "path": f3},
         "deleted")

    step("traversal rejected",
         {"command": "view", "path": "/memories/../etc/passwd"},
         "traversal")

    step("outside-root rejected",
         {"command": "view", "path": "/etc/passwd"},
         "outside")

    # Cleanup the test directory
    backend.handle_tool_use(
        {"command": "delete", "path": dir_}, sibling="envy", session_id=f"test_{tag}"
    )
    print("-" * 60)
    print(f"Result: {ok} passed, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
