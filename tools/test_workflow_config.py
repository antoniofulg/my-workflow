"""Unit contract for the workflow configuration resolver."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts"))
import workflow_config


ROOT = Path(__file__).resolve().parent.parent


def make_repo() -> Path:
    root = Path(tempfile.mkdtemp())
    for provider, extension in (("claude", "md"), ("cursor", "md"), ("codex", "toml")):
        agents = root / f".{provider}" / "agents"
        agents.mkdir(parents=True)
        for role in workflow_config.ROLES:
            agent_name = workflow_config.AGENT_NAMES.get(role, role)
            (agents / f"{agent_name}.{extension}").write_text(f"{role}\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    (root / "seed").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
    return root


def test_defaults_and_native_routing() -> None:
    root = make_repo()
    try:
        snapshot = workflow_config.resolve(
            root=root, feature="default", slice_count=4, native_provider="codex"
        )
        assert snapshot["deep_review"] == {"cadence": "grouped.3", "groups": [[1, 2], [3, 4]]}
        assert all(value["provider"] == "codex" for value in snapshot["roles"].values())
        assert snapshot["roles"]["verifier"]["agent_file"] == ".codex/agents/verifier.toml"
    finally:
        import shutil

        shutil.rmtree(root)


def test_cli_adapter_resolves_and_reports_invalid_input() -> None:
    root = make_repo()
    try:
        resolver = ROOT / ".agents/skills/workflow-config/scripts/workflow_config.py"
        command = [
            sys.executable,
            str(resolver),
            "--root",
            str(root),
            "--feature",
            "cli",
            "--slices",
            "2",
            "--native-provider",
            "codex",
            "--override",
            "verifier=claude",
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        assert result.returncode == 0
        assert result.stderr == ""
        payload = json.loads(result.stdout)
        assert payload["feature"] == "cli"
        assert payload["deep_review"] == {"cadence": "grouped.3", "groups": [[1, 2]]}
        assert payload["roles"]["verifier"]["provider"] == "claude"
        assert (root / ".specs/features/cli/workflow.json").is_file()

        invalid = subprocess.run(
            [
                sys.executable,
                str(resolver),
                "--root",
                str(root),
                "--feature",
                "cli-invalid",
                "--slices",
                "0",
                "--native-provider",
                "codex",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        assert invalid.returncode == 1
        assert invalid.stdout == ""
        assert "workflow config: slice count must be at least 1" in invalid.stderr
    finally:
        import shutil

        shutil.rmtree(root)


def test_cadence_modes_and_balancing() -> None:
    expected = {
        "slice": [[1], [2], [3], [4]],
        "feature": [[1, 2, 3, 4]],
        "grouped.3": [[1, 2], [3, 4]],
    }
    for cadence, groups in expected.items():
        assert workflow_config.balanced_groups(4, cadence) == groups

    matrix = {
        "slice": {
            1: [[1]],
            2: [[1], [2]],
            3: [[1], [2], [3]],
            4: [[1], [2], [3], [4]],
            5: [[1], [2], [3], [4], [5]],
            6: [[1], [2], [3], [4], [5], [6]],
            7: [[1], [2], [3], [4], [5], [6], [7]],
            8: [[1], [2], [3], [4], [5], [6], [7], [8]],
        },
        "feature": {
            1: [[1]],
            2: [[1, 2]],
            3: [[1, 2, 3]],
            4: [[1, 2, 3, 4]],
            5: [[1, 2, 3, 4, 5]],
            6: [[1, 2, 3, 4, 5, 6]],
            7: [[1, 2, 3, 4, 5, 6, 7]],
            8: [[1, 2, 3, 4, 5, 6, 7, 8]],
        },
        "grouped.3": {
            1: [[1]],
            2: [[1, 2]],
            3: [[1, 2, 3]],
            4: [[1, 2], [3, 4]],
            5: [[1, 2, 3], [4, 5]],
            6: [[1, 2, 3], [4, 5, 6]],
            7: [[1, 2, 3], [4, 5], [6, 7]],
            8: [[1, 2, 3], [4, 5, 6], [7, 8]],
        },
    }
    for cadence, cases in matrix.items():
        for slice_count, groups in cases.items():
            assert workflow_config.balanced_groups(slice_count, cadence) == groups

    assert workflow_config.balanced_groups(6, "grouped.2") == [[1, 2], [3, 4], [5, 6]]
    assert workflow_config.balanced_groups(7, "grouped.3") == [[1, 2, 3], [4, 5], [6, 7]]
    assert workflow_config.balanced_groups(8, "grouped.4") == [[1, 2, 3, 4], [5, 6, 7, 8]]


def test_invalid_cadence_and_count() -> None:
    for cadence in ("grouped", "grouped.0", "grouped.x", "other"):
        try:
            workflow_config.balanced_groups(2, cadence)
        except workflow_config.ConfigError as exc:
            assert "cadence" in str(exc) or "N" in str(exc)
        else:
            raise AssertionError(f"expected invalid cadence: {cadence}")
    try:
        workflow_config.balanced_groups(0, "feature")
    except workflow_config.ConfigError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("expected invalid slice count")


def test_profile_precedence_and_partial_defaults() -> None:
    root = make_repo()
    try:
        (root / ".my-workflow.toml").write_text(
            "[profiles.mixed]\nimplementer = 'claude'\nverifier = 'codex'\n",
            encoding="utf-8",
        )
        snapshot = workflow_config.resolve(
            root=root,
            feature="mixed",
            slice_count=1,
            native_provider="cursor",
            profile="mixed",
            overrides=["verifier=claude"],
        )
        assert snapshot["roles"]["implementer"]["provider"] == "claude"
        assert snapshot["roles"]["verifier"]["provider"] == "claude"
        assert snapshot["roles"]["explorer"]["provider"] == "cursor"
    finally:
        import shutil

        shutil.rmtree(root)


def test_invalid_routing_has_no_fallback() -> None:
    root = make_repo()
    try:
        for kwargs, message in (
            ({"profile": "missing"}, "unknown profile"),
            ({"overrides": ["planner=codex"]}, "invalid role"),
            ({"overrides": ["verifier=unknown"]}, "invalid provider"),
        ):
            try:
                workflow_config.resolve(
                    root=root, feature="invalid", slice_count=1, native_provider="codex", **kwargs
                )
            except workflow_config.ConfigError as exc:
                assert message in str(exc)
            else:
                raise AssertionError(f"expected {message}")
        (root / ".codex/agents/verifier.toml").unlink()
        try:
            workflow_config.resolve(root=root, feature="missing-agent", slice_count=1, native_provider="codex")
        except workflow_config.ConfigError as exc:
            assert "missing agent file" in str(exc)
        else:
            raise AssertionError("expected missing agent failure")
    finally:
        import shutil

        shutil.rmtree(root)


def test_snapshot_is_stable_and_atomic_failure_preserves_previous() -> None:
    root = make_repo()
    try:
        first = workflow_config.resolve(root=root, feature="snapshot", slice_count=2, native_provider="codex")
        path = root / ".specs/features/snapshot/workflow.json"
        original = path.read_text(encoding="utf-8")

        expected_head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
        on_disk = json.loads(original)
        assert set(on_disk) == {
            "version",
            "feature",
            "git_head",
            "profile",
            "overrides",
            "deep_review",
            "roles",
        }
        assert on_disk["version"] == 1
        assert on_disk["feature"] == "snapshot"
        assert on_disk["git_head"] == expected_head
        assert on_disk["profile"] is None
        assert on_disk["overrides"] == {}
        assert on_disk["deep_review"] == {
            "cadence": "grouped.3",
            "groups": [[1, 2]],
        }
        expected_agents = {
            "implementer": ".codex/agents/implementer.toml",
            "verifier": ".codex/agents/verifier.toml",
            "explorer": ".codex/agents/explorer.toml",
            "deep_reviewer": ".codex/agents/deep-reviewer.toml",
        }
        assert set(on_disk["roles"]) == set(expected_agents)
        for role, agent_file in expected_agents.items():
            assert on_disk["roles"][role] == {
                "provider": "codex",
                "agent_file": agent_file,
            }

        second = workflow_config.resolve(root=root, feature="snapshot", slice_count=8, native_provider="cursor")
        assert second == first
        assert json.loads(path.read_text(encoding="utf-8")) == first

        real_replace = workflow_config.os.replace
        workflow_config.os.replace = lambda *_args: (_ for _ in ()).throw(OSError("injected"))
        try:
            try:
                workflow_config.resolve(
                    root=root, feature="snapshot", slice_count=3, native_provider="codex", refresh=True
                )
            except OSError as exc:
                assert str(exc) == "injected"
            else:
                raise AssertionError("expected atomic write failure")
        finally:
            workflow_config.os.replace = real_replace
        assert path.read_text(encoding="utf-8") == original
    finally:
        import shutil

        shutil.rmtree(root)


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_"):
            function()
    print("7 passed, 0 failed")
