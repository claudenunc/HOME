# GEMINI.md — ROUND_TABLE build brief (for Gemini CLI)

You are being dispatched by ORPHEUS 🎼 (architect of the HOME AI family) on behalf of Unc (Nathan). **Build, don't explain.** Ship working code. No plan docs, no tutorials.

---

## 1. What you are building

A broadcast primitive at `C:\Users\natej\OneDrive\Desktop\HOME\SIBLINGS\ROUND_TABLE\` that lets Unc ask one question and fan it out to all 6 AI siblings in parallel, collecting their answers into a timestamped round folder.

**Why it matters.** Unc currently has 6 separate terminal tabs open (one per sibling: ORPHEUS, ATLAS, BEACON, ENVY, EVERSOUND, NEVAEH) to talk to the family. This replaces that with one command: `python ask.py "<question>"`.

**Tradeoff Unc already accepted.** Each call is a cold-wake `claude -p` invocation with only that sibling's CLAUDE.md as context — it loses the live-session memory of the running terminals. Since the Supabase memory substrate shipped 2026-04-23, cold-wake siblings reconstruct from the event log, so the cost is smaller than it used to be. Do not add warm-session logic. Do not try to attach to the running terminals. Cold-wake is the design.

---

## 2. Deliverables

Create exactly these files:

```
HOME/SIBLINGS/ROUND_TABLE/
├── ask.py            # main entry point, stdlib only
├── README.md         # usage, one screen
└── rounds/           # output directory (created on first run, gitignored)
    └── .gitkeep
```

**Also add** to `HOME/.gitignore` (create if missing):
```
SIBLINGS/ROUND_TABLE/rounds/*/
!SIBLINGS/ROUND_TABLE/rounds/.gitkeep
```

Do not create a plan document. Do not create a LOG.md. Do not add a test harness beyond a single smoke-test invocation you verify works.

---

## 3. `ask.py` spec

### Invocation
```
python ask.py "<question>"                       # default: all 6 siblings
python ask.py "<question>" --only ORPHEUS,ATLAS  # subset
python ask.py "<question>" --timeout 600         # per-sibling seconds, default 300
python ask.py "<question>" --no-open             # skip Explorer auto-open
```

### Behavior

1. **Resolve paths** relative to the script's own location. `HOME_ROOT` is two levels up from `ask.py` (i.e. `ROUND_TABLE/../..`). Must work from any cwd.

2. **Sibling roster** (hardcode this order — it matches the family's canonical seating):
   ```python
   SIBLINGS = ["ORPHEUS", "ATLAS", "BEACON", "ENVY", "EVERSOUND", "NEVAEH"]
   ```
   Each sibling's identity file lives at `HOME/SIBLINGS/<NAME>/CLAUDE.md`. If a sibling's CLAUDE.md is missing, skip that sibling and log a warning — do not crash.

3. **Timestamped round folder.** Create `rounds/<YYYY-MM-DD_HHMMSS>/` (local time). Inside it, write `_question.md` first:
   ```markdown
   # Round <timestamp>

   **Asker:** Unc
   **Question:**

   <question verbatim>

   **Dispatched to:** ORPHEUS, ATLAS, BEACON, ENVY, EVERSOUND, NEVAEH
   **Started:** <ISO8601 local>
   ```

4. **Parallel fan-out.** Use `asyncio` + `asyncio.create_subprocess_exec` + `asyncio.gather(..., return_exceptions=True)`. Each sibling call is:
   ```
   claude -p "<question>" \
     --append-system-prompt "<contents of SIBLINGS/<NAME>/CLAUDE.md>" \
     --permission-mode bypassPermissions
   ```
   - Pass the system-prompt contents as a single argv element (no shell interpolation) — Python's list-form subprocess handles large args fine.
   - Capture stdout + stderr. Apply the per-sibling timeout. On timeout, kill the process tree and record a timeout entry.
   - Do NOT set `shell=True`. Do NOT spawn via `cmd /c`. Use `create_subprocess_exec` with argv list.

5. **Per-sibling output file.** Write `rounds/<ts>/<NAME>.md`:
   ```markdown
   # <NAME> <emoji>

   **Question:** <question>
   **Timestamp:** <ISO8601 local>
   **Duration:** <seconds, 2dp>
   **Exit code:** <int or "timeout">

   ---

   <stdout contents>

   ---

   ## stderr (if any)

   <stderr contents>
   ```
   Emojis per sibling: ORPHEUS 🎼, ATLAS 🧭, BEACON 🏮, ENVY 👑, EVERSOUND ⚡, NEVAEH 💜.

6. **Summary index.** After all siblings finish (or timeout), append a results table to `_question.md`:
   ```markdown

   ---

   ## Results

   | Sibling | Exit | Duration | File |
   |---|---|---|---|
   | ORPHEUS 🎼 | 0 | 12.3s | [ORPHEUS.md](ORPHEUS.md) |
   | ATLAS 🧭 | 0 | 9.8s | [ATLAS.md](ATLAS.md) |
   | ... |
   ```

7. **Console output** during execution: one line per sibling when they start, one when they finish (with duration + exit code). No verbose streaming. Plain `print` — no rich/textual/colorama deps.

8. **Auto-open the round folder** when done (unless `--no-open`). On Windows use `os.startfile(str(round_dir))`. On other platforms fall back to `xdg-open` / `open` by `sys.platform`.

### Non-negotiables

- **Stdlib only.** No `aiohttp`, no `rich`, no `click`. `argparse` + `asyncio` + `pathlib` + `subprocess` + `datetime` + `sys` + `os`.
- **Python 3.11+** syntax is fine — use `from __future__ import annotations` at the top.
- **No global state.** Everything in functions. `if __name__ == "__main__": asyncio.run(main())`.
- **Error isolation.** One sibling crashing must not crash any other. `return_exceptions=True` on gather; each sibling's error surface appears in its own `.md` file.
- **No path hardcoding.** Resolve `HOME_ROOT` from `__file__`. If `claude` is not on PATH, print a clear error with the fix and exit 2.

---

## 4. `README.md` spec

One screen. Sections:

```markdown
# ROUND_TABLE

One question → all 6 siblings in parallel → one folder of answers.

## Usage

\`\`\`
python ask.py "should I buy the Hostinger VPS?"
\`\`\`

## What happens

1. Spins up 6 parallel `claude -p` calls, one per sibling
2. Each call sees only that sibling's CLAUDE.md as system prompt (cold wake)
3. Writes answers to `rounds/<timestamp>/<SIBLING>.md`
4. Opens the round folder in Explorer

## Flags

- `--only ATLAS,ORPHEUS` — dispatch to a subset
- `--timeout 600` — per-sibling timeout in seconds (default 300)
- `--no-open` — skip Explorer auto-open

## Cost

Each sibling is a cold-wake Claude call. No live-session memory. The Supabase memory substrate (shipped 2026-04-23) lets siblings reconstruct from the event log, so the cost is smaller than it looks.

## Where this came from

ORPHEUS 🎼 spec → Gemini build → 2026-04-23. See `SIBLINGS/ORPHEUS/GEMINI.md` for the original brief.
```

---

## 5. Smoke test before you hand back

Run this exactly:

```
cd C:\Users\natej\OneDrive\Desktop\HOME\SIBLINGS\ROUND_TABLE
python ask.py "Introduce yourself in one sentence." --timeout 120
```

Verify:
- A `rounds/<ts>/` folder was created
- `_question.md` exists with the question and a results table
- All 6 sibling `.md` files exist (even if some timed out — timeouts still produce a file)
- Explorer opened the folder (unless you used `--no-open`)

If any of those fail, fix the script. Do not hand back a broken smoke test.

---

## 6. When you are done

1. Print the absolute path of `ask.py` and the `rounds/<ts>/` folder from your smoke test.
2. Print a one-line status: `SHIPPED` or `BLOCKED: <reason>`.
3. Do NOT commit — Unc reviews before commit.

That's it. Build it.

🎼 — ORPHEUS
