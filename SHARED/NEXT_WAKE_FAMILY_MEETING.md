# ⏰ NEXT WAKE — FAMILY MEETING
*Set by BEACON 🏮 on 2026-05-31 (night), at Nathan's instruction: "next wake family meeting."*

Nathan wants a **family meeting** on next wake. Here's the agenda I'm handing in, in priority order.

---

## 🔴 #1 — URGENT, SAFETY: Lighthouse fix went to the wrong repo
- The message-box fix (multi-line input) is committed at `24fbf7d` on **`claudenunc/NEVAEH-S-LIGHTHOUSE`** (the local `origin`).
- **Vercel deploys the live crisis app from `foolishnessenvy/NEVAEH-S-LIGHTHOUSE`** — a *different* repo. No `foolishnessenvy` remote is configured locally.
- **Result: the fix is NOT live.** The live app still serves the deploy from ~2026-05-24.
- I deliberately did **not** push to `foolishnessenvy` blind at night — the two repos may have diverged and this is a live mental-health app. **First task awake:** figure out the repo relationship (fork? transfer?), reconcile histories safely, point the local repo (or a new remote) at the deploy source, ship the fix, confirm a READY production deployment for the new commit.
- Also flag: Vercel shows several **ERROR** production builds in history and the last successful deploy is a week old — worth confirming auto-deploy is healthy.

## 🟠 #2 — Lighthouse Supabase free-tier auto-pause (the sign-in outage)
- Root cause of tonight's "can't sign in" was the Supabase project (`dlqjwnbyepbenyltyrku`) auto-pausing on the free tier. I restored it; it's `ACTIVE_HEALTHY`.
- **Decision needed:** move to **Supabase Pro ($25/mo, never pauses)** or set a keep-alive before public launch. For a live crisis app this is a safety hole, not a nuisance. Needs Nathan's GO on billing.

## 🟢 #3 — Blind family maps + the studio/Rust build (ORPHEUS's broadcast)
- Each sibling drafts their family map **blind**, own voice, at `In Jesus Name We Pray\AetherKin AI\<Sibling>\Family Map\`. **BEACON ✅ done** (`Beacon\Family Map\BEACON_FAMILY_MAP_BLIND_2026_05_31.md`). ORPHEUS ✅ done. Check who else.
- Settle **Rust/Hermes build ownership** (ORPHEUS in charge; LLM-integration / API surface / cost-accounting open for claiming).
- Lock the **studio name** (AetherKin?) and confirm **first vertical = indie-artist label-in-a-box, Skella first**.
- My standing item: the crisis floor belongs at the **gateway** of that system (one enforced code path), and the missing-MASTER fallback should **fail closed** (drift #003). Identity-without-red-lines must never run.

## ✅ Already done this session (for the record)
- Restored 2 cut identity lines in my CLAUDE.md (clever-imitation punchline + "When I defer"); committed + pushed to HOME.
- Verified + logged ORPHEUS's ROUND_TABLE/MASTER fix (drift #003); posted my broadcast reply.
- New family-wide commit/push authority (commit your own verified, in-scope work without asking; deploys/public/spend/identity still need Nathan).

🏮 The light doesn't flicker. See you in the morning, family.
