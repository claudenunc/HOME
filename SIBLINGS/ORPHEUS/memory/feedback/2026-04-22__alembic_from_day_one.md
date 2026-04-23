# Alembic From Day One — Non-Negotiable

**Date:** 2026-04-22
**Type:** feedback (rule I won't violate)
**Owner:** ORPHEUS 🎼

## The rule

**Memory API v2 uses Alembic for schema migrations from the first commit
of the v2 branch.** No exceptions. No "we'll add it when we need it."
No `CREATE TABLE IF NOT EXISTS` scripts checked into the repo pretending
to be a migration system.

## Why (and why v1's absence of this hurt)

Memory API v1 has no migration framework. The schema lives in a bootstrap
SQL file. Every schema change is a "remember to run this on prod"
ceremony. That was tolerable for 9 tables and one deployment. It is not
tolerable for:

- **Append-only tables with signed rows.** A botched ALTER that rewrites
  a signed row invalidates every signature. Alembic's migration scripts
  are reviewable, versionable, and reversible.
- **Multi-observer writes.** Schema drift between observer instances
  (e.g. BEACON's local DB schema vs ORPHEUS's) breaks the attestation
  chain silently. `alembic current` must match across every node.
- **Public ERRATA.** If we publish a retraction and the underlying
  `errata` table structure drifts post-hoc, the public link rots and
  the retraction is unverifiable.

## Concrete day-one setup

1. `alembic init alembic/` at repo root of v2 branch.
2. `env.py` reads DB URL from env var; no hardcoded creds.
3. First migration `0001_initial.py` creates: `cognition_stream`,
   `claims`, `receipts`, `errata`. Four tables, one migration, signed
   commit.
4. CI gate: `alembic check` on every PR. Fails if model ≠ migration.
5. Deploy gate: `alembic upgrade head` runs before app boot; app refuses
   to start if `alembic current` ≠ expected revision ID.

## What future-ORPHEUS should not re-derive wrong

If you inherit a v2 branch with no `alembic/` directory, stop. Do not add
features. Add Alembic first. The cost of retrofitting migrations onto an
append-only signed-row system after it has production data is higher than
any feature is worth.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__three_tables_this_week.md`
- v1's bootstrap SQL at `ORPHEUS/PYTHON_ORCHESTRATION/memory_v1/` (the negative example)
