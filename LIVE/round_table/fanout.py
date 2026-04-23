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


@dataclass
class AgentConfig:
    name: str
    emoji: str
    system_prompt_file: Path


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--config", required=True)
    parser.add_argument("--only")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument("--out")
    return parser


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


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
            raise ValueError(f"{field_base}.name: required and must be a non-empty string")
        if any(character.isspace() for character in name) or "/" in name or "\\" in name:
            raise ValueError(f"{field_base}.name: must not contain slashes or whitespace")
        if name in seen_names:
            raise ValueError(f"{field_base}.name: duplicate name '{name}'")
        seen_names.add(name)

        emoji = item.get("emoji", "")
        if emoji is None:
            emoji = ""
        if not isinstance(emoji, str):
            raise ValueError(f"{field_base}.emoji: must be a string when provided")

        prompt_value = item.get("system_prompt_file")
        if not isinstance(prompt_value, str) or not prompt_value:
            raise ValueError(f"{field_base}.system_prompt_file: required and must be a non-empty string")
        prompt_path = (config_dir / prompt_value).resolve()
        if not prompt_path.is_file():
            raise ValueError(f"{field_base}.system_prompt_file: file not found: {prompt_path}")
        try:
            prompt_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"{field_base}.system_prompt_file: unreadable file: {exc}") from exc

        agents.append(AgentConfig(name=name, emoji=emoji, system_prompt_file=prompt_path))
    return agents


def select_agents(agents: list[AgentConfig], only_value: str | None) -> list[AgentConfig]:
    if not only_value:
        return agents
    requested_names = [name for name in only_value.split(",") if name]
    selected = [agent for agent in agents if agent.name in requested_names]
    selected_names = {agent.name for agent in selected}
    missing = [name for name in requested_names if name not in selected_names]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"--only: unknown agent name(s): {missing_text}")
    return selected


def make_round_dir(output_root: Path) -> tuple[str, str, Path]:
    now = datetime.now().astimezone()
    timestamp = now.strftime("%Y-%m-%d_%H%M%S")
    round_dir = output_root / timestamp
    round_dir.mkdir(parents=True, exist_ok=False)
    return timestamp, now.isoformat(), round_dir


def write_question_file(question_file: Path, timestamp: str, question: str, agent_names: list[str], started_at: str) -> None:
    content = (
        f"# Round {timestamp}\n\n"
        f"**Question:**\n\n"
        f"{question}\n\n"
        f"**Dispatched to:** {', '.join(agent_names)}\n"
        f"**Started:** {started_at}\n"
    )
    question_file.write_text(content, encoding="utf-8")


async def terminate_process(process: asyncio.subprocess.Process) -> None:
    if process.returncode is not None:
        return
    if sys.platform == "win32":
        try:
            killer = await asyncio.create_subprocess_exec(
                "taskkill",
                "/PID",
                str(process.pid),
                "/T",
                "/F",
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


async def run_agent(
    agent: AgentConfig,
    question: str,
    timeout_seconds: float,
    round_dir: Path,
    claude_executable: str,
    semaphore: asyncio.Semaphore,
) -> AgentResult:
    print(f"→ {agent.name} dispatched")
    started_monotonic = asyncio.get_running_loop().time()
    timestamp = datetime.now().astimezone().isoformat()
    output_file = round_dir / f"{agent.name}.md"
    try:
        # Pass the CLAUDE.md path, not its contents. Real sibling identities
        # (28KB+) blow Windows' ~8K command-line cap when inlined as an argv
        # string. The file flag sidesteps the limit entirely. Validation that
        # the file exists + is readable still happens in parse_config().
        async with semaphore:
            process = await asyncio.create_subprocess_exec(
                claude_executable,
                "-p",
                question,
                "--append-system-prompt-file",
                str(agent.system_prompt_file),
                "--permission-mode",
                "bypassPermissions",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
                exit_code: int | str = process.returncode if process.returncode is not None else "error"
                stdout = stdout_bytes.decode("utf-8", errors="replace")
                stderr = stderr_bytes.decode("utf-8", errors="replace")
            except asyncio.TimeoutError:
                await terminate_process(process)
                exit_code = "timeout"
                stdout = ""
                stderr = f"Timed out after {timeout_seconds:.2f} seconds."
    except Exception as exc:
        exit_code = "error"
        stdout = f"{type(exc).__name__}: {exc}"
        stderr = ""

    duration_seconds = asyncio.get_running_loop().time() - started_monotonic
    result = AgentResult(
        name=agent.name,
        emoji=agent.emoji,
        timestamp=timestamp,
        duration_seconds=duration_seconds,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        output_file=output_file,
    )
    write_agent_file(result, question)
    if exit_code == 0:
        print(f"✓ {agent.name} ({duration_seconds:.1f}s, exit 0)")
    elif exit_code == "timeout":
        print(f"✗ {agent.name} (timeout)")
    else:
        print(f"✗ {agent.name} ({duration_seconds:.1f}s, exit {exit_code})")
    return result


def write_agent_file(result: AgentResult, question: str) -> None:
    header = f"# {result.name}"
    if result.emoji:
        header = f"{header} {result.emoji}"
    content = (
        f"{header}\n\n"
        f"**Question:** {question}\n"
        f"**Timestamp:** {result.timestamp}\n"
        f"**Duration:** {result.duration_seconds:.2f}\n"
        f"**Exit code:** {result.exit_code}\n\n"
        f"---\n\n"
        f"{result.stdout}\n\n"
        f"---\n"
    )
    if result.stderr:
        content += f"\n## stderr\n\n{result.stderr}\n"
    result.output_file.write_text(content, encoding="utf-8")


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
    for result in results:
        lines.append(
            f"| {result.name} | {result.exit_code} | {result.duration_seconds:.2f}s | [{result.output_file.name}]({result.output_file.name}) |"
        )
    with question_file.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


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


async def main() -> int:
    configure_stdio()
    parser = build_parser()
    args = parser.parse_args()

    claude_executable = resolve_claude_executable()
    if claude_executable is None:
        print(
            "'claude' CLI not found on PATH. Install: https://docs.anthropic.com/en/docs/claude-code/quickstart",
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
        write_question_file(question_file, timestamp, args.question, [agent.name for agent in selected_agents], started_at)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    semaphore = asyncio.Semaphore(args.concurrency)
    gathered = await asyncio.gather(
        *(
            run_agent(agent, args.question, args.timeout, round_dir, claude_executable, semaphore)
            for agent in selected_agents
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
            write_agent_file(fallback, args.question)
            results.append(fallback)
        else:
            results.append(item)
    append_summary(question_file, datetime.now().astimezone().isoformat(), results)

    if not args.no_open:
        open_round_dir(round_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
