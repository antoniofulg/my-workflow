"""Runnable fake-Orca checks for the shipped assisted coordinator probe."""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from pathlib import Path
from typing import Callable

import orca_assisted_probe as probe


ROOT = Path(__file__).resolve().parent


def test_mutations_are_one_shot_and_reads_reconcile() -> None:
    calls: list[list[str]] = []
    read_attempts = 0
    original = probe.raw

    def fake(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
        nonlocal read_attempts
        calls.append(argv)
        if probe._is_mutation(argv):
            raise probe.ProbeError("induced transient mutation failure")
        read_attempts += 1
        if read_attempts < 3:
            raise probe.ProbeError("induced transient read failure")
        return {"ok": True}

    probe.raw = fake  # type: ignore[assignment]
    try:
        for command in (
            ["orca", "worktree", "create"],
            ["orca", "terminal", "send"],
            ["orca", "worktree", "set"],
            ["orca", "terminal", "stop"],
            ["orca", "worktree", "rm"],
        ):
            try:
                probe.resilient_run(command, attempts=3, interval=0)
            except probe.ProbeError:
                pass
        probe.resilient_run(["orca", "terminal", "show"], attempts=3, interval=0)
    finally:
        probe.raw = original  # type: ignore[assignment]

    mutation_calls = [call for call in calls if probe._is_mutation(call)]
    assert len(mutation_calls) == 5
    assert [call[2] for call in mutation_calls] == ["create", "send", "set", "stop", "rm"]
    assert calls[-3:] == [["orca", "terminal", "show"]] * 3


def test_pointer_transport_excludes_packet_body_and_import_is_inert() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        calls = root / "calls"
        fake = root / "orca"
        fake.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >> \"$CALLS\"\n"
            "case \"$*\" in\n"
            "  *worktree\\ set*) printf '%s\\n' '{\"ok\":false}' ;;\n"
            "  *worktree\\ show*) printf '%s\\n' '{\"result\":{\"worktree\":{\"comment\":\"parked\"}}}' ;;\n"
            "  *terminal\\ stop*) printf '%s\\n' '{\"ok\":false}' ;;\n"
            "  *terminal\\ list*) printf '%s\\n' '{\"result\":{\"terminals\":[]}}' ;;\n"
            "  *worktree\\ rm*) printf '%s\\n' '{\"ok\":false}' ;;\n"
            "  *worktree\\ list*) printf '%s\\n' '{\"result\":{\"worktrees\":[]}}' ;;\n"
            "  *terminal\\ send*) printf '%s\\n' '{\"ok\":false,\"result\":{\"send\":{\"accepted\":false}}}' ;;\n"
            "  *) printf '%s\\n' '{\"ok\":true}' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        packet = root / "coordinator-packet.md"
        worktree = root / "slice-worktree"
        worktree.mkdir()
        packet.write_text("SECRET_PACKET_BODY\n" + ("body line\n" * 80)
                          + "TURN_DONE PHASE head=<current exact 40-hex HEAD>\n", encoding="utf-8")
        log = root / "probe.jsonl"
        env = {**os.environ, "CALLS": str(calls)}
        completed = subprocess.run(
            [sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "--repo", "repo",
             "send-pointer", "--handle", "term-1", "--packet", str(packet), "--worktree", str(worktree), "--log", str(log)],
            capture_output=True, text=True, env=env, check=False,
        )
        assert completed.returncode == 0, completed.stderr
        sent = calls.read_text(encoding="utf-8")
        assert sent.count("terminal send") == 1
        assert f"read {packet.resolve()} and execute it as your packet" in sent
        assert "SECRET_PACKET_BODY" not in sent
        records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        assert records[0]["pointer_chars"] < records[0]["packet_body_chars"]

        for command, options in (
            ("set-comment", ["--worktree", "owned", "--comment", "parked"]),
            ("stop", ["--handle", "owned-terminal"]),
            ("rm", ["--worktree", "owned"]),
        ):
            completed = subprocess.run(
                [sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "--repo", "repo",
                 command, *options], capture_output=True, text=True, env=env, check=False,
            )
            assert completed.returncode == 0, completed.stderr

        import_result = subprocess.run(
            [sys.executable, "-c", f"import runpy; runpy.run_path({str(ROOT / 'orca_assisted_probe.py')!r})"],
            capture_output=True, text=True, env=env, check=False,
        )
        assert import_result.returncode == 0, import_result.stderr
        sent_calls = calls.read_text(encoding="utf-8").splitlines()
        assert sum("terminal send" in call for call in sent_calls) == 1
        assert sum("worktree set" in call for call in sent_calls) == 1
        assert sum("terminal stop" in call for call in sent_calls) == 1
        assert sum("worktree rm" in call for call in sent_calls) == 1


def test_create_reconciles_late_effect_without_duplicate_worktree() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        state = root / "created"
        calls = root / "calls"
        fake = root / "orca"
        candidate = json.dumps({"id": "owned", "repoId": "repo", "displayName": "slice-a",
                                "instanceId": "instance", "path": str(root),
                                "branch": "refs/heads/slice-a", "head": head})
        candidate_payload = json.dumps({"result": {"worktrees": [json.loads(candidate)]}})
        terminal = '{"handle":"owned-terminal","connected":true,"writable":true}'
        fake.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >> '" + str(calls) + "'\n"
            "case \"$*\" in\n"
            "  *worktree\\ create*) touch '" + str(state) + "'; printf '%s\\n' '{\"ok\":false}' ;;\n"
            "  *worktree\\ list*) if test -e '" + str(state) + "'; then printf '%s\\n' '" + candidate_payload.replace("'", "'\\''") + "'; else printf '%s\\n' '{\"result\":{\"worktrees\":[]}}'; fi ;;\n"
            "  *terminal\\ list*--worktree*) printf '%s\\n' '{\"result\":{\"terminals\":[" + terminal + "]}}' ;;\n"
            "  *terminal\\ list*) printf '%s\\n' '{\"result\":{\"terminals\":[]}}' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        receipt = root / "receipt.json"
        args = SimpleNamespace(repo="repo", orca=str(fake), name="slice-a", base="main",
                               receipt=str(receipt), log=str(root / "log"), create_timeout=1.0,
                               settle_window=0.1, interval=0.0)
        with contextlib.redirect_stdout(io.StringIO()):
            probe.create(args)
        assert calls.read_text(encoding="utf-8").count("worktree create") == 1
        assert json.loads(receipt.read_text(encoding="utf-8"))["id"] == "owned"


def test_route_requires_two_consecutive_screen_frames_after_reset() -> None:
    assert probe.route_command("codex", "gpt-5.6-luna", "low") == (
        "exec codex --model gpt-5.6-luna -c model_reasoning_effort=low"
    )
    assert probe.route_command("claude", "sonnet", "medium") == (
        "exec claude --model sonnet --effort medium"
    )
    assert probe.route_command("cursor", "gpt-5.6-luna", "high") == (
        "exec cursor agent --model 'gpt-5.6-luna[effort=high]'"
    )
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        receipt = root / "receipt.json"
        receipt.write_text(json.dumps({"id": "lane", "path": str(root), "branch": "branch",
                                       "pre_head": "a" * 40, "startupTerminal": {"handle": "h"},
                                       "gitdir": "", "worktree_gitdir": "",
                                       "before": {"terminals": {}}}), encoding="utf-8")
        reads = [
            {"source": "screen", "text": "Claude Code Sonnet 5 with low effort"},
            {"source": "ansi", "text": "Claude Code Sonnet 5 with low effort"},
            {"source": "screen", "text": "Claude Code Sonnet 5 with low effort"},
            {"source": "screen", "text": "Claude Code Sonnet 5 with low effort"},
        ]
        read_index = 0
        sends: list[list[str]] = []
        original_raw = probe.raw
        original_run = probe.OrcaProbe.run

        def fake_raw(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            sends.append(argv)
            return {"ok": False}

        def fake_run(self: object, argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            nonlocal read_index
            if "list" in argv:
                return {"result": {"terminals": [{"handle": "h"}]}}
            if "wait" in argv:
                return {"ok": True}
            if "read" in argv:
                value = reads[min(read_index, len(reads) - 1)]
                read_index += 1
                return {"result": {"terminal": value}}
            return {"result": {"terminal": {"handle": "h", "connected": True,
                                                "writable": True, "agentWait": None, "preview": "❯"}}}

        probe.raw = fake_raw  # type: ignore[assignment]
        probe.OrcaProbe.run = fake_run  # type: ignore[assignment]
        args = SimpleNamespace(repo="repo", orca="orca", receipt=str(receipt), log=str(root / "route.log"),
                               provider="claude", model="sonnet", effort="low", timeout=1.0,
                               send_timeout=1.0, interval=0.0)
        try:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                probe.route(args)
        finally:
            probe.raw = original_raw  # type: ignore[assignment]
            probe.OrcaProbe.run = original_run  # type: ignore[assignment]
        assert len([call for call in sends if "send" in call]) == 1
        assert read_index == 4
        assert output.getvalue().count('"status": "accepted"') == 1


def test_cleanup_refuses_when_owned_branch_ref_remains() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        receipt = root / "receipt.json"
        common_git = root.parent / f"common-{root.name}.git"
        admin = common_git / "worktrees" / "lane"
        admin.mkdir(parents=True)
        (admin / "gitdir").write_text(str(root / ".git") + "\n", encoding="utf-8")
        head = "a" * 40
        receipt.write_text(json.dumps({"id": "lane", "path": str(root), "branch": "refs/heads/lane",
                                       "instance": "instance", "pre_head": head, "gitdir": str(common_git),
                                       "worktree_gitdir": str(admin),
                                       "startupTerminal": {"handle": "h"}, "before": {"terminals": {}}}), encoding="utf-8")
        before = {"worktrees": {"lane": {"id": "lane", "repoId": "repo", "instanceId": "instance",
                                           "path": str(root.resolve()), "branch": "refs/heads/lane"}}, "terminals": {}}
        original_inventory = probe.OrcaProbe.inventory
        original_terminals = probe.OrcaProbe.worktree_terminals
        original_git = probe.git
        probe.OrcaProbe.inventory = lambda self: before  # type: ignore[assignment]
        probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: []  # type: ignore[assignment]

        def fake_git(path: str | Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
            if args[:2] == ("rev-parse", "--git-common-dir"):
                return subprocess.CompletedProcess([], 0, str(common_git) + "\n", "")
            if "worktree" in args and "list" in args:
                return subprocess.CompletedProcess([], 0, f"worktree {root}\n", "")
            if args[:2] == ("show-ref", "--verify"):
                return subprocess.CompletedProcess([], 0, "", "")
            if args[:2] == ("rev-parse", "HEAD") or args[:2] == ("rev-parse", "refs/heads/lane"):
                return subprocess.CompletedProcess([], 0, head + "\n", "")
            return subprocess.CompletedProcess([], 0, "", "")

        probe.git = fake_git  # type: ignore[assignment]
        args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--receipt", str(receipt),
                                          "--integration-head", head, "--settle-window", "0"])
        try:
            try:
                probe.cleanup(args)
            except probe.ProbeError as error:
                assert "branch ref remains" in str(error)
            else:
                raise AssertionError("cleanup must fail closed while owned ref remains")
        finally:
            probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = original_terminals  # type: ignore[assignment]
            probe.git = original_git  # type: ignore[assignment]


def test_cleanup_stops_only_owned_handle_and_preserves_foreign_worktree() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        worktree = root / "lane"
        worktree.mkdir()
        common_git = root / "common.git"
        admin = common_git / "worktrees" / "owned"
        admin.mkdir(parents=True)
        (admin / "gitdir").write_text(str(worktree / ".git") + "\n", encoding="utf-8")
        foreign_admin = common_git / "worktrees" / "foreign"
        foreign_admin.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=worktree, check=True)
        (worktree / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=worktree, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        subprocess.run(["git", "branch", "owned"], cwd=worktree, check=True)
        receipt_path = root / "receipt.json"
        receipt_path.write_text(
            json.dumps({
                "id": "owned-worktree", "path": str(worktree), "branch": "refs/heads/owned",
                "instance": "owned-instance", "pre_head": head, "gitdir": str(common_git),
                "worktree_gitdir": str(admin),
                "startupTerminal": {"handle": "owned-terminal"},
                "before": {"terminals": {}, "worktrees": {}},
            }), encoding="utf-8",
        )
        before = {"worktrees": {"owned-worktree": {"id": "owned-worktree", "repoId": "repo", "instanceId": "owned-instance", "path": str(worktree.resolve()), "branch": "refs/heads/owned"}, "foreign": {"id": "foreign"}}, "terminals": {"owned-terminal": {"handle": "owned-terminal"}, "foreign-terminal": {"handle": "foreign-terminal"}}}
        after = {"worktrees": {"foreign": {"id": "foreign"}}, "terminals": {"foreign-terminal": {"handle": "foreign-terminal"}}}
        inventories = iter((before, after, after))
        calls: list[list[str]] = []
        state = {"stopped": False, "removed": False}
        original_raw = probe.raw
        original_inventory = probe.OrcaProbe.inventory
        original_terminals = probe.OrcaProbe.worktree_terminals
        original_git = probe.git

        def fake_raw(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            calls.append(argv)
            if len(argv) > 2 and argv[2] == "stop":
                state["stopped"] = True
            if len(argv) > 2 and argv[2] == "rm":
                shutil.rmtree(worktree)
                shutil.rmtree(admin)
                state["removed"] = True
            return {"ok": False}

        probe.raw = fake_raw  # type: ignore[assignment]
        probe.OrcaProbe.inventory = lambda self: next(inventories)  # type: ignore[assignment]
        probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: [] if state["stopped"] else [{"handle": "owned-terminal"}]  # type: ignore[assignment]
        def fake_git(path: str | Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
            if args[:2] == ("rev-parse", "--git-common-dir"):
                return subprocess.CompletedProcess([], 0, str(common_git) + "\n", "")
            if "worktree" in args and "list" in args:
                paths = [] if state["removed"] else [str(worktree)]
                return subprocess.CompletedProcess([], 0, "".join(f"worktree {value}\n" for value in paths), "")
            if "for-each-ref" in args:
                return subprocess.CompletedProcess([], 0, "refs/heads/owned\nrefs/heads/foreign\n", "")
            if "show-ref" in args:
                return subprocess.CompletedProcess([], 1, "", "")
            if args[:2] in (("rev-parse", "HEAD"), ("rev-parse", "refs/heads/owned")):
                return subprocess.CompletedProcess([], 0, head + "\n", "")
            return subprocess.CompletedProcess([], 0, "", "")
        probe.git = fake_git  # type: ignore[assignment]
        args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--receipt", str(receipt_path), "--integration-head", head])
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                probe.cleanup(args)
        finally:
            probe.raw = original_raw  # type: ignore[assignment]
            probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = original_terminals  # type: ignore[assignment]
            probe.git = original_git  # type: ignore[assignment]
        assert [call[2] for call in calls] == ["stop", "rm"]
        assert calls[0][4] == "owned-terminal"
        assert calls[1][4] == "id:owned-worktree"
        assert "foreign" in after["worktrees"]
        assert "foreign-terminal" in after["terminals"]


def _cleanup_failure_case(*, retain_owned: bool, remove_foreign: bool,
                          remove_foreign_ref: bool = False, fail_ref_audit: bool = False,
                          fail_ref_state: bool = False) -> str:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        common_git = root.parent / f"common-{root.name}.git"
        admin = common_git / "worktrees" / "lane"
        admin.mkdir(parents=True)
        (admin / "gitdir").write_text(str(root / ".git") + "\n", encoding="utf-8")
        foreign_admin = common_git / "worktrees" / "foreign"
        foreign_admin.mkdir()
        foreign_path = root.parent / f"foreign-{root.name}"
        foreign_path.write_text("foreign\n", encoding="utf-8")
        head = "a" * 40
        receipt_path = root / "receipt.json"
        receipt_path.write_text(json.dumps({"id": "lane", "path": str(root), "branch": "refs/heads/lane",
                                            "instance": "instance", "pre_head": head,
                                            "gitdir": str(common_git),
                                            "worktree_gitdir": str(admin),
                                            "startupTerminal": {"handle": "owned-terminal"},
                                            "before": {"terminals": {}}}), encoding="utf-8")
        before = {"worktrees": {"lane": {"id": "lane", "repoId": "repo", "instanceId": "instance",
                                           "path": str(root.resolve()), "branch": "refs/heads/lane"},
                                 "foreign": {"id": "foreign"}},
                  "terminals": {"owned-terminal": {"handle": "owned-terminal"},
                                "foreign-terminal": {"handle": "foreign-terminal"}}}
        settled = {"worktrees": {"foreign": {"id": "foreign"}},
                   "terminals": {"foreign-terminal": {"handle": "foreign-terminal"}}}
        final = before if retain_owned else settled
        inventories = iter((before, settled, final))
        stopped = {"value": False, "removed": False}
        original_raw = probe.raw
        original_inventory = probe.OrcaProbe.inventory
        original_terminals = probe.OrcaProbe.worktree_terminals
        original_git = probe.git

        def fake_raw(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            if len(argv) > 2 and argv[2] == "stop":
                stopped["value"] = True
            if len(argv) > 2 and argv[2] == "rm":
                stopped["removed"] = True
                if remove_foreign:
                    foreign_path.unlink()
                if not retain_owned:
                    shutil.rmtree(root)
                    shutil.rmtree(admin)
            return {"ok": False}

        def fake_git(path: str | Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
            if args[:2] == ("rev-parse", "--git-common-dir"):
                return subprocess.CompletedProcess([], 0, str(common_git) + "\n", "")
            if "worktree" in args and "list" in args:
                paths = [] if stopped["removed"] else [str(root)]
                return subprocess.CompletedProcess([], 0, "".join(f"worktree {value}\n" for value in paths), "")
            if "for-each-ref" in args:
                if stopped["removed"] and fail_ref_audit:
                    return subprocess.CompletedProcess([], 1, "", "ref audit failed")
                refs = "refs/heads/lane\n" if stopped["removed"] and remove_foreign_ref else "refs/heads/lane\nrefs/heads/foreign\n"
                return subprocess.CompletedProcess([], 0, refs, "")
            if "show-ref" in args:
                if fail_ref_state:
                    return subprocess.CompletedProcess([], 128, "", "fatal: ref state unavailable")
                return subprocess.CompletedProcess([], 1, "", "")
            if args[:2] in (("rev-parse", "HEAD"), ("rev-parse", "refs/heads/lane")):
                return subprocess.CompletedProcess([], 0, head + "\n", "")
            return subprocess.CompletedProcess([], 0, "", "")

        probe.raw = fake_raw  # type: ignore[assignment]
        probe.OrcaProbe.inventory = lambda self: next(inventories)  # type: ignore[assignment]
        probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: [] if stopped["value"] else [{"handle": "owned-terminal"}]  # type: ignore[assignment]
        probe.git = fake_git  # type: ignore[assignment]
        args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--receipt", str(receipt_path),
                                          "--integration-head", head, "--foreign-path", str(foreign_path),
                                          "--settle-window", "0.01", "--interval", "0"])
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                probe.cleanup(args)
        except probe.ProbeError as error:
            return str(error)
        finally:
            probe.raw = original_raw  # type: ignore[assignment]
            probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = original_terminals  # type: ignore[assignment]
            probe.git = original_git  # type: ignore[assignment]
            if foreign_path.exists():
                foreign_path.unlink()
        raise AssertionError("cleanup unexpectedly reported success")


def test_cleanup_refuses_owned_residue_after_rm() -> None:
    assert "owned residue" in _cleanup_failure_case(retain_owned=True, remove_foreign=False)


def test_cleanup_refuses_foreign_resource_change() -> None:
    assert "foreign resource" in _cleanup_failure_case(retain_owned=False, remove_foreign=True)


def test_cleanup_refuses_foreign_branch_ref_change() -> None:
    assert "foreign resource" in _cleanup_failure_case(
        retain_owned=False, remove_foreign=False, remove_foreign_ref=True
    )


def test_cleanup_refuses_ref_audit_failure() -> None:
    assert "could not enumerate repository refs after cleanup" in _cleanup_failure_case(
        retain_owned=False, remove_foreign=False, fail_ref_audit=True
    )


def test_cleanup_refuses_show_ref_error() -> None:
    assert "could not verify repository ref state" in _cleanup_failure_case(
        retain_owned=False, remove_foreign=False, fail_ref_state=True
    )


def _cleanup_git_residue_case(*, retain_registration: bool, retain_gitdir: bool) -> str:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = root / "repo"
        worktree = root / "lane"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        (repo / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=repo, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=repo, check=True)
        subprocess.run(["git", "worktree", "add", "-q", "-b", "lane", str(worktree), "HEAD"], cwd=repo, check=True)
        common_git = Path(subprocess.check_output(
            ["git", "-C", str(worktree), "rev-parse", "--git-common-dir"], text=True,
        ).strip()).resolve()
        worktree_gitdir = Path(subprocess.check_output(
            ["git", "-C", str(worktree), "rev-parse", "--git-dir"], text=True,
        ).strip()).resolve()
        head = subprocess.check_output(["git", "-C", str(worktree), "rev-parse", "HEAD"], text=True).strip()
        if retain_registration:
            stale = common_git / "worktrees" / "stale"
            shutil.copytree(worktree_gitdir, stale)
            (stale / "HEAD").write_text(head + "\n", encoding="utf-8")
        receipt_path = root / "receipt.json"
        receipt_path.write_text(json.dumps({
            "id": "lane", "path": str(worktree), "branch": "refs/heads/lane",
            "instance": "instance", "pre_head": head, "gitdir": str(common_git),
            "worktree_gitdir": str(worktree_gitdir),
            "startupTerminal": {"handle": "owned-terminal"}, "before": {"terminals": {}},
        }), encoding="utf-8")
        before = {"worktrees": {"lane": {
            "id": "lane", "repoId": "repo", "instanceId": "instance",
            "path": str(worktree.resolve()), "branch": "refs/heads/lane",
        }}, "terminals": {}}
        after = {"worktrees": {}, "terminals": {}}
        inventories = iter((before, after, after))
        original_raw = probe.raw
        original_inventory = probe.OrcaProbe.inventory
        original_terminals = probe.OrcaProbe.worktree_terminals

        def fake_raw(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            if argv[1:3] == ["worktree", "rm"]:
                shutil.rmtree(worktree)
                if retain_registration:
                    shutil.rmtree(worktree_gitdir)
                elif not retain_gitdir:
                    shutil.rmtree(worktree_gitdir)
                else:
                    (worktree_gitdir / "gitdir").unlink()
            return {"ok": False}

        probe.raw = fake_raw  # type: ignore[assignment]
        probe.OrcaProbe.inventory = lambda self: next(inventories)  # type: ignore[assignment]
        probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: []  # type: ignore[assignment]
        args = probe.parser().parse_args([
            "--repo", "repo", "cleanup", "--receipt", str(receipt_path),
            "--integration-head", head, "--settle-window", "1", "--interval", "0",
        ])
        try:
            try:
                probe.cleanup(args)
            except probe.ProbeError as error:
                return str(error)
            raise AssertionError("cleanup unexpectedly accepted Git residue")
        finally:
            probe.raw = original_raw  # type: ignore[assignment]
            probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = original_terminals  # type: ignore[assignment]


def test_cleanup_refuses_registration_residue_after_path_removal() -> None:
    assert "owned residue" in _cleanup_git_residue_case(retain_registration=True, retain_gitdir=False)


def test_cleanup_refuses_admin_gitdir_residue_after_registration_and_path_removal() -> None:
    assert "owned residue" in _cleanup_git_residue_case(retain_registration=False, retain_gitdir=True)


def test_task_states_reads_canonical_records_and_effect_requires_ids() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "tasks.md").write_text(
            "### T1: producer\n\n**Status:** complete\n\n"
            "### T2: dependent\n\n**Status:** pending\n",
            encoding="utf-8",
        )
        assert probe.task_states(root) == {"T1": "complete", "T2": "pending"}
        try:
            probe.effect(
                SimpleNamespace(expected_task=[], timeout=1.0),
                probe.OrcaProbe("repo"),
                {"startupTerminal": {"handle": "handle"}},
                {"ok": False},
            )
        except probe.ProbeError as error:
            assert "expected task ids are required" in str(error)
        else:
            raise AssertionError("effect must require canonical expected task ids")


def test_effect_reconciliation_accepts_one_same_handle_commit() -> None:
    with tempfile.TemporaryDirectory() as directory:
        worktree = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=worktree, check=True)
        (worktree / "change.txt").write_text("before\n", encoding="utf-8")
        (worktree / "tasks.md").write_text("### T1: one slice\n\n**Status:** complete\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt", "tasks.md"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=worktree, check=True)
        pre_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        (worktree / "change.txt").write_text("after\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt", "tasks.md"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "feat: one slice"], cwd=worktree, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        receipt = {"id": "lane", "path": str(worktree), "startupTerminal": {"handle": "same-handle"}}
        args = SimpleNamespace(
            phase="A_FINAL", timeout=1.0, log=str(worktree.parent / "effect-log"), pre_head=pre_head,
            expected_count=1, expected_subject=["feat: one slice"], expected_task=["T1"],
            allow_path=["change.txt"], task_file="tasks.md", gate=["true"], park_comment="",
        )
        original_marker_frame = probe.marker_frame
        original_worktree_comment = probe.worktree_comment
        probe.marker_frame = lambda _probe, handle, phase: (head, None,
            {"result": {"terminal": {"handle": handle, "connected": True}}},
            {"result": {"terminal": {"handle": handle, "source": "screen"}}},
            f"TURN_DONE {phase} head={head}")
        probe.worktree_comment = lambda *_args: ""
        configured = probe.OrcaProbe("repo")
        configured.run = lambda _argv, timeout=30.0: {"ok": True}  # type: ignore[method-assign]
        try:
            result = probe.effect(args, configured, receipt, {"ok": False})
        finally:
            probe.marker_frame = original_marker_frame
            probe.worktree_comment = original_worktree_comment
        assert result["checks"]["same_handle"] is True
        assert result["checks"]["commit_subjects"] is True
        assert result["checks"]["paths"] is True
        assert result["checks"]["tasks"] is True


def test_effect_reconciliation_rejects_pending_expected_task() -> None:
    with tempfile.TemporaryDirectory() as directory:
        worktree = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=worktree, check=True)
        (worktree / "change.txt").write_text("before\n", encoding="utf-8")
        (worktree / "tasks.md").write_text("### T1: one slice\n\n**Status:** pending\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt", "tasks.md"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=worktree, check=True)
        pre_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        (worktree / "change.txt").write_text("after\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "feat: one slice"], cwd=worktree, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        receipt = {"id": "lane", "path": str(worktree), "startupTerminal": {"handle": "same-handle"}}
        args = SimpleNamespace(
            phase="A_FINAL", timeout=1.0, log=str(worktree.parent / "pending-effect-log"), pre_head=pre_head,
            expected_count=1, expected_subject=["feat: one slice"], expected_task=["T1"],
            allow_path=["change.txt"], task_file="tasks.md", gate=["true"], park_comment="",
        )
        original_marker_frame = probe.marker_frame
        original_worktree_comment = probe.worktree_comment
        probe.marker_frame = lambda _probe, handle, phase: (
            head, None,
            {"result": {"terminal": {"handle": handle, "connected": True}}},
            {"result": {"terminal": {"handle": handle, "source": "screen"}}},
            f"TURN_DONE {phase} head={head}",
        )
        probe.worktree_comment = lambda *_args: ""
        configured = probe.OrcaProbe("repo")
        configured.run = lambda _argv, timeout=30.0: {"ok": True}  # type: ignore[method-assign]
        try:
            try:
                probe.effect(args, configured, receipt, {"ok": False})
            except probe.ProbeError as error:
                assert "incomplete or ambiguous effect" in str(error)
            else:
                raise AssertionError("pending expected task must fail reconciliation")
        finally:
            probe.marker_frame = original_marker_frame
            probe.worktree_comment = original_worktree_comment


def test_effect_requires_positive_count_and_matching_subjects() -> None:
    for expected_count, expected_subject, message in (
        (0, ["feat: slice"], "expected commit count must be positive"),
        (1, [], "expected commit subjects must match expected commit count"),
        (2, ["feat: slice"], "expected commit subjects must match expected commit count"),
    ):
        try:
            probe.effect(
                SimpleNamespace(
                    expected_task=["T1"], expected_count=expected_count,
                    expected_subject=expected_subject, timeout=1.0,
                ),
                probe.OrcaProbe("repo"),
                {"startupTerminal": {"handle": "handle"}},
                {"ok": False},
            )
        except probe.ProbeError as error:
            assert message in str(error)
        else:
            raise AssertionError("invalid commit expectations must fail before reconciliation")


def test_effect_reconciliation_rejects_foreign_second_frame_handle() -> None:
    with tempfile.TemporaryDirectory() as directory:
        worktree = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=worktree, check=True)
        (worktree / "change.txt").write_text("before\n", encoding="utf-8")
        (worktree / "tasks.md").write_text("### T1: one slice\n\n**Status:** complete\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt", "tasks.md"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=worktree, check=True)
        pre_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        (worktree / "change.txt").write_text("after\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "feat: one slice"], cwd=worktree, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        receipt = {"id": "lane", "path": str(worktree), "startupTerminal": {"handle": "same-handle"}}
        args = SimpleNamespace(phase="A_FINAL", timeout=1.0, log=str(worktree.parent / "foreign-log"),
                              pre_head=pre_head, expected_count=1, expected_subject=["feat: one slice"],
                              expected_task=["T1"], allow_path=["change.txt"], task_file="tasks.md",
                              gate=["true"], park_comment="")
        frames = iter(("same-handle", "foreign-handle"))
        original_marker_frame = probe.marker_frame
        original_worktree_comment = probe.worktree_comment
        probe.marker_frame = lambda _probe, handle, phase: (
            head, None,
            {"result": {"terminal": {"handle": next(frames), "connected": True}}},
            {"result": {"terminal": {"handle": handle, "source": "screen"}}},
            f"TURN_DONE {phase} head={head}",
        )
        probe.worktree_comment = lambda *_args: ""
        configured = probe.OrcaProbe("repo")
        configured.run = lambda _argv, timeout=30.0: {"ok": True}  # type: ignore[method-assign]
        try:
            try:
                probe.effect(args, configured, receipt, {"ok": False})
            except probe.ProbeError as error:
                assert "incomplete or ambiguous effect" in str(error)
            else:
                raise AssertionError("foreign handle must fail reconciliation")
        finally:
            probe.marker_frame = original_marker_frame
            probe.worktree_comment = original_worktree_comment


def test_sync_moves_dependent_lane_to_exact_producer_commit_and_gate() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
        seed = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        subprocess.run(["git", "switch", "-c", "producer"], cwd=root, check=True, capture_output=True)
        (root / "producer").write_text("producer\n", encoding="utf-8")
        subprocess.run(["git", "add", "producer"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "producer"], cwd=root, check=True)
        producer = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        subprocess.run(["git", "switch", "-c", "dependent", seed], cwd=root, check=True, capture_output=True)
        args = SimpleNamespace(worktree=str(root), commit=producer, gate=["true"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            probe.sync_commit(args)
        assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == producer
        assert '"status": "synchronized"' in output.getvalue()


def test_fake_two_slice_lifecycle_parks_syncs_resumes_integrates_and_cleans() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "tasks.md").write_text(
            "### T1: producer\n\n**Status:** pending\n\n"
            "### T2: dependent\n\n**Status:** pending\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "tasks.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
        subprocess.run(["git", "branch", "foreign"], cwd=root, check=True)
        seed = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        producer_path, dependent_path = root / "producer", root / "dependent"
        subprocess.run(["git", "worktree", "add", "-q", "-b", "slice-a", str(producer_path)], cwd=root, check=True)
        subprocess.run(["git", "worktree", "add", "-q", "-b", "slice-b", str(dependent_path)], cwd=root, check=True)

        common_git = Path(subprocess.check_output(
            ["git", "-C", str(producer_path), "rev-parse", "--git-common-dir"],
            text=True,
        ).strip()).resolve()

        (producer_path / "tasks.md").write_text(
            "### T1: producer\n\n**Status:** complete\n\n"
            "### T2: dependent\n\n**Status:** pending\n",
            encoding="utf-8",
        )
        (producer_path / "producer.txt").write_text("producer\n", encoding="utf-8")
        subprocess.run(["git", "add", "tasks.md", "producer.txt"], cwd=producer_path, check=True)
        subprocess.run(["git", "commit", "-qm", "feat: producer slice"], cwd=producer_path, check=True)
        producer_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=producer_path, text=True).strip()

        handles = {"producer": "handle-a", "dependent": "handle-b"}
        receipt_probe = probe.OrcaProbe("repo", interval=0)
        receipt_probe.worktree_terminals = lambda worktree_id: [{
            "handle": handles["producer" if worktree_id == "lane-a" else "dependent"]
        }]  # type: ignore[method-assign]
        receipts = {}
        for name, worktree_id, worktree_path, branch, instance in (
            ("producer", "lane-a", producer_path, "refs/heads/slice-a", "instance-a"),
            ("dependent", "lane-b", dependent_path, "refs/heads/slice-b", "instance-b"),
        ):
            receipts[name] = probe.make_receipt(
                receipt_probe,
                {"id": worktree_id, "instanceId": instance, "path": str(worktree_path),
                 "branch": branch, "head": seed},
                {"terminals": {}, "worktrees": {}},
                {"handle": handles[name]},
            )
        assert receipts["producer"]["gitdir"] == str(common_git)
        assert receipts["dependent"]["gitdir"] == str(common_git)
        producer_registration = producer_path.resolve()
        dependent_registration = dependent_path.resolve()
        foreign_git_registrations = probe.worktree_registrations(common_git) - {
            producer_registration, dependent_registration
        }
        assert producer_registration in probe.worktree_registrations(common_git)
        assert dependent_registration in probe.worktree_registrations(common_git)
        heads = {handles["producer"]: producer_head}
        marker_original = probe.marker_frame
        comment_original = probe.worktree_comment
        run_original = probe.OrcaProbe.run
        probe.marker_frame = lambda _probe, handle, phase: (
            heads[handle], None,
            {"result": {"terminal": {"handle": handle, "connected": True}}},
            {"result": {"terminal": {"handle": handle, "source": "screen"}}},
            f"TURN_DONE {phase} head={heads[handle]}",
        )
        probe.worktree_comment = lambda _probe, worktree_id: comments.get(worktree_id, "")
        configured = probe.OrcaProbe("repo", interval=0)
        configured.run = lambda _argv, timeout=30.0: {"ok": True}  # type: ignore[method-assign]
        try:
            producer_args = SimpleNamespace(
                phase="A_FINAL", timeout=1.0, log=str(root / "producer-effect.log"), pre_head=seed,
                expected_count=1, expected_subject=["feat: producer slice"], expected_task=["T1"],
                allow_path=["tasks.md", "producer.txt"], task_file="tasks.md", gate=["true"], park_comment="",
            )
            producer_effect = probe.effect(producer_args, configured, receipts["producer"], {"ok": False})
            assert producer_effect["checks"]["tasks"] is True

            comments: dict[str, str] = {}
            worktrees = {
                "lane-a": {"id": "lane-a", "repoId": "repo", "instanceId": "instance-a",
                           "path": str(producer_path.resolve()), "branch": "refs/heads/slice-a"},
                "lane-b": {"id": "lane-b", "repoId": "repo", "instanceId": "instance-b",
                           "path": str(dependent_path.resolve()), "branch": "refs/heads/slice-b"},
                "foreign": {"id": "foreign"},
            }
            terminals = {"handle-a": {"handle": "handle-a"}, "handle-b": {"handle": "handle-b"},
                         "foreign-terminal": {"handle": "foreign-terminal"}}
            calls: list[list[str]] = []
            original_raw = probe.raw
            original_inventory = probe.OrcaProbe.inventory
            original_terminals = probe.OrcaProbe.worktree_terminals

            def fake_raw(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
                calls.append(argv)
                if argv[1:3] == ["worktree", "set"]:
                    comments[argv[4].removeprefix("id:")] = argv[6]
                elif argv[1:3] == ["terminal", "stop"]:
                    terminals.pop(argv[4], None)
                elif argv[1:3] == ["worktree", "rm"]:
                    worktree_id = argv[4].removeprefix("id:")
                    worktrees.pop(worktree_id, None)
                    worktree_path = Path(receipts["producer" if worktree_id == "lane-a" else "dependent"]["path"])
                    removed = subprocess.run(
                        ["git", "-C", str(root), "worktree", "remove", "--force", str(worktree_path)],
                        capture_output=True, text=True, check=False,
                    )
                    assert removed.returncode == 0, removed.stderr
                return {"ok": False}

            probe.raw = fake_raw  # type: ignore[assignment]
            probe.OrcaProbe.inventory = lambda self: {"worktrees": dict(worktrees), "terminals": dict(terminals)}  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: [terminals[handles["producer" if worktree_id == "lane-a" else "dependent"]]] if handles["producer" if worktree_id == "lane-a" else "dependent"] in terminals else []  # type: ignore[assignment]

            comment_args = probe.parser().parse_args([
                "--repo", "repo", "set-comment", "--worktree", "lane-b", "--comment", "parked slice-b at T1",
                "--settle-window", "1", "--interval", "0",
            ])
            probe.set_comment(comment_args)
            assert comments["lane-b"] == "parked slice-b at T1"

            gate_command = [sys.executable, "-c", "from pathlib import Path; assert '**Status:** complete' in Path('tasks.md').read_text()"]
            sync_output = io.StringIO()
            with contextlib.redirect_stdout(sync_output):
                probe.sync_commit(SimpleNamespace(worktree=str(dependent_path), commit=producer_head, gate=gate_command))
            assert '"status": "synchronized"' in sync_output.getvalue()

            packet = root / "dependent-packet.md"
            packet.write_text(
                "DEPENDENT_PACKET_SECRET\nTURN_DONE B_FINAL head=<current exact 40-hex HEAD>\n",
                encoding="utf-8",
            )
            probe.send_pointer(configured, handles["dependent"], packet, root / "dependent-send.log",
                               worktree=dependent_path, phase="B_FINAL", turn_id="turn-b")

            (dependent_path / "tasks.md").write_text(
                "### T1: producer\n\n**Status:** complete\n\n"
                "### T2: dependent\n\n**Status:** complete\n",
                encoding="utf-8",
            )
            (dependent_path / "dependent.txt").write_text("dependent\n", encoding="utf-8")
            subprocess.run(["git", "add", "tasks.md", "dependent.txt"], cwd=dependent_path, check=True)
            subprocess.run(["git", "commit", "-qm", "feat: dependent slice"], cwd=dependent_path, check=True)
            dependent_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dependent_path, text=True).strip()
            heads[handles["dependent"]] = dependent_head
            dependent_effect = probe.effect(SimpleNamespace(
                phase="B_FINAL", timeout=1.0, log=str(root / "dependent-effect.log"), pre_head=producer_head,
                expected_count=1, expected_subject=["feat: dependent slice"], expected_task=["T2"],
                allow_path=["tasks.md", "dependent.txt"], task_file="tasks.md", gate=gate_command, park_comment="",
            ), configured, receipts["dependent"], {"ok": False})
            assert dependent_effect["checks"]["tasks"] is True
            assert dependent_effect["checks"]["same_handle"] is True

            subprocess.run(["git", "merge", "--ff-only", dependent_head], cwd=root, check=True, capture_output=True)
            integration_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            for name in ("producer", "dependent"):
                cleanup_args = probe.parser().parse_args([
                    "--repo", "repo", "cleanup", "--receipt", str(root / f"{name}.receipt.json"),
                    "--integration-head", integration_head, "--settle-window", "1", "--interval", "0",
                ])
                (root / f"{name}.receipt.json").write_text(json.dumps(receipts[name]), encoding="utf-8")
                with contextlib.redirect_stdout(io.StringIO()):
                    probe.cleanup(cleanup_args)
                assert Path(receipts[name]["path"]).resolve() not in probe.worktree_registrations(common_git)
                assert not Path(receipts[name]["worktree_gitdir"]).exists()
                assert probe.worktree_registrations(common_git) == foreign_git_registrations | {
                    Path(value["path"]).resolve() for value in receipts.values() if Path(value["path"]).exists()
                }
            assert [call[2] for call in calls if len(call) > 2 and call[2] in {"stop", "rm"}] == ["stop", "rm", "stop", "rm"]
            sends = [call for call in calls if len(call) > 2 and call[2] == "send"]
            assert len(sends) == 1
            assert sends[0][sends[0].index("--text") + 1] == f"read {packet.resolve()} and execute it as your packet"
            assert "DEPENDENT_PACKET_SECRET" not in " ".join(sends[0])
            assert "foreign" in worktrees
            assert "foreign-terminal" in terminals
        finally:
            probe.marker_frame = marker_original
            probe.worktree_comment = comment_original
            probe.OrcaProbe.run = run_original
            if "original_raw" in locals():
                probe.raw = original_raw  # type: ignore[assignment]
                probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
                probe.OrcaProbe.worktree_terminals = original_terminals  # type: ignore[assignment]


def main() -> None:
    checks: tuple[Callable[[], None], ...] = tuple(
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    )
    executed = 0
    for check in checks:
        check()
        executed += 1
    if executed != len(checks):
        raise AssertionError(f"executed {executed} of {len(checks)} declared checks")
    print(f"orca assisted probe contract: {executed}/{len(checks)} passed")


if __name__ == "__main__":
    main()
