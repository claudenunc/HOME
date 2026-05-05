#!/bin/bash
# HOME family Telegram chat bot launcher
# Run this to start listening to Nathan's Telegram messages.
#
# Usage:
#   bash start_chat.sh           # foreground (Ctrl+C to stop)
#   bash start_chat.sh &         # background
#   nohup bash start_chat.sh &   # background, survives logout
#
# The bot will:
#   1. Poll Telegram for Nathan's messages
#   2. Generate Claude responses using the HOME family context
#   3. Send replies back on Telegram
#   4. Write all messages + replies to SHARED/CLIPBOARD.jsonl

cd "$(dirname "$0")/../.."
echo "Starting HOME family chat from $(pwd)"
python3 SHARED/ROOM/family_chat.py "$@"
