"""Self-check for tools/gate_cache.py. Run: python3 tools/test_gate_cache.py"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "gate_cache.py"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, env={**os.environ, **GIT_ENV}
    )


def counting_command(counter: Path, exit_code: int = 0) -> list[str]:
    script = f"import sys; open({str(counter)!r},'a').write('x'); print('gate ran'); sys.exit({exit_code})"
    return [sys.executable, "-c", script]


def runs(counter: Path) -> int:
    return len(counter.read_text(encoding="utf-8")) if counter.exists() else 0


def invoke(repo: Path, gate: str, command: list[str], **kwargs: object):
    return subprocess.run(
        [sys.executable, str(TOOL), "run", "--gate", gate, "--root", str(repo), "--", *command],
        capture_output=True,
        text=True,
        **kwargs,
    )


def field(stdout: str, name: str) -> str:
    """One field of the single `gate-cache ...` evidence line, spaces in the value included."""
    line = [row for row in stdout.splitlines() if row.startswith("gate-cache ")]
    assert len(line) == 1, stdout
    found = re.search(rf"\b{name}=(.*?)(?=\s+\w+=|$)", line[0])
    assert found, line[0]
    return found.group(1)


def index_path(repo: Path) -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--git-path", "index"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    return repo / out


def records(repo: Path) -> list[Path]:
    return sorted((repo / ".gate-cache").glob("*.json")) if (repo / ".gate-cache").is_dir() else []


def scratch(stack):
    raw = tempfile.TemporaryDirectory()
    stack.append(raw)
    root = Path(raw.name)
    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "src.txt").write_text("one\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "init")
    return repo, root / "count"


def test_independent_test_for_p1() -> None:
    stack: list = []
    repo, counter = scratch(stack)
    command = counting_command(counter)

    first = invoke(repo, "scoped", command)
    assert first.returncode == 0, first.stderr
    assert "MISS" in first.stdout and "gate ran" in first.stdout
    assert runs(counter) == 1

    second = invoke(repo, "scoped", command)
    assert second.returncode == 0, second.stderr
    assert "HIT" in second.stdout
    assert runs(counter) == 1, "an unchanged tree must not re-execute the gate"

    (repo / "src.txt").write_text("two\n", encoding="utf-8")
    invoke(repo, "scoped", command)
    assert runs(counter) == 2, "a tracked edit must invalidate the record"

    (repo / "extra.txt").write_text("new\n", encoding="utf-8")
    invoke(repo, "scoped", command)
    assert runs(counter) == 3, "an untracked unignored file must invalidate the record"

    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "same content")
    hit = invoke(repo, "scoped", command)
    assert "HIT" in hit.stdout
    assert runs(counter) == 3, "a commit that changes no content must stay a hit"

    invoke(repo, "full", command)
    assert runs(counter) == 4, "a different gate label must execute"

    invoke(repo, "scoped", [*command, "ignored-arg"])
    assert runs(counter) == 5, "a different command must execute"

    failing = counting_command(counter, 1)
    first_fail = invoke(repo, "failing", failing)
    assert first_fail.returncode == 1
    assert runs(counter) == 6
    second_fail = invoke(repo, "failing", failing)
    assert second_fail.returncode == 1
    assert runs(counter) == 7, "a failing record must never short-circuit"

    stack.clear()


def test_record_contents_and_log() -> None:
    stack: list = []
    repo, counter = scratch(stack)
    command = counting_command(counter)
    result = invoke(repo, "scoped", command)

    assert len(records(repo)) == 1
    record = json.loads(records(repo)[0].read_text(encoding="utf-8"))
    assert record["gate"] == "scoped"
    assert record["command"] == command
    assert record["status"] == "pass" and record["exit_code"] == 0
    assert record["tree"] and record["fingerprint"] and record["finished_at"]
    assert Path(record["log"]).read_text(encoding="utf-8").strip() == "gate ran"
    assert record["fingerprint"] in result.stdout and record["log"] in result.stdout

    Path(record["log"]).unlink()
    again = invoke(repo, "scoped", command)
    assert "MISS" in again.stdout, "a record without its log is absent"
    stack.clear()


def test_git_unavailable_runs_and_caches_nothing() -> None:
    stack: list = []
    repo, counter = scratch(stack)
    with tempfile.TemporaryDirectory() as empty:
        result = invoke(repo, "scoped", counting_command(counter), env={"PATH": empty})
    assert result.returncode == 0, result.stderr
    assert "NOCACHE" in result.stdout and "gate ran" in result.stdout
    assert runs(counter) == 1
    assert records(repo) == [], "no fingerprint means no record"
    stack.clear()


def test_missing_command_is_a_usage_error() -> None:
    stack: list = []
    repo, _counter = scratch(stack)
    result = invoke(repo, "scoped", [])
    assert result.returncode != 0
    assert result.stdout.count("gate-cache ") == 1
    assert records(repo) == []
    stack.clear()


def test_a_same_second_same_size_edit_is_never_a_hit() -> None:
    """A changed tree must never reuse a record, even when Git's cached stat cannot see it."""
    stack: list = []
    repo, counter = scratch(stack)
    # Only mtime, size and inode separate the two revisions below, which is the state a fast
    # edit-then-gate loop produces on a one-second-resolution stat.
    git(repo, "config", "core.trustctime", "false")
    target = repo / "src.txt"
    target.write_text("aaaa\n", encoding="utf-8")
    stamp = os.stat(target).st_mtime_ns
    # Stage a second later so the entry records the real size, then date the index to the file:
    # this is a checkout whose last index write shares a second with its newest file.
    time.sleep(1.1)
    git(repo, "add", "-A")
    os.utime(index_path(repo), ns=(stamp, stamp))

    command = counting_command(counter)
    before = invoke(repo, "scoped", command)
    target.write_text("bbbb\n", encoding="utf-8")
    os.utime(target, ns=(stamp, stamp))
    after = invoke(repo, "scoped", command)

    assert field(before.stdout, "fingerprint") != field(after.stdout, "fingerprint"), (
        "an edit that leaves the cached stat intact must still change the fingerprint"
    )
    assert runs(counter) == 2, "changed content must re-execute the gate"
    stack.clear()


def test_an_unexpected_schema_version_is_absent() -> None:
    stack: list = []
    repo, counter = scratch(stack)
    command = counting_command(counter)
    invoke(repo, "scoped", command)
    record_path = records(repo)[0]
    stored = json.loads(record_path.read_text(encoding="utf-8"))
    stored["version"] = stored["version"] + 998
    record_path.write_text(json.dumps(stored), encoding="utf-8")

    result = invoke(repo, "scoped", command)
    assert "MISS" in result.stdout, "a record of an unknown schema version is absent"
    assert runs(counter) == 2
    stack.clear()


def test_a_partial_record_is_absent() -> None:
    """AC3: a record that does not parse completely never yields a hit, whatever tore it."""
    stack: list = []
    repo, counter = scratch(stack)
    command = counting_command(counter, 3)
    assert invoke(repo, "scoped", command).returncode == 3
    record_path = records(repo)[0]
    complete = json.loads(record_path.read_text(encoding="utf-8"))
    complete["status"] = "pass"
    intact = json.dumps(complete)
    record_path.write_text(intact, encoding="utf-8")

    control = invoke(repo, "scoped", command)
    assert "HIT" in control.stdout and control.returncode == 0
    assert runs(counter) == 1, "the record is otherwise usable, so only its parse state can matter"

    # A prefix of the write, and a parseable record whose write stopped before its later keys.
    partial = json.dumps({k: complete[k] for k in ("command", "gate")})
    for damaged in (intact[: len(intact) // 2], partial, "null", "[]", '"pass"'):
        record_path.write_text(damaged, encoding="utf-8")
        before = runs(counter)
        result = invoke(repo, "scoped", command)
        assert "HIT" not in result.stdout, damaged
        assert result.returncode == 3, "the gate runs again and its status is the tool's status"
        assert runs(counter) == before + 1
        record_path.write_text(intact, encoding="utf-8")
    stack.clear()


def test_each_run_writes_its_own_log_and_leaves_one_behind() -> None:
    """Runs sharing a fingerprint never share a log path, and never leak one per retry either."""
    stack: list = []
    repo, _counter = scratch(stack)
    # Same argv, different output, so a shared path shows up as one run's output overwriting the other.
    command = [sys.executable, "-c", "import os, sys; print(os.getpid()); sys.exit(3)"]
    first = invoke(repo, "scoped", command)
    second = invoke(repo, "scoped", command)
    third = invoke(repo, "scoped", command)

    assert len({field(run.stdout, "log") for run in (first, second, third)}) == 3, "one log per run"
    logs = sorted((repo / ".gate-cache").glob("*.log"))
    assert [path.resolve() for path in logs] == [Path(field(third.stdout, "log")).resolve()], logs
    assert logs[0].read_text(encoding="utf-8").strip().isdigit(), "the surviving log is complete"
    stack.clear()


def test_an_interrupted_command_writes_no_record() -> None:
    stack: list = []
    repo, _counter = scratch(stack)
    argv = [
        sys.executable,
        str(TOOL), "run", "--gate", "scoped", "--root", str(repo),
        "--", sys.executable, "-c", "import time; time.sleep(60)",
    ]
    process = subprocess.Popen(argv, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 30
    while not list((repo / ".gate-cache").glob("*.log")) and time.monotonic() < deadline:
        time.sleep(0.05)
    os.killpg(process.pid, signal.SIGINT)
    process.wait(timeout=30)

    assert records(repo) == [], "an interrupted gate must leave no record"
    stack.clear()


def test_a_staged_change_alters_the_fingerprint() -> None:
    stack: list = []
    repo, counter = scratch(stack)
    command = counting_command(counter)
    before = invoke(repo, "scoped", command)
    (repo / "src.txt").write_text("staged\n", encoding="utf-8")
    git(repo, "add", "-A")
    after = invoke(repo, "scoped", command)

    assert field(before.stdout, "fingerprint") != field(after.stdout, "fingerprint")
    assert runs(counter) == 2, "a staged, uncommitted change must re-execute the gate"
    stack.clear()


def test_the_hit_line_cites_gate_fingerprint_and_log() -> None:
    stack: list = []
    repo, counter = scratch(stack)
    command = counting_command(counter)
    miss = invoke(repo, "scoped", command)
    hit = invoke(repo, "scoped", command)

    assert "HIT" in hit.stdout
    assert field(hit.stdout, "gate") == "scoped"
    assert field(hit.stdout, "fingerprint") == field(miss.stdout, "fingerprint")
    assert Path(field(hit.stdout, "log")).is_file()
    stack.clear()


if __name__ == "__main__":
    test_independent_test_for_p1()
    test_record_contents_and_log()
    test_git_unavailable_runs_and_caches_nothing()
    test_missing_command_is_a_usage_error()
    test_a_same_second_same_size_edit_is_never_a_hit()
    test_an_unexpected_schema_version_is_absent()
    test_a_partial_record_is_absent()
    test_each_run_writes_its_own_log_and_leaves_one_behind()
    test_an_interrupted_command_writes_no_record()
    test_a_staged_change_alters_the_fingerprint()
    test_the_hit_line_cites_gate_fingerprint_and_log()
    print("ok")
