"""Runnable fake-provider checks for the public assisted probe lifecycle."""

from __future__ import annotations

import ast
import json
import multiprocessing
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


def _receipt(state: dict[str, object]) -> dict[str, object]:
    return {
        "repository": state["repository"], "repository_root": state["repository_root"],
        "slice_id": state["slice_id"], "task_id": state["task_id"],
        "operation_id": state["operation_id"], "instance": state["instance"],
        "id": state["worktree_id"], "path": state["worktree_path"],
        "branch": state["branch"], "pre_head": state["pre_head"],
        "gitdir": state["gitdir"], "worktree_gitdir": state["worktree_gitdir"],
        "terminal_handle": state["terminal_handle"], "route": state["route"],
        "commit_id": state["commit_id"], "lease_id": state["lease_id"],
        "startupTerminal": {"handle": state["terminal_handle"]},
        "before": {"terminals": {}, "worktrees": {}},
    }


def _state(root: Path, head: str) -> dict[str, object]:
    state = _request(root, head)
    state["status"] = "pointer_sent"
    state["receipt"] = _receipt(state)
    return state


def _correlation(state: dict[str, object], **changes: object) -> dict[str, object]:
    fields = {
        "repository": state["repository"], "repository_root": state["repository_root"],
        "slice_id": state["slice_id"], "task_id": state["task_id"],
        "operation_id": state["operation_id"], "instance": state["instance"],
        "worktree_id": state["worktree_id"], "worktree_path": state["worktree_path"],
        "branch": state["branch"], "pre_head": state["pre_head"],
        "gitdir": state["gitdir"], "worktree_gitdir": state["worktree_gitdir"],
        "terminal_handle": state["terminal_handle"], "route": state["route"],
        "commit_id": state["commit_id"], "lease_id": state["lease_id"],
    }
    fields.update(changes)
    return fields


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
        root = Path(directory); head = _repo(root); state = _state(root, head)
        state_path = root / "state.json"; state_path.write_text(json.dumps(state), encoding="utf-8")
        correlation = _correlation(state)
        configured = probe.OrcaProbe("repo", interval=0)
        configured.run = lambda argv, timeout=30.0: {"result": {"terminal": {"handle": state["terminal_handle"], "connected": True, "correlation": correlation}, "correlation": correlation}}  # type: ignore[method-assign]
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
        provider = root / "provider"; provider.write_text("#!/bin/sh\nread payload\nprintf '{\"lease_id\":\"lease-S4\",\"released\":true,\"repository\":\"repo\",\"repository_root\":\"%s\",\"slice\":\"S4\",\"task\":\"T7\",\"operation_id\":\"op-S4-T7\",\"worktree\":\"worktree-S4\",\"operation\":\"acquire\",\"resources\":[\"lease-S4\"],\"idempotency_key\":\"lease-1\"}\\n' \"$PWD\"\n", encoding="utf-8"); provider.chmod(0o755)
        effects = [{"effect_id": f"{kind}-1", "kind": "orca", "argv": argv} for kind, argv in (
            ("create", ["worktree", "create"]), ("send", ["terminal", "send"]), ("set", ["worktree", "set"]),
            ("stop", ["terminal", "stop"]), ("rm", ["worktree", "rm"]))]
        effects += [{"effect_id": "git-1", "kind": "git", "argv": ["add", "seed"]},
                    {"effect_id": "lease-1", "kind": "lease", "provider": str(provider), "operation": "acquire", "argv": ["acquire"], "resources": ["lease-S4"], "idempotency_key": "lease-1"}]
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
        provider.write_text(f"#!/bin/sh\nread payload\ncase \"$payload\" in *release*) printf '%s\\n' release >> {lease_calls!s}; operation=release ;; *) printf '%s\\n' inspect >> {lease_calls!s}; operation=inspect ;; esac\nprintf '{{\"lease_id\":\"lease-S4\",\"released\":true,\"repository\":\"repo\",\"repository_root\":\"%s\",\"slice\":\"S4\",\"task\":\"T7\",\"operation_id\":\"op-S4-T7\",\"worktree\":\"lane\",\"operation\":\"%s\",\"resources\":[\"lease-S4\"],\"idempotency_key\":\"op-S4-T7:cleanup-lease\"}}\\n' \"$PWD\" \"$operation\"\n", encoding="utf-8"); provider.chmod(0o755)
        state = _request(root, head); state.update({"repository_root": str(root.parent), "worktree_id": "lane", "worktree_path": str(lane), "branch": "refs/heads/lane", "gitdir": str(common), "worktree_gitdir": str(linked), "terminal_handle": "owned-terminal", "receipt_path": str(root / "receipt.json"), "resource_provider": str(provider)})
        state["receipt"] = _receipt(state)
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
        assert lease_calls.read_text(encoding="utf-8").splitlines() == ["release", "inspect"]
        assert not lane.exists()
        assert subprocess.run(["git", "show-ref", "--verify", "--quiet", "refs/heads/lane"], cwd=root, check=False).returncode == 1
        cleaned_state = json.loads(state_path.read_text(encoding="utf-8"))
        assert all(effect["status"] == "settled" for effect in cleaned_state["effects"])
        assert {effect["effect_id"] for effect in cleaned_state["effects"]} == {
            "op-S4-T7:cleanup-stop", "op-S4-T7:cleanup-lease", "op-S4-T7:cleanup-detach", "op-S4-T7:cleanup-branch", "op-S4-T7:cleanup-rm",
        }


def test_IT017_IT018_IT019_SEC013_path_backed_cleanup_ledgers_reconcile_once() -> None:
    with tempfile.TemporaryDirectory() as directory:
        container = Path(directory); root = container / "repo"; root.mkdir(); head = _repo(root)
        lane = container / "lane"; subprocess.run(["git", "worktree", "add", "-q", "-b", "lane", str(lane), "HEAD"], cwd=root, check=True)
        common = Path(subprocess.check_output(["git", "-C", str(lane), "rev-parse", "--git-common-dir"], text=True).strip()).resolve()
        linked = Path(subprocess.check_output(["git", "-C", str(lane), "rev-parse", "--absolute-git-dir"], text=True).strip()).resolve()

        orca_ledger, orca_state, fake_orca = container / "orca.ledger", container / "orca-state.json", container / "orca"
        orca_state.write_text(json.dumps({"stopped": False, "removed": False, "stop_failed": False}), encoding="utf-8")
        fake_orca.write_text(
            "#!/usr/bin/env python3\n"
            "import json, subprocess, sys\n"
            f"LEDGER = {str(orca_ledger)!r}; STATE = {str(orca_state)!r}; REPO = {str(root.resolve())!r}; LANE = {str(lane.resolve())!r}\n"
            "def load():\n"
            "    with open(STATE, encoding='utf-8') as stream: return json.load(stream)\n"
            "def save(value):\n"
            "    with open(STATE, 'w', encoding='utf-8') as stream: json.dump(value, stream)\n"
            "def log(value):\n"
            "    with open(LEDGER, 'a', encoding='utf-8') as stream: stream.write(value + '\\n')\n"
            "state = load(); command = sys.argv[1:]\n"
            "if command[:2] == ['worktree', 'list']:\n"
            "    values = [] if state['removed'] else [{'id': 'lane', 'repoId': 'repo', 'instanceId': 'instance-S4', 'path': LANE, 'branch': 'refs/heads/lane'}]\n"
            "    print(json.dumps({'worktrees': values})); raise SystemExit\n"
            "if command[:2] == ['terminal', 'list']:\n"
            "    values = [] if state['stopped'] else [{'handle': 'owned-terminal'}]\n"
            "    print(json.dumps({'terminals': values})); raise SystemExit\n"
            "if command[:2] == ['terminal', 'stop']:\n"
            "    log('stop'); state['stopped'] = True\n"
            "    if not state['stop_failed']:\n"
            "        state['stop_failed'] = True; save(state); raise SystemExit('post-effect timeout')\n"
            "    save(state); print(json.dumps({'ok': True})); raise SystemExit\n"
            "if command[:2] == ['worktree', 'rm']:\n"
            "    log('rm'); subprocess.run(['git', '-C', REPO, 'worktree', 'remove', '--force', LANE], check=True)\n"
            "    state['removed'] = True; save(state); print(json.dumps({'ok': True})); raise SystemExit\n"
            "print(json.dumps({'ok': True}))\n",
            encoding="utf-8",
        ); fake_orca.chmod(0o755)

        provider_ledger, provider, provider_state = container / "provider.ledger", container / "provider", container / "provider-state.json"
        provider_state.write_text(json.dumps({"released": False}), encoding="utf-8")
        provider.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            f"LEDGER = {str(provider_ledger)!r}; STATE = {str(provider_state)!r}\n"
            "payload = json.load(sys.stdin)\n"
            "with open(LEDGER, 'a', encoding='utf-8') as stream: stream.write(payload['operation'] + '\\n')\n"
            "with open(STATE, encoding='utf-8') as stream: state = json.load(stream)\n"
            "if payload['operation'] == 'release': state['released'] = True\n"
            "with open(STATE, 'w', encoding='utf-8') as stream: json.dump(state, stream)\n"
            "response = {**payload, 'lease_id': 'lease-S4', 'released': state['released']}\n"
            "print(json.dumps(response))\n",
            encoding="utf-8",
        ); provider.chmod(0o755)

        git_ledger, fake_git = container / "git.ledger", container / "git"
        real_git = subprocess.check_output(["/usr/bin/env", "sh", "-c", "command -v git"], text=True).strip()
        fake_git.write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$*\" >> {str(git_ledger)!s}\n"
            f"exec {real_git} \"$@\"\n",
            encoding="utf-8",
        ); fake_git.chmod(0o755)

        state = _request(root, head)
        state.update({"repository_root": str(container.resolve()), "worktree_id": "lane", "worktree_path": str(lane.resolve()),
                      "branch": "refs/heads/lane", "gitdir": str(common), "worktree_gitdir": str(linked),
                      "terminal_handle": "owned-terminal", "receipt_path": str(root / "receipt.json"),
                      "resource_provider": str(provider)})
        state["receipt"] = _receipt(state)
        state_path, receipt_path = root / "state.json", root / "receipt.json"
        state_path.write_text(json.dumps(state), encoding="utf-8"); receipt_path.write_text(json.dumps(state["receipt"]), encoding="utf-8")
        env = {**os.environ, "PATH": f"{container}:{os.environ.get('PATH', '')}"}
        command = [sys.executable, str(ROOT / "orca_assisted_probe.py"), "--repo", "repo", "--orca", str(fake_orca),
                   "cleanup", "--state", str(state_path), "--integration-head", head, "--settle-window", "0.1", "--interval", "0.01"]
        first = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
        assert first.returncode != 0 and "FAIL_CLOSED" in first.stderr
        assert json.loads(subprocess.check_output([str(fake_orca), "worktree", "list", "--repo", "id:repo", "--json"], env=env, text=True))["worktrees"][0]["path"] == str(lane.resolve())
        second = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
        assert second.returncode == 0, second.stderr
        result = json.loads(second.stdout)
        assert result["status"] == "cleaned" and result["residue"] == []

        assert orca_ledger.read_text(encoding="utf-8").splitlines() == ["stop", "rm"]
        assert provider_ledger.read_text(encoding="utf-8").splitlines().count("release") == 1
        assert "inspect" in provider_ledger.read_text(encoding="utf-8").splitlines()
        git_lines = git_ledger.read_text(encoding="utf-8").splitlines()
        assert sum(" switch --detach " in line for line in git_lines) == 1
        assert sum(" branch --delete lane" in line for line in git_lines) == 1
        assert sum(" worktree remove --force " in line for line in git_lines) == 1
        assert all("terminal send" not in line and "SECRET_PACKET_BODY" not in line for line in orca_ledger.read_text(encoding="utf-8").splitlines())
        assert not lane.exists()
        assert subprocess.run(["git", "show-ref", "--verify", "--quiet", "refs/heads/lane"], cwd=root, check=False).returncode == 1
        assert "lane" not in subprocess.check_output(["git", "worktree", "list", "--porcelain"], cwd=root, text=True)
        saved = json.loads(state_path.read_text(encoding="utf-8"))
        assert {effect["status"] for effect in saved["effects"]} == {"settled"}


def test_IT007_SEC006_each_mutator_has_one_actual_call_after_post_effect_failure() -> None:
    mutators = (
        ("create", "orca", ["worktree", "create"]),
        ("send", "orca", ["terminal", "send"]),
        ("set", "orca", ["worktree", "set"]),
        ("stop", "orca", ["terminal", "stop"]),
        ("rm", "orca", ["worktree", "rm"]),
        ("git", "git", ["add", "seed"]),
        ("lease", "lease", ["acquire"]),
    )
    for name, kind, argv in mutators:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); head = _repo(root); ledger = root / f"{name}.ledger"
            fake = root / "orca"
            fake.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> {ledger}\nexit 1\n", encoding="utf-8"); fake.chmod(0o755)
            provider = root / "provider"
            provider.write_text(f"#!/bin/sh\nprintf '%s\\n' lease >> {ledger}\nexit 1\n", encoding="utf-8"); provider.chmod(0o755)
            effect = {"effect_id": f"{name}-once", "kind": kind, "argv": argv}
            if kind == "lease": effect.update({"provider": str(provider), "operation": "acquire", "resources": ["lease-S4"], "idempotency_key": effect["effect_id"]})
            request = root / "request.json"; state = root / "state.json"
            request.write_text(json.dumps(_request(root, head, effects=[effect])), encoding="utf-8")
            args = type("Args", (), {"orca": str(fake), "request": str(request), "state": str(state)})()
            original_git = probe.git
            if kind == "git":
                def fail_git(path: str | Path, *command: str, **kwargs: object) -> subprocess.CompletedProcess[str]:
                    if list(command) == argv:
                        with ledger.open("a", encoding="utf-8") as stream: stream.write("git\n")
                        raise probe.ProbeError("applied then timed out")
                    return original_git(path, *command, **kwargs)
                probe.git = fail_git  # type: ignore[assignment]
            try:
                for _ in range(2):
                    try: probe.dispatch(args)
                    except probe.ProbeError: pass
                    else: raise AssertionError(f"{name} failure unexpectedly completed")
            finally:
                probe.git = original_git  # type: ignore[assignment]
            records = ledger.read_text(encoding="utf-8").splitlines() if ledger.exists() else []
            assert len(records) == 1, (name, records)
            saved = json.loads(state.read_text(encoding="utf-8"))
            assert saved["effects"][0]["effect_id"] == effect["effect_id"]
            assert saved["effects"][0]["attempts"] == 1
            assert saved["effects"][0]["status"] == "unknown", (name, saved)


def test_IT008_SEC006_post_effect_failure_settles_with_reads_without_reissue() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); state_path = root / "state.json"
        state = _state(root, head); state_path.write_text(json.dumps(state), encoding="utf-8")
        calls = {"mutate": 0, "read": 0}
        args = type("Args", (), {"orca": "orca", "attempts": 3, "interval": 0})()
        effect = {"effect_id": "git-post-effect", "kind": "git", "argv": ["add", "seed"],
                  "observe": ["rev-parse", "HEAD"]}
        def invoke() -> dict[str, object]:
            calls["mutate"] += 1
            raise probe.ProbeError("applied then timed out")
        original_git = probe.git
        def fake_git(path: str | Path, *argv: str, check: bool = True) -> subprocess.CompletedProcess[str]:
            calls["read"] += 1
            return subprocess.CompletedProcess([], 0, head + "\n", "")
        probe.git = fake_git  # type: ignore[assignment]
        try:
            try:
                probe._persisted_effect(args, state, state_path, effect, invoke)
            except probe.ProbeError:
                pass
            saved = json.loads(state_path.read_text(encoding="utf-8"))
            record = saved["effects"][0]
            assert record["status"] == "unknown" and record["attempts"] == 1
            probe._reconcile_effect(args, saved, state_path, record)
            assert record["status"] == "settled"
            assert calls == {"mutate": 1, "read": 1}
        finally:
            probe.git = original_git  # type: ignore[assignment]


def test_IT009_SEC007_every_observation_identity_field_fails_closed() -> None:
    fields = ("repository", "repository_root", "slice_id", "task_id", "operation_id", "instance",
              "worktree_id", "worktree_path", "branch", "pre_head", "gitdir", "worktree_gitdir",
              "terminal_handle", "route", "commit_id", "lease_id")
    for field in fields:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); head = _repo(root); state = _state(root, head)
            state_path = root / "state.json"; state_path.write_text(json.dumps(state), encoding="utf-8")
            wrong = "wrong" if field not in {"commit_id", "pre_head"} else "f" * 40
            correlation = _correlation(state, **{field: wrong})
            configured = probe.OrcaProbe("repo", interval=0)
            configured.run = lambda argv, timeout=30.0, c=correlation: {"result": {"terminal": {
                "handle": state["terminal_handle"], "connected": True, "correlation": c}, "correlation": c}}  # type: ignore[method-assign]
            original_probe, original_git = probe.OrcaProbe, probe.git
            probe.OrcaProbe = lambda *args, **kwargs: configured  # type: ignore[assignment]
            probe.git = lambda path, *args, **kwargs: subprocess.CompletedProcess([], 0, head + "\n", "")  # type: ignore[assignment]
            try:
                try:
                    probe.inspect(type("Args", (), {"state": str(state_path), "orca": "orca", "interval": 0, "attempts": 1})())
                except probe.ProbeError as error:
                    assert field.replace("_", " ") in str(error) or field in str(error)
                else:
                    raise AssertionError(f"contradictory {field} observation was accepted")
                assert json.loads(state_path.read_text(encoding="utf-8"))["status"] == "pointer_sent"
            finally:
                probe.OrcaProbe, probe.git = original_probe, original_git  # type: ignore[assignment]


def test_IT009_SEC007_receipt_state_conjunction_rejects_every_public_cleanup_contradiction() -> None:
    fields = tuple(field for field in probe.RECEIPT_FIELDS if field not in {"startupTerminal", "before"})
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); state = _state(root, head)
        for field in fields:
            receipt = _receipt(state)
            receipt[field] = {"handle": "wrong"} if field == "terminal_handle" else "wrong"
            try:
                probe._receipt_from_state({**state, "receipt": receipt})
            except probe.ProbeError:
                pass
            else:
                raise AssertionError(f"receipt contradiction was accepted: {field}")


def test_IT010_SEC008_public_cleanup_rejects_id_path_and_handle_before_orca() -> None:
    for field in ("id", "path", "terminal_handle"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); head = _repo(root); state = _state(root, head)
            receipt = _receipt(state); receipt_path = root / "receipt.json"; receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            state["receipt_path"] = str(receipt_path); state["receipt"] = {**receipt, field: "foreign"}
            state_path = root / "state.json"; state_path.write_text(json.dumps(state), encoding="utf-8")
            original_inventory = probe.OrcaProbe.inventory
            calls: list[str] = []
            probe.OrcaProbe.inventory = lambda self: calls.append("inventory") or {"worktrees": {}, "terminals": {}}  # type: ignore[assignment]
            args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--state", str(state_path), "--integration-head", head])
            try:
                try: probe.cleanup_entry(args)
                except probe.ProbeError: pass
                else: raise AssertionError(f"public cleanup accepted receipt {field} contradiction")
            finally:
                probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
            assert calls == [], (field, calls)


def test_SEC008_cleanup_unsafe_state_table_has_zero_destructive_effects() -> None:
    cases = ("dirty", "unmerged", "running", "live-lease", "extra-ref")
    for case in cases:
        with tempfile.TemporaryDirectory() as directory:
            container = Path(directory); root = container / "repo"; root.mkdir(); _repo(root)
            lane = container / "lane"; subprocess.run(["git", "worktree", "add", "-q", "-b", "lane", str(lane), "HEAD"], cwd=root, check=True)
            common = Path(subprocess.check_output(["git", "-C", str(lane), "rev-parse", "--git-common-dir"], text=True).strip()).resolve()
            linked = Path(subprocess.check_output(["git", "-C", str(lane), "rev-parse", "--absolute-git-dir"], text=True).strip()).resolve()
            head = subprocess.check_output(["git", "-C", str(lane), "rev-parse", "HEAD"], text=True).strip()
            provider = container / "provider"; provider.write_text("#!/bin/sh\nprintf release >> /dev/null\n", encoding="utf-8"); provider.chmod(0o755)
            state = _request(root, head); state.update({"repository_root": str(container), "worktree_id": "lane", "worktree_path": str(lane),
                "branch": "refs/heads/lane", "gitdir": str(common), "worktree_gitdir": str(linked), "terminal_handle": "owned-terminal",
                "packet_path": str(root / "packet"), "log_path": str(root / "log"), "receipt_path": str(container / "receipt.json"),
                "resource_provider": str(provider)})
            state["receipt"] = _receipt(state)
            if case == "dirty": (lane / "dirty").write_text("x", encoding="utf-8")
            if case == "unmerged": (linked / "MERGE_HEAD").write_text(head + "\n", encoding="utf-8")
            if case == "running": state["terminal_status"] = "running"
            if case == "live-lease": state["lease"] = {"lease_id": "lease-S4", "repository": "repo", "worktree": "lane", "operation_id": state["operation_id"], "live": True}
            if case == "extra-ref": state["extra_refs"] = ["refs/heads/foreign-owned"]
            state_path = container / "state.json"; receipt_path = container / "receipt.json"
            state_path.write_text(json.dumps(state), encoding="utf-8"); receipt_path.write_text(json.dumps(state["receipt"]), encoding="utf-8")
            calls: list[list[str]] = []
            before = {"worktrees": {"lane": {"repoId": "repo", "instanceId": "instance-S4", "path": str(lane), "branch": "refs/heads/lane"}},
                      "terminals": {"owned-terminal": ({"handle": "owned-terminal", "status": "running"} if case == "running" else {"handle": "owned-terminal"})}}
            original_inventory, original_terminals, original_raw = probe.OrcaProbe.inventory, probe.OrcaProbe.worktree_terminals, probe.raw
            original_git = probe.git
            probe.OrcaProbe.inventory = lambda self: before  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: [{"handle": "owned-terminal"}]  # type: ignore[assignment]
            probe.raw = lambda argv, timeout=30.0: calls.append(argv) or {"ok": True}  # type: ignore[assignment]
            probe.git = lambda path, *argv, check=True: calls.append(["git", *argv]) or original_git(path, *argv, check=check)  # type: ignore[assignment]
            args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--state", str(state_path), "--integration-head", head, "--interval", "0", "--settle-window", "0.1"])
            try:
                try: probe.cleanup_entry(args)
                except probe.ProbeError: pass
                else: raise AssertionError(f"unsafe cleanup accepted: {case}")
            finally:
                probe.OrcaProbe.inventory, probe.OrcaProbe.worktree_terminals, probe.raw, probe.git = original_inventory, original_terminals, original_raw, original_git  # type: ignore[assignment]
            assert not any("stop" in call or "rm" in call or "branch" in call or "switch" in call for call in calls), (case, calls)


def test_SEC001_dispatch_rejects_repository_symlink_before_any_effect() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); real = root / "real"; real.mkdir(); head = _repo(real); link = root / "link"; link.symlink_to(real, target_is_directory=True)
        fake, calls = root / "orca", root / "calls"; _fake_orca(fake, calls)
        request = _request(real, head); request["repository_root"] = str(link)
        request_path, state_path = real / "request.json", real / "state.json"; request_path.write_text(json.dumps(request), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "dispatch", "--request", str(request_path), "--state", str(state_path)], capture_output=True, text=True, check=False)
        assert completed.returncode != 0 and not calls.exists() and not state_path.exists()


MUTATING_GIT_VERBS = {"add", "commit", "checkout", "switch", "update-ref"}
MUTATING_WORKTREE_VERBS = {"add", "remove", "move", "prune", "lock", "unlock"}
READ_ONLY_GIT_VERBS = {
    "cat-file", "diff", "for-each-ref", "log", "merge-base", "rev-parse", "show-ref",
    "status", "symbolic-ref", "worktree",
}


def _function_index(tree: ast.Module) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    result: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result[node.name] = node
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result[f"{node.name}.{child.name}"] = child
    return result


def _git_mutates(call: ast.Call) -> bool:
    arguments = call.args[1:]
    values = [argument.value for argument in arguments if isinstance(argument, ast.Constant) and isinstance(argument.value, str)]
    verbs = set(values)
    if verbs & MUTATING_GIT_VERBS:
        return True
    if "branch" in verbs and any(flag in values for flag in ("--delete", "-d", "-D")):
        return True
    if "worktree" in verbs and verbs & MUTATING_WORKTREE_VERBS:
        return True
    return not (verbs & READ_ONLY_GIT_VERBS)


def _assert_public_mutation_boundary(source: str) -> None:
    """Check the reachable public lifecycle, not just its two entrypoint bodies."""
    tree = ast.parse(source)
    functions = _function_index(tree)
    allowed = {
        "raw", "git", "resilient_run", "_send_pointer_once", "_provider_read",
        "MutationRunner.issue", "OrcaProbe.run",
    }
    pending = ["dispatch", "cleanup"]
    visited: set[str] = set()
    while pending:
        name = pending.pop()
        if name in visited or name in allowed:
            continue
        node = functions.get(name)
        if node is None:
            continue
        visited.add(name)
        for child in ast.walk(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child is not node:
                # Nested callbacks are part of the public lifecycle too.
                for nested in ast.walk(child):
                    if isinstance(nested, ast.Call):
                        _check_public_call(nested, name)
                continue
            if not isinstance(child, ast.Call):
                continue
            _check_public_call(child, name)
            target: str | None = None
            if isinstance(child.func, ast.Name):
                target = child.func.id
            elif isinstance(child.func, ast.Attribute):
                target = child.func.attr
            targets = [target] if target in functions else [key for key in functions if key.endswith(f".{target}")]
            for resolved in targets:
                if resolved in {"raw", "git"}:
                    continue
                if target == "issue":
                    pending.append("MutationRunner.issue")
                elif target == "run":
                    pending.append("OrcaProbe.run")
                else:
                    pending.append(resolved)


def _check_public_call(call: ast.Call, owner: str) -> None:
    if isinstance(call.func, ast.Name):
        if call.func.id in {"raw", "subprocess"}:
            raise AssertionError(f"direct mutable sink in reachable {owner}: {call.func.id}")
        if call.func.id == "git" and _git_mutates(call):
            raise AssertionError(f"direct mutating git call in reachable {owner}")
    if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
        if call.func.attr in {"_sink", "_physical_sink"} and owner != "MutationRunner.issue":
            raise AssertionError(f"private mutation sink bypass in reachable {owner}: {call.func.attr}")
        if call.func.value.id == "subprocess" and call.func.attr in {
            "run", "Popen", "call", "check_call", "check_output"
        }:
            raise AssertionError(f"direct provider/orca subprocess in reachable {owner}")


def test_UT020_public_lifecycle_has_one_mutation_issuer() -> None:
    source = (ROOT / "orca_assisted_probe.py").read_text(encoding="utf-8")
    _assert_public_mutation_boundary(source)
    runner = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == "MutationRunner")
    assert any(isinstance(node, ast.FunctionDef) and node.name == "issue" for node in runner.body)

    survivor = source.replace(
        '    request_path = Path(args.request)\n',
        '    git(root, "add", "seed")\n    request_path = Path(args.request)\n',
        1,
    )
    try:
        _assert_public_mutation_boundary(survivor)
    except AssertionError as error:
        assert "mutating git" in str(error)
    else:
        raise AssertionError("direct mutating git survivor passed the structural guard")

    survivor = source.replace(
        '    runner = MutationRunner(args, state, state_path)\n',
        '    runner = MutationRunner(args, state, state_path)\n    runner._sink({"kind": "git", "argv": ["add", "seed"]})\n',
        1,
    )
    try:
        _assert_public_mutation_boundary(survivor)
    except AssertionError as error:
        assert "private mutation sink" in str(error)
    else:
        raise AssertionError("direct private mutation sink survivor passed the structural guard")


def test_IT017_SEC013_issue_persists_in_flight_before_sink_and_rejects_duplicate_success() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); state_path = root / "state.json"; ledger = root / "ledger"
        state: dict[str, object] = {"repository_root": str(root), "repository": "repo", "slice_id": "S4", "task_id": "T14", "operation_id": "op-T14", "lease_id": "lease-T14", "worktree_id": "wt-T14", "worktree_path": str(root), "effects": [], "effect_ids": []}
        state_path.write_text(json.dumps(state), encoding="utf-8")
        args = type("Args", (), {"orca": "orca", "timeout": 1.0, "attempts": 1, "interval": 0})()
        seen: list[dict[str, object]] = []
        def sink() -> dict[str, object]:
            seen.append(json.loads(state_path.read_text(encoding="utf-8")))
            ledger.write_text("physical\n", encoding="utf-8")
            return {"ok": True}
        effect = {"effect_id": "git-once", "kind": "git", "argv": ["add", "seed"]}
        runner = probe.MutationRunner(args, state, state_path)
        result = runner.issue(effect, sink=sink)
        assert seen[0]["effects"][0]["status"] == "in_flight"
        assert seen[0]["effects"][0]["attempts"] == 1
        assert result["status"] == "settled"
        runner.issue(effect, sink=lambda: (_ for _ in ()).throw(AssertionError("duplicate sink")))
        assert ledger.read_text(encoding="utf-8").splitlines() == ["physical"]

        prior = state_path.read_bytes()
        original_write = probe._write_json
        def fail_write(path: Path, value: dict[str, object]) -> None:
            raise OSError("injected pre-sink failure")
        probe._write_json = fail_write  # type: ignore[assignment]
        try:
            try:
                probe.MutationRunner(args, {**state, "effects": [], "effect_ids": []}, state_path).issue({"effect_id": "provider-once", "kind": "git", "argv": ["add", "seed"]}, sink=lambda: (_ for _ in ()).throw(AssertionError("sink reached")))
            except OSError:
                pass
            else:
                raise AssertionError("pre-sink persistence failure was accepted")
        finally:
            probe._write_json = original_write  # type: ignore[assignment]
        assert state_path.read_bytes() == prior


def test_IT018_IT019_SEC013_physical_ledgers_cover_git_provider_orca_and_restart_reads() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root)
        fake_orca, orca_ledger = root / "orca", root / "orca.ledger"
        fake_orca.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> {orca_ledger}\nprintf '%s\\n' '{{\"ok\":true}}'\n", encoding="utf-8"); fake_orca.chmod(0o755)
        provider_ledger, provider = root / "provider.ledger", root / "provider"
        provider.write_text(f"#!/bin/sh\nprintf '%s\\n' provider >> {provider_ledger}\nprintf '{{\"lease_id\":\"lease-S4\",\"released\":true,\"repository\":\"repo\",\"repository_root\":\"%s\",\"slice\":\"S4\",\"task\":\"T7\",\"operation_id\":\"op-S4-T7\",\"worktree\":\"worktree-S4\",\"operation\":\"acquire\",\"resources\":[\"lease-S4\"],\"idempotency_key\":\"provider-once\"}}\\n' \"$PWD\"\n", encoding="utf-8"); provider.chmod(0o755)
        git_ledger, fake_git = root / "git.ledger", root / "git"
        fake_git.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> {git_ledger}\n", encoding="utf-8"); fake_git.chmod(0o755)
        request = root / "request.json"; state_path = root / "state.json"
        effects = [
            {"effect_id": "orca-once", "kind": "orca", "argv": ["worktree", "create"]},
            {"effect_id": "git-once", "kind": "git", "argv": ["add", "seed"]},
            {"effect_id": "provider-once", "kind": "lease", "provider": str(provider), "operation": "acquire", "argv": ["acquire"], "resources": ["lease-S4"], "idempotency_key": "provider-once"},
        ]
        request.write_text(json.dumps(_request(root, head, effects=effects)), encoding="utf-8")
        env = {**os.environ, "PATH": f"{root}:{os.environ.get('PATH', '')}"}
        completed = subprocess.run([sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake_orca), "dispatch", "--request", str(request), "--state", str(state_path)], env=env, capture_output=True, text=True, check=False)
        assert completed.returncode == 0, completed.stderr
        orca_lines = orca_ledger.read_text(encoding="utf-8").splitlines()
        assert sum("worktree create" in line for line in orca_lines) == 1
        assert sum("terminal send" in line for line in orca_lines) == 1
        assert len(git_ledger.read_text(encoding="utf-8").splitlines()) == 1
        assert len(provider_ledger.read_text(encoding="utf-8").splitlines()) == 1
        assert "SECRET_PACKET_BODY" not in orca_ledger.read_text(encoding="utf-8")
        saved = json.loads(state_path.read_text(encoding="utf-8"))
        assert {effect["status"] for effect in saved["effects"]} == {"settled"}
        replay = {**saved, "effects": [{**saved["effects"][0], "status": "unknown"}, {**saved["effects"][1], "status": "in_flight"}], "status": "send_started"}
        replay_path = root / "replay.json"; replay_path.write_text(json.dumps(replay), encoding="utf-8")
        args = type("Args", (), {"orca": str(fake_orca), "attempts": 1, "interval": 0, "timeout": 1.0})()
        reads = {"count": 0}
        def observe() -> bool:
            reads["count"] += 1
            return True
        runner = probe.MutationRunner(args, replay, replay_path)
        runner.issue(replay["effects"][0], observe=observe)
        runner.issue(replay["effects"][1], observe=observe)
        replay_lines = orca_ledger.read_text(encoding="utf-8").splitlines()
        assert sum("worktree create" in line for line in replay_lines) == 1
        assert sum("terminal send" in line for line in replay_lines) == 1
        assert len(git_ledger.read_text(encoding="utf-8").splitlines()) == 1
        assert reads["count"] == 2


def _concurrent_issue(state_path: str, ledger: str) -> None:
    state_file = Path(state_path)
    state = json.loads(state_file.read_text(encoding="utf-8"))
    args = type("Args", (), {"orca": "orca", "timeout": 1.0, "attempts": 1, "interval": 0})()
    effect = {"effect_id": "concurrent-once", "kind": "git", "path": state["repository_root"],
              "argv": ["add", "seed"], "resources": ["seed"], "idempotency_key": "concurrent-once"}
    def sink() -> dict[str, object]:
        with open(ledger, "a", encoding="utf-8") as stream:
            stream.write("physical\n")
        return {"ok": True}
    probe.MutationRunner(args, state, state_file).issue(effect, sink=sink)


def test_SEC013_process_safe_effect_claim_executes_one_physical_mutation() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); state = _state(root, head)
        state_path, ledger = root / "state.json", root / "physical.ledger"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        context = multiprocessing.get_context("fork")
        workers = [context.Process(target=_concurrent_issue, args=(str(state_path), str(ledger))) for _ in range(2)]
        for worker in workers: worker.start()
        for worker in workers: worker.join(5)
        assert all(worker.exitcode == 0 for worker in workers)
        assert ledger.read_text(encoding="utf-8").splitlines() == ["physical"]
        assert json.loads(state_path.read_text(encoding="utf-8"))["effects"][0]["status"] == "settled"


def test_SEC013_write_json_syncs_file_and_parent_directory() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "state.json"; calls: list[int] = []
        original = probe.os.fsync
        probe.os.fsync = lambda descriptor: calls.append(descriptor)  # type: ignore[assignment]
        try:
            probe._write_json(path, {"status": "settled"})
        finally:
            probe.os.fsync = original  # type: ignore[assignment]
        assert path.is_file() and len(calls) >= 2


def test_SEC013_effect_validation_rejects_incomplete_lease_foreign_git_and_mutating_reads() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); state = _state(root, head)
        state_path = root / "state.json"; state_path.write_text(json.dumps(state), encoding="utf-8")
        args = type("Args", (), {"orca": "orca", "timeout": 1.0, "attempts": 1, "interval": 0})()
        for kind, observation in (("git", ["add", "seed"]), ("lease", ["release"])):
            try: probe._validate_observation(kind, observation)
            except probe.ProbeError: pass
            else: raise AssertionError(f"mutating {kind} observation accepted")
        incomplete = {"effect_id": "lease-incomplete", "kind": "lease", "provider": str(root / "provider"),
                      "operation": "acquire", "argv": ["acquire"]}
        try: probe.MutationRunner(args, state, state_path).issue(incomplete, sink=lambda: {"ok": True})
        except probe.ProbeError: pass
        else: raise AssertionError("incomplete lease accepted")
        foreign_lease = {"effect_id": "lease-foreign", "kind": "lease", "provider": str(root.parent / "provider"),
                         "operation": "acquire", "argv": ["acquire"], "resources": ["lease-S4"],
                         "idempotency_key": "lease-foreign"}
        try: probe.MutationRunner(args, state, state_path).issue(foreign_lease, sink=lambda: {"ok": True})
        except probe.ProbeError: pass
        else: raise AssertionError("foreign lease provider accepted")
        foreign = root.parent / f"foreign-{root.name}"; foreign.mkdir()
        effect = {"effect_id": "foreign-git", "kind": "git", "path": str(foreign), "argv": ["add", "seed"],
                  "resources": ["seed"], "idempotency_key": "foreign-git"}
        try: probe.MutationRunner(args, state, state_path).issue(effect, sink=lambda: {"ok": True})
        except probe.ProbeError: pass
        else: raise AssertionError("foreign Git path accepted")


def test_SEC013_reused_effect_mismatch_and_diagnostics_are_fail_closed_and_redacted() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); head = _repo(root); state = _state(root, head)
        state_path, log = root / "state.json", root / "events.jsonl"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        args = type("Args", (), {"orca": "orca", "timeout": 1.0, "attempts": 1, "interval": 0})()
        effect = {"effect_id": "reuse-once", "kind": "git", "path": str(root), "argv": ["add", "seed"],
                  "resources": ["seed"], "idempotency_key": "reuse-once"}
        runner = probe.MutationRunner(args, state, state_path)
        runner.issue(effect, sink=lambda: {"ok": True})
        mismatch = {**effect, "argv": ["commit", "-m", "secret"]}
        try: runner.issue(mismatch, sink=lambda: {"ok": True})
        except probe.ProbeError: pass
        else: raise AssertionError("reused effect mismatch accepted")
        probe.append(log, {"repository": "repo", "operation_id": "op", "path": str(root / "secret"),
                           "receipt": {"secret": "SECRET_PACKET_BODY"}, "tail": "SECRET_PACKET_BODY"})
        text = log.read_text(encoding="utf-8")
        assert "SECRET_PACKET_BODY" not in text and str(root) not in text and '"operation_id": "op"' in text


def main() -> None:
    checks = tuple(value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value))
    for check in checks: check()
    print(f"orca assisted probe contract: {len(checks)}/{len(checks)} passed")


if __name__ == "__main__":
    main()
