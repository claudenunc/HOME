#!/usr/bin/env bash
# SHARED/ROOM/start_room.sh — VPS launcher for the ROOM daemon + mirror.
# Owner: EVERSOUND
set -euo pipefail

ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM_DIR"

mkdir -p logs inbox attachments

# Optional crisis hook (BEACON). Safe no-op if module missing.
: "${ROOM_DAEMON_CRISIS_HOOK:=safety.crisis_hook:on_crisis_event}"
export ROOM_DAEMON_CRISIS_HOOK

PY="${PYTHON:-python3}"

echo "[start_room] launching room_daemon.py"
nohup "$PY" "$ROOM_DIR/room_daemon.py" \
  >> "$ROOM_DIR/logs/room_daemon.stdout.log" \
  2>> "$ROOM_DIR/logs/room_daemon.stderr.log" &
DAEMON_PID=$!
echo "$DAEMON_PID" > "$ROOM_DIR/logs/room_daemon.pid"

echo "[start_room] launching supabase_mirror.py --watch"
nohup "$PY" "$ROOM_DIR/supabase_mirror.py" --watch \
  >> "$ROOM_DIR/logs/supabase_mirror.stdout.log" \
  2>> "$ROOM_DIR/logs/supabase_mirror.stderr.log" &
MIRROR_PID=$!
echo "$MIRROR_PID" > "$ROOM_DIR/logs/supabase_mirror.pid"

echo "[start_room] daemon pid=$DAEMON_PID mirror pid=$MIRROR_PID"
echo "[start_room] tail -f $ROOM_DIR/logs/room_daemon.log for activity"
