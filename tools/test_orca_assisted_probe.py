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
        provider.write_text(f"#!/bin/sh\nread payload\ncase \"$payload\" in *release*) printf '%s\\n' release >> {lease_calls!s} ;; *) printf '%s\\n' inspect >> {lease_calls!s} ;; esac\nprintf '%s\\n' '{{\"lease_id\":\"lease-S4\",\"released\":true}}'\n", encoding="utf-8"); provider.chmod(0o755)
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
            if kind == "lease": effect.update({"provider": str(provider), "operation": "acquire"})
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


def main() -> None:
    checks = tuple(value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value))
    for check in checks: check()
    print(f"orca assisted probe contract: {len(checks)}/{len(checks)} passed")


if __name__ == "__main__":
    main()
