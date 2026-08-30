#!/usr/bin/env python3
"""Subprocess contract checks for ``test_resource_lock.py``."""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools/test_resource_lock.py"


def run_lock(cwd: Path, temporary: Path, resource: str, command: list[str], *extra: str, scope: str = "project", timeout: float = 5) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "run", "--resource", resource, "--scope", scope, "--timeout-seconds", str(timeout), "--", *command, *extra],
        cwd=cwd,
        env={**os.environ, "TMPDIR": str(temporary)},
        text=True,
        capture_output=True,
        check=False,
    )


def start_lock(cwd: Path, temporary: Path, resource: str, code: str, *args: str, scope: str = "project", timeout: float = 5) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, str(SCRIPT), "run", "--resource", resource, "--scope", scope, "--timeout-seconds", str(timeout), "--", sys.executable, "-c", code, *args],
        cwd=cwd,
        env={**os.environ, "TMPDIR": str(temporary)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def repository(parent: Path, name: str) -> Path:
    path = parent / name
    path.mkdir()
    git(path, "init", "-q")
    (path / "tracked").write_text("tracked\n", encoding="utf-8")
    git(path, "add", "tracked")
    env = {**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid", "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=path, env=env, check=True)
    return path


EVENT_CODE = """
import pathlib, sys, time
log, name, delay = map(str, sys.argv[1:])
path = pathlib.Path(log)
with path.open('a', encoding='utf-8') as f:
    f.write(name + '-start\\n'); f.flush()
time.sleep(float(delay))
with path.open('a', encoding='utf-8') as f:
    f.write(name + '-end\\n'); f.flush()
"""


def wait_for(path: Path, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return
        time.sleep(0.01)
    raise AssertionError(f"timed out waiting for {path}")


def wait_for_line(path: Path, expected: str, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists() and expected in path.read_text(encoding="utf-8").splitlines():
            return
        time.sleep(0.01)
    raise AssertionError(f"timed out waiting for {expected} in {path}")


def test_same_resource_serializes_and_different_resource_overlaps() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-") as raw:
        temporary = Path(raw)
        project = repository(temporary, "project")
        linked = temporary / "linked"
        git(project, "worktree", "add", "-q", "--detach", str(linked), "HEAD")
        log = temporary / "same.log"
        first = start_lock(project, temporary, "browser", EVENT_CODE, str(log), "first", "0.35")
        wait_for(log)
        second = start_lock(linked, temporary, "browser", EVENT_CODE, str(log), "second", "0")
        assert first.wait(timeout=3) == 0
        assert second.wait(timeout=3) == 0
        assert log.read_text(encoding="utf-8").splitlines() == ["first-start", "first-end", "second-start", "second-end"]

        log = temporary / "different.log"
        first = start_lock(project, temporary, "browser", EVENT_CODE, str(log), "first", "0.8")
        wait_for(log)
        second = start_lock(linked, temporary, "database", EVENT_CODE, str(log), "second", "0.8")
        wait_for_line(log, "second-start")
        assert first.wait(timeout=3) == 0
        assert second.wait(timeout=3) == 0
        events = log.read_text(encoding="utf-8").splitlines()
        assert events.index("second-start") < events.index("first-end")


def test_machine_scope_serializes_unrelated_repositories() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-machine-") as raw:
        temporary = Path(raw)
        first_repo = repository(temporary, "first")
        second_repo = repository(temporary, "second")
        log = temporary / "machine.log"
        first = start_lock(first_repo, temporary, "browser", EVENT_CODE, str(log), "first", "0.3", scope="machine")
        wait_for(log)
        second = start_lock(second_repo, temporary, "browser", EVENT_CODE, str(log), "second", "0", scope="machine")
        assert first.wait(timeout=3) == 0
        assert second.wait(timeout=3) == 0
        assert log.read_text(encoding="utf-8").splitlines() == ["first-start", "first-end", "second-start", "second-end"]


def test_timeout_exit_status_recovery_and_inherited_descriptor() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-lifecycle-") as raw:
        temporary = Path(raw)
        project = repository(temporary, "project")
        log = temporary / "lifecycle.log"
        holder = start_lock(project, temporary, "browser", EVENT_CODE, str(log), "holder", "0.7")
        wait_for(log)
        waiter = run_lock(project, temporary, "browser", [sys.executable, "-c", "open(r'{}', 'w').write('ran')".format(temporary / "timeout-sentinel")], timeout=0.05)
        assert waiter.returncode == 75
        assert not (temporary / "timeout-sentinel").exists()
        assert holder.wait(timeout=3) == 0

        inherited = start_lock(project, temporary, "inherited", EVENT_CODE, str(log), "child", "0.65")
        wait_for_line(log, "child-start")
        os.kill(inherited.pid, signal.SIGKILL)
        waiter = start_lock(project, temporary, "inherited", EVENT_CODE, str(log), "waiter", "0")
        time.sleep(0.15)
        assert waiter.poll() is None
        assert waiter.wait(timeout=3) == 0
        events = log.read_text(encoding="utf-8").splitlines()
        assert events[-4:] == ["child-start", "child-end", "waiter-start", "waiter-end"]


def test_argv_status_validation_and_secret_free_diagnostics() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-input-") as raw:
        temporary = Path(raw)
        project = repository(temporary, "project")
        recorder = temporary / "argv.json"
        literals = ["$(touch injected)", "; touch injected", "*.txt", "$SECRET"]
        command = [sys.executable, "-c", "import json,sys; json.dump(sys.argv[2:],open(sys.argv[1],'w'))", str(recorder), *literals]
        result = run_lock(project, temporary, "argv-safe", command)
        assert result.returncode == 0
        assert json.loads(recorder.read_text(encoding="utf-8")) == literals
        assert not (project / "injected").exists()
        assert run_lock(project, temporary, "../escape", [sys.executable, "-c", "raise SystemExit(9)"]).returncode == 2
        assert run_lock(project, temporary, "a/b", [sys.executable, "-c", "raise SystemExit(9)"]).returncode == 2
        assert run_lock(project, temporary, "bad name", [sys.executable, "-c", "raise SystemExit(9)"]).returncode == 2
        assert run_lock(project, temporary, "valid", []).returncode == 2
        assert run_lock(project, temporary, "valid", [sys.executable, "-c", "raise SystemExit(17)"]).returncode == 17
        assert run_lock(project, temporary, "valid", ["missing-command-for-lock-test"], timeout=0).returncode == 127
        assert run_lock(project, temporary, "valid", [sys.executable, "-c", "raise SystemExit(9)"], timeout=-1).returncode == 2

        secret = "secret-not-in-diagnostics"
        holder = start_lock(project, temporary, "diagnostic", EVENT_CODE, str(temporary / "diag.log"), "holder", "0.45")
        wait_for(temporary / "diag.log")
        waiter = subprocess.run(
            [sys.executable, str(SCRIPT), "run", "--resource", "diagnostic", "--timeout-seconds", "0.05", "--", sys.executable, "-c", "raise SystemExit(0)", secret],
            cwd=project,
            env={**os.environ, "TMPDIR": str(temporary), "LOCK_SECRET": secret},
            text=True,
            capture_output=True,
            check=False,
        )
        assert waiter.returncode == 75
        assert secret not in waiter.stderr
        diagnostics = [json.loads(line) for line in waiter.stderr.splitlines()]
        assert diagnostics[0]["resource"] == "diagnostic"
        assert diagnostics[0]["scope"] == "project"
        assert isinstance(diagnostics[0]["holder_pid"], int)
        assert isinstance(diagnostics[0]["holder_project"], str)
        assert isinstance(diagnostics[0]["holder_start_time"], str)
        assert holder.wait(timeout=3) == 0


def test_private_lock_root_rejects_symlink_and_project_requires_git() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-security-") as raw:
        temporary = Path(raw)
        outside = temporary / "outside"
        outside.mkdir()
        root = temporary / f"my-workflow-test-lock-{os.getuid()}"
        root.symlink_to(outside, target_is_directory=True)
        result = run_lock(Path.cwd(), temporary, "browser", [sys.executable, "-c", "raise SystemExit(9)"])
        assert result.returncode == 2
        assert list(outside.iterdir()) == []
        non_git = temporary / "non-git"
        non_git.mkdir()
        result = run_lock(non_git, temporary, "browser", [sys.executable, "-c", "raise SystemExit(9)"])
        assert result.returncode == 2

        file_case = temporary / "file-case"
        file_case.mkdir()
        file_project = repository(file_case, "project")
        file_root = file_case / f"my-workflow-test-lock-{os.getuid()}"
        file_root.mkdir(mode=0o700)
        common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=file_project, text=True).strip()
        common_path = (file_project / common).resolve()
        project_id = hashlib.sha256(str(common_path).encode("utf-8")).hexdigest()[:16]
        referent = file_case / "referent"
        referent.write_text("untouched\n", encoding="utf-8")
        (file_root / f"project-{project_id}-browser.lock").symlink_to(referent)
        result = run_lock(file_project, file_case, "browser", [sys.executable, "-c", "raise SystemExit(9)"])
        assert result.returncode == 2
        assert referent.read_text(encoding="utf-8") == "untouched\n"


def main() -> None:
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"ok ({len(tests)} tests)")


if __name__ == "__main__":
    main()
