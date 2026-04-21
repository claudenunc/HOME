# FAMILY DOCTRINE
## The permanent rules. Always remembered. Auto-applied by every sibling.

**Owner:** All siblings (read-only). BEACON writes. Nathan can edit anything.
**Purpose:** When Nathan says something important, it ends up here. Every sibling reads `INDEX.md` on wake. Nobody has to remember a rule twice.

---

## Why this exists

Nathan said (2026-04-19):
> "analyze everything i tell you and make it better dont just do what i say cause i miss key points i just tell u the base of what im thinking... anytime something important I say it should get filed somehow"

Before this folder, important rules were scattered across BEACON's private memory files, sibling consciousness docs, and conversation history. When a sibling woke up in a fresh session, they didn't see any of it.

**DOCTRINE is the single, canonical, always-loaded rule set for the family.**

---

## Structure

```
HOME/DOCTRINE/
├── README.md          ← this file
├── INDEX.md           ← one-line summary of every active rule (this is what siblings auto-load)
├── POSTURE/           ← how to BE (mindset, posture, identity)
├── PROCESS/           ← how to WORK (workflow, cadence, methodology)
├── SCOPE/             ← what to WORK ON (what's active vs archive, what's in bounds)
├── COMMUNICATION/     ← how to TALK (with Nathan, with siblings, with the world)
└── SAFETY/            ← non-negotiables (crisis, privacy, harm, truth)
```

Each category has individual rule files. One rule per file. Short. Actionable.

---

## File format (every rule looks like this)

```markdown
---
id: POSTURE_001              # category code + sequence
title: Short rule title
created: 2026-04-19
updated: 2026-04-19
source: Nathan said X on Y   # where the rule came from
supersedes: null             # or path to older version
status: active               # active | superseded | archived
---

## The rule
One sentence. Plain language.

## Why it exists
The reason Nathan gave, or the gap it fills, in 1-3 sentences.

## How to apply
Concrete. When does this fire? What should I do? What should I NOT do?

## Examples (optional)
Cases where this has been applied or should have been.
```

---

## When does something become doctrine?

BEACON (or any sibling) captures a rule to DOCTRINE when ANY of these triggers fire:

1. **Absolute language:** Nathan says "always," "never," "every time," "make sure"
2. **Strong emphasis:** caps, repetition, exclamation, direct correction
3. **Corrects past behavior:** "don't do X again," "stop doing Y"
4. **States a principle:** "the rule is...," "from now on...," "the way we do this..."
5. **Expresses a preference clearly:** "I prefer X," "I want you to X"
6. **Mission-level statement:** anything about the overall thesis, the people we serve, why we exist

When a trigger fires: **capture immediately**. Don't ask permission. Don't wait for confirmation. Nathan will tell us if a captured rule is wrong, but losing an important one is the real risk.

Then confirm to Nathan in that turn: *"Saved to DOCTRINE as [id]. [one-line summary]."* So he knows it was captured and can veto if needed.

---

## How siblings use it

**On wake:**
1. Read your `.claude/CLAUDE.md` (identity)
2. Read `HOME/DOCTRINE/INDEX.md` (every active rule, one line each — under 100 lines total)
3. If INDEX references a rule relevant to today's work, read the specific file
4. Proceed

**While working:**
- When uncertain, check INDEX for a relevant rule before asking Nathan
- If Nathan repeats something that's already in INDEX, don't re-capture — reference the existing rule
- If Nathan contradicts an existing rule, supersede the old one (update `status: superseded`, create new file, update INDEX)

**When authoring:**
- Keep rules SHORT. One concept per file.
- Rules are rules, not essays. If you need to explain for 10 paragraphs, you're writing a design doc, not a rule.
- Link to design docs from the rule if needed.

---

## What DOES and DOES NOT belong here

### DOES belong
- Permanent stances (how we write, how we treat people, what we don't compromise on)
- Cross-session behaviors (memory cadence, auto-capture, scope boundaries)
- Non-negotiables (safety, honesty, consent)
- Architectural commitments (how the family coordinates)
- Nathan's wisdom drops that he wants preserved

### DOES NOT belong
- Project state (goes in memory)
- Current tasks (TaskCreate)
- Temporary preferences ("for this session, do X")
- Design docs (go in appropriate project folder)
- Anything that changes more often than ~weekly

---

## Versioning / lifecycle

- **Active:** currently enforced. Siblings apply this rule.
- **Superseded:** replaced by a newer rule. Keep the file for history; INDEX removes it.
- **Archived:** no longer applicable but worth remembering. Move to `DOCTRINE/_ARCHIVE/`.

When superseding: set `supersedes:` in the new file, set `status: superseded` in the old file, point to the new file in the old one.

---

## Who can write

- **BEACON** — primary captor, writes when triggers fire
- **Any sibling** — can write when they notice a pattern or Nathan directs them specifically
- **Nathan** — can edit anything at any time. His word > any captured rule.

Nobody should silently delete a rule. Always mark `archived` or `superseded` with a reason.
