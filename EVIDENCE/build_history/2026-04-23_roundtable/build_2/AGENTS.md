# AGENTS.md — build brief (Task 2)

You are being asked to build a small, self-contained local web app that wraps an existing command-line tool. **Ship working code.** No plan documents, no design notes. Just the files listed below and a successful smoke test.

---

## 1. What you are building

A localhost-only web UI that wraps the `fanout.py` script already built at:

```
C:\Users\natej\OneDrive\Desktop\build task 1\fanout.py
```

`fanout.py` takes a question and fans it out as parallel `claude` CLI calls — one per agent defined in a JSON config — and writes the answers to a timestamped folder (`rounds/<YYYY-MM-DD_HHMMSS>/<agent_name>.md` plus `_question.md`). You can read its source and its `README.md` at `C:\Users\natej\OneDrive\Desktop\build task 1\` to understand the contract. Do not modify it. Treat it as a stable external tool.

Your job: put a browser UI on top of it. One textbox at the top, a grid of agent panes below, answers stream in (via poll) as each agent finishes.

---

## 2. Deliverables

Create exactly these files inside `C:\Users\natej\OneDrive\Desktop\build task 2\`:

```
build task 2/
├── server.py            # HTTP server, stdlib only
├── index.html           # single-page UI, served by server.py
├── config.example.json  # server configuration example
└── README.md            # usage, one screen
```

Do **not** create LOG.md, DESIGN.md, CHANGELOG.md, or any other commentary file. Do **not** modify AGENTS.md. Do **not** create files outside this folder. Do **not** run any `git` command.

---

## 3. `server.py` spec

### Invocation

```
python server.py --config config.example.json
python server.py --config config.example.json --port 8080
python server.py --config config.example.json --no-open
```

Flags:
- `--config PATH` — **required**. JSON file with server configuration (schema in §5).
- `--port N` — override port from config. Default from config, final default 8080.
- `--no-open` — do not auto-open the browser on startup.

### Server behavior

Use `http.server.ThreadingHTTPServer` + a subclass of `BaseHTTPRequestHandler`. **Stdlib only.** No Flask, no FastAPI, no aiohttp, no starlette.

Bind to `127.0.0.1` only (localhost). **Never** bind to `0.0.0.0` or any external interface. If binding fails (port in use), print a clear error and exit 2.

On startup:
1. Validate config (see §5).
2. Verify the `fanout_script` path from config exists and is a file.
3. Verify the `agents_config` path from config exists and can be parsed as JSON with the shape `fanout.py` expects (an object with an `agents` array, each item having `name` and `system_prompt_file` and optional `emoji`).
4. Print `Listening on http://127.0.0.1:<port>`.
5. Unless `--no-open`, open that URL in the default browser.

### Routes

**`GET /`**
Serve `index.html` as `text/html; charset=utf-8`.

**`GET /api/agents`**
Return JSON describing the agents from `agents_config`:
```json
{
  "agents": [
    {"name": "alpha", "emoji": "🔵"},
    {"name": "bravo", "emoji": "🟢"}
  ]
}
```
The UI uses this to render the right number of panes on load.

**`POST /api/ask`**
Request body (JSON):
```json
{
  "question": "string, required, non-empty",
  "only": ["alpha", "bravo"],     // optional, list of names
  "timeout": 300,                  // optional, number, seconds
  "concurrency": 2                 // optional, integer
}
```

Behavior:
1. Validate the body. On any error, return 400 with `{"error": "..."}`.
2. Build the argv for `fanout.py`:
   ```
   python <fanout_script> <question> --config <agents_config>
       [--only a,b,c] [--timeout N] [--concurrency N]
   ```
   - Use the same Python executable the server is running under (`sys.executable`). Do not assume `python` is on PATH.
   - Pass `--no-open` always (the server, not fanout, owns UI behavior).
3. Spawn the subprocess using `subprocess.Popen` with `stdout=DEVNULL, stderr=PIPE` (we don't need fanout's stdout; we watch its output folder directly). Do **not** block on it.
4. Compute the round ID: spawn-time in the same format `fanout.py` uses (`YYYY-MM-DD_HHMMSS`, local time). Because fanout creates its folder with its own timestamp, there's a small race — see §4 for how to handle it.
5. Return 200 with JSON:
   ```json
   {
     "round_id": "2026-04-23_170530",
     "agents": ["alpha", "bravo", "charlie"],
     "rounds_dir": "<absolute path to the rounds/ directory>"
   }
   ```

**`GET /api/rounds/<round_id>/state`**
Read the round folder. Return JSON:
```json
{
  "round_id": "2026-04-23_170530",
  "started": "2026-04-23T17:05:30-05:00",
  "completed": "2026-04-23T17:05:55-05:00",    // null if not done
  "agents": {
    "alpha":   {"status": "done",    "exit_code": 0, "duration": 12.3},
    "bravo":   {"status": "done",    "exit_code": 0, "duration": 11.7},
    "charlie": {"status": "pending", "exit_code": null, "duration": null}
  }
}
```

Derivation rules:
- A round is "complete" when `_question.md` contains a `## Results` section (fanout writes this after all agents finish). Parse the `**Completed:** <ISO>` line. If not present, `completed` is null.
- An agent is "done" when its `<name>.md` file exists in the folder AND contains the line `---\n\n## Results` in `_question.md` (meaning fanout finished the round) OR the agent's file is fully written (presence + stable size). Simplest rule: agent's `.md` file exists → status is "done". Before it exists → "pending". A "running" state is optional; if you want it, treat "pending" as "pending" until the file appears.
- Exit code and duration are parsed out of the results table in `_question.md`, not out of the agent's own file (the table is the authoritative record). Before the table exists, those fields are null.
- If `round_id` does not correspond to any folder under `rounds_dir`, return 404 with `{"error": "round not found"}`.

**`GET /api/rounds/<round_id>/agent/<name>`**
Read the agent's markdown file and return its raw content as `text/markdown; charset=utf-8`. If the file doesn't exist yet, return 404. If the name contains slashes or `..`, return 400.

**`GET /api/rounds/<round_id>/question`**
Return `_question.md` as `text/markdown; charset=utf-8`. 404 if not found.

### Threading / safety

- `ThreadingHTTPServer` — each request on its own thread. Fine.
- No global mutable state. If you must cache anything (like the agents list), cache per-request or behind a small lock.
- **No shell=True** in subprocess calls. **No** `os.system`. **No** `os.popen`. Use `subprocess.Popen` with argv list.
- All path joins via `pathlib.Path`. Paths may contain spaces ("build task 1", "build task 2"). No string concatenation.
- Reject any path containing `..` in URL routes. Reject agent names containing anything but letters, digits, `_`, `-`.
- If the server process dies, any fanout subprocesses it spawned keep running in the background. That's fine — they write their output folder and exit. Do not try to track or reap them.

### Non-negotiables

- **Stdlib only.** `http.server`, `socketserver`, `json`, `pathlib`, `subprocess`, `threading`, `argparse`, `sys`, `os`, `webbrowser`, `urllib.parse`, `re`, `datetime`.
- **Python 3.11+** syntax OK. `from __future__ import annotations` at the top.
- **No global state.** Functions and classes, not module-level dicts that mutate.
- **UTF-8 everywhere.** All `write_text` / `read_text` with `encoding="utf-8"`. All HTTP response headers include `charset=utf-8`.
- **Localhost only.** The server binds `127.0.0.1` and must not respond to non-localhost requests. `ThreadingHTTPServer(("127.0.0.1", port), Handler)` handles this; don't override with `""` or `"0.0.0.0"`.

---

## 4. Handling the timestamp race

When the server spawns `fanout.py`, it doesn't know fanout's timestamp until fanout creates the folder. Resolve this cleanly:

**Option A (preferred):** After spawning, the server polls the `rounds/` directory for the most recent folder matching the `YYYY-MM-DD_HHMMSS` pattern whose mtime is after the spawn time. It has ~5 seconds to appear. Return that folder's name as the `round_id`. If no new folder appears within 5s, return 502 with `{"error": "fanout did not create a round folder in time"}`.

**Option B (simpler but weaker):** Assume the server's clock and fanout's clock agree. Compute the round_id as `datetime.now().strftime("%Y-%m-%d_%H%M%S")` at spawn time, but then verify the folder exists (wait up to 5s); if it differs by 1 second due to clock skew, pick the closest folder.

Pick A. It's the right answer.

---

## 5. `config.example.json` schema

```json
{
  "port": 8080,
  "fanout_script": "C:\\Users\\natej\\OneDrive\\Desktop\\build task 1\\fanout.py",
  "agents_config": "C:\\Users\\natej\\OneDrive\\Desktop\\build task 1\\agents.example.json",
  "rounds_dir": "C:\\Users\\natej\\OneDrive\\Desktop\\build task 1\\rounds"
}
```

Field rules:
- `port` — optional, integer 1-65535. Default 8080.
- `fanout_script` — required, path to `fanout.py`. Must exist.
- `agents_config` — required, path to the agents JSON. Must exist and parse. Must match `fanout.py`'s schema.
- `rounds_dir` — required, absolute path where fanout writes round folders. Must exist (create it if missing, including parents).

On any validation error, print `ERROR: <field>: <reason>` to stderr and exit 2. Do not start the server.

---

## 6. `index.html` spec

**Single file.** HTML + CSS + JS inline. No external fetches — no Google Fonts, no CDN for any library, no favicon fetch. Nothing but what the server itself serves.

Structure:

1. **Top bar:**
   - A `<textarea>` or `<input type="text">` spanning most of the width.
   - An "Ask" button to the right.
   - A small status line below: "Idle" / "Dispatching..." / "Round <id> in flight" / "Round <id> complete in <X>s".
   - The textbox should submit on Ctrl+Enter or button click. **Not** plain Enter (because the textarea needs newlines for multi-line questions).

2. **Agents grid:**
   - Rendered from `GET /api/agents` on page load.
   - One pane per agent. Each pane:
     - Header: `<emoji> <name>`
     - Status indicator: pending (dim), running (pulsing), done (solid), error (red-tinted).
     - Body: agent's markdown rendered as text. Use `<pre style="white-space: pre-wrap;">` — raw markdown is fine. Do not pull in a markdown library.
     - Meta row at the bottom: `exit: <code> · <duration>s`.

3. **Poll loop:**
   - When a round is in flight, poll `GET /api/rounds/<id>/state` every 750ms.
   - When an agent transitions from pending → done, fetch `GET /api/rounds/<id>/agent/<name>` once and fill the pane.
   - When the round's `completed` field is non-null, stop polling and update the status line.
   - Errors: if any fetch returns non-2xx, show the error text in the status line. Keep polling unless `/state` returns 404 (round gone).

4. **Styling:**
   - Dark background (`#0f0f10` or similar), light text, monospace font (`ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`).
   - Grid layout for panes: 3 columns on wide screens, 1 column under 800px. Use CSS grid, not a library.
   - No emoji-font fetches; emojis render with the system emoji font.
   - Keep it simple. This is an ops tool, not a product.

5. **No external dependencies whatsoever.** No `<script src="https://...">`, no `@font-face` pointing at a CDN. Only same-origin fetches (`/api/...`).

---

## 7. `README.md` spec

One screen. Exactly:

```markdown
# fanout-ui

Local web UI that wraps fanout.py. One textbox → parallel Claude calls → live-updating grid of answers.

## Usage

python server.py --config config.example.json

Opens http://127.0.0.1:8080 in your browser.

## Configuration

See `config.example.json`:
- `port` (optional, default 8080)
- `fanout_script` (required, path to fanout.py)
- `agents_config` (required, path to the agents JSON fanout reads)
- `rounds_dir` (required, absolute path where fanout writes round folders)

## Flags

- `--config PATH` (required)
- `--port N` — override port from config
- `--no-open` — don't auto-open the browser

## Requirements

- Python 3.11+
- `fanout.py` already built and working (see ../build task 1/)

## Security

Binds to 127.0.0.1 only. Not reachable from other machines on the LAN.
```

No other sections.

---

## 8. Smoke test — you must run these and they must pass

From `C:\Users\natej\OneDrive\Desktop\build task 2\`:

### Test 1 — server starts and serves agents

```
python server.py --config config.example.json --no-open --port 8765
```

In another shell (or use `curl` via `Start-Process` if no other shell handy):

```
curl http://127.0.0.1:8765/api/agents
```

Expected: JSON with three agents (alpha, bravo, charlie) from the Task 1 `agents.example.json`.

### Test 2 — ask flow end-to-end

```
curl -X POST http://127.0.0.1:8765/api/ask -H "Content-Type: application/json" -d "{\"question\":\"Say hello.\",\"concurrency\":2}"
```

Expected: 200 with `{"round_id": "...", "agents": [...], "rounds_dir": "..."}`.

Then poll:

```
curl http://127.0.0.1:8765/api/rounds/<round_id>/state
```

Expected: eventually (within ~120s) `completed` is non-null and all three agents show `status: "done"` with `exit_code: 0`.

### Test 3 — agent content fetch

```
curl http://127.0.0.1:8765/api/rounds/<round_id>/agent/alpha
```

Expected: 200, `text/markdown`, body starts with `# alpha` and contains "Alpha says:".

### Test 4 — the browser works

Stop the server. Restart it without `--no-open`. Browser should open to `http://127.0.0.1:8080`. Type a short question, click Ask (or Ctrl+Enter). Watch three panes fill in as agents finish. Status line should end at "Round <id> complete in <X>s".

**All four must pass.** Do not hand back with a broken test.

---

## 9. Hand-back

When all smoke tests pass, print exactly:

```
STATUS: SHIPPED
SERVER: <absolute path to server.py>
INDEX: <absolute path to index.html>
LATEST_ROUND: <absolute path to the last rounds/<ts>/ folder you exercised>
TESTS_PASSED: agents-list, ask-flow, agent-fetch, browser
PYTHON_VERSION: <output of `python --version`>
```

If blocked:

```
STATUS: BLOCKED
REASON: <one sentence>
```

Do **not** commit. Do **not** create files outside `C:\Users\natej\OneDrive\Desktop\build task 2\`. Do **not** run any `git` command. Do **not** modify `fanout.py` or anything in `build task 1\`.

That is the entire job.
