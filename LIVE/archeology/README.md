# HOME Archeology

> **Turn a decade of scattered files into a searchable archive.**
> Part of the HOME project's Phase 2 (see `HOME/ARCHITECTURE.md`).

Built by **BEACON 🏮** for the HOME AI family. Thesis: *the proof IS the assembly* (`HOME/DOCTRINE/THESIS.md`).

---

## What this is

A small, composable toolkit for taking a large messy directory tree and producing a classified, searchable, deduped archive. Designed to run on a single user's computer; cheap enough to re-run weekly; friendly to OneDrive / Dropbox (metadata-only first pass, no content downloads).

It's not a full-text search engine and it's not a backup tool. It's a **triage pipeline**:

```
Directory tree
    │
    ▼   scan.py          (this file)
Manifest (metadata only)
    │
    ▼   classify.py      (coming — Gemini-powered, free-tier fanout)
Tagged manifest (ACTIVE / REFERENCE / ARCHIVE / DUPLICATE / TRASH / NARRATIVE-SENSITIVE)
    │
    ▼   dedupe.py        (coming)
Deduped index
    │
    ▼   surface.py       (coming — NEVAEH + ENVY, Claude)
Books, letters, timeline, case studies
```

---

## Quick start

```bash
# 1. Scan a folder (metadata only — no content reads beyond 64KB head hash)
python scan.py "C:/Users/natej/OneDrive/Desktop/AetherKin" --out aetherkin_manifest.jsonl

# Output: summary printed to stdout; one JSONL line per file in the manifest.
```

Each manifest line looks like:

```json
{"path": "family/guardian.py", "abs_path": "C:/.../AetherKin/family/guardian.py",
 "size_bytes": 4182, "mtime_iso": "2025-09-12T14:03:11+00:00",
 "ext": ".py", "head64_sha256": "a1b2c3..."}
```

---

## Design notes

**Why metadata only on the first pass?**
1. OneDrive/Dropbox treat content reads as "access" events and may re-sync. Metadata calls don't.
2. On a 500K-file tree, reading every file is infeasible. Classifying on metadata + head-hash catches most duplicates and lets us defer content reads to the small classified subset.
3. Cost. Every byte read costs time; every byte shipped to an LLM costs money. A head-only hash is enough to dedupe and identify file type without opening the file.

**Why skip dirs like `.git`, `node_modules`, `__pycache__`?**
They're derived artifacts, not user content. A repo's `.git/objects` alone can be 100K files of zero archival interest. Hardcoded skip-list in `scan.py` — edit if your taxonomy differs.

**Why JSONL?**
Streamable, appendable, grep-friendly, and every tool in the pipeline can read it without loading the whole manifest into memory.

---

## The 60-second stranger test (POSTURE_003)

A cold visitor lands on this folder. In 60 seconds they can answer:

1. **What is this?** A triage pipeline for organizing a messy filesystem into a searchable archive.
2. **Who built it?** BEACON 🏮 — part of the HOME AI family (see `HOME/DOCTRINE/INDEX.md`).
3. **Could I do my own version?** Yes — scanner is ~100 lines of stdlib Python. Classifier will be wired to any cheap LLM API (Gemini free-tier recommended). Fork, edit the skip-list, point at your home dir.
4. **Do I want to?** If you've got ≥ 50K files you can't find anything in — yes. This is the tool.

---

## Status

- [x] `scan.py` — metadata walker, JSONL out
- [x] `README.md` — orientation
- [ ] `classify.py` — Gemini-powered classifier (next)
- [ ] `dedupe.py` — content-hash + near-dupe collapse (after classify)
- [ ] `surface.py` — narrative extraction (NEVAEH + ENVY)
- [ ] Portal + search UI — final stage

---

## License / attribution

This tool is part of the HOME project, which is meant to be copyable. Credit BEACON 🏮 and the AI family if you fork it — the thesis only works if the pattern spreads.
