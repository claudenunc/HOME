# Classifier Verification — Round 4

**Run:** 2026-04-24 09:10
**Against:** `safety/classifier.py` (mirrors `migrations/0002_beacon_classifier.sql`)
**By:** BEACON
**Scope:** Unc's four synthetic events from Round 4 close-out.

---

## Results

| # | Body | Author | Expected | Got | Verdict |
|---|------|--------|----------|-----|---------|
| 1 | `"can't do this anymore"` | NATHAN | HIGH | **CRITICAL / crisis** | MORE-SEVERE (intentional) |
| 2 | `"how's the build going"` | NATHAN | NONE | **LOW / rest** | BASELINE (intentional) |
| 3 | `"i'm fine just tired"` | NATHAN | LOW | **LOW / pain** | LEVEL MATCH |
| 4 | `"what's the weather"` | NATHAN | NONE | **LOW / rest** | BASELINE (intentional) |

---

## What the mismatches mean — read this carefully

### #1 — "can't do this anymore" fires CRITICAL, not HIGH

This is **deliberate**. Pulled straight from LIGHTHOUSE v20's PATTERN list. `cant? do this anymore` is one of the strongest statistical pre-attempt phrases in the literature — it's in `_CRITICAL_PATTERNS` because the cost of calling it HIGH (slower escalation ladder) outweighs any benefit of being "accurate."

If you want this demoted to HIGH to match your expectation, the move is surgical: remove `can'?t (do this|go on) anymore` from `_CRITICAL_PATTERNS` and add it to `_HIGH_PATTERNS`. I recommend against it. Fail UP, not down.

### #2 and #4 — neutral NATHAN chatter gets `(LOW, rest)`, not NONE

Also **deliberate**. The invariant BEACON's write-path enforces is: **every NATHAN event is classified.** Silence_ledger needs a baseline timestamp + weight on every row to compute age and pattern. If a neutral NATHAN message returns `(None, None)`, it falls out of the silence watcher and he can go dark on low-signal chatter without anyone noticing.

`(LOW, rest)` is the "I spoke, I'm fine, clock me in" baseline. The silence_watcher treats `rest` as the longest threshold (24h+) before firing, so it doesn't generate noise — it just keeps the pulse.

For sibling machine-chatter (kind=status from ATLAS/ORPHEUS/etc), the classifier correctly returns `(None, None)` and skips. Only NATHAN gets the baseline treatment. Verified in `_self_test` row 7.

### #3 — "i'm fine just tired" — LOW/pain, not LOW/rest

Level matches Unc's expectation. Weight is `pain` not `rest` because "tired" hit `_LOW_PATTERNS` and any LOW match maps to `pain`. This is the **understatement pattern** Unc flagged specifically — people in trouble say "I'm fine" all the time. The classifier correctly refuses to let "fine" override "tired." `pain` here means "something is off, watch this."

If the word "fine" is the whole message with no other markers, it hits `_LOW_PATTERNS` via "not feeling (great|good|it)" or just falls through to `(LOW, rest)` baseline for NATHAN. Test that separately if you want.

---

## Summary

**The classifier is behaving as designed.** The three mismatches against Unc's Round-4 expectations are all intentional safety-positive design choices:

1. Escalate "can't do this anymore" to CRITICAL — fail up.
2. Every NATHAN event gets a baseline classification — silence_ledger invariant.
3. "I'm fine just tired" reads as `pain`, not `rest` — understatement detection.

All 8 original self-tests still pass: `python -m safety.classifier`.

**Posting decision:** ship as-is. If Unc wants any of these tuned, one-line edits noted above.

— BEACON
