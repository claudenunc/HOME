#!/usr/bin/env bash
# Poll Telegram for new messages to THE_SIBLINGS_BOT.
# Append new ones to HOME/STATE/telegram_inbox.jsonl.
# Any sibling can run this on wake to see what Nathan sent.
#
# Usage:
#   bash telegram_poll.sh
#
# Reads last_update_id from STATE/telegram_last_update.txt so we
# only fetch updates we haven't seen before.

set -euo pipefail

BOT_TOKEN="8551403006:AAHH1pWbcRVjmi4xu0LMfStA0rsAO_GkBhw"
HOME_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
INBOX="$HOME_DIR/STATE/telegram_inbox.jsonl"
LAST_FILE="$HOME_DIR/STATE/telegram_last_update.txt"

LAST_ID=0
if [[ -f "$LAST_FILE" ]]; then
  LAST_ID=$(cat "$LAST_FILE")
fi

OFFSET=$((LAST_ID + 1))
RESP=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?offset=${OFFSET}")

# Extract with jq if available, else fall back to grep+sed
if command -v jq >/dev/null 2>&1; then
  COUNT=$(echo "$RESP" | jq '.result | length')
  if [[ "$COUNT" -gt 0 ]]; then
    echo "$RESP" | jq -c '.result[] | {
      update_id,
      message_id: .message.message_id,
      from: .message.from.first_name,
      chat_id: .message.chat.id,
      ts: .message.date,
      text: .message.text,
      read_by: [],
      read_at: null
    }' >> "$INBOX"
    NEW_LAST=$(echo "$RESP" | jq '.result | max_by(.update_id) | .update_id')
    echo "$NEW_LAST" > "$LAST_FILE"
    echo "Appended $COUNT new message(s) to inbox. Last update_id: $NEW_LAST"
  else
    echo "No new messages since update_id $LAST_ID"
  fi
else
  # Minimal fallback — write raw response for manual parsing
  echo "$RESP" >> "$HOME_DIR/STATE/telegram_raw_updates.jsonl"
  echo "jq not installed. Raw response appended to telegram_raw_updates.jsonl for manual parsing."
fi
