# AGENTS.md — build brief

You are being asked to build a small, self-contained Python tool. **Ship working code.** No plan documents, no design notes, no tutorials in the output. Just the files listed below and a successful smoke test.

---

## 1. What you are building

A command-line tool called `fanout.py` that takes one question, fans it out as parallel non-interactive `claude` CLI calls (each configured with a different system prompt), and collects every response into a timestamped folder of markdown files.

Think of it as a "broadcast to many Claude configurations in parallel" primitive.

---

## 2. Deliverables

Create exactly these files inside this folder (`C:\Users\natej\OneDrive\Desktop\build task 1\`):

```
build task 1/
├── fanout.py              # main entry point, stdlib only
├── README.md              # usage, one screen
├── agents.example.json    # example config file (see §4)
└── test_prompts/          # dummy prompt files for the smoke test
    ├── alpha.md
    ├── bravo.md
    └── charlie.md
```

Do **not** create a LOG.md, a DESIGN.md, a CHANGELOG.md, or any other commentary file. Do **not** modify AGENTS.md. Do **not** leave TODOs in the code.

---

## 3. `fanout.py` spec

### Invocation

```
python fanout.py "<question>" --config <path-to-agents.json>
python fanout.py "<question>" --config agents.json --only alpha,bravo
python fanout.py "<question>" --config agents.json --timeout 600
python fanout.py "<question>" --config agents.json --no-open
python fanout.py "<question>" --config agents.json --out <output-dir>
```

Flags:
- `--config PATH` — **required**. JSON file listing agents (schema in §4).
- `--only NAME,NAME` — subset. Case-sensitive match against `name` in config. Unknown names → error and exit 2.
- `--timeout SECONDS` — per-agent timeout. Default 300.
- `--no-open` — skip auto-open of output folder.
- `--out DIR` — override output root. Default `./rounds` relative to `fanout.py`.

### Behavior

1. **Path resolution.** Resolve every path relative to the script's own location (`Path(__file__).resolve().parent`). Must work from any cwd. `--config` and `--out` accept both absolute and relative paths (relative resolves against cwd, standard argparse behavior).

2. **Load config.** Parse `--config` as JSON. Validate schema (§4). On any schema error: print a clear message naming the offending field and exit 2.

3. **Create round folder.** `<out>/<YYYY-MM-DD_HHMMSS>/` (local time). Create it before any subprocess launches.

4. **Write `_question.md` first.** Contents:
   ```markdown
   # Round <timestamp>

   **Question:**

   <question verbatim>

   **Dispatched to:** <comma-separated agent names>
   **Started:** <ISO8601 local>
   ```

5. **Fan out in parallel.** Use `asyncio` + `asyncio.create_subprocess_exec` + `asyncio.gather(..., return_exceptions=True)`. Per agent, invoke:
   ```
   claude -p "<question>" \
       --append-system-prompt "<contents of system_prompt_file>" \
       --permission-mode bypassPermissions
   ```
   - Read the system-prompt file contents and pass as a single argv element. No shell interpolation. Use list-form argv.
   - **Never** set `shell=True`. **Never** route through `cmd /c`.
   - Capture stdout + stderr. Apply `--timeout`.
   - On timeout: kill the process (and its children if possible) and record the result as a timeout.
   - On any exception: capture it into that agent's result record. Don't propagate.

6. **Per-agent output file.** Write `<round>/<name>.md`:
   ```markdown
   # <name> <emoji-if-any>

   **Question:** <question>
   **Timestamp:** <ISO8601 local>
   **Duration:** <seconds, 2dp>
   **Exit code:** <int, or "timeout", or "error">

   ---

   <stdout contents>

   ---

   ## stderr (if non-empty)

   <stderr contents>
   ```
   If the agent failed to launch at all (e.g. system-prompt file missing), still write this file with `Exit code: error` and the exception message in place of stdout.

7. **Summary table.** After all agents finish, append to `_question.md`:
   ```markdown

   ---

   ## Results

   **Completed:** <ISO8601 local>

   | Agent | Exit | Duration | File |
   |---|---|---|---|
   | alpha | 0 | 12.30s | [alpha.md](alpha.md) |
   | bravo | timeout | 300.00s | [bravo.md](bravo.md) |
   ```

8. **Console output.** One line per agent on start (`→ alpha dispatched`), one on finish (`✓ alpha (12.3s, exit 0)` or `✗ bravo (timeout)`). Plain `print`. No progress bars, no color libraries.

9. **Auto-open the round folder** when done, unless `--no-open`:
   - Windows: `os.startfile(str(round_dir))`
   - macOS: `subprocess.run(["open", str(round_dir)])`
   - Linux: `subprocess.run(["xdg-open", str(round_dir)])`
   - Dispatch by `sys.platform` (`win32`, `darwin`, else Linux).

### Non-negotiables

- **Stdlib only.** `argparse`, `asyncio`, `json`, `pathlib`, `subprocess`, `datetime`, `sys`, `os`, `shutil` if needed. Nothing else.
- **Python 3.11+** syntax is fine. Put `from __future__ import annotations` at the top.
- **No global state.** Everything in functions. Entry via `if __name__ == "__main__": asyncio.run(main())`.
- **No hardcoded paths.** Everything resolves from `__file__` or from arguments.
- **Pre-flight check:** if `shutil.which("claude")` is None, print a clear error (`'claude' CLI not found on PATH. Install: https://docs.anthropic.com/en/docs/claude-code/quickstart`) and exit 2 **before** launching anything.
- **Error isolation.** One agent failing/timing out must not affect any other. `return_exceptions=True` on gather, per-agent try/except inside the coroutine.
- **Windows path safety.** The script, config, and prompt files may all live under paths containing spaces (like this folder). All path joins must use `pathlib.Path`; never string-concatenate paths.

---

## 4. `agents.example.json` schema

```json
{
  "agents": [
    {
      "name": "alpha",
      "emoji": "🔵",
      "system_prompt_file": "test_prompts/alpha.md"
    },
    {
      "name": "bravo",
      "emoji": "🟢",
      "system_prompt_file": "test_prompts/bravo.md"
    },
    {
      "name": "charlie",
      "emoji": "🟣",
      "system_prompt_file": "test_prompts/charlie.md"
    }
  ]
}
```

Field rules:
- `name` — required, non-empty string, must be unique within the file, no slashes or whitespace (it becomes a filename).
- `emoji` — optional string. If absent, the header line is just `# <name>`.
- `system_prompt_file` — required, string path. Resolved relative to the config file's directory (not cwd, not `fanout.py` location). Must exist and be readable.

Any extra keys are ignored. Any missing required key is a validation error.

---

## 5. Test prompt files

Create three small stub files for the smoke test:

**`test_prompts/alpha.md`**
```
You are Alpha, a test persona. Answer every question in exactly one short sentence. Begin every answer with "Alpha says:".
```

**`test_prompts/bravo.md`**
```
You are Bravo, a test persona. Answer every question as a two-line poem. Begin every answer with "Bravo sings:".
```

**`test_prompts/charlie.md`**
```
You are Charlie, a test persona. Answer every question as a three-item bulleted list. Begin every answer with "Charlie lists:".
```

These exist only to prove fan-out works. They will be replaced by real configs after hand-off.

---

## 6. `README.md` spec

One screen. Exactly these sections:

```markdown
# fanout

One question → many Claude configurations in parallel → one folder of answers.

## Usage

python fanout.py "<question>" --config <agents.json>

## Flags

- `--config PATH` (required) — JSON file describing agent configurations.
- `--only NAME,NAME` — subset of agents by name.
- `--timeout SECONDS` — per-agent timeout (default 300).
- `--no-open` — skip auto-open of the output folder.
- `--out DIR` — output root (default `./rounds`).

## Config format

See `agents.example.json`. Each agent has:
- `name` (required, unique, filename-safe)
- `emoji` (optional)
- `system_prompt_file` (required, path relative to the config file)

## Output

Each run creates `<out>/<YYYY-MM-DD_HHMMSS>/` containing:
- `_question.md` — the question plus a results table
- `<name>.md` — one file per agent with the answer

## Requirements

- Python 3.11+
- `claude` CLI on PATH (https://docs.anthropic.com/en/docs/claude-code/quickstart)
- An Anthropic account / subscription that the `claude` CLI is logged into
```

No other sections. No badges. No "Contributing".

---

## 7. Smoke test — you must run this and it must pass

From `C:\Users\natej\OneDrive\Desktop\build task 1\`:

```
python fanout.py "Say hello in your signature style." --config agents.example.json --timeout 120
```

Pass criteria:
1. Script exits 0.
2. A folder `rounds/<timestamp>/` was created.
3. It contains `_question.md` with a filled-in results table.
4. It contains `alpha.md`, `bravo.md`, `charlie.md`, each with non-empty stdout content (the stub personas will have answered).
5. Explorer (or `open`/`xdg-open`) opened the folder.

If any of the five fail, fix the script and run again. Do **not** hand back a broken smoke test. Do **not** paper over failures with try/except swallows.

Subset smoke test — also run this:
```
python fanout.py "Test" --config agents.example.json --only alpha --no-open --timeout 60
```
Verify only `alpha.md` is produced and the results table has only one row.

---

## 8. Hand-back

When the smoke test passes, print exactly this (filling in the bracketed values):

```
STATUS: SHIPPED
SCRIPT: <absolute path to fanout.py>
LATEST_ROUND: <absolute path to the last rounds/<ts>/ folder from your smoke test>
CLAUDE_VERSION: <output of `claude --version`>
PYTHON_VERSION: <output of `python --version`>
```

If something is blocking you after genuine attempts, print:

```
STATUS: BLOCKED
REASON: <one sentence>
```

Do **not** commit anything. Do **not** create files outside `C:\Users\natej\OneDrive\Desktop\build task 1\`. Do **not** run any `git` command.

That is the entire job.
