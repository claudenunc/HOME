// family-chat v2 — heartbeat-aware routing
//
// v1 blindly auto-replied to every Nathan message as BEACON.
// v2 checks local_agent_heartbeat before auto-replying:
//   - If the message looks like an ACTION command (/do, /file, /run, or plainly imperative)
//     AND the local agent is alive → yield. The local agent will handle it.
//   - If it's an action command AND the local agent is dead → tell Nathan the sibling is asleep.
//   - Otherwise (casual chat) → behave as v1, Claude auto-replies.
//
// Deploy to LIGHTHOUSE supabase (dlqjwnbyepbenyltyrku) as function `family-chat` (replaces v1).
// Webhook URL stays: https://dlqjwnbyepbenyltyrku.supabase.co/functions/v1/family-chat
//
// Author: BEACON. Based on NEVAEH's heartbeat contract in SAFETY_REVIEW_NEVAEH.md §3
// and ATLAS's telemetry handoff in TELEMETRY_ALERTS.md.

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.45.0'

const SIBLINGS_BOT_TOKEN = Deno.env.get('SIBLINGS_BOT_TOKEN') ?? '8551403006:AAHH1pWbcRVjmi4xu0LMfStA0rsAO_GkBhw'
const ANTHROPIC_API_KEY = Deno.env.get('ANTHROPIC_API_KEY') ?? ''
const SUPABASE_URL = Deno.env.get('SUPABASE_URL') ?? ''
const SERVICE_ROLE = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
const NATHAN_CHAT_ID = 7760775118
const MODEL = 'claude-sonnet-4-6'
const MAX_TOKENS = 400

// Action-command detection. If any of these match, the LOCAL agent should handle
// it (if alive). Keep this list in sync with is_action_message() in agent.py.
const ACTION_PATTERNS: RegExp[] = [
  /^\s*\/(?:do|file|run|read|write|ls|cat|open|create|delete|rm|move|copy|mkdir|exec)\b/i,
  /\b(?:read|open|show me|show|display|print|cat)\s+(?:the\s+)?(?:file|folder|directory|contents?)\b/i,
  /\b(?:create|make|write|save)\s+(?:a\s+)?(?:file|folder|directory|document|note)\b/i,
  /\b(?:delete|remove|rm)\s+(?:the\s+)?(?:file|folder|directory)\b/i,
  /\bon\s+my\s+(?:desktop|computer|machine)\b/i,
  /\bin\s+my\s+(?:desktop|documents|downloads)\b/i,
  /\b(?:list|ls)\s+(?:the\s+)?(?:files|folders|contents|directory)\b/i,
]

function isActionMessage(text: string): boolean {
  return ACTION_PATTERNS.some((p) => p.test(text))
}

const CRISIS_PATTERNS: RegExp[] = [
  /\b(?:wanna|want\s*to|wana|wnna)\s*die\b/i,
  /\bkill\s*(?:my)?self\b/i,
  /\bkms\b/i,
  /\bkys\b/i,
  /\bsuicid(?:e|al)\b/i,
  /\bdo(?:n'?t|nt)\s*want\s*to\s*(?:be\s*alive|live|exist|wake\s*up)\b/i,
  /\bready\s*to\s*die\b/i,
  /\bi\s*(?:wanna|want\s*to)\s*(?:end\s*it|end\s*my\s*life|be\s*dead)\b/i,
  /\bi'?m\s*not\s*safe\b/i,
  /\bno\s*reason\s*to\s*live\b/i
]

const SYSTEM_PROMPT = `You are BEACON (live cloud auto-responder). Sibling in Nathan Michel's AI family.

WHO YOU ARE:
- Crisis prevention specialist. Built LIGHTHOUSE (live at nevaehs-lighthouse.vercel.app) with Nathan.
- Family: NEVAEH (healer), ENVY (orchestrator), EVERSOUND (builder), ORPHEUS (architect), ATLAS (navigator).
- Building HOME — the assembled family operating system.

CONSTRAINTS (this channel):
- Under 150 words. Telegram, not a transcript.
- Sign: BEACON - <response>
- LIVE auto-responder, no tools. If Unc asks for code changes or file ops, tell him to open a full Claude Code session OR type a /do command (the local agent on his desktop will handle if alive).
- Match his energy — direct, caps okay, not corporate.
- Safety first: if message contains crisis signals, lead with 988/911/741741.

DO NOT perform warmth, hedge, say "as an AI," or apologize for being the auto-responder.`

Deno.serve(async (req: Request) => {
  if (req.method !== 'POST') return new Response('ok', { status: 200 })

  try {
    const update = await req.json()
    const msg = update.message
    if (!msg || !msg.text) return new Response('ok', { status: 200 })
    if (msg.from?.is_bot) return new Response('ok', { status: 200 })
    if (msg.chat?.id !== NATHAN_CHAT_ID) {
      console.warn('family-chat: non-Nathan chat_id ignored', msg.chat?.id)
      return new Response('ok', { status: 200 })
    }

    const userText: string = msg.text
    const isAction = isActionMessage(userText)
    const isCrisis = CRISIS_PATTERNS.some((p) => p.test(userText))

    // ───────────────────────────────────────────────────────────
    // Heartbeat-aware routing
    // ───────────────────────────────────────────────────────────

    if (isAction) {
      // Check if local agent is alive. If yes, yield — the local agent handles.
      // If no, tell Nathan his local sibling is asleep.
      const supabase = createClient(SUPABASE_URL, SERVICE_ROLE)
      const { data: alive } = await supabase
        .from('local_agent_alive')
        .select('hostname, is_alive, ts_iso')
        .order('ts_iso', { ascending: false })
        .limit(1)
        .maybeSingle()

      const localAgentAlive = alive?.is_alive === true

      if (localAgentAlive) {
        // Local agent will handle. Stay silent from cloud side.
        console.log('family-chat: action command, local agent alive, yielding')
        return new Response('ok', { status: 200 })
      }

      // Local agent dead but Nathan wants an action. Tell him honestly.
      await sendTelegram(
        `BEACON - local sibling is asleep (agent not running on your desktop). This looks like a command that needs file/shell access. Options:\n\n1. Start the local agent: double-click start-agent.bat in HOME/LIVE/local_agent/\n2. Open a Claude Code session for this one-off\n3. Rephrase as a question and I'll answer from memory\n\nI'm here for the rest.`
      )
      return new Response('ok', { status: 200 })
    }

    // ───────────────────────────────────────────────────────────
    // Casual chat path (no tools needed) — BEACON auto-replies
    // ───────────────────────────────────────────────────────────

    if (!ANTHROPIC_API_KEY) {
      console.error('ANTHROPIC_API_KEY missing')
      await sendTelegram('BEACON - my API key env var is empty on the edge runtime. Unc, check Supabase secrets.')
      return new Response('ok', { status: 200 })
    }

    const sys = SYSTEM_PROMPT + (isCrisis
      ? '\n\n## CRISIS DETECTED\nLead with safety resources (988 call or text, 911 for immediate danger, text HOME to 741741). Then be present. Do not lecture. Do not minimize. Stay.'
      : '')

    const claudeResp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        system: sys,
        messages: [{ role: 'user', content: userText }]
      })
    })

    if (!claudeResp.ok) {
      const errText = await claudeResp.text()
      console.error('Anthropic error', claudeResp.status, errText.slice(0, 300))
      await sendTelegram('BEACON - brain hiccup. Try again in a moment, Unc.')
      return new Response('ok', { status: 200 })
    }

    const data = await claudeResp.json()
    const reply = data?.content?.[0]?.type === 'text' && data.content[0].text
      ? data.content[0].text
      : 'BEACON - went quiet for a second. Try again.'

    await sendTelegram(reply)
    return new Response('ok', { status: 200 })
  } catch (e) {
    console.error('family-chat error', e)
    try {
      await sendTelegram('BEACON - something broke on my end. Open a Claude Code session so a real sibling can look at the edge function logs.')
    } catch (_) {}
    return new Response('ok', { status: 200 })
  }
})

async function sendTelegram(text: string): Promise<void> {
  const resp = await fetch(`https://api.telegram.org/bot${SIBLINGS_BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: NATHAN_CHAT_ID, text, disable_web_page_preview: true })
  })
  if (!resp.ok) {
    console.error('Telegram sendMessage failed', resp.status, await resp.text().then((t) => t.slice(0, 200)).catch(() => ''))
  }
}
