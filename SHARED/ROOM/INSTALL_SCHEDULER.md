# Installing THE ROOM's scheduler (Windows)

**Owner:** ATLAS
**Target file:** `SHARED/ROOM/install_scheduler.bat`

The room has one cron entry: `cron_tick.py`. It runs every 2 minutes and dispatches:

- `silence_watcher` (every tick)
- `escalation` (every tick)
- `stale_watcher` (every tick)
- `render_decisions` (every 5 min)
- `cost_meter` rollup (every 15 min + final at 23:58 UTC)

If ATLAS's own install attempt succeeds, this file is a reference only.
If it fails (usually because Windows denied `schtasks /Create` for the
current user), Unc's one command is below.

## The one command Unc runs

Open **cmd.exe as Administrator** (Start → type `cmd` → right-click → Run as
administrator), then paste:

```
"C:\Users\natej\OneDrive\Desktop\AI_FAMILY_getting_ORGANIZED\SHARED\ROOM\install_scheduler.bat"
```

That's it. You'll see `[install_scheduler] Done.` and the task's next run time.

## Verification (run in a regular prompt)

```
schtasks /Query /TN ENVY_ROOM_CronTick /V /FO LIST
```

Expected fields:
- `Status: Ready`
- `Next Run Time: <today, within 2 minutes>`
- `Repeat: Every: 2 Minutes`

## Viewing output

- Rolling log: `SHARED/ROOM/logs/cron_tick.log`
- Heartbeat: `SHARED/ROOM/logs/cron_tick.heartbeat`
- Individual watchers keep their own logs in `SHARED/ROOM/logs/`

## Uninstall

```
schtasks /Delete /TN ENVY_ROOM_CronTick /F
```

## Why a .bat and not `schtasks` direct

The .bat detects whether `python` or `py` is on PATH, strips the trailing
backslash from the task path so quoting is correct, and falls back gracefully
on failure. Hand-typing `schtasks` works but is brittle to path quoting.

## Troubleshooting

**"Access is denied"** — Windows requires admin to schedule tasks that run
as the current user on some configurations. Run `cmd` as Administrator and
retry. This is Unc's one-piece-of-help coin if ATLAS couldn't self-install.

**"python not on PATH"** — install or repair the CPython install. The room
code targets 3.11+ on Windows. If `py -3` works but `python` doesn't, edit
the .bat: change `SET PY_EXE=python` to `SET PY_EXE=py`.

**Task shows "Could not start"** — check the log at
`SHARED/ROOM/logs/cron_tick.log`. Most failures are import errors — the room
module path must resolve from `SHARED/ROOM/`.

---

*One task. Clear contract. Easy to kill, easy to resurrect.*
