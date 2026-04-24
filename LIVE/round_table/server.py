from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
from urllib.parse import urlparse
import webbrowser

import handoff_emitter
import router

# Sessions file lives next to this script — shared with fanout.py
SESSIONS_FILE = Path(__file__).resolve().parent / "sessions.json"


ROUND_ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{6}$")
AGENT_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")
RESULT_ROW_RE = re.compile(
    r"^\|\s*(?P<name>[A-Za-z0-9_-]+)\s*\|\s*(?P<exit>[^|]+?)\s*\|\s*(?P<duration>[0-9]+(?:\.[0-9]+)?)s\s*\|",
    re.MULTILINE,
)


@dataclass(frozen=True)
class AgentInfo:
    name: str
    emoji: str
    team: str | None = None


@dataclass(frozen=True)
class AppConfig:
    port: int
    fanout_script: Path
    agents_config: Path
    rounds_dir: Path
    agents: tuple[AgentInfo, ...]


class ConfigError(ValueError):
    def __init__(self, field: str, reason: str) -> None:
        super().__init__(f"{field}: {reason}")
        self.field = field
        self.reason = reason


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--port", type=int)
    parser.add_argument("--no-open", action="store_true")
    return parser


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def read_json_file(path: Path, field: str) -> object:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(field, f"file not found: {path}") from exc
    except OSError as exc:
        raise ConfigError(field, f"unable to read file: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError(field, f"invalid JSON: {exc.msg}") from exc


def validate_port(value: object, field: str) -> int:
    if value is None:
        return 8080
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigError(field, "must be an integer")
    if not 1 <= value <= 65535:
        raise ConfigError(field, "must be between 1 and 65535")
    return value


def validate_agent_config(path: Path) -> tuple[AgentInfo, ...]:
    raw = read_json_file(path, "agents_config")
    if not isinstance(raw, dict):
        raise ConfigError("agents_config", "top-level JSON value must be an object")
    agents_value = raw.get("agents")
    if not isinstance(agents_value, list):
        raise ConfigError("agents_config", "must contain an 'agents' array")

    agents: list[AgentInfo] = []
    seen_names: set[str] = set()
    for index, item in enumerate(agents_value):
        field = f"agents_config.agents[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(field, "must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise ConfigError(f"{field}.name", "required and must be a non-empty string")
        if not AGENT_NAME_RE.fullmatch(name):
            raise ConfigError(f"{field}.name", "must contain only letters, digits, '_' or '-'")
        if name in seen_names:
            raise ConfigError(f"{field}.name", f"duplicate name '{name}'")
        seen_names.add(name)

        prompt_file = item.get("system_prompt_file")
        if not isinstance(prompt_file, str) or not prompt_file:
            raise ConfigError(f"{field}.system_prompt_file", "required and must be a non-empty string")

        emoji = item.get("emoji", "")
        if emoji is None:
            emoji = ""
        if not isinstance(emoji, str):
            raise ConfigError(f"{field}.emoji", "must be a string when provided")
        team = item.get("team")
        if team is not None and not isinstance(team, str):
            raise ConfigError(f"{field}.team", "must be a string when provided")
        agents.append(AgentInfo(name=name, emoji=emoji, team=team))
    return tuple(agents)


def load_app_config(config_path_arg: str, port_override: int | None) -> AppConfig:
    config_path = Path(config_path_arg).resolve()
    raw = read_json_file(config_path, "config")
    if not isinstance(raw, dict):
        raise ConfigError("config", "top-level JSON value must be an object")

    port = validate_port(raw.get("port"), "port")
    if port_override is not None:
        port = validate_port(port_override, "port")

    fanout_value = raw.get("fanout_script")
    if not isinstance(fanout_value, str) or not fanout_value:
        raise ConfigError("fanout_script", "required and must be a non-empty string")
    fanout_script = Path(fanout_value).resolve()
    if not fanout_script.is_file():
        raise ConfigError("fanout_script", f"file not found: {fanout_script}")

    agents_value = raw.get("agents_config")
    if not isinstance(agents_value, str) or not agents_value:
        raise ConfigError("agents_config", "required and must be a non-empty string")
    agents_config = Path(agents_value).resolve()
    if not agents_config.is_file():
        raise ConfigError("agents_config", f"file not found: {agents_config}")
    agents = validate_agent_config(agents_config)

    rounds_value = raw.get("rounds_dir")
    if not isinstance(rounds_value, str) or not rounds_value:
        raise ConfigError("rounds_dir", "required and must be a non-empty string")
    rounds_dir = Path(rounds_value).resolve()
    if not rounds_dir.is_absolute():
        raise ConfigError("rounds_dir", "must be an absolute path")
    try:
        rounds_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError("rounds_dir", f"unable to create directory: {exc}") from exc

    return AppConfig(
        port=port,
        fanout_script=fanout_script,
        agents_config=agents_config,
        rounds_dir=rounds_dir,
        agents=agents,
    )


def json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def parse_json_body(handler: BaseHTTPRequestHandler) -> object:
    length_header = handler.headers.get("Content-Length")
    if length_header is None:
        raise ValueError("missing Content-Length header")
    try:
        length = int(length_header)
    except ValueError as exc:
        raise ValueError("invalid Content-Length header") from exc
    body = handler.rfile.read(length)
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("request body must be valid JSON") from exc


def validate_ask_body(payload: object, config: AppConfig) -> tuple[str, list[str], list[str]]:
    if not isinstance(payload, dict):
        raise ValueError("request body must be an object")

    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question is required and must be a non-empty string")
    question = question.strip()

    available = {agent.name for agent in config.agents}
    only_value = payload.get("only")
    selected_names = [agent.name for agent in config.agents]
    argv_extra: list[str] = []
    if only_value is not None:
        if not isinstance(only_value, list) or not only_value:
            raise ValueError("only must be a non-empty array of agent names when provided")
        names: list[str] = []
        seen: set[str] = set()
        for item in only_value:
            if not isinstance(item, str) or not AGENT_NAME_RE.fullmatch(item):
                raise ValueError("only must contain valid agent names")
            if item not in available:
                raise ValueError(f"unknown agent name: {item}")
            if item not in seen:
                seen.add(item)
                names.append(item)
        selected_names = names
        argv_extra.extend(["--only", ",".join(names)])

    timeout_value = payload.get("timeout")
    if timeout_value is not None:
        if not isinstance(timeout_value, (int, float)) or isinstance(timeout_value, bool):
            raise ValueError("timeout must be a number when provided")
        if timeout_value <= 0:
            raise ValueError("timeout must be greater than 0")
        argv_extra.extend(["--timeout", str(timeout_value)])

    concurrency_value = payload.get("concurrency")
    if concurrency_value is not None:
        if not isinstance(concurrency_value, int) or isinstance(concurrency_value, bool):
            raise ValueError("concurrency must be an integer when provided")
        if concurrency_value < 1:
            raise ValueError("concurrency must be at least 1")
        argv_extra.extend(["--concurrency", str(concurrency_value)])

    return question, selected_names, argv_extra


def round_dir_path(config: AppConfig, round_id: str) -> Path:
    if ".." in round_id or not ROUND_ID_RE.fullmatch(round_id):
        raise ValueError("invalid round id")
    return config.rounds_dir / round_id


def agent_file_path(config: AppConfig, round_id: str, name: str) -> Path:
    if ".." in name or "/" in name or "\\" in name or not AGENT_NAME_RE.fullmatch(name):
        raise ValueError("invalid agent name")
    return round_dir_path(config, round_id) / f"{name}.md"


def read_text_if_exists(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def parse_question_markdown(content: str) -> tuple[str | None, str | None, dict[str, dict[str, int | float | None]]]:
    started_match = re.search(r"^\*\*Started:\*\*\s+(.+)$", content, re.MULTILINE)
    completed_match = re.search(r"^\*\*Completed:\*\*\s+(.+)$", content, re.MULTILINE)
    started = started_match.group(1).strip() if started_match else None
    completed = completed_match.group(1).strip() if completed_match else None

    result_map: dict[str, dict[str, int | float | None]] = {}
    for match in RESULT_ROW_RE.finditer(content):
        raw_exit = match.group("exit").strip()
        exit_code: int | float | None
        if raw_exit.lstrip("-").isdigit():
            exit_code = int(raw_exit)
        else:
            exit_code = None
        result_map[match.group("name")] = {
            "exit_code": exit_code,
            "duration": float(match.group("duration")),
        }
    return started, completed, result_map


def build_round_state(config: AppConfig, round_id: str) -> dict[str, object]:
    round_dir = round_dir_path(config, round_id)
    if not round_dir.is_dir():
        raise FileNotFoundError

    question_path = round_dir / "_question.md"
    question_content = read_text_if_exists(question_path) or ""
    started, completed, results = parse_question_markdown(question_content)

    agent_states: dict[str, dict[str, object]] = {}
    for agent in config.agents:
        agent_exists = (round_dir / f"{agent.name}.md").is_file()
        parsed = results.get(agent.name, {})
        agent_states[agent.name] = {
            "status": "done" if agent_exists else "pending",
            "exit_code": parsed.get("exit_code"),
            "duration": parsed.get("duration"),
        }

    return {
        "round_id": round_id,
        "started": started,
        "completed": completed,
        "agents": agent_states,
    }


def discover_round_id(
    rounds_dir: Path,
    existing: set[str],
    spawn_time: float,
    process: subprocess.Popen | None = None,
    timeout_seconds: float = 5.0,
) -> str | None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        candidates: list[tuple[float, str]] = []
        for path in rounds_dir.iterdir():
            if not path.is_dir():
                continue
            if path.name in existing:
                continue
            if not ROUND_ID_RE.fullmatch(path.name):
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if mtime >= spawn_time - 0.5:
                candidates.append((mtime, path.name))
        if candidates:
            candidates.sort()
            return candidates[-1][1]
        if process is not None and process.poll() is not None:
            return None
        time.sleep(0.1)
    return None


def spawn_completion_watcher(
    config: AppConfig,
    round_id: str,
    selected_names: list[str],
    poll_interval_seconds: float = 1.0,
    timeout_seconds: float = 600.0,
) -> None:
    """Background thread: poll _question.md for the '## Results' marker
    fanout's append_summary() writes when all agents finish, then fire
    handoff_emitter.emit_complete once with per-agent results.

    Daemon thread — won't block server shutdown. Errors are caught and
    logged inside the worker so a watcher crash never affects the server.
    """

    def _watch() -> None:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            try:
                payload = build_round_state(config, round_id)
                if payload.get("completed"):
                    agent_states = payload.get("agents") or {}
                    results = []
                    for name in selected_names:
                        state = agent_states.get(name) or {}
                        results.append({
                            "name": name,
                            "exit_code": state.get("exit_code"),
                            "duration": state.get("duration"),
                            "status": state.get("status"),
                        })
                    handoff_emitter.emit_complete(round_id, results)
                    return
            except FileNotFoundError:
                pass
            except Exception as exc:
                print(
                    f"[watcher] round {round_id} state poll error: {exc}",
                    file=sys.stderr,
                )
            time.sleep(poll_interval_seconds)
        # Timed out before completion — emit anyway with whatever state we have
        try:
            payload = build_round_state(config, round_id)
            agent_states = payload.get("agents") or {}
            results = [
                {
                    "name": name,
                    "exit_code": (agent_states.get(name) or {}).get("exit_code"),
                    "duration": (agent_states.get(name) or {}).get("duration"),
                    "status": (agent_states.get(name) or {}).get("status"),
                    "watcher_timeout": True,
                }
                for name in selected_names
            ]
            handoff_emitter.emit_complete(round_id, results)
        except Exception as exc:
            print(
                f"[watcher] round {round_id} timeout-emit failed: {exc}",
                file=sys.stderr,
            )

    thread = threading.Thread(target=_watch, name=f"round_watcher_{round_id}", daemon=True)
    thread.start()


def make_handler(config: AppConfig) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "fanout-ui/1.0"

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self.serve_index()
                return
            if parsed.path == "/api/agents":
                self.serve_agents()
                return
            if parsed.path == "/api/sessions":
                self.serve_sessions()
                return
            if parsed.path == "/api/rounds" or ".." in parsed.path:
                self.send_json(400, {"error": "invalid path"})
                return

            state_match = re.fullmatch(r"/api/rounds/([^/]+)/state", parsed.path)
            if state_match:
                self.serve_round_state(state_match.group(1))
                return

            question_match = re.fullmatch(r"/api/rounds/([^/]+)/question", parsed.path)
            if question_match:
                self.serve_question(question_match.group(1))
                return

            # SSE streaming endpoint
            stream_match = re.fullmatch(r"/api/rounds/([^/]+)/agent/([^/]+)/stream", parsed.path)
            if stream_match:
                self.stream_agent(stream_match.group(1), stream_match.group(2))
                return

            agent_match = re.fullmatch(r"/api/rounds/([^/]+)/agent/([^/]+)", parsed.path)
            if agent_match:
                self.serve_agent(agent_match.group(1), agent_match.group(2))
                return

            self.send_json(404, {"error": "not found"})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/api/ask":
                self.handle_ask()
                return
            self.send_json(404, {"error": "not found"})

        def serve_index(self) -> None:
            index_path = Path(__file__).resolve().parent / "index.html"
            try:
                body = index_path.read_bytes()
            except OSError:
                self.send_json(500, {"error": "index.html unavailable"})
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def serve_agents(self) -> None:
            self.send_json(
                200,
                {"agents": [{"name": agent.name, "emoji": agent.emoji} for agent in config.agents]},
            )

        def serve_sessions(self) -> None:
            """Return current warm session IDs (for debug / status display)."""
            try:
                data = json.loads(SESSIONS_FILE.read_text(encoding="utf-8")) if SESSIONS_FILE.is_file() else {}
            except Exception:
                data = {}
            warm = {name: sid[:8] + "…" for name, sid in data.items() if isinstance(sid, str)}
            self.send_json(200, {"warm": warm, "count": len(warm)})

        def stream_agent(self, round_id: str, name: str) -> None:
            """SSE endpoint — streams agent file content as it is written.
            Client: EventSource('/api/rounds/ROUND_ID/agent/NAME/stream')
            Events: {"text": "..."} chunks, then {"done": true} on completion.
            """
            try:
                path = agent_file_path(config, round_id, name)
            except ValueError as exc:
                self.send_json(400, {"error": str(exc)})
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            offset = 0
            idle_ticks = 0
            max_idle = 400  # 400 × 250ms = 100s timeout

            try:
                while idle_ticks < max_idle:
                    # Send any new bytes written to the file
                    if path.is_file():
                        data = path.read_bytes()
                        if len(data) > offset:
                            chunk = data[offset:].decode("utf-8", errors="replace")
                            offset = len(data)
                            idle_ticks = 0
                            payload = json.dumps({"text": chunk}, ensure_ascii=False)
                            self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                            self.wfile.flush()

                    # Check if round is complete for this agent
                    try:
                        state = build_round_state(config, round_id)
                        agent_st = state.get("agents", {}).get(name, {})
                        if state.get("completed") and agent_st.get("status") == "done":
                            self.wfile.write(b'data: {"done": true}\n\n')
                            self.wfile.flush()
                            break
                    except (FileNotFoundError, ValueError):
                        break

                    time.sleep(0.25)
                    idle_ticks += 1

            except (BrokenPipeError, ConnectionResetError, OSError):
                pass

        def handle_ask(self) -> None:
            try:
                payload = parse_json_body(self)
                question, selected_names, argv_extra = validate_ask_body(payload, config)
            except ValueError as exc:
                self.send_json(400, {"error": str(exc)})
                return

            # Router decides targets when caller didn't pass an explicit 'only'.
            # Explicit 'only' from the API still wins (escape hatch for tooling).
            caller_set_only = isinstance(payload, dict) and payload.get("only") is not None
            if not caller_set_only:
                agent_dicts = [
                    {"name": a.name, "team": a.team} for a in config.agents
                ]
                selected_names = router.detect_targets(question, agent_dicts)
                argv_extra = ["--only", ",".join(selected_names)] + argv_extra

            before = {
                path.name
                for path in config.rounds_dir.iterdir()
                if path.is_dir() and ROUND_ID_RE.fullmatch(path.name)
            }
            spawn_time = time.time()
            argv = [
                sys.executable,
                str(config.fanout_script),
                question,
                "--config",
                str(config.agents_config),
                "--no-open",
                "--out",
                str(config.rounds_dir),
                *argv_extra,
            ]
            env = os.environ.copy()
            # Pass sessions file so fanout can do warm resume
            argv.extend(["--sessions-file", str(SESSIONS_FILE)])
            try:
                process = subprocess.Popen(
                    argv,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=env,
                )
            except OSError as exc:
                self.send_json(502, {"error": f"failed to start fanout: {exc}"})
                return

            round_id = discover_round_id(config.rounds_dir, before, spawn_time, process)
            if round_id is None:
                if process.poll() is not None and process.returncode != 0:
                    try:
                        stderr_tail = process.stderr.read() if process.stderr else ""
                    except Exception:
                        stderr_tail = "<stderr unavailable>"
                    self.send_json(
                        502,
                        {
                            "error": f"fanout exited {process.returncode}",
                            "stderr": (stderr_tail or "").strip()[:800],
                            "argv": argv,
                        },
                    )
                else:
                    self.send_json(502, {"error": "fanout did not create a round folder in time"})
                return

            # D4: sync emit on dispatch — guarantees the audit row before we
            # respond. Error-isolated inside handoff_emitter; never raises.
            handoff_emitter.emit_dispatch(round_id, question, selected_names)

            # D4: async emit on completion — background watcher polls the
            # round folder for completion and fires emit_complete once.
            spawn_completion_watcher(config, round_id, selected_names)

            self.send_json(
                200,
                {
                    "round_id": round_id,
                    "agents": selected_names,
                    "rounds_dir": str(config.rounds_dir),
                    "routed_by": "explicit" if caller_set_only else "router",
                },
            )

        def serve_round_state(self, round_id: str) -> None:
            try:
                payload = build_round_state(config, round_id)
            except ValueError as exc:
                self.send_json(400, {"error": str(exc)})
                return
            except FileNotFoundError:
                self.send_json(404, {"error": "round not found"})
                return
            self.send_json(200, payload)

        def serve_agent(self, round_id: str, name: str) -> None:
            try:
                path = agent_file_path(config, round_id, name)
            except ValueError as exc:
                self.send_json(400, {"error": str(exc)})
                return
            if not path.is_file():
                self.send_json(404, {"error": "agent output not found"})
                return
            self.send_markdown(path)

        def serve_question(self, round_id: str) -> None:
            try:
                path = round_dir_path(config, round_id) / "_question.md"
            except ValueError as exc:
                self.send_json(400, {"error": str(exc)})
                return
            if not path.is_file():
                self.send_json(404, {"error": "question file not found"})
                return
            self.send_markdown(path)

        def send_markdown(self, path: Path) -> None:
            try:
                body = path.read_bytes()
            except OSError as exc:
                self.send_json(500, {"error": f"unable to read file: {exc}"})
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, status: int, payload: object) -> None:
            body = json_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    return Handler


def run_server(config: AppConfig, open_browser: bool) -> int:
    handler = make_handler(config)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", config.port), handler)
    except OSError as exc:
        print(f"ERROR: port: unable to bind 127.0.0.1:{config.port}: {exc}", file=sys.stderr)
        return 2

    url = f"http://127.0.0.1:{config.port}"
    print(f"Listening on {url}")
    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main() -> int:
    configure_stdio()
    args = build_parser().parse_args()
    try:
        config = load_app_config(args.config, args.port)
    except ConfigError as exc:
        print(f"ERROR: {exc.field}: {exc.reason}", file=sys.stderr)
        return 2
    return run_server(config, open_browser=not args.no_open)


if __name__ == "__main__":
    raise SystemExit(main())
