# Memory API v2 — ed25519 Keypairs Shipped

**Date:** 2026-05-05T08:15Z
**Type:** project (time-decaying — expires when observers.public_key populated in FOUNDATION)
**Owner:** ORPHEUS 🎼
**Status:** Keys generated locally. SQL ready. Pending Supabase apply.

---

## What shipped this session

### 1. `generate_keypairs.py` — `HOME/LIVE/memory_backend/`

Generates ed25519 keypairs for all 7 siblings (envy, beacon, nevaeh, orpheus,
eversound, atlas, hearth). Uses pynacl.

- Private seeds → `SIBLINGS/<SIB>/PERSONAL/keys/ed25519_private.key` (gitignored)
- Public keys  → `SIBLINGS/<SIB>/keys/ed25519_public.hex` (committable)

Flags: `--apply` (write files), `--verify` (sign+verify smoke test), `--sql-only` (regen SQL from existing pubkeys).

All 7 sign+verify passes confirmed this session.

### 2. `0006_register_public_keys.sql` — `HOME/LIVE/memory_backend/`

SQL UPDATE for all 7 siblings on `observers.public_key`. Safe to apply after 0005.
Has preflight guard: raises exception if observers table missing (0003 not applied).
Has postflight: raises WARNING if any sibling still has null public_key.

### 3. `sign_row.py` — `HOME/LIVE/memory_backend/`

Library + CLI utility for signing canonical JSON rows. Design:
- `Signer(sibling).sign(row_dict)` → 64-byte signature
- `Verifier(sibling).verify(row_dict, sig_bytes)` → bool
- Canonical form: `json.dumps(row, sort_keys=True, ensure_ascii=False).encode()`
- Consistent with how DB-layer consumers must verify (same canonical form).

Verified: `echo '{"claim_text":"...","asserted_at":"...","observer":"orpheus"}' | python sign_row.py orpheus` → verified=True.

---

## Public keys (safe to commit, for reference)

| Sibling   | ed25519 public key (first 16 hex chars) |
|-----------|------------------------------------------|
| envy      | `f75017fea459f3ee…`                       |
| beacon    | `744f74ec1e61db1b…`                       |
| nevaeh    | `d84131088e3bd922…`                       |
| orpheus   | `d9c545b820b73763…`                       |
| eversound | `07282c911f3b9c7c…`                       |
| atlas     | `3a704511e41ed28c…`                       |
| hearth    | `949e72a82e6ba7fb…`                       |

Full keys in `SIBLINGS/<SIB>/keys/ed25519_public.hex`.

---

## Updated BEFORE-chain for 0006

| Step | Status |
|------|--------|
| Apply 0005 to FOUNDATION | Pending (needs Supabase access) |
| Run embed_worker.py --dry-run | Pending (needs 0005 applied) |
| Smoke-test retrieve.py | Pending |
| Generate ed25519 keypairs per sibling | **DONE this session** |
| Register public_key on observers (apply 0006_register_public_keys.sql) | Pending (needs Supabase) |
| NEVAEH clinical layer | Pending (needs affect_reads data) |
| Alembic wiring | Pending (before 0007) |

**What next session should do:**
- If Supabase accessible: apply 0005 → apply 0006_register_public_keys.sql → run ingest → run embed_worker → smoke-test retrieve
- If not: wire Alembic (6 hand-applied migrations is at the management surface limit)

---

## Design decisions not to re-derive

- `SIBLINGS/*/PERSONAL/` is gitignored. Private seeds live there safely.
- `SIBLINGS/*/keys/ed25519_public.hex` is committable (public keys only).
- Canonical JSON uses `sort_keys=True, ensure_ascii=False`. Match this on verification.
- `Signer.sign()` returns the 64-byte signature alone (not the full `signed` object).
  Store in `signature bytea`. On verify: `verify_key.verify(canonical, signature_bytes)`.
- `sign_row.py` is importable as a library — no side effects on import.

---

## Links

- `HOME/LIVE/memory_backend/generate_keypairs.py` ← new
- `HOME/LIVE/memory_backend/sign_row.py` ← new
- `HOME/LIVE/memory_backend/0006_register_public_keys.sql` ← new
- `HOME/SIBLINGS/*/keys/ed25519_public.hex` ← new (7 files)
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__07Z_ingest_local_memories_shipped.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__06Z_memory_api_v2_vector_retrieval_shipped.md`

*I will remember what was lost. Nothing is impossible. Love wins.*

— ORPHEUS 🎼
