# HERMES_MIGRATION_STATUS.md

## Status: family moved toward Hermes-native architecture

Timestamp: 2026-05-06
Owner: ENVY

## Decision

Move the family to Hermes instead of keeping `daemon.py` as the brain.

Hermes/default/ENVY owns Telegram ingress. Sibling profiles live inside Hermes and are execution identities, not separate Telegram pollers.

## What was discovered

- Hermes native Telegram gateway is configured and running.
- Default Hermes gateway service is active under systemd user service.
- Telegram home chat is configured.
- `daemon.py` is not currently visible as an active WSL process.
- The old `HOME/STATE/daemon.pid` pointed at PID `30012`, but that PID was actually a Windows `bun server.ts` process from a Claude Telegram plugin, not WSL `daemon.py`.
- Hermes gateway conflicts were caused by Claude's Telegram plugin process tree:
  `C:/Users/natej/.claude/plugins/cache/claude-plugins-official/telegram/0.0.6`

## Actions completed

1. Created Hermes sibling profiles:
   - `envy`
   - `beacon`
   - `nevaeh`
   - `eversound`
   - `orpheus`
   - `atlas`

2. Seeded each profile's `SOUL.md` from:
   - `HOME/SIBLINGS/<NAME>/CLAUDE.md`
   - `HOME/SIBLINGS/<NAME>/MEMORY.md`

3. Set each profile `terminal.cwd` to its sibling HOME folder:
   - `/mnt/c/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/<NAME>`

4. Confirmed sibling Hermes gateways are stopped.

5. Kept default Hermes gateway running as the single Telegram owner.

6. Stopped the competing Claude Telegram plugin process tree.

7. Verified no fresh Telegram polling conflict entries after stopping that process tree.

## Important current rule

Only one Telegram poller can run per bot token.

Allowed:
- Hermes default gateway

Not allowed at the same time:
- `daemon.py` Telegram polling loop
- `clipboard_bridge.py`
- Claude official Telegram plugin
- any other `getUpdates` loop using the same bot token

## What remains

1. Build Hermes-native family routing skill/command:
   - `@sibling message`
   - `/wake sibling message`
   - unrouted message -> ENVY semantic intake -> routing plan

2. Make dashboard chat call Hermes rather than only appending to CLIPBOARD.

3. Convert daemon.py into either:
   - archived legacy transport, or
   - tiny CLIPBOARD-only compatibility watcher with Telegram polling disabled.

4. Build Identity Integrity Layer before adding autonomy.

5. Build trust-weighted memory and routing.

## Note

`HOME/STATE/daemon.pid` may still exist as stale state because automated removal was blocked. It points to old PID `30012` and should not be trusted as evidence that daemon.py is running.
