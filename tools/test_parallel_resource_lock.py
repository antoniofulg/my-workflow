#!/usr/bin/env python3
"""Subprocess contract checks for ``resource_lock.py``."""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import signal
import select
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools/resource_lock.py"
sys.path.insert(0, str(ROOT))
from tools import resource_lock


def run_lock(cwd: Path, temporary: Path, resource: str, command: list[str], *extra: str, scope: str | None = "project", timeout: float = 5) -> subprocess.CompletedProcess[str]:
    options = [sys.executable, str(SCRIPT), "run", "--resource", resource]
    if scope is not None:
        options += ["--scope", scope]
    return subprocess.run(
        options + ["--timeout-seconds", str(timeout), "--", *command, *extra],
        cwd=cwd,
        env={**os.environ, "TMPDIR": str(temporary)},
        text=True,
        capture_output=True,
        check=False,
    )


def start_lock(cwd: Path, temporary: Path, resource: str, code: str, *args: str, scope: str | None = "project", timeout: float = 5, environment: dict[str, str] | None = None) -> subprocess.Popen[str]:
    options = [sys.executable, str(SCRIPT), "run", "--resource", resource]
    if scope is not None:
        options += ["--scope", scope]
    return subprocess.Popen(
        options + ["--timeout-seconds", str(timeout), "--", sys.executable, "-c", code, *args],
        cwd=cwd,
        env={**os.environ, "TMPDIR": str(temporary), **(environment or {})},
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


def wait_for_wait_diagnostic(process: subprocess.Popen[str], timeout: float = 10) -> dict[str, object]:
    assert process.stderr is not None
    readable, _, _ = select.select([process.stderr], [], [], timeout)
    assert readable, "timed out waiting for lock wait diagnostic"
    payload = json.loads(process.stderr.readline())
    assert payload["event"] == "wait"
    return payload


def test_same_resource_serializes_and_different_resource_overlaps() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-") as raw:
        temporary = Path(raw)
        project = repository(temporary, "project")
        linked = temporary / "linked"
        git(project, "worktree", "add", "-q", "--detach", str(linked), "HEAD")
        log = temporary / "same.log"
        first = start_lock(project, temporary, "browser", EVENT_CODE, str(log), "first", "0.35", scope=None)
        wait_for(log)
        second = start_lock(linked, temporary, "browser", EVENT_CODE, str(log), "second", "0", scope=None)
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

        identity_log = temporary / "identity.log"
        first = start_lock(first_repo, temporary, "identity", EVENT_CODE, str(identity_log), "first", "0")
        second = start_lock(second_repo, temporary, "identity", EVENT_CODE, str(identity_log), "second", "0")
        assert first.wait(timeout=3) == 0
        assert second.wait(timeout=3) == 0
        lock_root = temporary / f"my-workflow-test-lock-{os.getuid()}"
        assert len(list(lock_root.glob("project-*-identity.lock"))) == 2


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

        interrupted_log = temporary / "interrupted.log"
        holder = start_lock(project, temporary, "interrupt", EVENT_CODE, str(interrupted_log), "holder", "0.65")
        wait_for_line(interrupted_log, "holder-start")
        waiter = start_lock(project, temporary, "interrupt", EVENT_CODE, str(interrupted_log), "interrupted", "0")
        diagnostic = wait_for_wait_diagnostic(waiter)
        assert diagnostic["resource"] == "interrupt"
        assert diagnostic["scope"] == "project"
        os.kill(waiter.pid, signal.SIGINT)
        assert waiter.wait(timeout=3) == 130
        assert holder.wait(timeout=3) == 0
        after = start_lock(project, temporary, "interrupt", EVENT_CODE, str(interrupted_log), "after", "0")
        assert after.wait(timeout=3) == 0
        assert interrupted_log.read_text(encoding="utf-8").splitlines() == ["holder-start", "holder-end", "after-start", "after-end"]


def test_argv_status_validation_and_secret_free_diagnostics() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-input-") as raw:
        temporary = Path(raw)
        project = repository(temporary, "project")
        invalid_command = [sys.executable, "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('ran')", str(temporary / "invalid-command-ran")]
        for resource in ("", "a" * 65, "/tmp/x", "a/b", "bad name", "../escape"):
            result = run_lock(project, temporary, resource, invalid_command)
            assert result.returncode == 2
            assert not (temporary / "invalid-command-ran").exists()
            assert not (temporary / f"my-workflow-test-lock-{os.getuid()}").exists()
        invalid_scope = run_lock(project, temporary, "browser", invalid_command, scope="invalid")
        assert invalid_scope.returncode == 2
        assert "resource_lock.py" in invalid_scope.stderr
        assert "test_resource_lock.py" not in invalid_scope.stderr

        recorder = temporary / "argv.json"
        literals = ["$(touch injected)", "; touch injected", "*.txt", "$SECRET"]
        command = [sys.executable, "-c", "import json,sys; json.dump(sys.argv[2:],open(sys.argv[1],'w'))", str(recorder), *literals]
        result = run_lock(project, temporary, "argv-safe", command)
        assert result.returncode == 0
        assert json.loads(recorder.read_text(encoding="utf-8")) == literals
        assert not (project / "injected").exists()
        assert run_lock(project, temporary, "valid", []).returncode == 2
        assert run_lock(project, temporary, "valid", [sys.executable, "-c", "raise SystemExit(17)"]).returncode == 17
        assert run_lock(project, temporary, "valid", ["missing-command-for-lock-test"], timeout=0).returncode == 127
        assert run_lock(project, temporary, "valid", [sys.executable, "-c", "raise SystemExit(9)"], timeout=-1).returncode == 2
        no_separator_sentinel = temporary / "no-separator-ran"
        missing_separator = subprocess.run(
            [sys.executable, str(SCRIPT), "run", "--resource", "valid", sys.executable, "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('ran'); raise SystemExit(17)", str(no_separator_sentinel)],
            cwd=project,
            env={**os.environ, "TMPDIR": str(temporary)},
            text=True,
            capture_output=True,
            check=False,
        )
        assert missing_separator.returncode == 2
        assert "literal --" in missing_separator.stderr
        assert not no_separator_sentinel.exists()

        secret = "secret-not-in-diagnostics"
        metadata_code = """
import pathlib, sys, time
path = pathlib.Path(sys.argv[1])
with path.open('a', encoding='utf-8') as f:
    f.write('holder-start\\n'); f.flush()
time.sleep(float(sys.argv[3]))
with path.open('a', encoding='utf-8') as f:
    f.write('holder-end\\n'); f.flush()
"""
        holder = start_lock(project, temporary, "diagnostic", metadata_code, str(temporary / "diag.log"), "holder", "0.45", secret, environment={"LOCK_SECRET": secret})
        wait_for_line(temporary / "diag.log", "holder-start")
        lock_root = temporary / f"my-workflow-test-lock-{os.getuid()}"
        lock_file = next(lock_root.glob("project-*-diagnostic.lock"))
        metadata = lock_file.read_text(encoding="utf-8")
        assert secret not in metadata
        assert '"holder_pid"' in metadata and '"holder_project"' in metadata and '"holder_start_time"' in metadata
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
        assert len(diagnostics) == 1
        assert all(len(line) <= 2048 for line in waiter.stderr.splitlines())
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

        foreign_root = file_case / "foreign-root"
        foreign_root.mkdir(mode=0o700)
        current_uid = os.getuid()
        with patch.object(resource_lock.os, "getuid", return_value=current_uid + 1):
            try:
                resource_lock._private_directory(foreign_root)
            except ValueError:
                pass
            else:
                raise AssertionError("foreign-owner lock root accepted")

        race_case = temporary / "race-case"
        race_case.mkdir()
        race_project = repository(race_case, "project")
        race_root = race_case / f"my-workflow-test-lock-{os.getuid()}"
        outside = race_case / "swap-target"
        outside.mkdir()
        stable_root = race_case / "stable-root"
        original_open = resource_lock.os.open

        def swap_after_directory_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777, *, dir_fd: int | None = None) -> int:
            fd = original_open(path, flags, mode, dir_fd=dir_fd)
            if dir_fd is None and Path(path) == race_root:
                race_root.rename(stable_root)
                race_root.symlink_to(outside, target_is_directory=True)
            return fd

        previous_directory = Path.cwd()
        previous_tmpdir = os.environ.get("TMPDIR")
        try:
            os.chdir(race_project)
            os.environ["TMPDIR"] = str(race_case)
            with patch.object(resource_lock.os, "open", side_effect=swap_after_directory_open):
                result = resource_lock.main(["run", "--resource", "race", "--", sys.executable, "-c", "raise SystemExit(0)"])
        finally:
            os.chdir(previous_directory)
            if previous_tmpdir is None:
                os.environ.pop("TMPDIR", None)
            else:
                os.environ["TMPDIR"] = previous_tmpdir
        assert result == 0
        assert list(outside.iterdir()) == []


def main() -> None:
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"ok ({len(tests)} tests)")


if __name__ == "__main__":
    main()
