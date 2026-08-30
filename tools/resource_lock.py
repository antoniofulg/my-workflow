#!/usr/bin/env python3
"""Run one command while holding a named, project- or machine-scoped lock.

The wrapper uses the Unix kernel's ``flock`` primitive.  The lock descriptor is
inherited by the child, so the resource remains held until the wrapped command
and every surviving descendant close it.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import stat
import sys
import time
from typing import Sequence


DEFAULT_TIMEOUT = 2700.0
TIMEOUT_STATUS = 75
MISSING_EXECUTABLE_STATUS = 127
RESOURCE_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
MAX_METADATA = 4096


def _resource(value: str) -> str:
    if not RESOURCE_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError("resource must match [a-z0-9][a-z0-9._-]{0,63}")
    return value


def _timeout(value: str) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a non-negative number") from exc
    if result < 0 or not _is_finite(result):
        raise argparse.ArgumentTypeError("timeout must be a non-negative number")
    return result


def _is_finite(value: float) -> bool:
    return value != float("inf") and value != float("-inf") and value == value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="resource_lock.py")
    commands = parser.add_subparsers(dest="action", required=True)
    run = commands.add_parser("run", help="run a command while holding a resource lock")
    run.add_argument("--resource", required=True, type=_resource)
    run.add_argument("--scope", choices=("project", "machine"), default="project")
    run.add_argument("--timeout-seconds", type=_timeout, default=DEFAULT_TIMEOUT)
    run.add_argument("command", nargs=argparse.REMAINDER)
    return parser


def _project_identifier(required: bool) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        result = None
    if result is not None and result.returncode == 0 and result.stdout.strip():
        common = Path(result.stdout.strip())
        if not common.is_absolute():
            common = Path.cwd() / common
        identity = str(common.resolve())
    elif required:
        raise ValueError("project scope requires a Git repository")
    else:
        identity = str(Path.cwd().resolve())
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


def _lock_root() -> Path:
    temporary = os.environ.get("TMPDIR", "/tmp")
    return Path(temporary) / f"my-workflow-test-lock-{os.getuid()}"


def _private_directory(root: Path) -> None:
    try:
        root.mkdir(mode=0o700)
    except FileExistsError:
        pass
    try:
        info = root.lstat()
    except OSError as exc:
        raise ValueError("lock directory is unavailable") from exc
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("lock directory is not a private current-user directory")


def _open_lock(root: Path, name: str) -> int:
    path = root / name
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError("lock file must not be a symlink") from exc
        raise ValueError("lock file is unavailable") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("lock file is not a private current-user file")
        return fd
    except BaseException:
        os.close(fd)
        raise


def _read_holder(fd: int) -> dict[str, object]:
    try:
        raw = os.pread(fd, MAX_METADATA, 0)
        value = json.loads(raw.decode("utf-8")) if raw else {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        value = {}
    if not isinstance(value, dict):
        value = {}
    return {
        "holder_pid": value.get("holder_pid"),
        "holder_project": value.get("holder_project"),
        "holder_start_time": value.get("holder_start_time"),
    }


def _diagnostic(event: str, scope: str, resource: str, fd: int) -> None:
    holder = _read_holder(fd)
    payload = {
        "event": event,
        "scope": scope,
        "resource": resource,
        **holder,
    }
    line = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    print(line[:2048], file=sys.stderr, flush=True)


def _write_holder(fd: int, scope: str, resource: str, project: str) -> None:
    payload = {
        "holder_pid": os.getpid(),
        "holder_project": project,
        "holder_start_time": _datetime.datetime.now(_datetime.timezone.utc).isoformat(),
        "scope": scope,
        "resource": resource,
    }
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    os.ftruncate(fd, 0)
    os.pwrite(fd, encoded, 0)


def _acquire(fd: int, scope: str, resource: str, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    announced = False
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError as exc:
            if exc.errno not in (errno.EACCES, errno.EAGAIN):
                raise
            if not announced:
                _diagnostic("wait", scope, resource, fd)
                announced = True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(0.1, remaining))


def _run(command: Sequence[str], fd: int) -> int:
    os.set_inheritable(fd, True)
    try:
        return subprocess.run(command, check=False, pass_fds=(fd,)).returncode
    except FileNotFoundError:
        return MISSING_EXECUTABLE_STATUS
    except KeyboardInterrupt:
        return 130


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command[:1] == ["--"]:
        args.command = args.command[1:]
    if args.action != "run" or not args.command:
        _parser().error("a command after -- is required")
    try:
        project = _project_identifier(args.scope == "project")
        root = _lock_root()
        _private_directory(root)
        namespace = project if args.scope == "project" else "machine"
        fd = _open_lock(root, f"{args.scope}-{namespace}-{args.resource}.lock")
    except (OSError, ValueError) as exc:
        print(f"test-resource-lock: {exc}", file=sys.stderr)
        return 2
    try:
        if not _acquire(fd, args.scope, args.resource, args.timeout_seconds):
            return TIMEOUT_STATUS
        _write_holder(fd, args.scope, args.resource, project or "unknown")
        return _run(args.command, fd)
    except KeyboardInterrupt:
        return 130
    finally:
        os.close(fd)


if __name__ == "__main__":
    raise SystemExit(main())
