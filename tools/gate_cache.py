#!/usr/bin/env python3
"""Run a gate once per tree. Reuse a passing record for an identical tree.

  python3 tools/gate_cache.py run --gate <label> [--root <path>] -- <command> [args...]

The key is the gate label, the exact command, and the Git tree object of every
non-ignored worktree file (`AD-018`). Records live in ignored `<root>/.gate-cache/`.
A passing record short-circuits; anything else runs the gate. The cache never
blocks or fakes a gate: with no tree object it runs the command and stores nothing.

ponytail: interpreter, dependency-binary and environment versions are outside the
key (`AD-018` trade-off). Upgrade path after a toolchain change: delete `.gate-cache/`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

VERSION = 1


def tree_sha(root: Path) -> str:
    """Tree object of the whole non-ignored worktree. Raises if Git cannot produce one."""

    def git(*args: str, **kwargs: object) -> str:
        return subprocess.run(
            ["git", *args], cwd=root, check=True, capture_output=True, text=True, **kwargs
        ).stdout.strip()

    with tempfile.TemporaryDirectory() as raw:
        temporary = Path(raw) / "index"
        real = root / git("rev-parse", "--git-path", "index")
        if real.is_file():
            # Seeded only for the stat cache; the real index is never written. copy2 keeps its
            # mtime, so Git's racy-index check still re-reads same-second edits.
            shutil.copy2(real, temporary)
        env = {**os.environ, "GIT_INDEX_FILE": str(temporary)}
        git("add", "-A", env=env)
        # The cache directory is its own churn; never let it key itself.
        git("rm", "-rf", "--cached", "--ignore-unmatch", "-q", "--", ".gate-cache", env=env)
        return git("write-tree", env=env)


def fingerprint(gate: str, command: list[str], tree: str) -> str:
    material = "\0".join([gate, *command, tree])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def cached_log(record_path: Path) -> Path | None:
    """The log of a record that short-circuits, or None when there is no such record.

    A record qualifies only when it parses as an object of this schema version, passed, and still
    has its log. Anything else — including JSON that is not an object — is absent, never an error:
    a damaged record costs a re-run, it never fails the gate.
    """
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict) or record.get("version") != VERSION:
        return None
    if record.get("status") != "pass":
        return None
    log = Path(str(record.get("log")))
    return log if log.is_file() else None


def write_record(path: Path, payload: dict[str, object]) -> None:
    # `os.replace` is load-bearing, and no test covers its removal — a torn record is observable
    # only mid-write. Two invocations of one gate on one tree share a fingerprint and so one record
    # path, and their payloads differ only in `status`, `exit_code` and `finished_at`. A non-atomic
    # writer could blend them into a valid record carrying one run's `status: "pass"` with the
    # other's `exit_code`, which `cached_log()` would accept because it never reads `exit_code`.
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def execute(command: list[str], root: Path, log: Path | None) -> int:
    """Run the command, streaming combined output to stdout and, when given, the log."""
    handle = log.open("wb") if log else None
    try:
        process = subprocess.Popen(
            command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        assert process.stdout is not None
        for chunk in iter(lambda: process.stdout.read1(65536), b""):
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            if handle:
                handle.write(chunk)
                handle.flush()
        return process.wait()
    finally:
        if handle:
            handle.close()


def evidence(outcome: str, gate: str, print_hash: str, log: str, extra: str = "") -> None:
    print(f"gate-cache {outcome} gate={gate} fingerprint={print_hash} log={log}{extra}")


def main(argv: list[str]) -> int:
    head, command = (argv[: argv.index("--")], argv[argv.index("--") + 1 :]) if "--" in argv else (argv, [])
    parser = argparse.ArgumentParser(prog="gate_cache.py")
    parser.add_argument("verb", choices=["run"])
    parser.add_argument("--gate", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args(head)
    root = Path(args.root).resolve()

    if not command:
        evidence("USAGE", args.gate, "-", "-")
        print("no command after --", file=sys.stderr)
        return 2

    try:
        tree = tree_sha(root)
    except (OSError, subprocess.SubprocessError) as exc:
        evidence("NOCACHE", args.gate, "-", "-", f" reason={type(exc).__name__}")
        return execute(command, root, None)

    print_hash = fingerprint(args.gate, command, tree)
    cache = root / ".gate-cache"
    cache.mkdir(parents=True, exist_ok=True)
    record_path = cache / f"{print_hash}.json"

    reusable = cached_log(record_path)
    if reusable:
        evidence("HIT", args.gate, print_hash, str(reusable))
        return 0

    # One log per run, created before the command starts: same-fingerprint runs would otherwise
    # share one path and truncate each other's output, and the log is the cited diagnostic. Only
    # the run about to replace this record can be cited, so its predecessors go now — otherwise a
    # gate failing repeatedly on one tree leaks a log per retry.
    for stale in cache.glob(f"{print_hash}.*.log"):
        stale.unlink(missing_ok=True)
    handle, name = tempfile.mkstemp(prefix=f"{print_hash}.", suffix=".log", dir=cache)
    os.close(handle)
    log = Path(name)
    code = execute(command, root, log)
    write_record(
        record_path,
        {
            "version": VERSION,
            "gate": args.gate,
            "command": command,
            "tree": tree,
            "fingerprint": print_hash,
            "status": "pass" if code == 0 else "fail",
            "exit_code": code,
            "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "log": str(log),
        },
    )
    evidence("MISS", args.gate, print_hash, str(log), f" status={'pass' if code == 0 else 'fail'}")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
