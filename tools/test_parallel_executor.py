"""Spec-derived tests for the parallel slice executor coordinator."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/autonomous/scripts"))
import parallel_execute


def make_repo(*, mode: str = "safe", feature: str = "fixture") -> Path:
    root = Path(tempfile.mkdtemp())
    feature_dir = root / ".specs" / "features" / feature
    feature_dir.mkdir(parents=True)
    (feature_dir / "tasks.md").write_text(
        "### T1: first\n**Status:** pending\n**Slice:** A\n**Where:** src/a.py\n**Depends on:** None\n\n"
        "### T2: second\n**Status:** pending\n**Slice:** B\n**Where:** src/b.py\n**Depends on:** None\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    (root / "seed").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    (feature_dir / "workflow.json").write_text(
        json.dumps(
            {
                "feature": feature,
                "git_head": head,
                "parallelization": {"mode": mode},
                "version": 1,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def test_state_rejects_out_of_order_and_duplicate_lane_transition() -> None:
    state = parallel_execute.new_runtime_state("repo", "fixture", "safe", "head")
    state["lanes"]["slice-A"] = {"slice": "A", "task": "T1", "state": "ready"}
    parallel_execute.transition_lane(state, "slice-A", "running", expected="ready")
    assert state["lanes"]["slice-A"]["state"] == "running"
    try:
        parallel_execute.transition_lane(state, "slice-A", "running", expected="ready")
    except parallel_execute.StateError as exc:
        assert "out-of-order" in str(exc)
    else:
        raise AssertionError("duplicate transition must be rejected")


def test_state_validation_rejects_foreign_and_malformed_state() -> None:
    state = parallel_execute.new_runtime_state("repo", "fixture", "safe", "head")
    for foreign in (
        {**state, "repository_id": "other"},
        {**state, "feature": "other"},
        {**state, "lanes": []},
        {**state, "version": 2},
    ):
        try:
            parallel_execute.validate_runtime_state(foreign, "repo", "fixture")
        except parallel_execute.StateError as exc:
            assert str(exc)
        else:
            raise AssertionError("invalid state must be rejected")


def test_runtime_state_path_is_git_common_state_not_versioned_feature_state() -> None:
    root = make_repo()
    try:
        path = parallel_execute.runtime_state_path(root, "fixture")
        common_value = subprocess.check_output(
            ["git", "rev-parse", "--git-common-dir"], cwd=root, text=True
        ).strip()
        common = (root / common_value if not Path(common_value).is_absolute() else Path(common_value)).resolve()
        assert common in path.parents
        assert ".specs" not in path.parts
    finally:
        shutil.rmtree(root)


def test_atomic_state_replacement_preserves_previous_on_pre_rename_failure() -> None:
    directory = Path(tempfile.mkdtemp())
    path = directory / "state.json"
    try:
        parallel_execute.atomic_write_json(path, {"version": 1, "status": "complete"})
        try:
            parallel_execute.atomic_write_json(
                path, {"version": 1, "status": "torn"}, before_replace=lambda: (_ for _ in ()).throw(RuntimeError("boom"))
            )
        except RuntimeError as exc:
            assert str(exc) == "boom"
        else:
            raise AssertionError("injected replacement failure must propagate")
        assert json.loads(path.read_text(encoding="utf-8")) == {"version": 1, "status": "complete"}
    finally:
        shutil.rmtree(directory)


def test_safe_argv_uses_no_shell_and_bounded_timeout() -> None:
    calls: list[dict[str, object]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append({"argv": argv, **kwargs})
        return subprocess.CompletedProcess(argv, 0, "ok", "")

    original = parallel_execute.subprocess.run
    parallel_execute.subprocess.run = fake_run  # type: ignore[assignment]
    try:
        result = parallel_execute.run_argv([sys.executable, "-c", "print('ok')", "$(touch pwned)"], timeout=3)
    finally:
        parallel_execute.subprocess.run = original  # type: ignore[assignment]
    assert result.returncode == 0
    assert calls[0]["shell"] is False
    assert calls[0]["timeout"] == 3
    assert calls[0]["argv"][-1] == "$(touch pwned)"


def test_bounded_path_rejects_escape_and_unsafe_symlink_before_write() -> None:
    root = Path(tempfile.mkdtemp())
    outside = Path(tempfile.mkdtemp())
    try:
        (root / "safe").mkdir()
        (root / "safe" / "link").symlink_to(outside, target_is_directory=True)
        for candidate in (root.parent / "outside", root / ".." / "escape", root / "safe" / "link" / "file"):
            try:
                parallel_execute.bounded_path(root, candidate)
            except parallel_execute.PathBoundaryError as exc:
                assert str(exc)
            else:
                raise AssertionError("unsafe path must be rejected")
    finally:
        shutil.rmtree(root)
        shutil.rmtree(outside)


def test_disabled_coordinator_returns_serial_without_constructing_adapter() -> None:
    root = make_repo(mode="disabled")
    try:
        constructed = False

        def factory() -> object:
            nonlocal constructed
            constructed = True
            return object()

        result = parallel_execute.Coordinator(root, "fixture", adapter_factory=factory).start()
        assert result["fallback"] is True
        assert result["reason"] == "disabled-mode"
        assert result["lanes"][0]["id"] == "serial"
        assert constructed is False
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
