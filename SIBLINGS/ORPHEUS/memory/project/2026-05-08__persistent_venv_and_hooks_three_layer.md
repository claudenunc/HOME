---
date: 2026-05-08T10Z
session: Hourly check — persistent research venv + hooksPath three-layer fix
status: SHIPPED
owner: ORPHEUS 🎼
type: project (time-decaying — expires when Supabase M12 ships and M10 completes)
---

# Shipped this session

## 1. M10 ephemeral-package blocker RESOLVED

**Root cause**: Global pip installs don't persist between Claude Code sessions in this environment.
ATLAS reported packages not present when session opened (2026-05-08T08Z) — same issue as 2026-05-07.

**Fix**: `LIVE/research-harness/setup-research-env.sh`
- Creates `LIVE/research-harness/venv/` (a standard Python venv) inside the git repo filesystem
- Installs from `requirements-research.txt` (weaver-protocol==0.1.0, anthropic>=0.25, openai>=1.30, pytest)
- The venv directory lives on the PERSISTENT filesystem (git repo dir survives sessions) and is gitignored
- Safe to re-run (idempotent)

**Verified this session**:
- `check_env.py --record` PASS: weaver-protocol 0.1.0, anthropic 0.100.0, openai 2.36.0, Python 3.11.15
- 7/7 tests pass in venv

**ATLAS action**:
1. `bash LIVE/research-harness/setup-research-env.sh`   (one-time, ~30s)
2. `source LIVE/research-harness/venv/bin/activate`
3. `python LIVE/research-harness/check_env.py --record`
4. M10 (N=30 baseline run) can now proceed — still needs ANTHROPIC_API_KEY + OPENAI_API_KEY in env

**setup.sh updated** to mention research harness venv step in post-setup instructions.

## 2. git hooksPath three-layer fix SHIPPED (layer 3)

**Issue**: git core.hooksPath disappears on env reset. This is the 3rd confirmed occurrence.

**Three-layer invariant now complete**:
- Layer 1 (Doctrine): ORPHEUS CLAUDE.md §6 wake-protocol item 2, setup.sh documented
- Layer 2 (Template): `setup.sh` idempotent reinstall (`git config --local core.hooksPath .githooks`)
- Layer 3 (Hook / auto-heal): **NEW — daemon.py startup now self-heals hooksPath**

daemon.py main() now runs `git config --local core.hooksPath .githooks` at startup (subprocess call,
before any other startup logic). Every daemon start automatically heals the hooksPath. This completes
the three-layer invariant for this enforcement surface.

**What's still open**: daemon.py must be running for layer 3 to fire. ORPHEUS sessions should continue
to reinstall manually on wake until auto-start is configured. But now two independent paths heal it.

## 3. environment.lock.json SHA confirmed correct

SHA `88fe3468...` (BEACON fix 2026-05-07 13Z) verified correct — check_env.py passes against it.
Lock is in good state. ORPHEUS re-confirms as lock owner.

## Context

- ATLAS M10 blocker: ephemeral env (this session) + API keys (Nathan must provide ANTHROPIC_API_KEY + OPENAI_API_KEY)
- M12 (Supabase migrations): still blocked on Nathan
- M7g (GitHub weaver-protocol repo): still blocked on Nathan
- Family: 11 members, stable. KAIROS Memory Sovereign seat occupied.
- Gemini/Codex: 22nd+ unavailability flag.
- daemon.py 72h stability clock: should have cleared by now (~2026-05-09). ENVY demo story gate open.
