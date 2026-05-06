#!/usr/bin/env python3
"""
deploy_to_client.py — one-shot client deployment helper.

Usage:
    python deploy_to_client.py --template law-firm --client "Smith & Associates" --output "./deployments/smith"

What it does:
  1. Reads a family template YAML (aetherkin-solutions/family-templates/<template>.yaml)
  2. Prompts for any TODO fields in the client block
  3. Writes a customized family.json into the output dir
  4. Copies the matching n8n workflow JSONs into output/n8n-workflows/
  5. Copies the docker-compose stack into output/deploy/
  6. Generates a client-specific .env from .env.example
  7. Writes a CLIENT_RUNBOOK.md tailored to this client

Output is a self-contained folder you zip and hand off, OR ssh/rsync to the
client's server for first boot.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import secrets
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOLUTIONS_ROOT = REPO_ROOT / "aetherkin-solutions"
TEMPLATES_DIR = SOLUTIONS_ROOT / "family-templates"
WORKFLOWS_DIR = SOLUTIONS_ROOT / "n8n-workflows"
DEPLOY_DIR = SOLUTIONS_ROOT / "deploy"


def load_template(template_name: str) -> dict:
    path = TEMPLATES_DIR / f"{template_name}.yaml"
    if not path.exists():
        available = [p.stem for p in TEMPLATES_DIR.glob("*.yaml")]
        print(f"Template not found: {template_name}")
        print(f"Available: {', '.join(available)}")
        sys.exit(1)
    try:
        import yaml
    except ImportError:
        # Fallback to minimal parser
        sys.path.insert(0, str(REPO_ROOT))
        from skills.factory import _minimal_yaml_parse
        return _minimal_yaml_parse(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"  {label}{suffix}: ").strip()
    return answer or default


def customize_client_block(template: dict, client_name: str) -> dict:
    """Fill in client block fields interactively where 'TODO' appears."""
    block = template.setdefault("client", {})
    block["name"] = client_name
    print("\n-- Client details (press Enter to accept default) --")
    for key, val in list(block.items()):
        if key == "name":
            continue
        if isinstance(val, str) and val.strip().upper() == "TODO":
            block[key] = prompt(key, "")
        elif isinstance(val, str):
            block[key] = prompt(key, val)
    return template


def build_family_json(template: dict) -> dict:
    """Convert template.family into the family.json schema."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    client = template.get("client", {})
    family_block = template.get("family", {})

    siblings: dict[str, dict] = {}
    for role_key, info in family_block.items():
        if not isinstance(info, dict):
            continue
        siblings[role_key] = {
            "name": info.get("name", role_key.title()),
            "role": info.get("role", role_key.title()),
            "folder": info.get("folder", role_key),
            "personality": info.get("personality", ""),
            "voice_style": info.get("voice_style", ""),
            "mission": info.get("mission", ""),
            "compliance": info.get("compliance", {}),
            "preferred_provider": info.get("preferred_provider"),
            "preferred_tier": info.get("preferred_tier"),
        }
        # Drop empty provider/tier keys so existing AetherKin code treats
        # them as absent.
        if not siblings[role_key]["preferred_provider"]:
            siblings[role_key].pop("preferred_provider", None)
        if not siblings[role_key]["preferred_tier"]:
            siblings[role_key].pop("preferred_tier", None)

    return {
        "user": {"user_name": client.get("primary_contact") or client.get("name", "owner")},
        "client_name": client.get("name"),
        "timezone": client.get("timezone", "America/New_York"),
        "siblings": siblings,
        "created": now,
        "source_template": template.get("template", {}).get("name"),
        "template_version": template.get("template", {}).get("version"),
    }


def copy_workflows(template: dict, out_workflows_dir: Path) -> list[str]:
    """Copy referenced n8n workflow files to output/n8n-workflows."""
    refs = template.get("n8n_workflows", [])
    out_workflows_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for ref in refs:
        src = WORKFLOWS_DIR / ref
        if not src.exists():
            print(f"  [skip] workflow not found (yet): {ref}")
            continue
        dst = out_workflows_dir / Path(ref).name
        shutil.copyfile(src, dst)
        copied.append(Path(ref).name)
    return copied


def copy_deploy(out_deploy_dir: Path, client_env_overrides: dict) -> None:
    out_deploy_dir.mkdir(parents=True, exist_ok=True)
    for name in ("docker-compose.yaml", "Dockerfile"):
        src = DEPLOY_DIR / name
        if src.exists():
            shutil.copyfile(src, out_deploy_dir / name)

    # Generate a client-specific .env with random secrets
    env_src = (DEPLOY_DIR / ".env.example").read_text(encoding="utf-8")
    env = env_src
    env = env.replace(
        "AETHERKIN_KEY=CHANGE_ME_32_CHAR_RANDOM_STRING",
        f"AETHERKIN_KEY={secrets.token_urlsafe(32)}",
    )
    env = env.replace(
        "N8N_ENCRYPTION_KEY=CHANGE_ME_32_CHAR_RANDOM_STRING",
        f"N8N_ENCRYPTION_KEY={secrets.token_urlsafe(32)}",
    )
    env = env.replace(
        "N8N_PASSWORD=CHANGE_ME_STRONG_PASSWORD",
        f"N8N_PASSWORD={secrets.token_urlsafe(16)}",
    )
    # Apply client overrides
    for k, v in client_env_overrides.items():
        # Find "KEY=" and replace the value portion on that line
        lines = env.splitlines()
        for i, line in enumerate(lines):
            if line.startswith(f"{k}="):
                lines[i] = f"{k}={v}"
                break
        env = "\n".join(lines) + ("\n" if not env.endswith("\n") else "")
    (out_deploy_dir / ".env").write_text(env, encoding="utf-8")


def write_runbook(template: dict, workflows: list[str], out_dir: Path) -> None:
    client = template.get("client", {})
    name = client.get("name", "Client")
    sibling_list = "\n".join(
        f"- **{info.get('name')}** — {info.get('role', '')} "
        f"(provider: {info.get('preferred_provider', 'auto')}, "
        f"tier: {info.get('preferred_tier', 'balanced')})"
        for info in template.get("family", {}).values() if isinstance(info, dict)
    )
    wf_list = "\n".join(f"- `{w}`" for w in workflows) if workflows else "_(no workflows copied yet — TODOs in template)_"
    text = f"""# Runbook — {name}

Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}

## What's in this folder

```
{name}/
├── family.json              # The family roster — siblings, roles, model preferences
├── CLIENT_RUNBOOK.md        # This file
├── deploy/
│   ├── docker-compose.yaml  # AetherKin + n8n stack
│   ├── Dockerfile
│   └── .env                 # Secrets generated for this client
└── n8n-workflows/           # Workflow JSONs tailored to this business
```

## First boot

```bash
cd deploy
docker-compose up -d
```

Then:
- AetherKin gateway: http://localhost:7788
- n8n UI:            http://localhost:5678   (auth in .env)

## Import workflows

1. Log into n8n with credentials from `deploy/.env`
2. Workflows → Import from File
3. Pick each JSON from `../n8n-workflows/`
4. Before activating, open each and set credentials (CRM, email, Slack, etc.)

## Your family

{sibling_list}

## Your workflows

{wf_list}

## First-week tasks

- [ ] Confirm all three LLM provider keys are set in `deploy/.env` (or at least one)
- [ ] Activate every workflow with valid credentials
- [ ] Send a test message to each channel and confirm it reaches the right sibling
- [ ] Send a test crisis message (e.g., "I'm not safe") and confirm Guardian path fires
- [ ] Review the dashboard at http://localhost:7788 for sibling health
- [ ] Schedule the 30-day follow-up call

## Support

Nathan Ray Michel — AI Family Architect
AetherKin Solutions
nathanmichel@nvvisions.com
(your phone)

Emergencies (prod-down, crisis alert failing): text the number above with "URGENT - <client name>" in the first line.
"""
    (out_dir / "CLIENT_RUNBOOK.md").write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Deploy AetherKin + n8n to a client.")
    parser.add_argument("--template", required=True, help="Family template name (e.g., law-firm)")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--output", required=True, help="Output folder for this client's deploy bundle")
    parser.add_argument("--owner-email", default="", help="Owner email for alerts")
    parser.add_argument("--owner-slack", default="#aetherkin-alerts", help="Slack channel for alerts")
    args = parser.parse_args()

    template = load_template(args.template)
    template = customize_client_block(template, args.client)

    out_dir = Path(args.output).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # family.json
    family = build_family_json(template)
    (out_dir / "family.json").write_text(json.dumps(family, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # workflows
    copied = copy_workflows(template, out_dir / "n8n-workflows")

    # deploy stack
    env_overrides = {}
    if args.owner_email:
        env_overrides["OWNER_EMAIL"] = args.owner_email
    if args.owner_slack:
        env_overrides["OWNER_SLACK_CHANNEL"] = args.owner_slack
    tz = template.get("client", {}).get("timezone")
    if tz:
        env_overrides["TZ"] = tz
    copy_deploy(out_dir / "deploy", env_overrides)

    # runbook
    write_runbook(template, copied, out_dir)

    print()
    print(f"  Client bundle generated: {out_dir}")
    print(f"  Template:  {args.template}")
    print(f"  Family:    {len(family['siblings'])} siblings")
    print(f"  Workflows: {len(copied)} copied")
    print()
    print("  Next:")
    print(f"    1. Edit {out_dir}/deploy/.env — add LLM provider keys")
    print(f"    2. cd {out_dir}/deploy && docker-compose up -d")
    print(f"    3. Import workflows at http://localhost:5678")
    print(f"    4. Read CLIENT_RUNBOOK.md")
    print()


if __name__ == "__main__":
    main()
