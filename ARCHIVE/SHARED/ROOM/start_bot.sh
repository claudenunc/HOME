#!/usr/bin/env bash
# Start the HOME family unified Telegram bot.
# Usage: bash start_bot.sh
#
# Requirements:
#   1. SHARED/.env must exist with TELEGRAM_BOT_TOKEN + ANTHROPIC_API_KEY
#   2. pip install anthropic requests (done once)

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install deps if missing
python3 -c "import anthropic, requests" 2>/dev/null || pip install anthropic requests --quiet

echo "[start_bot] Starting HOME family bot..."
exec python3 bot.py
