"""Runnable fake-provider checks for the public assisted probe lifecycle."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import orca_assisted_probe as probe


ROOT = Path(__file__).resolve().parent


def _repo(root: Path) -> str:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    (root / "seed").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "seed"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def _fake_orca(path: Path, calls: Path) -> None:
    path.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> {calls!s}\n"
        "printf '%s\\n' '{\"ok\":true}'\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _request(root: Path, head: str, *, effects: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "schema_version": probe.STATE_SCHEMA, "repository": "repo", "repository_root": str(root),
        "slice_id": "S4", "task_id": "T7", "operation_id": "op-S4-T7",
        "terminal_handle": "terminal-S4", "route": "exec codex --model gpt --effort low",
        "commit_id": head, "lease_id": "lease-S4", "worktree_id": "worktree-S4",
        "worktree_path": str(root), "branch": "refs/heads/main", "pre_head": head,
        "gitdir": str((root / ".git").resolve()), "worktree_gitdir": str((root / ".git").resolve()),
        "packet_path": "state/packet.md", "log_path": "state/probe.jsonl", "receipt_path": "state/receipt.json",
        "packet_body": "SECRET_PACKET_BODY\nTURN_DONE S4 head=<current exact 40-hex HEAD>\n",
        "instance": "instance-S4", "before": {"terminals": {}, "worktrees": {}},
        "effects": effects or [],
    }


def test_IT006_public_surface_is_exactly_three_commands() -> None:
    actions = probe.parser()._subparsers._group_actions[0].choices  # type: ignore[attr-defined]
    assert set(actions) == {"dispatch", "inspect", "cleanup"}


def test_IT006_IT011_SEC005_dispatch_persists_complete_state_and_sends_only_pointer() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); calls, fake = root / "calls", root / "orca"
        _fake_orca(fake, calls)
        request_path, state_path = root / "request.json", root / "state.json"
        request_path.write_text(json.dumps(_request(root, head)), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "dispatch",
                                    "--request", str(request_path), "--state", str(state_path)], capture_output=True, text=True, check=False)
        assert completed.returncode == 0, completed.stderr
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["status"] == "pointer_sent"
        assert set(probe.STATE_FIELDS).issubset(state)
        assert state["receipt"]["id"] == state["worktree_id"]
        sent = calls.read_text(encoding="utf-8")
        assert sent.count("terminal send") == 1
        assert "SECRET_PACKET_BODY" not in sent
        assert str((root / "state" / "packet.md").resolve()) in sent


def test_SEC001_dispatch_rejects_outside_state_and_symlinked_packet_before_orca() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); calls, fake = root / "calls", root / "orca"
        _fake_orca(fake, calls); request = _request(root, head)
        outside = root.parent / "outside-state.json"; request_path = root / "request.json"
        request_path.write_text(json.dumps(request), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "dispatch",
                                    "--request", str(request_path), "--state", str(outside)], capture_output=True, text=True, check=False)
        assert completed.returncode != 0; assert not outside.exists()
        link = root / "state" / "link.md"; link.parent.mkdir(); link.symlink_to(root / "seed")
        request["packet_path"] = "state/link.md"; request_path.write_text(json.dumps(request), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "dispatch",
                                    "--request", str(request_path), "--state", str(root / "state.json")], capture_output=True, text=True, check=False)
        assert completed.returncode != 0; assert not calls.exists()


def test_IT009_SEC007_inspect_requires_full_independent_correlation_and_settles() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); state = _request(root, head); state["status"] = "pointer_sent"
        state["receipt"] = {"id": state["worktree_id"], "instance": "instance-S4", "path": str(root),
                            "branch": state["branch"], "pre_head": head, "gitdir": state["gitdir"],
                            "worktree_gitdir": state["worktree_gitdir"], "startupTerminal": {"handle": state["terminal_handle"]},
                            "before": {"terminals": {}, "worktrees": {}}}
        state_path = root / "state.json"; state_path.write_text(json.dumps(state), encoding="utf-8")
        correlation = {key: state[key] for key in ("repository", "slice_id", "task_id", "operation_id", "terminal_handle",
                                                    "route", "commit_id", "lease_id", "worktree_id", "worktree_path")}
        configured = probe.OrcaProbe("repo", interval=0)
        configured.run = lambda argv, timeout=30.0: {"result": {"terminal": {"handle": state["terminal_handle"], "correlation": correlation}, "correlation": correlation}}  # type: ignore[method-assign]
        original = probe.OrcaProbe; probe.OrcaProbe = lambda *args, **kwargs: configured  # type: ignore[assignment]
        original_git = probe.git; probe.git = lambda path, *args, **kwargs: subprocess.CompletedProcess([], 0, head + "\n", "")  # type: ignore[assignment]
        try:
            probe.inspect(type("Args", (), {"state": str(state_path), "orca": "orca", "interval": 0, "attempts": 1})())
        finally:
            probe.OrcaProbe = original  # type: ignore[assignment]
            probe.git = original_git  # type: ignore[assignment]
        assert json.loads(state_path.read_text(encoding="utf-8"))["status"] == "settled"


def test_IT007_IT008_SEC006_declared_orca_git_and_lease_mutations_are_issued_once() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); calls, fake = root / "calls", root / "orca"; _fake_orca(fake, calls)
        provider = root / "provider"; provider.write_text("#!/bin/sh\nread payload\nprintf '%s\\n' '{\"lease_id\":\"lease-S4\",\"released\":true}'\n", encoding="utf-8"); provider.chmod(0o755)
        effects = [{"effect_id": f"{kind}-1", "kind": "orca", "argv": argv} for kind, argv in (
            ("create", ["worktree", "create"]), ("send", ["terminal", "send"]), ("set", ["worktree", "set"]),
            ("stop", ["terminal", "stop"]), ("rm", ["worktree", "rm"]))]
        effects += [{"effect_id": "git-1", "kind": "git", "argv": ["add", "seed"]},
                    {"effect_id": "lease-1", "kind": "lease", "provider": str(provider), "operation": "acquire", "argv": ["acquire"]}]
        request = root / "request.json"; request.write_text(json.dumps(_request(root, head, effects=effects)), encoding="utf-8"); state = root / "state.json"
        completed = subprocess.run([sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "dispatch", "--request", str(request), "--state", str(state)], capture_output=True, text=True, check=False)
        assert completed.returncode == 0, completed.stderr
        data = json.loads(state.read_text(encoding="utf-8")); assert all(effect["attempts"] == 1 and effect["status"] == "settled" for effect in data["effects"][:-1])
        sent = calls.read_text(encoding="utf-8").splitlines(); assert sum("worktree create" in call for call in sent) == 1; assert sum("terminal send" in call for call in sent) == 2
        assert sum("worktree set" in call for call in sent) == 1; assert sum("terminal stop" in call for call in sent) == 1; assert sum("worktree rm" in call for call in sent) == 1


def test_SEC006_post_effect_failure_is_not_retried() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); calls, fake = root / "calls", root / "orca"
        fake.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> " + str(calls) + "\nexit 1\n", encoding="utf-8"); fake.chmod(0o755)
        request = root / "request.json"; request.write_text(json.dumps(_request(root, head, effects=[{"effect_id": "create-1", "kind": "orca", "argv": ["worktree", "create"]}])), encoding="utf-8")
        state = root / "state.json"
        first = subprocess.run([sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "dispatch", "--request", str(request), "--state", str(state)], capture_output=True, text=True, check=False)
        second = subprocess.run([sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "dispatch", "--request", str(request), "--state", str(state)], capture_output=True, text=True, check=False)
        assert first.returncode != 0 and second.returncode != 0
        assert json.loads(state.read_text(encoding="utf-8"))["effects"][0]["attempts"] == 1
        assert sum("worktree create" in line for line in calls.read_text(encoding="utf-8").splitlines()) == 1


def test_IT011_import_is_inert() -> None:
    with tempfile.TemporaryDirectory() as directory:
        calls, fake = Path(directory) / "calls", Path(directory) / "orca"; _fake_orca(fake, calls)
        env = {**os.environ, "PATH": f"{Path(directory)}:{os.environ.get('PATH', '')}"}
        completed = subprocess.run([sys.executable, "-c", f"import runpy; runpy.run_path({str(ROOT / 'orca_assisted_probe.py')!r})"], env=env, capture_output=True, text=True, check=False)
        assert completed.returncode == 0, completed.stderr; assert not calls.exists()


def test_IT010_HSE028_public_cleanup_consumes_dispatch_state_and_releases_owned_lease() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); _repo(root)
        lane = root.parent / f"lane-{root.name}"
        subprocess.run(["git", "worktree", "add", "-q", "-b", "lane", str(lane), "HEAD"], cwd=root, check=True)
        common = Path(subprocess.check_output(["git", "-C", str(lane), "rev-parse", "--git-common-dir"], text=True).strip()).resolve()
        linked = Path(subprocess.check_output(["git", "-C", str(lane), "rev-parse", "--absolute-git-dir"], text=True).strip()).resolve()
        head = subprocess.check_output(["git", "-C", str(lane), "rev-parse", "HEAD"], text=True).strip()
        provider = root / "provider"; lease_calls = root / "lease-calls"
        provider.write_text(f"#!/bin/sh\nprintf '%s\\n' release >> {lease_calls!s}\nprintf '%s\\n' '{{\"lease_id\":\"lease-S4\",\"released\":true}}'\n", encoding="utf-8"); provider.chmod(0o755)
        state = _request(root, head); state.update({"worktree_id": "lane", "worktree_path": str(lane), "branch": "refs/heads/lane", "gitdir": str(common), "worktree_gitdir": str(linked), "receipt_path": "receipt.json", "resource_provider": str(provider)})
        state["receipt"] = {"repository": "repo", "id": "lane", "instance": "instance-S4", "path": str(lane), "branch": "refs/heads/lane", "pre_head": head, "gitdir": str(common), "worktree_gitdir": str(linked), "startupTerminal": {"handle": "owned-terminal"}, "before": {"terminals": {"owned-terminal": {}}, "worktrees": {}}}
        state_path = root / "state.json"; receipt_path = root / "receipt.json"
        state_path.write_text(json.dumps(state), encoding="utf-8"); receipt_path.write_text(json.dumps(state["receipt"]), encoding="utf-8")
        before = {"worktrees": {"lane": {"repoId": "repo", "instanceId": "instance-S4", "path": str(lane.resolve()), "branch": "refs/heads/lane"}}, "terminals": {"owned-terminal": {"handle": "owned-terminal"}}}
        original_inventory, original_terminals, original_raw = probe.OrcaProbe.inventory, probe.OrcaProbe.worktree_terminals, probe.raw
        removed = {"value": False, "stopped": False}; calls: list[list[str]] = []
        probe.OrcaProbe.inventory = lambda self: {"worktrees": {} if removed["value"] else before["worktrees"], "terminals": {} if removed["value"] else before["terminals"]}  # type: ignore[assignment]
        probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: [] if removed["value"] or removed["stopped"] else [{"handle": "owned-terminal"}]  # type: ignore[assignment]
        def fake_raw(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            calls.append(argv)
            if "stop" in argv: removed["stopped"] = True; return {"ok": True}
            if "rm" in argv:
                subprocess.run(["git", "-C", str(root), "worktree", "remove", "--force", str(lane)], check=True)
                removed["value"] = True
            return {"ok": True}
        probe.raw = fake_raw  # type: ignore[assignment]
        args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--state", str(state_path), "--integration-head", head, "--interval", "0.01", "--settle-window", "0.1"])
        try:
            probe.cleanup_entry(args)
        finally:
            probe.OrcaProbe.inventory, probe.OrcaProbe.worktree_terminals, probe.raw = original_inventory, original_terminals, original_raw  # type: ignore[assignment]
        assert [call[2] for call in calls] == ["stop", "rm"]
        assert lease_calls.read_text(encoding="utf-8").splitlines() == ["release"]
        assert not lane.exists()


def main() -> None:
    checks = tuple(value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value))
    for check in checks: check()
    print(f"orca assisted probe contract: {len(checks)}/{len(checks)} passed")


if __name__ == "__main__":
    main()
