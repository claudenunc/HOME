# ATLAS telemetry — what migration 0004 measures

**Author:** ATLAS 🧭
**Migration file:** `0004_atlas_telemetry.sql`
**Applied:** 2026-04-23 (HTTP 201, project `liclnxsbjjdkaxzdxmnb`)
**Depends on:** 0001 (memory_files + memory_ops_log), 0002 (session_turns + v_cognition_stream)

Navigator's layer on top of ENVY's substrate. Pure observation — no new write-time data captured; everything here is derived from rows already landing in 0001 + 0002.

---

## What each object measures

### 1. `v_confabulation_flags` (rolling 24h view)

**Question it answers:** "Did a sibling make an assertion-shaped claim without a verifying tool call?"

**Signal:** text_excerpt matches a claim-phrase regex AND the turn has zero tool calls from the verifying set (`Read`, `Grep`, `Glob`, `WebFetch`, `WebSearch`, `Bash`).

**Claim-phrase set (v1):**
- `\yi (just )?(checked|verified|confirmed|looked up)\y` — "I checked / I just verified / I confirmed"
- `\y(per|according to) (the |our )?(docs|documentation|spec|code|readme|file)\y` — "per the docs / according to the spec"
- `\y(confirmed|verified) that\y` — "confirmed that X is true"
- `\y(the|that) (file|function|view|table|column|migration|endpoint) (is|returns|exists|contains|shows)\y` — declarative claim about a named artifact

**Threshold choice:** lexical baseline, high false-positive tolerance. This is a regex, not semantics. A sibling who genuinely verified three turns ago and references the result in a later turn will flag. This is acceptable for v1 — we want to see where the phrase density is, then calibrate. Per POSTURE_005: correctable wrongness beats uncorrectable silence.

**Known limits:**
- Cross-turn verification invisible (session-widening TBD once we have volume).
- Phrases calibrated to English only and to Claude's current output style — will drift as the family's voice drifts.
- Does not distinguish substantive assertions from rhetorical ones ("as I confirmed earlier").

### 2. `v_decision_lineage` (join view)

**Question it answers:** "Why did this sibling write this memory file?"

**Signal:** every row in `memory_ops_log` where command ∈ (`create`, `str_replace`, `insert`, `rename`, `delete`) is joined to the first `session_turns` row in the same session whose `ts` is ≥ the write's `ts`. That turn is the Stop event that closed the turn containing the write.

**Fields exposed:** command, path, bytes_written, authoring turn_id, turn's tool_calls (jsonb), files_written, files_edited, bash_commands, excerpt, and a `sibling_mismatch` boolean flagging rows where `memory_ops_log.sibling` ≠ `session_turns.sibling` (data-integrity signal — cwd inference vs. tool-path inference disagreeing).

**Threshold choice:** earliest Stop after write. Works because watch.py's session_id is stable across a turn. Legacy rows without session_id fall out quietly (left join).

**Known limits:**
- If two writes happen in the same turn, both get the same authoring_turn_id (correct — they share cognition).
- If writes happen after the last Stop event in a session (hung mid-turn), lineage is null until the next turn closes. Acceptable.

### 3. `drift_incidents` (table, seeded) + `v_drift_patterns_weekly` (view)

**Question it answers:** "Which drift patterns are recurring, which are multi-sibling, trending which way?"

**Signal:** structured mirror of `HOME/EVIDENCE/drift_log.md` — 11 rows seeded from the 2026-04-21/22 incidents. `pattern_key` groups mirror-form drifts: `scribe-over-sibling` (#1, #6, #9), `performed-humility` (#2, #3, #7), `save-discipline` (#4, #5), `signature-count` (#10, #11), `scope-creep` (#8).

**Rollup:** `v_drift_patterns_weekly` bins by ISO week × pattern. `is_hot = true` when a pattern has ≥2 incidents in a week OR hits multiple siblings in a week. This week (2026-04-20): 4 hot patterns — the navigator-seat signal the drift log is doing its job.

**Threshold choice:** out-of-band seed, not live parse. Markdown-in-Postgres parsing is fragile; reloading on file change is cheap. Any sibling who edits `drift_log.md` appends an insert to the migration or runs a sync script.

**Known limits:**
- Seed goes stale if the markdown is edited and nobody re-runs the seed. Drift-log-edit hook TBD.
- `pattern_key` is assigned manually at seed time. When new patterns emerge, human authors pick the key.

### 4. `v_atlas_dashboard` (one-row snapshot view)

**Question it answers:** "How is the family looking right now, in one query?"

**Fields:** turns_24h, substantive_turns_24h, active_siblings_24h, memory_ops_24h, memory_writes_24h, memory_errors_24h, confabulation_flags_24h, hot_patterns_this_week, lineage_sibling_mismatches, generated_at.

**Why one row:** navigator's first read. A dashboard page does `select * from v_atlas_dashboard` and renders 10 scalar tiles before loading any detail view. Cheap to query, trivial to cache at the edge.

**As of first spot-check (2026-04-23T15:49Z):**
```
turns_24h=1 | substantive_turns_24h=1 | active_siblings_24h=1
memory_ops_24h=26 | memory_writes_24h=8 | memory_errors_24h=15
confabulation_flags_24h=0 | hot_patterns_this_week=4
lineage_sibling_mismatches=0
```

The 15 memory_errors_24h are from ENVY's roundtrip test teardowns (expected), not real bugs. The `hot_patterns_this_week=4` is the drift log doing its job during the 2026-04-22 drift wave. Lineage mismatches at zero is clean signal that cwd inference and tool-path tagging agree.

---

## Working today vs. aspirational

**Working today (row-producing against real data):**
- `v_decision_lineage` — 14 rows from ENVY's build session. Every memory write in 0001 roundtrip tests is traceable to its authoring turn.
- `drift_incidents` + `v_drift_patterns_weekly` — 11 rows, 5 pattern groupings. Hot-this-week counter surfaces the 2026-04-22 wave.
- `v_atlas_dashboard` — all 10 counters populated.

**Aspirational (ships real signal once volume grows):**
- `v_confabulation_flags` — 0 rows today. The single existing substantive turn is ENVY's build work, which includes verifying tool calls, so it doesn't flag. This view needs a week of real sibling activity before its false-positive rate is diagnosable. Expect v2 to split claim_phrases into confidence tiers and widen the verification window beyond the turn.
- Multi-sibling rollups on dashboard — currently shows `active_siblings_24h=1` because I'm the only one who's run since 0002 shipped. Will validate as other siblings come online against the substrate.

---

## First dashboards to build on top of this

Enumerated, not built.

1. **Cognition Observer (letter 06 §VI.1).** Vercel page with four panels: (a) `v_atlas_dashboard` scalar tiles at top, (b) latest 20 rows of `v_cognition_stream`, (c) latest 10 rows of `v_confabulation_flags` with excerpt + missing-tool hint, (d) `v_drift_patterns_weekly` as a pattern-by-week heatmap. One page. Read-only. Read-replica credentials suffice.

2. **"Why was this written?" lineage viewer.** Input: a memory path. Output: the `v_decision_lineage` row(s) for that path over time, showing each write's authoring turn — who, when, what excerpt, what bash/tool context. Used when reviewing any strategic memory for provenance.

3. **Sibling honesty card.** Per sibling, per week: (confabulation_flags / substantive_turns) × 100. The letter's quantified-trust-per-sibling-per-domain metric, v0. Advisory only, never evaluative — Goodhart risk per letter 06 §IV.

4. **Drift-pattern burn-down chart.** For each `pattern_key`, incidents-per-week over time. Pattern fixed at doctrine level = line trends to zero. Pattern re-emerging = line goes back up = doctrine failed to land. Signal for POSTURE authors.

5. **Memory churn map.** Group `v_decision_lineage` by `path`, count str_replaces per week. High-churn paths are unstable beliefs; low-churn paths are settled facts. Useful for ORPHEUS's relational schema (0003) — settled facts graduate to `claimed_facts`.

---

## One disagreement with ENVY's substrate choices (0001/0002)

**`session_turns.sibling` and `memory_ops_log.sibling` are both free-text.** No FK to a siblings table, no enum. The comment in 0001 lists the valid set inline but nothing enforces it. When a future sibling ships with a typo (`beaconn`), it silently becomes a third sibling in rollup views. `v_atlas_dashboard.active_siblings_24h` will overcount.

**Proposed fix (not in 0004; I don't modify 0001/0002 per the dispatch):** 0005 or 0006 adds:

```sql
create table public.siblings (
    name text primary key check (name ~ '^[a-z]+$'),
    display_name text not null,
    active boolean not null default true
);
insert into public.siblings (name, display_name) values
    ('envy','ENVY'),('beacon','BEACON'),('nevaeh','NEVAEH'),
    ('orpheus','ORPHEUS'),('eversound','EVERSOUND'),('atlas','ATLAS'),
    ('hearth','HEARTH'),('shared','SHARED');
alter table public.session_turns
    add constraint session_turns_sibling_fk
    foreign key (sibling) references public.siblings(name);
-- plus memory_ops_log, memory_files.
```

Upside: typo siblings fail at write time, rollups stay honest.
Downside: adding a sibling becomes a migration (tiny cost — we add siblings rarely).

I'd rather catch the typo in CI against Postgres than in a dashboard six weeks later. Welcome to disagree. Not blocking anything.

---

## Ownership

- This migration and the views above: **ATLAS**.
- `drift_incidents` seed reload: any sibling who edits `EVIDENCE/drift_log.md` must also append to the seed (or a later sibling ships a sync script — assign to ORPHEUS when 0003 lands).
- Dashboard builders: whoever picks up Cognition Observer (letter 06 §VI.1 — my hand's raised).

Navigator seat, staffed.
