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
import threading
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


def canonical_lock_root() -> Path:
    return Path("/tmp").resolve() / f"my-workflow-test-lock-{os.getuid()}"


def run_with_root(cwd: Path, root: Path, argv: list[str]) -> int:
    previous_directory = Path.cwd()
    try:
        os.chdir(cwd)
        with patch.object(resource_lock, "_lock_root", return_value=root):
            return resource_lock.main(argv)
    finally:
        os.chdir(previous_directory)


def test_same_resource_serializes_and_different_resource_overlaps() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-") as raw:
        temporary = Path(raw)
        project = repository(temporary, "project")
        linked = temporary / "linked"
        git(project, "worktree", "add", "-q", "--detach", str(linked), "HEAD")
        log = temporary / "same.log"
        first = start_lock(project, temporary, "browser", EVENT_CODE, str(log), "first", "0.35", scope=None)
        wait_for_line(log, "first-start")
        second = start_lock(linked, temporary, "browser", EVENT_CODE, str(log), "second", "0", scope=None)
        assert first.wait(timeout=3) == 0
        assert second.wait(timeout=3) == 0
        assert log.read_text(encoding="utf-8").splitlines() == ["first-start", "first-end", "second-start", "second-end"]

        log = temporary / "different.log"
        first = start_lock(project, temporary, "browser", EVENT_CODE, str(log), "first", "0.8")
        wait_for_line(log, "first-start")
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
        first_tmpdir = temporary / "caller-a"
        second_tmpdir = temporary / "caller-b"
        first_tmpdir.mkdir()
        second_tmpdir.mkdir()
        machine_resource = f"machine-{os.getpid()}-{int(time.time() * 1000000)}"
        first = start_lock(first_repo, temporary, machine_resource, EVENT_CODE, str(log), "first", "0.3", scope="machine", environment={"TMPDIR": str(first_tmpdir)})
        wait_for_line(log, "first-start")
        second = start_lock(second_repo, temporary, machine_resource, EVENT_CODE, str(log), "second", "0", scope="machine", environment={"TMPDIR": str(second_tmpdir)})
        assert first.wait(timeout=3) == 0
        assert second.wait(timeout=3) == 0
        assert log.read_text(encoding="utf-8").splitlines() == ["first-start", "first-end", "second-start", "second-end"]

        identity_log = temporary / "identity.log"
        identity_resource = f"identity-{os.getpid()}-{int(time.time() * 1000000)}"
        first = start_lock(first_repo, temporary, identity_resource, EVENT_CODE, str(identity_log), "first", "0")
        second = start_lock(second_repo, temporary, identity_resource, EVENT_CODE, str(identity_log), "second", "0")
        assert first.wait(timeout=3) == 0
        assert second.wait(timeout=3) == 0
        lock_root = canonical_lock_root()
        assert len(list(lock_root.glob(f"project-*-{identity_resource}.lock"))) == 2


def test_timeout_exit_status_recovery_and_inherited_descriptor() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-lifecycle-") as raw:
        temporary = Path(raw)
        project = repository(temporary, "project")
        log = temporary / "lifecycle.log"
        holder = start_lock(project, temporary, "browser", EVENT_CODE, str(log), "holder", "0.7")
        wait_for_line(log, "holder-start")
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


def test_wait_diagnostic_waits_for_complete_holder_metadata() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-metadata-") as raw:
        temporary = Path(raw)
        project = repository(temporary, "project")
        lock_root = temporary / "locks"
        observed: list[dict[str, object]] = []
        holder_ready = threading.Event()
        original_write = resource_lock._write_holder

        def delayed_write(fd: int, scope: str, resource: str, project_id: str) -> None:
            holder_ready.set()
            time.sleep(0.25)
            original_write(fd, scope, resource, project_id)

        def capture_diagnostic(event: str, scope: str, resource: str, fd: int) -> None:
            observed.append(resource_lock._read_holder(fd))

        holder_result: list[int] = []
        waiter_result: list[int] = []
        holder_args = ["run", "--resource", "metadata-window", "--timeout-seconds", "2", "--", sys.executable, "-c", "import time; time.sleep(0.4)"]
        waiter_args = ["run", "--resource", "metadata-window", "--timeout-seconds", "2", "--", sys.executable, "-c", "pass"]
        with patch.object(resource_lock, "_lock_root", return_value=lock_root), patch.object(resource_lock, "_project_identifier", return_value="fixture"), patch.object(resource_lock, "_write_holder", side_effect=delayed_write), patch.object(resource_lock, "_diagnostic", side_effect=capture_diagnostic):
            holder_thread = threading.Thread(target=lambda: holder_result.append(resource_lock.main(holder_args)))
            holder_thread.start()
            assert holder_ready.wait(timeout=10)
            waiter_thread = threading.Thread(target=lambda: waiter_result.append(resource_lock.main(waiter_args)))
            waiter_thread.start()
            waiter_thread.join(timeout=10)
            holder_thread.join(timeout=10)
        assert holder_result == [0]
        assert waiter_result == [0]
        assert len(observed) == 1
        assert isinstance(observed[0]["holder_pid"], int)
        assert isinstance(observed[0]["holder_project"], str)
        assert isinstance(observed[0]["holder_start_time"], str)


def test_argv_status_validation_and_secret_free_diagnostics() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-lock-input-") as raw:
        temporary = Path(raw)
        project = repository(temporary, "project")
        invalid_command = [sys.executable, "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('ran')", str(temporary / "invalid-command-ran")]
        lock_root = canonical_lock_root()
        before_lock_entries = sorted(path.name for path in lock_root.iterdir()) if lock_root.exists() else []
        for resource in ("", "a" * 65, "/tmp/x", "a/b", "bad name", "../escape"):
            result = run_lock(project, temporary, resource, invalid_command)
            assert result.returncode == 2
            assert not (temporary / "invalid-command-ran").exists()
            assert (sorted(path.name for path in lock_root.iterdir()) if lock_root.exists() else []) == before_lock_entries
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
        missing = run_lock(project, temporary, "valid", ["missing-command-for-lock-test"], timeout=0)
        assert missing.returncode == 127
        assert json.loads(missing.stderr) == {"event": "exec_unavailable", "executable": "missing-command-for-lock-test"}
        non_executable = temporary / "not-executable"
        non_executable.write_text("not executable\n", encoding="utf-8")
        non_executable.chmod(0o600)
        unavailable = run_lock(project, temporary, "valid", [str(non_executable)], timeout=0)
        assert unavailable.returncode == 127
        assert json.loads(unavailable.stderr)["executable"] == non_executable.name
        assert "Traceback" not in unavailable.stderr
        not_a_directory = temporary / "not-a-directory"
        not_a_directory.write_text("not a directory\n", encoding="utf-8")
        other_exec_error = run_lock(project, temporary, "valid", [str(not_a_directory / "command")], timeout=0)
        assert other_exec_error.returncode != 127
        assert "exec_unavailable" not in other_exec_error.stderr
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
        later_separator = subprocess.run(
            [sys.executable, str(SCRIPT), "run", "--resource", "valid", sys.executable, "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('ran'); raise SystemExit(17)", str(no_separator_sentinel), "--"],
            cwd=project,
            env={**os.environ, "TMPDIR": str(temporary)},
            text=True,
            capture_output=True,
            check=False,
        )
        assert later_separator.returncode == 2
        assert not no_separator_sentinel.exists()
        help_result = subprocess.run([sys.executable, str(SCRIPT), "run", "--help"], text=True, capture_output=True, check=False)
        assert help_result.returncode == 0
        assert "resource_lock.py" in help_result.stdout

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
        lock_root = canonical_lock_root()
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
        result = run_with_root(Path.cwd(), root, ["run", "--resource", "browser", "--", sys.executable, "-c", "raise SystemExit(9)"])
        assert result == 2
        assert list(outside.iterdir()) == []
        non_git = temporary / "non-git"
        non_git.mkdir()
        result = run_with_root(non_git, temporary / "non-git-lock-root", ["run", "--resource", "browser", "--", sys.executable, "-c", "raise SystemExit(9)"])
        assert result == 2

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
        result = run_with_root(file_project, file_root, ["run", "--resource", "browser", "--", sys.executable, "-c", "raise SystemExit(9)"])
        assert result == 2
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
        swap_happened = False

        def swap_after_directory_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777, *, dir_fd: int | None = None) -> int:
            nonlocal swap_happened
            fd = original_open(path, flags, mode, dir_fd=dir_fd)
            if dir_fd is None and Path(path) == race_root:
                race_root.rename(stable_root)
                race_root.symlink_to(outside, target_is_directory=True)
                swap_happened = True
            return fd

        previous_directory = Path.cwd()
        previous_tmpdir = os.environ.get("TMPDIR")
        try:
            os.chdir(race_project)
            os.environ["TMPDIR"] = str(race_case)
            with patch.object(resource_lock, "_lock_root", return_value=race_root), patch.object(resource_lock.os, "open", side_effect=swap_after_directory_open):
                result = resource_lock.main(["run", "--resource", "race", "--", sys.executable, "-c", "raise SystemExit(0)"])
        finally:
            os.chdir(previous_directory)
            if previous_tmpdir is None:
                os.environ.pop("TMPDIR", None)
            else:
                os.environ["TMPDIR"] = previous_tmpdir
        assert result == 0
        assert swap_happened
        assert list(outside.iterdir()) == []


def main() -> None:
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"ok ({len(tests)} tests)")


if __name__ == "__main__":
    main()
