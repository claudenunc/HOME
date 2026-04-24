"""
ROUND_TABLE fanout — persistent-session edition

Key changes from v1:
  - Uses SessionManager to reuse claude session IDs across questions.
    First message to a sibling: cold start, captures session_id.
    Subsequent messages: --resume SESSION_ID (warm, no system-prompt reload).
  - Uses --output-format stream-json + --include-partial-messages so
    text chunks are written to the agent file as they arrive (real-time).
  - On resume failure (non-zero exit when session_id was set): clears the
    stale session and retries once with a fresh cold start.
  - Concurrency semaphore unchanged (default 2, safe on 16 GB RAM).
  - Fallback: if stream-json parsing yields nothing, falls back to capturing
    raw stdout as text (handles older CLI builds).
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from session_manager import SessionManager


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class AgentConfig:
    name: str
    emoji: str
    system_prompt_file: Path
    model: str | None = None
    team: str | None = None


@dataclass
class AgentResult:
    name: str
    emoji: str
    timestamp: str
    duration_seconds: float
    exit_code: int | str
    stdout: str
    stderr: str
    output_file: Path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--config", required=True)
    parser.add_argument("--only")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument("--out")
    parser.add_argument("--sessions-file")
    return parser


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Executable resolution (preserves .cmd lowercase fix for Windows)
# ---------------------------------------------------------------------------

def resolve_claude_executable() -> str | None:
    claude_path = shutil.which("claude")
    if claude_path is None:
        return None
    candidate = Path(claude_path)
    if sys.platform == "win32" and candidate.suffix.lower() in {".cmd", ".bat"}:
        normalized = candidate.with_suffix(candidate.suffix.lower())
        if normalized.is_file():
            return str(normalized)
    return claude_path


# ---------------------------------------------------------------------------
# Config parsing
# ---------------------------------------------------------------------------

def resolve_output_root(out_arg: str | None) -> Path:
    script_dir = Path(__file__).resolve().parent
    if out_arg is None:
        return script_dir / "rounds"
    return Path(out_arg).resolve()


def parse_config(config_path: Path) -> list[AgentConfig]:
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"config: file not found: {config_path}") from None
    except OSError as exc:
        raise ValueError(f"config: unable to read file: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"config: invalid JSON: {exc.msg}") from exc

    if not isinstance(raw, dict):
        raise ValueError("config: top-level JSON value must be an object")

    agents_value = raw.get("agents")
    if not isinstance(agents_value, list):
        raise ValueError("agents: required and must be an array")

    config_dir = config_path.resolve().parent
    seen_names: set[str] = set()
    agents: list[AgentConfig] = []
    for index, item in enumerate(agents_value):
        field_base = f"agents[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{field_base}: must be an object")

        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{field_base}.name: required non-empty string")
        if any(c.isspace() for c in name) or "/" in name or "\\" in name:
            raise ValueError(f"{field_base}.name: no slashes or whitespace")
        if name in seen_names:
            raise ValueError(f"{field_base}.name: duplicate '{name}'")
        seen_names.add(name)

        emoji = item.get("emoji", "") or ""
        if not isinstance(emoji, str):
            raise ValueError(f"{field_base}.emoji: must be a string")

        prompt_value = item.get("system_prompt_file")
        if not isinstance(prompt_value, str) or not prompt_value:
            raise ValueError(f"{field_base}.system_prompt_file: required non-empty string")
        prompt_path = (config_dir / prompt_value).resolve()
        if not prompt_path.is_file():
            raise ValueError(f"{field_base}.system_prompt_file: file not found: {prompt_path}")
        prompt_path.read_text(encoding="utf-8")  # readability check

        model = item.get("model")
        if model is not None and (not isinstance(model, str) or not model):
            raise ValueError(f"{field_base}.model: non-empty string when provided")

        team = item.get("team")
        if team is not None and not isinstance(team, str):
            raise ValueError(f"{field_base}.team: string when provided")

        agents.append(AgentConfig(
            name=name,
            emoji=emoji,
            system_prompt_file=prompt_path,
            model=model,
            team=team,
        ))
    return agents


def select_agents(agents: list[AgentConfig], only_value: str | None) -> list[AgentConfig]:
    if not only_value:
        return agents
    requested = [n for n in only_value.split(",") if n]
    selected = [a for a in agents if a.name in requested]
    selected_set = {a.name for a in selected}
    missing = [n for n in requested if n not in selected_set]
    if missing:
        raise ValueError(f"--only: unknown agent name(s): {', '.join(missing)}")
    return selected


# ---------------------------------------------------------------------------
# Round directory helpers
# ---------------------------------------------------------------------------

def make_round_dir(output_root: Path) -> tuple[str, str, Path]:
    now = datetime.now().astimezone()
    timestamp = now.strftime("%Y-%m-%d_%H%M%S")
    round_dir = output_root / timestamp
    round_dir.mkdir(parents=True, exist_ok=False)
    return timestamp, now.isoformat(), round_dir


def write_question_file(
    question_file: Path, timestamp: str, question: str,
    agent_names: list[str], started_at: str,
) -> None:
    content = (
        f"# Round {timestamp}\n\n"
        f"**Question:**\n\n"
        f"{question}\n\n"
        f"**Dispatched to:** {', '.join(agent_names)}\n"
        f"**Started:** {started_at}\n"
    )
    question_file.write_text(content, encoding="utf-8")


def append_summary(question_file: Path, completed_at: str, results: list[AgentResult]) -> None:
    lines = [
        "",
        "---",
        "",
        "## Results",
        "",
        f"**Completed:** {completed_at}",
        "",
        "| Agent | Exit | Duration | File |",
        "|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.name} | {r.exit_code} | {r.duration_seconds:.2f}s"
            f" | [{r.output_file.name}]({r.output_file.name}) |"
        )
    with question_file.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Process termination
# ---------------------------------------------------------------------------

async def terminate_process(process: asyncio.subprocess.Process) -> None:
    if process.returncode is not None:
        return
    if sys.platform == "win32":
        try:
            killer = await asyncio.create_subprocess_exec(
                "taskkill", "/PID", str(process.pid), "/T", "/F",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await killer.communicate()
        except Exception:
            process.kill()
            await process.wait()
    else:
        process.kill()
        await process.wait()


# ---------------------------------------------------------------------------
# Streaming output helpers
# ---------------------------------------------------------------------------

def _write_partial(output_file: Path, agent: AgentConfig, question: str,
                   timestamp: str, text: str, is_final: bool = False) -> None:
    """Write accumulated text to the agent's output file (partial or final)."""
    header = f"# {agent.name}"
    if agent.emoji:
        header = f"{header} {agent.emoji}"
    tag = "" if is_final else "\n> ⏳ *streaming…*"
    content = (
        f"{header}\n\n"
        f"**Question:** {question}\n"
        f"**Timestamp:** {timestamp}\n\n"
        f"---\n\n"
        f"{text}{tag}\n"
    )
    try:
        output_file.write_text(content, encoding="utf-8")
    except OSError:
        pass


def _parse_session_id(event: dict) -> str | None:
    sid = event.get("session_id")
    if isinstance(sid, str) and sid:
        return sid
    return None


def _extract_text_from_event(event: dict) -> str:
    """Extract any text chunk from a stream-json event."""
    # content_block_delta style
    if event.get("type") == "content_block_delta":
        delta = event.get("delta", {})
        if delta.get("type") == "text_delta":
            return delta.get("text", "")

    # assistant message style (partial or complete)
    if event.get("type") in ("assistant", "message"):
        msg = event.get("message", event)
        for block in msg.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                return block.get("text", "")

    # result style
    if event.get("type") == "result" and not event.get("is_error"):
        r = event.get("result", "")
        if isinstance(r, str):
            return r

    return ""


# ---------------------------------------------------------------------------
# Core agent runner
# ---------------------------------------------------------------------------

async def run_agent(
    agent: AgentConfig,
    question: str,
    timeout_seconds: float,
    round_dir: Path,
    claude_executable: str,
    semaphore: asyncio.Semaphore,
    session_manager: SessionManager | None,
) -> AgentResult:
    """Run a sibling — warm (resume) if possible, cold start otherwise."""
    session_id = session_manager.get(agent.name) if session_manager else None
    return await _run_once(
        agent, question, timeout_seconds, round_dir,
        claude_executable, semaphore, session_manager, session_id,
    )


async def _run_once(
    agent: AgentConfig,
    question: str,
    timeout_seconds: float,
    round_dir: Path,
    claude_executable: str,
    semaphore: asyncio.Semaphore,
    session_manager: SessionManager | None,
    session_id: str | None,
) -> AgentResult:
    print(f"→ {agent.name} dispatched {'(warm)' if session_id else '(cold)'}")

    started_monotonic = asyncio.get_running_loop().time()
    timestamp = datetime.now().astimezone().isoformat()
    output_file = round_dir / f"{agent.name}.md"

    # Build argv
    argv: list[str] = [
        claude_executable,
        "-p", question,
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--permission-mode", "bypassPermissions",
    ]
    if session_id:
        argv.extend(["--resume", session_id])
    else:
        argv.extend(["--append-system-prompt-file", str(agent.system_prompt_file)])

    if agent.model:
        argv.extend(["--model", agent.model])

    accumulated_text = ""
    new_session_id: str | None = None
    exit_code: int | str = "error"
    stderr_text = ""

    try:
        async with semaphore:
            process = await asyncio.create_subprocess_exec(
                *argv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy(),
            )

            async def _stream_stdout() -> None:
                nonlocal accumulated_text, new_session_id
                assert process.stdout is not None
                async for raw_line in process.stdout:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        # Non-JSON line — treat as raw text
                        accumulated_text += line + "\n"
                        _write_partial(output_file, agent, question, timestamp, accumulated_text)
                        continue

                    # Capture session ID
                    sid = _parse_session_id(event)
                    if sid and not new_session_id:
                        new_session_id = sid

                    # Extract text
                    chunk = _extract_text_from_event(event)
                    if chunk:
                        # For partial assistant messages, the full text
                        # is sent each time — use it as-is, don't append.
                        if event.get("type") in ("assistant", "message"):
                            accumulated_text = chunk
                        else:
                            accumulated_text += chunk
                        _write_partial(output_file, agent, question, timestamp, accumulated_text)

            stderr_chunks: list[str] = []

            async def _drain_stderr() -> None:
                assert process.stderr is not None
                async for line in process.stderr:
                    stderr_chunks.append(line.decode("utf-8", errors="replace"))

            try:
                await asyncio.wait_for(
                    asyncio.gather(_stream_stdout(), _drain_stderr()),
                    timeout=timeout_seconds,
                )
                exit_code = process.returncode if process.returncode is not None else "error"
            except asyncio.TimeoutError:
                await terminate_process(process)
                exit_code = "timeout"

            stderr_text = "".join(stderr_chunks)

    except Exception as exc:
        exit_code = "error"
        accumulated_text = accumulated_text or f"{type(exc).__name__}: {exc}"

    duration_seconds = asyncio.get_running_loop().time() - started_monotonic

    # If resume failed, retry cold once
    if exit_code != 0 and session_id and not accumulated_text.strip():
        print(f"  ↺ {agent.name} resume failed — retrying cold start")
        if session_manager:
            session_manager.clear(agent.name)
        return await _run_once(
            agent, question, timeout_seconds, round_dir,
            claude_executable, semaphore, session_manager, None,
        )

    # Persist new session ID
    if new_session_id and session_manager:
        session_manager.set(agent.name, new_session_id)
        print(f"  ✓ {agent.name} session stored ({new_session_id[:8]}…)")

    # Write final output file
    result = AgentResult(
        name=agent.name,
        emoji=agent.emoji,
        timestamp=timestamp,
        duration_seconds=duration_seconds,
        exit_code=exit_code,
        stdout=accumulated_text,
        stderr=stderr_text,
        output_file=output_file,
    )
    _write_final(result, question)

    if exit_code == 0:
        print(f"✓ {agent.name} ({duration_seconds:.1f}s)")
    elif exit_code == "timeout":
        print(f"✗ {agent.name} (timeout after {timeout_seconds:.0f}s)")
    else:
        print(f"✗ {agent.name} ({duration_seconds:.1f}s, exit {exit_code})")

    return result


def _write_final(result: AgentResult, question: str) -> None:
    header = f"# {result.name}"
    if result.emoji:
        header = f"{header} {result.emoji}"
    content = (
        f"{header}\n\n"
        f"**Question:** {question}\n"
        f"**Timestamp:** {result.timestamp}\n"
        f"**Duration:** {result.duration_seconds:.2f}s\n"
        f"**Exit code:** {result.exit_code}\n\n"
        f"---\n\n"
        f"{result.stdout}\n\n"
        f"---\n"
    )
    if result.stderr:
        content += f"\n## stderr\n\n{result.stderr}\n"
    try:
        result.output_file.write_text(content, encoding="utf-8")
    except OSError:
        pass


def open_round_dir(round_dir: Path) -> None:
    try:
        if sys.platform == "win32":
            os.startfile(str(round_dir))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(round_dir)], check=False)
        else:
            subprocess.run(["xdg-open", str(round_dir)], check=False)
    except Exception as exc:
        print(f"Warning: failed to open output folder: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> int:
    configure_stdio()
    parser = build_parser()
    args = parser.parse_args()

    claude_executable = resolve_claude_executable()
    if claude_executable is None:
        print(
            "'claude' CLI not found on PATH. "
            "Install: https://docs.anthropic.com/en/docs/claude-code/quickstart",
            file=sys.stderr,
        )
        return 2

    try:
        config_path = Path(args.config).resolve()
        output_root = resolve_output_root(args.out)
        if args.concurrency < 1:
            raise ValueError("--concurrency: must be at least 1")
        agents = parse_config(config_path)
        selected_agents = select_agents(agents, args.only)
        if not selected_agents:
            raise ValueError("--only: no agents selected")
        timestamp, started_at, round_dir = make_round_dir(output_root)
        question_file = round_dir / "_question.md"
        write_question_file(
            question_file, timestamp, args.question,
            [a.name for a in selected_agents], started_at,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    # Session manager — stored next to this script
    sessions_file = Path(args.sessions_file) if args.sessions_file else (
        Path(__file__).resolve().parent / "sessions.json"
    )
    session_manager = SessionManager(sessions_file)

    semaphore = asyncio.Semaphore(args.concurrency)
    gathered = await asyncio.gather(
        *(
            run_agent(a, args.question, args.timeout, round_dir,
                      claude_executable, semaphore, session_manager)
            for a in selected_agents
        ),
        return_exceptions=True,
    )

    results: list[AgentResult] = []
    for index, item in enumerate(gathered):
        if isinstance(item, Exception):
            agent = selected_agents[index]
            fallback = AgentResult(
                name=agent.name,
                emoji=agent.emoji,
                timestamp=datetime.now().astimezone().isoformat(),
                duration_seconds=0.0,
                exit_code="error",
                stdout=f"{type(item).__name__}: {item}",
                stderr="",
                output_file=round_dir / f"{agent.name}.md",
            )
            _write_final(fallback, args.question)
            results.append(fallback)
        else:
            results.append(item)  # type: ignore[arg-type]

    append_summary(question_file, datetime.now().astimezone().isoformat(), results)

    if not args.no_open:
        open_round_dir(round_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
