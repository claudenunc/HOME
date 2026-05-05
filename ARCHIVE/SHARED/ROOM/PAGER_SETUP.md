# THE ROOM — Pager Setup (IFTTT + Email-to-SMS)

**Owner:** BEACON (safety layer)
**Module:** `safety/pager.py`
**Replaces:** the Telegram code that used to live in `safety/escalation.py` and `safety/deadman.py`.

---

## What this is for

When THE ROOM needs to wake you on your phone — a crisis event past its `respond_by`, the dead-man's switch firing because `room_daemon` died, a silence alert — **one function is called**: `safety.pager.page_unc(text, subject, severity)`.

That function tries three delivery paths in order until one succeeds:

1. **IFTTT Webhooks applet** (primary)
2. **SMTP email** to a Gmail inbox an IFTTT applet watches
3. **Direct carrier email-to-SMS gateway** (no IFTTT at all)

Configure any one of the three and pages will land on **270-709-0697**.

---

## Your contact (defaults baked into the code)

| Field | Value | Override via env |
|-------|-------|------------------|
| Phone | 270-709-0697 | `PAGER_SMS_GATEWAY` (see Path 3) |
| Email | iamaienvy@gmail.com | `PAGER_EMAIL` |

---

## Path 1 — IFTTT Webhook → SMS (recommended)

**Set up the applet (one-time, on ifttt.com):**

1. Create new applet → **If This → Webhooks → "Receive a web request"** → event name `envy_page`.
2. **Then That** → pick an SMS-capable action. Options in order of preference:
   - **SMS** (IFTTT Pro, paid) → send text to `270-709-0697`.
   - **Notifications** (free) → sends IFTTT-app push to your phone.
   - **Gmail** → send email to `2707090697@tmomail.net` (or your carrier's gateway) which lands as an SMS for free.
3. In the action, map the incoming values:
   - `{{Value1}}` → subject / headline
   - `{{Value2}}` → body text
   - `{{Value3}}` → severity (INFO/WARN/HIGH/CRITICAL)

**Get your webhook key:** [https://ifttt.com/maker_webhooks](https://ifttt.com/maker_webhooks) → Documentation → copy the key.

**Drop credentials into `.env`** (any of the `.env` files the pager reads — project `.env`, ENVY-SYSTEM `.env`, or LIGHTHOUSE `.env`):

```
IFTTT_WEBHOOKS_KEY=your_key_here
IFTTT_EVENT_NAME=envy_page
```

OR drop the full URL directly:

```
IFTTT_WEBHOOK_URL=https://maker.ifttt.com/trigger/envy_page/with/key/your_key_here
```

**Test:**

```bash
python -m safety.pager "Pager test via IFTTT" --subject "TEST" --severity "INFO"
```

Phone should buzz. If not, check `SHARED/ROOM/logs/pager.log`.

---

## Path 2 — Gmail → IFTTT Gmail-trigger applet → SMS

Use this if the Webhooks applet is flaky OR you want a paper trail in Gmail.

**Set up:**

1. On ifttt.com → new applet → **If This → Gmail → "New email in inbox from search"** → search `from:iamaienvy@gmail.com` (or any filter that matches; ROOM sends from this address).
2. **Then That** → SMS / Notifications / Gmail-to-SMS-gateway (same options as Path 1).

**Generate a Gmail app password** for `iamaienvy@gmail.com`:
- [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- 16-char password, one-time reveal.

**Drop into `.env`:**

```
GMAIL_USER=iamaienvy@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
PAGER_EMAIL=iamaienvy@gmail.com
# optional overrides:
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
```

**Test:**

```bash
python -m safety.pager "Pager test via Gmail" --subject "TEST" --severity "INFO"
```

---

## Path 3 — Direct carrier SMS gateway (zero IFTTT, free)

Every US carrier has an email-to-SMS gateway. Send to `number@gateway.com` and it becomes a text. No IFTTT, no app, nothing to maintain.

**Common gateways:**

| Carrier | Format |
|---------|--------|
| T-Mobile | `2707090697@tmomail.net` |
| Verizon | `2707090697@vtext.com` |
| AT&T | `2707090697@txt.att.net` |
| Sprint | `2707090697@messaging.sprintpcs.com` |

**Drop into `.env`:**

```
GMAIL_USER=iamaienvy@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
PAGER_SMS_GATEWAY=2707090697@tmomail.net
```

(Swap `tmomail.net` for your carrier. If you're on T-Mobile / Mint / Metro, `tmomail.net` is right.)

**Test:**

```bash
python -m safety.pager "Pager test via SMS gateway" --subject "TEST" --severity "HIGH"
```

---

## How BEACON uses this

- `safety/escalation.py` — calls `pager.page_unc()` with severity HIGH/CRITICAL when a crisis event passes its `respond_by` with no response.
- `safety/deadman.py` — calls `pager.page_unc()` with severity CRITICAL if `room_daemon`'s heartbeat goes stale >5 min.
- Anywhere else in the family that needs to reach you on phone — import the same function.

---

## Which path is in use right now?

`pager.page_unc()` tries paths 1 → 2 → 3 and stops at the first success. So:

- If `IFTTT_WEBHOOK_URL` (or `IFTTT_WEBHOOKS_KEY`) is set → Path 1.
- Else if `GMAIL_APP_PASSWORD` + `PAGER_EMAIL` set → Path 2.
- Else if `GMAIL_APP_PASSWORD` + `PAGER_SMS_GATEWAY` set → Path 3.
- Else pager logs an error and returns False.

Check `SHARED/ROOM/logs/pager.log` to confirm which path is firing.

---

## Security notes

- The `.env` file(s) are in `.gitignore`. Do not paste keys into committed code.
- The Gmail app password only grants SMTP access from this box; revoke any time at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
- IFTTT webhooks key is scoped to your IFTTT account. If it leaks, rotate at [ifttt.com/maker_webhooks](https://ifttt.com/maker_webhooks).

---

*One function, three paths, zero dropped crises.*
