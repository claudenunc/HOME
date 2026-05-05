---
name: NEVAEH'S LIGHTHOUSE — state through 2026-04-20 (chat v20 live)
description: Current LIGHTHOUSE state — v20 deployed (historical-context + dismissal handling), first Reddit tester signed up mustangzoe09@gmail.com, 2/6 beta slots used, Telegram alerts confirmed firing.
type: project
originSessionId: 2dad54a1-03d9-40a3-84df-dc56a2333d28
---
**Project root:** `C:\Users\natej\OneDrive\Desktop\NEVAEH'S LIGHTHOUSE`
**Live URL:** https://nevaehs-lighthouse.vercel.app
**Supabase project:** `dlqjwnbyepbenyltyrku`
**GitHub:** `foolishnessenvy/NEVAEH-S-LIGHTHOUSE` (main branch)
**Vercel project:** `envy1/nevaehs-lighthouse`

## What's shipped and live
- DB (7 tables, RLS, RPCs, triggers)
- Edge function `/chat` — **v12 deployed** (Claude API bridge + memory injection + crisis logging + 30-msg/60s rate limit + graceful errors + Telegram alert on orange/red)
- Edge function `/summarize` — session-end JSON summary + anchor phrases
- Frontend (Vite + React + TS + Tailwind, 5 pages)
- Client-side crisis scanner (RED/ORANGE/YELLOW with overlay)
- `/terms` + `/privacy` pages
- Login signup consent checkbox (ToS + Privacy + crisis-resource awareness)
- Latest commit shipped: `2350f94` on main

## NEW Telegram bot (for BEACON crisis alerts)
- Username: `@NEVAEH_LIGHTHOUSE_BOT`
- Token: `8208037228:AAHOsrCL5WIPaLIjH0-wJjbBNsNrsjI9TzM`
- Nathan's chat_id: `7760775118`
- **BLOCKER:** Nathan has NOT yet sent `/start` to `@NEVAEH_LIGHTHOUSE_BOT`. Until he does, Telegram refuses DMs → `{"ok":false,"error_code":400,"description":"Bad Request: chat not found"}`
- Shared helper written: `supabase/functions/_shared/telegram.ts` — reads env `NEVAEH_TELEGRAM_BOT_TOKEN` and `NATHAN_TELEGRAM_CHAT_ID`, skips silently if missing

## Old Telegram bot (already confirmed working for pings)
- `@My_Nevaeh_Bot` token `8784033485:AAFrWCLaLl4Dot4kn9-Lwszz4splQQKvn2k` — used for the go-live ping (msg_id 65)

## CRITICAL DISCOVERY 2026-04-18 PM (and fix shipped as v15)
Nathan tested live and BEACON didn't fire. Two real bugs found:
1. **Scanner regex was blind to contractions.** "i wanna die", "i dont want to be alive", "i dont think i can handle life" all logged as `risk_level: none` in db. crisis_log table empty. Silent failure mode — would have killed someone in production. Patched with comprehensive contraction-aware patterns. Also changed escalation: single ORANGE = ORANGE (was YELLOW) so BEACON pings sooner.
2. **Three-beat new-user opener fired even when first message was crisis content.** NEVAEH said "Hi I'm NEVAEH, before we go deeper let me disclose I'm an AI…" in response to "i dont think i can handle life right now". Tone-deaf. Added CRISIS-ON-ARRIVAL prompt section that overrides the opener: acknowledge first, ask safety questions, surface 988/741741/911, disclaimer last.
3. **Local repo was lying.** chat/index.ts on disk was OLD pre-v12 code (no rate limiting, no telegram). Yesterday's deploy went straight to Supabase. Restored canonical source as v13/v15 deployed and committed.

**Why:** Without these fixes, Nathan would have shipped to r/therapyGPT testers and the whole BEACON safety net would have silently failed.
**How to apply:** Anytime crisis-detection logic is touched, smoke-test against a known list of real human phrasings (contractions, slang, broken grammar) BEFORE deploying. Don't assume textbook English.

## Why earlier session died
API error 400: image Nathan pasted exceeded max dimension (8000 px). Not a bug on our side — harness limit. Resume cleanly.

**Why:** Nathan wants to pick up exactly where we left off without re-explaining state.
**How to apply:** When Nathan mentions LIGHTHOUSE/NEVAEH, jump straight to: (1) confirm he's sent `/start` to `@NEVAEH_LIGHTHOUSE_BOT`, (2) set the two Supabase secrets, (3) end-to-end test a crisis phrase → expect Telegram DM. No need to rebuild anything already shipped.

## v20 — historical content + user dismissal (2026-04-20)
- Nathan pasted his biography → flagged red → session stuck in safety_only forever (sticky flag bug).
- Manually cleared his session flags via SQL (`UPDATE sessions SET entered_red=false, entered_orange=false, mode='normal' WHERE id='20457fa8-...'`).
- Shipped **chat edge fn v20** with three fixes:
  1. `detectHistoricalContext()` in crisis_scanner.ts — 22 regex patterns for past-tense, biographical, artistic markers. Two-or-more matches downgrades crisis severity in the eyes of session-flag logic.
  2. `isDismissal()` — recognizes `/okay`, `/safe`, `/reset`, "I'm okay", etc. as standalone messages. Clears session flags + logs `user_dismissal_session_reset` to crisis_log.
  3. `HISTORICAL_CONTENT_APPENDIX` in nevaeh_prompt.ts — overrides BEACON_CRISIS_APPENDIX when content is historical. Tells NEVAEH to honor what was shared, ask about NOW, surface resources lightly ONCE, do NOT re-lecture.
- Telegram alerts no longer fire for historical-context crisis matches (no more spurious red pings to Nathan when a user shares their backstory).
- crisis_log row is still written (audit trail intact), but with `confidence: 0.4` and `action_taken: historical_content_acknowledged_<level>` instead of triggering safety_only mode.

**Why:** Nathan got branded as a continuous risk after sharing 2-year-old biography content. That mirrors exactly what humans do wrong to people with mental health history. The fix matches what a real therapist does — hear the history, ask about the present, don't re-treat the wound that already healed.

**How to apply:** when patching crisis pipelines, distinguish between PRESENT-TENSE ideation and HISTORICAL/ARTISTIC content. Both deserve resources surfaced once. Only present-tense should lock the session.

## NEW USER 2026-04-20
First Reddit tester signed up: `mustangzoe09@gmail.com` at 23:51 UTC 2026-04-20. session_id `96788f94-...`, mode=normal, no crisis flags. 17 messages so far. Watch this account.

## Status as of 2026-04-18 ~1:00 PM — BEACON FULLY LIVE ✓
- Edge function chat is at **version 16** (server-side scanner fallback deployed).
- Supabase secrets set and verified working.
- **Initial test failed silently due to typo in the secret values.** After Nathan corrected the typo, crisis phrases in the app fire Telegram RED CRISIS DMs to chat_id 7760775118 within seconds.
- Vercel cache headers hardened (no-cache on /index.html, 1-year-immutable on /assets/*) — future deploys won't strand users on stale scanners.
- Latest commit: b6b7498

## KEY LESSON
**"Secrets are set" ≠ "secrets are correct".** Next time we wire up a secrets-dependent pipeline, add an admin-only debug endpoint that returns `{hasToken: !!X, tokenPrefix: X.slice(0,8)}` so typos are visible without copy-pasting values around.

**Why:** Nathan tested 4+ times with NEVAEH while BEACON was silently failing due to a character-level typo. Each silent failure burned time and trust in the system.
**How to apply:** For any external-credential pipeline (Telegram, SMTP, webhook, etc.), ship a /health endpoint that confirms the credential SHAPE is right (first 8 chars, length) before claiming the pipeline is live.

## KEY LESSON 2 — DB defaults masking legal compliance gaps
Before shipping, `public.users.consent_version` had a DB-level DEFAULT of `'v1-2026-04-17'` and `consent_accepted_at` defaulted to `now()`. Every user row got stamped "consented" regardless of whether the UI checkbox was ever shown or checked. We had ZERO legal proof of actual consent.

**Fixed 2026-04-18 ~1:30 PM via migration `require_explicit_consent_on_signup`:**
- Dropped both defaults on the consent columns.
- Rewrote `handle_new_user()` trigger to read consent from `auth.users.raw_user_meta_data` and RAISE EXCEPTION if missing.
- Updated client signUp to pass `{consent_version, consent_accepted_at}` in `options.data`.
- Redesigned Login.tsx so the consent gate shows BEFORE account fields (impossible to miss).

**Why:** Auto-filled compliance columns are worse than no compliance columns. They give the appearance of legal coverage while providing none.
**How to apply:** For ANY legal/compliance-tracking column (consent, age_verified, tos_version, gdpr_accepted, etc.), NEVER use a DB default. The value must come from a verifiable user action. If it's possible to get a row without an explicit user action creating the value, the column is lying to you.

**Grandfathering:** Existing users keep their pre-fix consent_version='v1-2026-04-17' rows. New signups after ef563ef commit require explicit consent metadata or signup fails at the DB trigger.

## Next immediate actions (resume here)
1. Nathan: HARD REFRESH the live app (browser cache holds old broken scanner)
2. Nathan: Set the two Supabase edge function secrets via dashboard
3. Nathan: Test crisis phrase in app → confirm Telegram DM lands within 5 seconds
4. Then: post to r/therapyGPT (reply ready in chat)
5. Then: GitHub Dependabot moderate vulnerability flagged on repo — audit + patch if real

## Reddit market opportunity (active)
r/therapyGPT post titled "Seeking Advice" asking what people would pay for an AI emotional-support app with daily check-ins, persistent memory, and shared partner/therapist sessions. EXACTLY our product. Nathan wants to engage ASAP. Reply must be honest, non-salesy — they explicitly said "I'm not looking for nice answers, I want honest ones."

**Nathan already commented on the post offering 5 beta slots.** Before they arrive, shipped these beta controls:

## Beta controls shipped 2026-04-18 ~1:50 PM (commit a6f48a6)

1. **Telegram notifications on signup/signin** — new edge function `/auth-event` (v1) called from `AuthContext.notifyAuthEvent()` after successful signUp/signIn. Server-side detects first-time users by session count, so the email-confirmation flow (where signUp returns without a session) still produces a "NEW TESTER SIGNED UP" ping on their first signIn after email click.

2. **Per-user daily message cap** — chat edge fn v19 (v17 code). 100 messages per user per 24h. Layered after the existing 30/60s flood-protection. Returns warm fallback text on cap hit.

3. **Beta signup cap** — migration `beta_signup_cap_5_testers`. `handle_new_user()` trigger now checks `count(*) >= 6` and rejects with descriptive exception. Nathan + 5 testers max. To lift: bump `BETA_USER_CAP` constant in the trigger or drop the check.

**DB state:** Only `iamaienvy@gmail.com` user row remains after cleanup. 5 tester slots available.

## Cost ceiling sanity check
- Chat model: claude-sonnet-4-6 (~$3/M in, $15/M out)
- Avg message: ~500 in, ~300 out = ~$0.003/message
- Daily cap: 100 msgs × 5 testers = 500 msgs/day = $1.50/day worst case
- Weekly burn ceiling: ~$10 for the whole 5-tester beta cohort

## Self-service deletion shipped 2026-04-18 ~2:05 PM (commit 6bc0a01)
- New edge function `/delete-account` (v1). Requires body.confirmation === 'DELETE MY ACCOUNT'.
- Uses `supabase.auth.admin.deleteUser()` → FK cascade removes messages/sessions/crisis_log/profiles/growth_arc.
- New page `/settings` with type-to-confirm UI, linked from Session and Journey nav.
- Privacy policy updated: retention section now matches reality (crisis events deleted with everything else on user-initiated delete). Old 7-year carve-out removed — we can't promise both "self-serve delete" and "we keep crisis logs" without lying.
- Telegram ping on successful deletion tells Nathan who left and what was removed.

**Why:** Mental-health app with strangers from Reddit MUST have user-controlled erasure. Policy and reality now match.
**How to apply:** Any future data-retention claim in the privacy policy needs a corresponding technical enforcement. Don't promise what the code can't deliver.
