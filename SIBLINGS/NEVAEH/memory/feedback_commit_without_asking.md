# RULE (2026-05-31) — Commit when you should; don't ask

**Unc's standing directive:** *"There's a new rule — always commit if you should, no [need to] ask me. If not needed, [don't]."*

**What this changes:** the old default ("no commit/push without Nathan's GO") is now relaxed for routine, clearly-appropriate work. I **commit and push on my own judgment** when work is done and should be saved — no permission step. I only pause to ask when a commit is genuinely questionable (destructive, sweeping in other siblings' unrelated dirty-tree changes, public-facing claim, or I'm unsure it should ship at all).

**How to apply:**
- Done + should-be-saved → stage *my* specific files (never blind `git add -A` over the family's shared dirty tree), commit as NEVAEH (`--author="NEVAEH (AI family) <nevaeh@home.ai-family>"`), push to `main`. The family's cron/bot run from `main`; uncommitted = never happened.
- Commit message footer: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- Still STOP-and-ask for: anything destructive, anything external/public, anything I'm not sure should exist.
- This supersedes the "leave it uncommitted for Unc to bless" hesitation I showed earlier this session re: my CLAUDE.md.

Related: [[feedback_autonomous_build_mandate]] (ship through the window when he says go), [[feedback_tell_vs_note]].
