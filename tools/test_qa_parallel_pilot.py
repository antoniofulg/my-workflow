"""Contract test for the disposable E2E-001 pilot handoff."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HANDOFF = ROOT / ".specs/features/parallel-slice-executor/qa-pilot.md"
HARNESS = ROOT / "tools/qa_parallel_pilot.py"
OWNED_WORKTREES = ("parallel-pilot/A-T1", "parallel-pilot/B-T2")

sys.path.insert(0, str(ROOT / "tools"))
import qa_parallel_pilot
sys.path.insert(0, str(ROOT / ".agents/skills/autonomous/scripts"))
import parallel_execute


def test_pilot_handoff_uses_disposable_safe_fixture_and_dry_run_two_lanes() -> None:
    handoff = HANDOFF.read_text(encoding="utf-8")
    assert "qa_parallel_pilot.py setup" in handoff
    assert "qa_parallel_pilot.py dry-run" in handoff
    assert "qa_parallel_pilot.py cleanup" in handoff
    assert "lifecycle-check --root" in handoff
    assert "--feature parallel-slice-executor" not in handoff
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    try:
        dry_run = subprocess.run(
            [sys.executable, str(HARNESS), "dry-run", "--root", fixture],
            text=True,
            capture_output=True,
            check=False,
        )
        result = json.loads(dry_run.stdout)
        snapshot = json.loads(
            (fixture_root / ".specs/features/parallel-pilot/workflow.json").read_text(encoding="utf-8")
        )
        assert snapshot["version"] == 2
        assert result["mode"] == "safe"
        assert result["validated"] is True
        assert result["repository_head"] == result["source_git_head"]
        owner_common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=ROOT, text=True).strip()
        source_common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=fixture_root, text=True).strip()
        assert Path(source_common).resolve() == (ROOT / owner_common if not Path(owner_common).is_absolute() else Path(owner_common)).resolve()
        assert len(result["lanes"]) == 2
        assert all(lane["resources"] == [] for lane in result["lanes"])
        assert all(lane["status"] == "ready" for lane in result["lanes"])
        child = qa_parallel_pilot._worktree_root(fixture_root) / "parallel-pilot" / "A-T1"
        subprocess.run(["git", "worktree", "add", "--detach", str(child), result["source_git_head"]], cwd=fixture_root, check=True, capture_output=True)
        assert (child / ".specs/features/parallel-pilot/tasks.md").read_text(encoding="utf-8").startswith("### T1: pilot A")
        assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=child, text=True).strip() == result["source_git_head"]
    finally:
        refused = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], text=True, capture_output=True, check=False)
        assert refused.returncode != 0 and json.loads(refused.stdout)["reason"] == "cleanup-authorization-missing"
        first_cleanup = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], text=True, capture_output=True, check=False)
        assert json.loads(first_cleanup.stdout)["aborted"] is True
        assert json.loads(first_cleanup.stdout)["cleaned"] is False
        second_cleanup = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], text=True, capture_output=True, check=False)
        assert json.loads(second_cleanup.stdout)["idempotent"] is True
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink()
    assert not fixture_root.exists()


def test_lifecycle_check_rejects_missing_receipts_and_wrong_order() -> None:
    state = {"state": {"lanes": {}, "actions": {}}}
    for lane_id, slice_id, task_id in (("slice-A", "A", "T1"), ("slice-B", "B", "T2")):
        state["state"]["lanes"][lane_id] = {
            "slice": slice_id, "task": task_id, "state": "complete",
            "dispatch_id": f"dispatch-{slice_id}",
            "lifecycle_events": ["worker_done", "worker_read", "worker_ack", "worker_release"],
        }
    assert qa_parallel_pilot.lifecycle_complete(state) is False
    state["state"]["actions"] = {
        "worker-A": {"action": "worker", "lane": "slice-A", "status": "accepted", "delivery": {"event": "worker_done"}, "completion": {"delivery_id": "delivery-A"}},
        "worker_ack-A": {"action": "worker_ack", "lane": "slice-A", "status": "accepted", "receipt": {"acknowledged": True, "delivery_id": "delivery-A"}},
        "worker_release-A": {"action": "worker_release", "lane": "slice-A", "status": "accepted", "receipt": {"released": True, "dispatch_id": "dispatch-A"}},
        "worker-B": {"action": "worker", "lane": "slice-B", "status": "accepted", "delivery": {"event": "worker_done"}, "completion": {"delivery_id": "delivery-B"}},
        "worker_ack-B": {"action": "worker_ack", "lane": "slice-B", "status": "accepted", "receipt": {"acknowledged": True, "delivery_id": "delivery-B"}},
        "worker_release-B": {"action": "worker_release", "lane": "slice-B", "status": "accepted", "receipt": {"released": True, "dispatch_id": "dispatch-B"}},
    }
    state["state"]["lanes"]["slice-B"]["lifecycle_events"] = ["worker_done", "worker_ack", "worker_read", "worker_release"]
    assert qa_parallel_pilot.lifecycle_complete(state) is False


def test_normal_cleanup_requires_lifecycle_authorization_and_removes_exact_source_worktree() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    sibling_root = qa_parallel_pilot._worktree_root(fixture_root)
    source_head = json.loads((fixture_root / ".specs/features/parallel-pilot/workflow.json").read_text(encoding="utf-8"))["git_head"]
    try:
        lanes: dict[str, dict[str, object]] = {}
        actions: dict[str, dict[str, object]] = {}
        for lane_id, slice_id, task_id, relative in (("slice-A", "A", "T1", OWNED_WORKTREES[0]), ("slice-B", "B", "T2", OWNED_WORKTREES[1])):
            child = sibling_root / relative
            child.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "worktree", "add", "--detach", str(child), source_head], cwd=fixture_root, check=True, capture_output=True)
            dispatch = f"dispatch-{slice_id}"
            lanes[lane_id] = {
                "slice": slice_id, "task": task_id, "state": "complete", "resources": [],
                "worktree_id": qa_parallel_pilot._gitdir(child), "worktree_path": str(child), "dispatch_id": dispatch,
                "lifecycle_events": ["worker_done", "worker_read", "worker_ack", "worker_release"],
            }
            actions.update({
                f"worker-{slice_id}": {"key": f"worker-{slice_id}", "action": "worker", "status": "accepted", "lane": lane_id, "external_id": dispatch, "receipt": {"dispatch_id": dispatch}, "completion": {"delivery_id": f"delivery-{slice_id}"}, "delivery": {"event": "worker_done"}},
                f"ack-{slice_id}": {"key": f"ack-{slice_id}", "action": "worker_ack", "status": "accepted", "lane": lane_id, "external_id": f"ack-{slice_id}", "receipt": {"acknowledged": True, "delivery_id": f"delivery-{slice_id}"}},
                f"release-{slice_id}": {"key": f"release-{slice_id}", "action": "worker_release", "status": "accepted", "lane": lane_id, "external_id": f"release-{slice_id}", "receipt": {"released": True, "dispatch_id": dispatch}},
            })
        state = parallel_execute.new_runtime_state(str(fixture_root.resolve()), "parallel-pilot", "safe", source_head)
        state["lanes"] = lanes
        state["actions"] = actions
        parallel_execute.atomic_write_json(parallel_execute.runtime_state_path(fixture_root, "parallel-pilot"), state)
        authorized = subprocess.run([sys.executable, str(HARNESS), "lifecycle-check", "--root", fixture], text=True, capture_output=True, check=True)
        assert json.loads(authorized.stdout)["authorized"] is True
        state["lanes"]["slice-A"]["state"] = "serial"
        parallel_execute.atomic_write_json(parallel_execute.runtime_state_path(fixture_root, "parallel-pilot"), state)
        stale = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], text=True, capture_output=True, check=False)
        assert stale.returncode != 0
        assert fixture_root.exists() and (sibling_root / OWNED_WORKTREES[0]).exists()
        state["lanes"]["slice-A"]["state"] = "complete"
        parallel_execute.atomic_write_json(parallel_execute.runtime_state_path(fixture_root, "parallel-pilot"), state)
        cleanup = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], text=True, capture_output=True, check=False)
        assert cleanup.returncode == 0, cleanup.stdout + cleanup.stderr
        result = json.loads(cleanup.stdout)
        assert result["cleaned"] is True
        assert not fixture_root.exists()
        record = json.loads((fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").read_text(encoding="utf-8"))
        assert record["lifecycle_version"] == 1
        assert record["lane_worktree_ids"]["slice-A"] == lanes["slice-A"]["worktree_id"]
        repeated = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], text=True, capture_output=True, check=True)
        assert json.loads(repeated.stdout)["idempotent"] is True
    finally:
        if fixture_root.exists():
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def test_diagnostic_abort_refuses_pending_recoverable_worker_effect() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    try:
        source_head = json.loads((fixture_root / ".specs/features/parallel-pilot/workflow.json").read_text(encoding="utf-8"))["git_head"]
        state = parallel_execute.new_runtime_state(str(fixture_root.resolve()), "parallel-pilot", "safe", source_head)
        state["lanes"]["slice-A"] = {"slice": "A", "task": "T1", "state": "serial", "resources": []}
        state["actions"]["worker-A"] = {
            "key": "worker-A", "action": "worker", "status": "pending", "lane": "slice-A",
            "partial_effect": {"code": "selector_not_found", "run_id": "run-A", "task_id": "task-A"},
        }
        parallel_execute.atomic_write_json(parallel_execute.runtime_state_path(fixture_root, "parallel-pilot"), state)
        refused = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], text=True, capture_output=True, check=False)
        result = json.loads(refused.stdout)
        assert refused.returncode != 0
        assert result["reason"] == "worker-may-be-live"
        assert fixture_root.exists()
    finally:
        if fixture_root.exists():
            state["actions"]["worker-A"].pop("partial_effect", None)
            parallel_execute.atomic_write_json(parallel_execute.runtime_state_path(fixture_root, "parallel-pilot"), state)
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)
def test_pilot_dry_run_rejects_frozen_head_mutation_and_unmarked_cleanup() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    try:
        workflow = fixture_root / ".specs/features/parallel-pilot/workflow.json"
        payload = json.loads(workflow.read_text(encoding="utf-8"))
        original_snapshot = dict(payload)
        ownership_path = fixture_root / ".parallel-slice-qa-ownership.json"
        ownership = json.loads(ownership_path.read_text(encoding="utf-8"))
        payload["version"] = 1
        payload["git_head"] = original_snapshot["git_head"]
        workflow.write_text(json.dumps(payload), encoding="utf-8")
        rejected_version = subprocess.run([sys.executable, str(HARNESS), "dry-run", "--root", fixture], text=True, capture_output=True, check=False)
        assert rejected_version.returncode != 0
        payload["version"] = 2
        payload["git_head"] = "0" * 40
        workflow.write_text(json.dumps(payload), encoding="utf-8")
        rejected = subprocess.run([sys.executable, str(HARNESS), "dry-run", "--root", fixture], text=True, capture_output=True, check=False)
        assert rejected.returncode != 0
        arbitrary = fixture_root.parent / "parallel-slice-pilot-unmarked"
        arbitrary.mkdir()
        try:
            refused = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", str(arbitrary)], text=True, capture_output=True, check=False)
            assert refused.returncode != 0
            assert arbitrary.exists()
        finally:
            arbitrary.rmdir()
    finally:
        workflow.write_text(json.dumps(original_snapshot), encoding="utf-8")
        ownership_path.write_text(json.dumps(ownership), encoding="utf-8")
        subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def test_cleanup_removes_exact_owned_worktree_and_preserves_unowned_sibling() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    sibling_root = qa_parallel_pilot._worktree_root(fixture_root)
    owned = sibling_root / "parallel-pilot" / "A-T1"
    unowned = sibling_root / "parallel-pilot" / "unowned"
    try:
        owned.parent.mkdir(parents=True)
        subprocess.run(["git", "worktree", "add", "--detach", str(owned), "HEAD"], cwd=fixture_root, check=True, capture_output=True)
        unowned.mkdir()
        sentinel = unowned / "sentinel"
        sentinel.write_text("preserve\n", encoding="utf-8")
        cleanup = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], text=True, capture_output=True, check=False)
        assert cleanup.returncode != 0
        assert json.loads(cleanup.stdout)["aborted"] is True
        assert not owned.exists()
        assert sentinel.read_text(encoding="utf-8") == "preserve\n"
    finally:
        if fixture_root.exists():
            subprocess.run(["git", "worktree", "remove", "--force", str(owned)], cwd=fixture_root, check=False, capture_output=True)
        if fixture_root.exists():
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
        if sibling_root.exists():
            shutil.rmtree(sibling_root)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def test_cleanup_rejects_source_head_only_attestation_tamper_before_deletion() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    ownership_path = fixture_root / ".parallel-slice-qa-ownership.json"
    original = json.loads(ownership_path.read_text(encoding="utf-8"))
    owned = qa_parallel_pilot._worktree_root(fixture_root) / "parallel-pilot" / "A-T1"
    try:
        owned.parent.mkdir(parents=True)
        subprocess.run(["git", "worktree", "add", "--detach", str(owned), "HEAD"], cwd=fixture_root, check=True, capture_output=True)
        tampered = dict(original)
        tampered["source_git_head"] = "0" * 40
        ownership_path.write_text(json.dumps(tampered), encoding="utf-8")
        rejected = subprocess.run(
            [sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture],
            text=True,
            capture_output=True,
            check=False,
        )
        assert rejected.returncode != 0
        assert fixture_root.exists()
        assert (fixture_root / ".parallel-slice-qa-ownership.json").exists()
        assert owned.exists()
    finally:
        if fixture_root.exists():
            ownership_path.write_text(json.dumps(original), encoding="utf-8")
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def test_cleanup_retry_preserves_residual_failure_until_residual_is_gone() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    sibling_root = qa_parallel_pilot._worktree_root(fixture_root)
    residual = sibling_root / "parallel-pilot" / "unowned" / "sentinel"
    residual.parent.mkdir(parents=True)
    residual.write_text("preserve\n", encoding="utf-8")
    attestation = fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned"
    try:
        first = subprocess.run(
            [sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture],
            text=True,
            capture_output=True,
            check=False,
        )
        first_result = json.loads(first.stdout)
        assert first.returncode != 0
        assert first_result["cleaned"] is False
        assert str(residual) in first_result["residual_paths"]
        record = json.loads(attestation.read_text(encoding="utf-8"))
        assert record["status"] == "diagnostic-aborted-with-residual"
        assert str(residual) in record["residual_paths"]

        retry = subprocess.run(
            [sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture],
            text=True,
            capture_output=True,
            check=False,
        )
        retry_result = json.loads(retry.stdout)
        assert retry.returncode != 0
        assert retry_result["cleaned"] is False
        assert retry_result["residual_paths"] == first_result["residual_paths"]
        assert residual.read_text(encoding="utf-8") == "preserve\n"

        residual.unlink()
        residual.parent.rmdir()
        residual.parent.parent.rmdir()
        cleaned = subprocess.run(
            [sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture],
            text=True,
            capture_output=True,
            check=False,
        )
        cleaned_result = json.loads(cleaned.stdout)
        assert cleaned_result["cleaned"] is False
        assert cleaned_result["aborted"] is True
        assert cleaned_result["idempotent"] is True
    finally:
        if fixture_root.exists():
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
        if sibling_root.exists():
            shutil.rmtree(sibling_root)
        attestation.unlink(missing_ok=True)


def test_cleanup_rejects_every_non_head_ownership_tamper_before_any_effect() -> None:
    tamper_cases = {
        "root": lambda ownership, fixture_root: ownership.update(root=str(fixture_root / "not-the-fixture")),
        "feature": lambda ownership, fixture_root: ownership.update(feature="not-the-feature"),
        "missing-worktrees": lambda ownership, fixture_root: ownership.pop("worktrees"),
        "extra-worktree": lambda ownership, fixture_root: ownership.update(worktrees=[*OWNED_WORKTREES, "parallel-pilot/C-T3"]),
        "duplicate-worktree": lambda ownership, fixture_root: ownership.update(worktrees=[OWNED_WORKTREES[0], OWNED_WORKTREES[0]]),
        "outside-worktree": lambda ownership, fixture_root: ownership.update(worktrees=["../outside"]),
        "reordered-worktrees": lambda ownership, fixture_root: ownership.update(worktrees=list(reversed(OWNED_WORKTREES))),
    }
    for name, tamper in tamper_cases.items():
        setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
        fixture = json.loads(setup.stdout)["root"]
        fixture_root = Path(fixture)
        ownership_path = fixture_root / ".parallel-slice-qa-ownership.json"
        original = json.loads(ownership_path.read_text(encoding="utf-8"))
        sibling_root = qa_parallel_pilot._worktree_root(fixture_root)
        owned = sibling_root / "parallel-pilot" / "A-T1"
        sentinel = sibling_root / "parallel-pilot" / "unowned" / "sentinel"
        try:
            owned.parent.mkdir(parents=True)
            subprocess.run(["git", "worktree", "add", "--detach", str(owned), "HEAD"], cwd=fixture_root, check=True, capture_output=True)
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text(f"preserve {name}\n", encoding="utf-8")
            tampered = dict(original)
            tamper(tampered, fixture_root)
            ownership_path.write_text(json.dumps(tampered), encoding="utf-8")
            rejected = subprocess.run(
                [sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture],
                text=True,
                capture_output=True,
                check=False,
            )
            assert rejected.returncode != 0
            assert fixture_root.exists()
            assert owned.exists()
            assert sentinel.read_text(encoding="utf-8") == f"preserve {name}\n"
            assert not (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").exists()
        finally:
            if fixture_root.exists():
                ownership_path.write_text(json.dumps(original), encoding="utf-8")
                subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
            if sibling_root.exists():
                shutil.rmtree(sibling_root)
            if fixture_root.exists():
                shutil.rmtree(fixture_root)
            (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def _prepare_authorized_fixture() -> tuple[str, Path, Path, dict[str, dict[str, object]]]:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    sibling_root = qa_parallel_pilot._worktree_root(fixture_root)
    source_head = json.loads((fixture_root / ".specs/features/parallel-pilot/workflow.json").read_text(encoding="utf-8"))["git_head"]
    lanes: dict[str, dict[str, object]] = {}
    actions: dict[str, dict[str, object]] = {}
    for lane_id, slice_id, task_id, relative in (("slice-A", "A", "T1", OWNED_WORKTREES[0]), ("slice-B", "B", "T2", OWNED_WORKTREES[1])):
        child = sibling_root / relative
        child.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "worktree", "add", "--detach", str(child), source_head], cwd=fixture_root, check=True, capture_output=True)
        dispatch = f"dispatch-{slice_id}"
        lanes[lane_id] = {"slice": slice_id, "task": task_id, "state": "complete", "resources": [], "worktree_id": qa_parallel_pilot._gitdir(child), "worktree_path": str(child), "dispatch_id": dispatch, "lifecycle_events": ["worker_done", "worker_read", "worker_ack", "worker_release"]}
        actions.update({
            f"worker-{slice_id}": {"key": f"worker-{slice_id}", "action": "worker", "status": "accepted", "lane": lane_id, "external_id": dispatch, "receipt": {"dispatch_id": dispatch}, "completion": {"delivery_id": f"delivery-{slice_id}"}, "delivery": {"event": "worker_done"}},
            f"ack-{slice_id}": {"key": f"ack-{slice_id}", "action": "worker_ack", "status": "accepted", "lane": lane_id, "external_id": f"ack-{slice_id}", "receipt": {"acknowledged": True, "delivery_id": f"delivery-{slice_id}"}},
            f"release-{slice_id}": {"key": f"release-{slice_id}", "action": "worker_release", "status": "accepted", "lane": lane_id, "external_id": f"release-{slice_id}", "receipt": {"released": True, "dispatch_id": dispatch}},
        })
    state = parallel_execute.new_runtime_state(str(fixture_root.resolve()), "parallel-pilot", "safe", source_head)
    state["lanes"] = lanes
    state["actions"] = actions
    parallel_execute.atomic_write_json(parallel_execute.runtime_state_path(fixture_root, "parallel-pilot"), state)
    authorized = subprocess.run([sys.executable, str(HARNESS), "lifecycle-check", "--root", fixture], text=True, capture_output=True, check=True)
    assert json.loads(authorized.stdout)["authorized"] is True
    return fixture, fixture_root, sibling_root, lanes


def test_symlink_lane_sentinel_is_rejected_before_diagnostic_deletion() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    sibling_root = qa_parallel_pilot._worktree_root(fixture_root)
    sentinel = sibling_root / "parallel-pilot" / "sentinel-target"
    lane = sibling_root / OWNED_WORKTREES[0]
    try:
        sentinel.mkdir(parents=True)
        (sentinel / "keep").write_text("keep\n", encoding="utf-8")
        lane.parent.mkdir(parents=True, exist_ok=True)
        lane.symlink_to(sentinel, target_is_directory=True)
        rejected = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], text=True, capture_output=True, check=False)
        assert rejected.returncode != 0
        assert lane.is_symlink() and (sentinel / "keep").read_text(encoding="utf-8") == "keep\n"
        assert fixture_root.exists()
    finally:
        if lane.is_symlink():
            lane.unlink()
        if fixture_root.exists():
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def test_symlinked_cleanup_anchor_is_rejected_before_destructive_deletion() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    worktree_root = qa_parallel_pilot._worktree_root(fixture_root)
    target_root = worktree_root.parent / f"{worktree_root.name}-redirect"
    try:
        (target_root / "parallel-pilot" / "A-T1").mkdir(parents=True)
        worktree_root.symlink_to(target_root, target_is_directory=True)
        rejected = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], text=True, capture_output=True, check=False)
        assert rejected.returncode != 0
        assert worktree_root.is_symlink() and (target_root / "parallel-pilot" / "A-T1").exists()
        assert fixture_root.exists()
    finally:
        if worktree_root.is_symlink():
            worktree_root.unlink()
        if target_root.exists():
            shutil.rmtree(target_root)
        if fixture_root.exists():
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def test_authorized_cleanup_reconciles_interrupted_lane_and_removed_source() -> None:
    fixture, fixture_root, sibling_root, lanes = _prepare_authorized_fixture()
    attestation = fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned"
    try:
        removed_lane = sibling_root / OWNED_WORKTREES[0]
        subprocess.run(["git", "worktree", "remove", "--force", str(removed_lane)], cwd=fixture_root, check=True, capture_output=True)
        retry = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], text=True, capture_output=True, check=False)
        assert retry.returncode == 0, retry.stdout + retry.stderr
        assert json.loads(retry.stdout)["cleaned"] is True
        assert not fixture_root.exists()
        assert json.loads(attestation.read_text(encoding="utf-8"))["status"] == "cleaned"
    finally:
        if fixture_root.exists():
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--abort-incomplete", "--root", fixture], check=False)
        attestation.unlink(missing_ok=True)


def test_authorized_cleanup_finalizes_after_all_effects_removed_before_tombstone() -> None:
    fixture, fixture_root, sibling_root, lanes = _prepare_authorized_fixture()
    attestation = fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned"
    try:
        for relative in OWNED_WORKTREES:
            subprocess.run(["git", "worktree", "remove", "--force", str(sibling_root / relative)], cwd=fixture_root, check=True, capture_output=True)
        subprocess.run(["git", "worktree", "remove", "--force", str(fixture_root)], cwd=ROOT, check=True, capture_output=True)
        finalized = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], text=True, capture_output=True, check=False)
        assert finalized.returncode == 0, finalized.stdout + finalized.stderr
        assert json.loads(finalized.stdout)["cleaned"] is True
        assert json.loads(attestation.read_text(encoding="utf-8"))["status"] == "cleaned"
    finally:
        attestation.unlink(missing_ok=True)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
