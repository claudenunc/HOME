# fanout-ui

Local web UI that wraps fanout.py. One textbox → parallel Claude calls → live-updating grid of answers.

## Usage

python server.py --config config.example.json

Opens http://127.0.0.1:8080 in your browser.

## Configuration

See `config.example.json`:
- `port` (optional, default 8080)
- `fanout_script` (required, path to fanout.py)
- `agents_config` (required, path to the agents JSON fanout reads)
- `rounds_dir` (required, absolute path where fanout writes round folders)

## Flags

- `--config PATH` (required)
- `--port N` — override port from config
- `--no-open` — don't auto-open the browser

## Requirements

- Python 3.11+
- `fanout.py` already built and working (see ../build task 1/)

## Security

Binds to 127.0.0.1 only. Not reachable from other machines on the LAN.
