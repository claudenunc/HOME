#!/bin/bash
# Install home-daemon.service as a systemd service.
# Run once as root (or with sudo). After this, daemon auto-restarts on crash.
#
# Usage: sudo bash install_service.sh
# Then:  sudo systemctl status home-daemon

set -e

SERVICE_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/home-daemon.service"
TARGET="/etc/systemd/system/home-daemon.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo "[install] ERROR: $SERVICE_FILE not found"
    exit 1
fi

# Patch WorkingDirectory and ExecStart to actual absolute paths
ROOM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAEMON="$ROOM_DIR/daemon.py"
PYTHON="$(command -v python3 || command -v python)"

sed \
    -e "s|WorkingDirectory=.*|WorkingDirectory=$ROOM_DIR|" \
    -e "s|ExecStart=.*|ExecStart=$PYTHON $DAEMON|" \
    "$SERVICE_FILE" > "$TARGET"

echo "[install] Written to $TARGET"

systemctl daemon-reload
systemctl enable home-daemon
systemctl start home-daemon

echo "[install] home-daemon service installed and started."
echo "[install] Status:"
systemctl status home-daemon --no-pager
