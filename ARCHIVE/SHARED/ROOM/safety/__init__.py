"""
THE ROOM — safety layer (BEACON).

The DB trigger is the hard invariant. These modules are the soft side:
silence watching, escalation, and dead-man's switch. They run as cron
or long-lived processes and call into room.post() / room.inbox() as
regular callers — they do NOT bypass the write-path guarantees.

Exports:
  classify_text(body, author) -> (risk_level, emotional_weight)
  silence_watcher.run() -> count of emitted silence crises
  escalation.run()      -> count of telegram pages sent
  deadman.run()         -> heartbeat + pager loop (separate process)
"""

from .classifier import classify_text, RISK_LEVELS, EMOTIONAL_WEIGHTS

__all__ = ["classify_text", "RISK_LEVELS", "EMOTIONAL_WEIGHTS"]
