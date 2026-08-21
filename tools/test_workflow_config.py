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
            (agents / f"{role}.{extension}").write_text(f"{role}\n", encoding="utf-8")
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


def test_cadence_modes_and_balancing() -> None:
    expected = {
        "slice": [[1], [2], [3], [4]],
        "feature": [[1, 2, 3, 4]],
        "grouped.3": [[1, 2], [3, 4]],
    }
    for cadence, groups in expected.items():
        assert workflow_config.balanced_groups(4, cadence) == groups
    assert workflow_config.balanced_groups(7, "grouped.3") == [[1, 2, 3], [4, 5], [6, 7]]


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
    print("6 passed, 0 failed")
