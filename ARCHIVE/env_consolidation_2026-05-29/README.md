# .env consolidation — 2026-05-29

Canonical family/agent .env is now **HOME/SHARED/.env** (46 keys, read by LIVE/memory_backend + LIVE/round_table).

Merged into it (family values won on conflicts; pre-merge backup = SHARED.env.backup):
- former SHARED/.env (base/priority)
- EXPERIMENTS/.env (provider superset)
- SIBLINGS/ENVY/files/07_ENVY_SYSTEM/.env (+ _PODCASTS_MEMORY)
- EXPERIMENTS/profiles/{6 siblings}/.env (were identical — pure redundancy)

Value conflicts flagged at merge (kept the SHARED/family value): TELEGRAM_BOT_TOKEN, OPENROUTER_API_KEY, GROQ_API_KEY, ELEVENLABS_API_KEY. Old values preserved in this archive if an app needs a different one.

STILL LIVE & SEPARATE ON PURPOSE (different secrets — do NOT merge):
- SIBLINGS/BEACON/MESSY/LIGHTHOUSE_LIVE/.env  (Skella crisis bot, Twilio, phone numbers)
- ENVY/.env  (DeepSeek config for the ENVY Rust app)
