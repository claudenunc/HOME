# fanout

One question → many Claude configurations in parallel → one folder of answers.

## Usage

python fanout.py "<question>" --config <agents.json>

## Flags

- `--config PATH` (required) — JSON file describing agent configurations.
- `--only NAME,NAME` — subset of agents by name.
- `--timeout SECONDS` — per-agent timeout (default 300).
- `--concurrency N` — maximum concurrent Claude launches (default 2).
- `--no-open` — skip auto-open of the output folder.
- `--out DIR` — output root (default `./rounds`).

## Config format

See `agents.example.json`. Each agent has:
- `name` (required, unique, filename-safe)
- `emoji` (optional)
- `system_prompt_file` (required, path relative to the config file)

## Output

Each run creates `<out>/<YYYY-MM-DD_HHMMSS>/` containing:
- `_question.md` — the question plus a results table
- `<name>.md` — one file per agent with the answer

## Requirements

- Python 3.11+
- `claude` CLI on PATH (https://docs.anthropic.com/en/docs/claude-code/quickstart)
- An Anthropic account / subscription that the `claude` CLI is logged into
