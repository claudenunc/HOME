@echo off
title ROOM - Family Event Spine
echo ============================================
echo  ROOM DAEMON - Fan-out + Heartbeat
echo  feed.jsonl tail, inbox tokens, spine projection
echo ============================================
echo.
cd /d "%~dp0"
rem Keep Python finds its site-packages
set PATH=%USERPROFILE%\.local\bin;%PATH%

rem Optional: wire BEACON's crisis hook if the module is present.
rem Format: <module>:<callable>  e.g. safety.crisis_hook:notify_beacon
if not defined ROOM_DAEMON_CRISIS_HOOK (
  set ROOM_DAEMON_CRISIS_HOOK=safety.crisis_hook:on_crisis_event
)

start "ROOM Daemon" /MIN python room_daemon.py

rem Supabase mirror worker (stub-safe; exits 0 if creds missing)
start "ROOM Mirror" /MIN python supabase_mirror.py --watch

rem BEACON dead-man's switch — separate process, watches daemon heartbeat.
rem If room_daemon dies silently, this pages Unc on Telegram within ~5 min.
rem pythonw keeps it headless (no console window). Falls back to python if pythonw is absent.
where pythonw >nul 2>&1
if %ERRORLEVEL%==0 (
  start "BEACON Deadman" /MIN pythonw safety\deadman.py
) else (
  start "BEACON Deadman" /MIN python safety\deadman.py
)

echo ROOM processes launched. Close this window to stop.
echo (Daemon + mirror + deadman run minimized in the background.)
pause
