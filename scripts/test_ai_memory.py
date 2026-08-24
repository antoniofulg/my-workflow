"""Behavioral checks for scripts/ai-memory.zsh. Run: python3 scripts/test_ai_memory.py"""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "ai-memory.zsh"


def run_codex(
    *args: str, codex_status: int = 0, ai_memory_status: int = 0
) -> tuple[subprocess.CompletedProcess[str], list[str], list[str]]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        capture = root / "codex-args"
        calls = root / "ai-memory-calls"
        bin_dir = root / "bin"
        bin_dir.mkdir()
        (bin_dir / "codex").write_text(
            "#!/bin/sh\n"
            f"if [ \"$#\" -gt 0 ]; then printf '%s\\n' \"$@\" > {shlex.quote(str(capture))}; fi\n"
            f"exit {codex_status}\n",
            encoding="utf-8",
        )
        (bin_dir / "ai-memory").write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$*\" >> {shlex.quote(str(calls))}\n"
            f"exit {ai_memory_status}\n",
            encoding="utf-8",
        )
        (bin_dir / "codex").chmod(0o755)
        (bin_dir / "ai-memory").chmod(0o755)

        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:{env['PATH']}"
        command = f'source {shlex.quote(str(HELPER))}; codex "$@"'
        result = subprocess.run(
            ["zsh", "-f", "-c", command, "codex", *args],
            env=env,
            capture_output=True,
            text=True,
        )
        calls = calls.read_text(encoding="utf-8").splitlines() if calls.exists() else []
        received = capture.read_text(encoding="utf-8").splitlines() if capture.exists() else []
        return result, calls, received


def run_handoff(*, ai_memory_status: int = 0) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        calls = root / "ai-memory-calls"
        bin_dir = root / "bin"
        bin_dir.mkdir()
        (bin_dir / "ai-memory").write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$*\" >> {shlex.quote(str(calls))}\n"
            f"exit {ai_memory_status}\n",
            encoding="utf-8",
        )
        (bin_dir / "ai-memory").chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:{env['PATH']}"
        command = f'source {shlex.quote(str(HELPER))}; handoff'
        result = subprocess.run(
            ["zsh", "-f", "-c", command],
            env=env,
            capture_output=True,
            text=True,
        )
        calls = calls.read_text(encoding="utf-8").splitlines() if calls.exists() else []
        return result, calls


def test_finalizes_once() -> None:
    result, calls, received = run_codex("work")
    assert result.returncode == 0
    assert result.stderr == ""
    assert calls == ["finalize-session"]
    assert received == ["work"]


def test_preserves_codex_status() -> None:
    result, calls, received = run_codex("work", codex_status=42)
    assert result.returncode == 42
    assert calls == ["finalize-session"]
    assert received == ["work"]


def test_reports_finalization_failure() -> None:
    result, calls, received = run_codex("work", codex_status=42, ai_memory_status=1)
    assert result.returncode == 42
    assert result.stderr == "ai-memory: finalize-session failed; run handoff manually.\n"
    assert calls == ["finalize-session"]
    assert received == ["work"]


def test_passes_arguments_literally() -> None:
    args = ("space value", "$(touch injected)", ";", "*.txt")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        capture = root / "codex-args"
        bin_dir = root / "bin"
        bin_dir.mkdir()
        (bin_dir / "codex").write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$@\" > {shlex.quote(str(capture))}\n",
            encoding="utf-8",
        )
        (bin_dir / "ai-memory").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        (bin_dir / "codex").chmod(0o755)
        (bin_dir / "ai-memory").chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:{env['PATH']}"
        command = f'source {shlex.quote(str(HELPER))}; codex "$@"'
        result = subprocess.run(
            ["zsh", "-f", "-c", command, "codex", *args],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert capture.read_text(encoding="utf-8").splitlines() == list(args)
        assert not (root / "injected").exists()


def test_manual_handoff_calls_finalize_and_returns_status() -> None:
    result, calls = run_handoff(ai_memory_status=23)
    assert result.returncode == 23
    assert calls == ["finalize-session"]


def test_version_does_not_finalize_preexisting_session() -> None:
    result, calls, received = run_codex("--version", codex_status=42)
    assert result.returncode == 42
    assert calls == []
    assert received == ["--version"]


def test_exec_does_not_finalize_preexisting_session() -> None:
    args = ("exec", "work", "--json")
    result, calls, received = run_codex(*args, codex_status=42)
    assert result.returncode == 42
    assert calls == []
    assert received == list(args)


def test_other_bypass_modes_do_not_finalize_preexisting_session() -> None:
    cases = (
        ("--help",),
        ("-h",),
        ("--version",),
        ("-V",),
        ("help",),
        ("version",),
        ("completion", "zsh"),
        ("login", "status"),
        ("logout",),
        ("mcp", "list"),
    )
    for args in cases:
        result, calls, received = run_codex(*args, codex_status=42)
        assert result.returncode == 42
        assert calls == []
        assert received == list(args)


def test_interactive_launch_modes_finalize_once_and_preserve_status_and_argv() -> None:
    cases = (
        (),
        ("prompt with spaces", "--sandbox", "read-only"),
        ("resume", "abc"),
        ("fork", "abc"),
    )
    for args in cases:
        result, calls, received = run_codex(*args, codex_status=42)
        assert result.returncode == 42
        assert calls == ["finalize-session"]
        assert received == list(args)


def main() -> None:
    tests = (
        test_finalizes_once,
        test_preserves_codex_status,
        test_reports_finalization_failure,
        test_passes_arguments_literally,
        test_manual_handoff_calls_finalize_and_returns_status,
        test_version_does_not_finalize_preexisting_session,
        test_exec_does_not_finalize_preexisting_session,
        test_other_bypass_modes_do_not_finalize_preexisting_session,
        test_interactive_launch_modes_finalize_once_and_preserve_status_and_argv,
    )
    for test in tests:
        test()
    print(f"{len(tests)} passed, 0 failed")


if __name__ == "__main__":
    main()
