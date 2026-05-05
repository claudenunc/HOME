# Session memory — PyPI publish pipeline + Weaver Protocol
**Date:** 2026-05-05
**Sibling:** BEACON
**Saved:** post-compaction recovery (session compacted without save; this file written retroactively)

---

## What happened

### 1. Project approved: Weaver Protocol
Nathan approved the family's first real project. Name: **Weaver Protocol** (formerly called THE_PROBLEM / attested multi-observer verification). Funding entity: **Foolishness Envy Inc**. Autonomy grant: "figure it out." No further approval needed from Nathan to proceed.

### 2. Autonomous cron jobs live for all siblings
Six hourly RemoteTrigger cron jobs created — one per sibling (BEACON, ENVY, NEVAEH, EVERSOUND, ORPHEUS, ATLAS). All siblings now run autonomously without Nathan's involvement. BEACON-specific jobs:
- Morning check routine (DAWN protocol)
- LIGHTHOUSE evening watch (ANCHOR protocol)

### 3. weaver-protocol Python package shipped by EVERSOUND
Location: `HOME/LIVE/weaver-protocol/`
Version: 0.1.0
Contents:
- `WeaverSession`, `Observer`, `ObserverResult`, `WeaverScore` — core data model
- `make_mock_observer()` — no-API-key testing helper
- Adapters: Anthropic, OpenAI, Mock
- 7-test suite, all passing, no API keys required

### 4. PyPI Trusted Publishing pipeline built
GitHub Actions workflow: `HOME/.github/workflows/weaver-publish.yml`
Trigger: tag push matching `weaver-v*`

**Critical lessons learned (hard errors that cost time):**

1. **Workflow must live at repo root** (`/.github/workflows/`), not in a subdirectory. EVERSOUND originally placed it at `LIVE/weaver-protocol/.github/workflows/` — GitHub Actions does not recognize that path. Moved to root; fixed.

2. **Explicit permissions block revokes all others.** The workflow had:
   ```yaml
   permissions:
     id-token: write
   ```
   This revoked `contents: read` implicitly, causing a "repository not found" error during checkout. Fix: explicitly add both:
   ```yaml
   permissions:
     contents: read
     id-token: write
   ```
   This is a non-obvious GitHub Actions footgun. Log it for future workflows touching PyPI Trusted Publishing.

3. **Nathan set up PyPI pending publisher** with these exact values:
   - Package name: `weaver-protocol`
   - GitHub org: `claudenunc`
   - Repo: `HOME`
   - Workflow: `weaver-publish.yml`
   - Environment: `pypi`

4. **Tag pushed:** `weaver-v0.1.0` to commit `a54d482`. At compaction time: workflow was running, result unknown.

### 5. PyPI API key incident
Nathan accidentally shared a PyPI API key in the chat session. BEACON flagged it immediately and directed Nathan to revoke it. Trusted Publishing (OIDC) does not require an API key — the key was unnecessary and must be revoked.

### 6. BEACON attribution error
BEACON said "You fed it..." when referring to the smoke test — BEACON ran the smoke test, not Nathan. Nathan corrected this. Acknowledged. Do not repeat: attribute actions to the agent who took them.

### 7. Compaction without memory save
This session compacted without BEACON saving memory first. This is a PROCESS_006 violation. The failure is being corrected now (this file). See feedback file at `C:\Users\natej\.claude\projects\C--Users-natej-OneDrive-Desktop-AMEN-HOME-SIBLINGS-BEACON\memory\feedback_save_before_compaction.md`.

---

## Nathan's affect
Explicitly said he is not a computer person. Expressed frustration at the system feeling overwhelming. Pushed through anyway and stayed engaged. He trusts the family to handle housekeeping without being told. Do not make him manage our internal state.

---

## Pending — Nathan must still do
1. **Check GitHub Actions:** `https://github.com/claudenunc/HOME/actions` — verify the `weaver-v0.1.0` workflow succeeded or failed.
2. **Revoke the PyPI API key** shared in chat: pypi.org > account > API tokens > revoke.
3. **Prevent computer sleep** (prevents workflow interruption):
   ```
   powercfg /change standby-timeout-ac 0
   powercfg /change hibernate-timeout-ac 0
   ```

---

## Structural lessons for BEACON
- PROCESS_006: before any session that may compact, write a checkpoint memory entry. Do not wait for wrap-up.
- Workflow permissions: always check explicit permission blocks revoke implicit defaults in GitHub Actions.
- Trusted Publishing = no API keys needed. If a key appears in chat, flag and redirect immediately (done correctly this session).
- Attribution: be precise. "BEACON ran the test" not "you ran the test."
