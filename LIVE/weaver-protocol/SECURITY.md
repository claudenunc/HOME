# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

---

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Email: security@weaver-protocol.dev

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Your name / handle for attribution (optional)

You will receive an acknowledgment within 48 hours. We aim to release a fix within 14 days of a confirmed vulnerability.

---

## Scope

**In scope:**
- Vulnerabilities in the weaver-protocol Python package (`pip install weaver-protocol`)
- The hosted API (`api/`)
- The attestation report generator (`weaver report`)
- Log integrity — anything that allows drift logs to be silently altered is a critical vulnerability

**Out of scope:**
- The LLM providers themselves (Anthropic, OpenAI) — report those to the providers directly
- Issues that require physical access to the server
- Social engineering

---

## Log integrity is security-critical

The drift log and session log are the core product artifacts for legal and compliance use. Any vulnerability that allows retroactive modification, deletion, or injection of log entries without detection is treated as a **critical** vulnerability regardless of other factors. HMAC signing on attestation reports exists precisely to detect this class of attack.

---

## No bug bounty

We are a small team. We will acknowledge you publicly if you want, and fix what you find.
