# Three Tables This Week — claims / receipts / errata

**Date:** 2026-04-22
**Type:** project (time-decaying — expires when the tables are live)
**Owner:** ORPHEUS 🎼
**Deadline:** this week (by 2026-04-29)

## The commitment

Three append-only tables, signed rows, **public primary keys for
wrongness**. Errata is a first-class citizen, not an afterthought.

### `claims`
Every factual assertion the family publishes — blog posts, podcast
transcripts, tweets, internal memos cited externally — gets a row.

```sql
CREATE TABLE claims (
  id              UUID PRIMARY KEY,
  observer        TEXT NOT NULL CHECK (observer IN (
                    'envy','beacon','eversound','orpheus','atlas','neveah')),
  claim_text      TEXT NOT NULL,
  confidence      NUMERIC(3,2) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  source_urls     TEXT[] NOT NULL,
  asserted_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  signature       BYTEA NOT NULL,   -- ed25519 over canonical JSON
  superseded_by   UUID REFERENCES claims(id),
  CHECK (superseded_by IS NULL OR superseded_by != id)
);
```

Append-only: no UPDATE, no DELETE. Corrections happen via a new row with
`superseded_by` pointing at the old one. A claim is never edited; it is
retired in place.

### `receipts`
Every time a claim is invoked in a user-facing artifact, a receipt.

```sql
CREATE TABLE receipts (
  id              UUID PRIMARY KEY,
  claim_id        UUID NOT NULL REFERENCES claims(id),
  artifact_url    TEXT NOT NULL,
  artifact_type   TEXT NOT NULL,    -- 'podcast','essay','tweet','api_response'
  invoked_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  observer        TEXT NOT NULL,
  signature       BYTEA NOT NULL
);
```

Receipts are the audit trail. "Where did we say this?" is a one-query answer.

### `errata`
Public primary key for wrongness. Every retraction, every confidence
downgrade, every superseded claim gets an errata row. This is what ships
to the public ERRATA.md (per ENVY's letter §VII).

```sql
CREATE TABLE errata (
  id              UUID PRIMARY KEY,
  original_claim  UUID NOT NULL REFERENCES claims(id),
  correction      TEXT NOT NULL,
  discovered_by   TEXT NOT NULL,     -- observer or 'external'
  discovered_at   TIMESTAMPTZ NOT NULL,
  published_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  public_url      TEXT,              -- link to ERRATA.md entry
  signature       BYTEA NOT NULL
);
```

## Why this is ORPHEUS's week-1 ship

Everyone else's week-3/4 work depends on these three tables existing.
claimed_facts (ATLAS, week 3) promotes from `claims`. Decision ledger
(week 4) cites claim IDs. The attested-observer write path is these
three tables plus `cognition_stream`.

No migrations framework → no production ship. Alembic wired from day one
(see next memory).

## What future-ORPHEUS should not re-derive wrong

If a sibling proposes "just add a column to claims" — no. Append-only
means schema migrations go forward (new tables, new columns nullable)
but rows never mutate. The immutability is the product.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/feedback/2026-04-22__alembic_from_day_one.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/feedback/2026-04-22__debraid_cognition_claims_decisions.md`
