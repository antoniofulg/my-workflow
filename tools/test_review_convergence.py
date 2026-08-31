"""Spec-derived tests for durable blocker-fingerprint convergence."""

from __future__ import annotations

import shutil
import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/workflow-spec-driven/scripts"))
import review_convergence


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
CONVERGENCE_CLI = REPOSITORY_ROOT / ".agents/skills/workflow-spec-driven/scripts/review_convergence.py"


def configured_root(stall_attempts: int = 3) -> Path:
    root = Path(tempfile.mkdtemp())
    config = (REPOSITORY_ROOT / ".my-workflow.toml.example").read_text(encoding="utf-8")
    (root / ".my-workflow.toml").write_text(
        config.replace("stall_attempts = 3", f"stall_attempts = {stall_attempts}"),
        encoding="utf-8",
    )
    return root


def record_cli(root: Path, *arguments: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(CONVERGENCE_CLI), "--root", str(root), "--feature", "fixture", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_feature_path_is_strict_kebab_and_bounded() -> None:
    root = configured_root()
    try:
        for feature in ("../escape", "feature/sub", ".", "Feature", "feature_name", "feature."):
            try:
                review_convergence.state_path(root, feature)
            except ValueError:
                pass
            else:
                raise AssertionError(f"unsafe feature slug accepted: {feature}")
        path = review_convergence.state_path(root, "parallel-slice-executor")
        assert path.resolve().parent == (root / ".specs/features/parallel-slice-executor").resolve()
    finally:
        shutil.rmtree(root)


def test_previous_fingerprint_must_exist_and_belong_to_same_requirement() -> None:
    root = configured_root()
    try:
        try:
            review_convergence.record_failure(root, "fixture", "EXE-08", "root", "path", previous_fingerprint="unknown")
        except ValueError as exc:
            assert "previous" in str(exc)
        else:
            raise AssertionError("unknown previous fingerprint must not create state")
        first = review_convergence.record_failure(root, "fixture", "EXE-08", "root", "path")
        try:
            review_convergence.record_failure(root, "fixture", "EXE-09", "changed", "path", previous_fingerprint=first["fingerprint"])
        except ValueError as exc:
            assert "requirement" in str(exc)
        else:
            raise AssertionError("foreign previous fingerprint must halt")
    finally:
        shutil.rmtree(root)


def test_matching_previous_fingerprint_and_green_gate_closes_without_increment() -> None:
    root = configured_root()
    try:
        failed = review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release")
        closed = review_convergence.record_result(
            root,
            "fixture",
            "EXE-08",
            "release ordering",
            "worker-release",
            verifier_failed=False,
            gate_passed=True,
            previous_fingerprint=failed["fingerprint"],
        )
        assert closed["fingerprint"] == failed["fingerprint"]
        assert closed["failed_remediations"] == 1
        assert closed["status"] == "closed"
    finally:
        shutil.rmtree(root)


def test_python_gate_discovers_every_tracked_python_suite() -> None:
    root = Path(__file__).resolve().parent.parent
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    script = package["scripts"]["test:python"]
    assert "git ls-files" in script
    assert "scripts/test_*.py" in script and "tools/test_*.py" in script and "sort" in script
    discovered = subprocess.check_output(
        ["git", "ls-files", "--", "scripts/test_*.py", "tools/test_*.py"],
        cwd=root,
        text=True,
    ).splitlines()
    assert "scripts/test_ai_memory.py" in discovered
    assert Path(__file__).relative_to(root).as_posix() in discovered


def test_public_flow_persists_live_remediation_and_keeps_gate_unavailable_distinct() -> None:
    root = configured_root(2)
    try:
        common = ("EXE-08", "progress boundary", "post-cap remediation")
        first = record_cli(
            root, "--requirement", common[0], "--root-cause", common[1], "--failure-path", common[2],
            "--verifier-failed", "--failing-test", "/tmp/project/case.test.ts:8:2 > alpha (9ms)",
            "--failing-test", "/tmp/project/case.test.ts:9:2 > beta (11ms)", "--fix-tried", "guard input",
        )
        fingerprint = str(first["fingerprint"])
        generation = first["generations"][-1]
        assert generation["attempt_count"] == 1
        assert generation["minimum_failing_count"] == 2
        assert generation["consecutive_stalls"] == 0
        assert generation["failing_signature"] == "case.test.ts > alpha | case.test.ts > beta"

        stalled = record_cli(
            root, "--requirement", common[0], "--root-cause", common[1], "--failure-path", common[2],
            "--previous-fingerprint", fingerprint, "--verifier-failed",
            "--failing-test", "case.test.ts:9:2 > beta", "--failing-test", "case.test.ts:8:2 > alpha",
            "--fix-tried", "retry",
        )
        assert stalled["generations"][-1]["consecutive_stalls"] == 1

        progress = record_cli(
            root, "--requirement", common[0], "--root-cause", common[1], "--failure-path", common[2],
            "--previous-fingerprint", fingerprint, "--verifier-failed", "--failing-test", "case.test.ts:8:2 > alpha",
            "--fix-tried", "split test",
        )
        generation = progress["generations"][-1]
        assert generation["minimum_failing_count"] == 1
        assert generation["consecutive_stalls"] == 0
        assert generation["attempt_count"] == 3
        assert generation["fixes_tried"] == ["guard input", "retry", "split test"]

        config = root / ".my-workflow.toml"
        config.write_text(config.read_text(encoding="utf-8").replace("stall_attempts = 2", "stall_attempts = 1"), encoding="utf-8")
        halted = record_cli(
            root, "--requirement", common[0], "--root-cause", common[1], "--failure-path", common[2],
            "--previous-fingerprint", fingerprint, "--verifier-failed", "--failing-test", "case.test.ts:8:2 > alpha",
            "--fix-tried", "re-run",
        )
        generation = halted["generations"][-1]
        assert halted["status"] == "halted"
        assert generation["halt_reason"] == "stall_threshold_reached"
        assert generation["consecutive_stalls"] == 1
        assert generation["attempt_count"] == 4
        assert generation["failing_signature"] == "case.test.ts > alpha"

        unavailable = record_cli(
            root, "--requirement", "EXE-09", "--root-cause", "provider outage", "--failure-path", "gate",
            "--gate-unavailable", "--failing-test", "case.test.ts:3:1 > gamma", "--fix-tried", "inspect output",
        )
        unavailable_generation = unavailable["generations"][-1]
        assert unavailable["status"] == "halted"
        assert unavailable["failed_remediations"] == 0
        assert unavailable_generation["halt_reason"] == "scoped_gate_unavailable"
        assert unavailable_generation["consecutive_stalls"] == 0
        assert unavailable_generation["attempt_count"] == 1
        assert unavailable_generation["fixes_tried"] == ["inspect output"]

        payload = json.loads(review_convergence.state_path(root, "fixture").read_text(encoding="utf-8"))
        stored = payload["fingerprints"][fingerprint]
        assert stored["generations"][-1]["minimum_failing_count"] == 1
        assert stored["generations"][-1]["failed_remediations"] == 4
        assert len(payload["fingerprints"]) == 2
    finally:
        shutil.rmtree(root)


def test_same_fingerprint_counts_failed_verifier_and_halts_after_three_stalls() -> None:
    root = configured_root()
    try:
        results = [
            review_convergence.record_failure(
                root, "fixture", "EXE-08", "release ordering", "worker-release",
                gate_passed=True, failing_tests=["a"],
            )
            for _ in range(4)
        ]
        first, second, third, fourth = results
        assert first["failed_remediations"] == 1
        assert second["failed_remediations"] == 2
        assert third["failed_remediations"] == 3
        assert third["status"] == "open"
        assert fourth["failed_remediations"] == 4
        assert fourth["status"] == "halted"
    finally:
        shutil.rmtree(root)


def test_distinct_fingerprints_are_independent_and_pass_does_not_increment() -> None:
    root = configured_root()
    try:
        first = review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release")
        passed = review_convergence.record_result(root, "fixture", "EXE-08", "release ordering", "worker-release", verifier_failed=False, gate_passed=False)
        distinct = review_convergence.record_failure(root, "fixture", "EXE-09", "waiter state", "follow-up")
        assert first["failed_remediations"] == 1
        assert passed["failed_remediations"] == 1
        assert distinct["failed_remediations"] == 1
        assert first["fingerprint"] != distinct["fingerprint"]
    finally:
        shutil.rmtree(root)


def test_reopen_with_rewording_preserves_identity_and_count_after_restart() -> None:
    root = configured_root()
    try:
        first = review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release")
        review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release")
        reopened = review_convergence.record_failure(
            root, "fixture", "EXE-08", "release acceptance order", "worker-release", previous_fingerprint=first["fingerprint"]
        )
        halted = review_convergence.record_failure(
            root, "fixture", "EXE-08", "release acceptance order", "worker-release",
            previous_fingerprint=first["fingerprint"],
        )
        assert reopened["fingerprint"] == first["fingerprint"]
        assert reopened["failed_remediations"] == 3
        assert reopened["status"] == "open"
        assert halted["failed_remediations"] == 4
        assert halted["status"] == "halted"
    finally:
        shutil.rmtree(root)


def _halted(root: Path) -> dict[str, object]:
    entry: dict[str, object] = {}
    for _ in range(4):
        entry = review_convergence.record_failure(
            root, "hybrid-slice-execution", "HSE-24,HSE-25,HSE-39",
            "repository-owned request writes state outside repository while canonical exact-once ledger omits git and lease mutations",
            "a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd",
            gate_passed=True,
        )
    return entry


AUTHORIZATION = ".specs/features/hybrid-slice-execution/decisions.md#authorized-cp-s4-resume--2026-08-28"


def test_UT017_authorized_resume_appends_generation_and_preserves_halt_history() -> None:
    root = configured_root()
    try:
        halted = _halted(root)
        path = review_convergence.state_path(root, "hybrid-slice-execution")
        before = json.loads(path.read_text(encoding="utf-8"))
        entry_before = deepcopy(before["fingerprints"][halted["fingerprint"]])
        resumed = review_convergence.resume(root, "hybrid-slice-execution", str(halted["fingerprint"]), AUTHORIZATION)
        assert resumed["current_generation"] == 2
        assert resumed["failed_remediations"] == 4
        assert resumed["status"] == "open"
        generation_one = resumed["generations"][0]
        assert generation_one == entry_before["generations"][0]
        assert resumed["generations"][0]["halt_event"]["status"] == "halted"
        assert resumed["generations"][1]["failed_remediations"] == 0
        assert resumed["generations"][1]["authorization_ref"] == AUTHORIZATION
    finally:
        shutil.rmtree(root)


def test_UT018_SEC012_resume_rejects_every_bypass_before_writing() -> None:
    root = configured_root()
    try:
        halted = _halted(root)
        path = review_convergence.state_path(root, "hybrid-slice-execution")
        original = path.read_bytes()
        attempts = (
            lambda: review_convergence.resume(root, "hybrid-slice-execution", str(halted["fingerprint"]), ""),
            lambda: review_convergence.resume(root, "hybrid-slice-execution", "f" * 64, AUTHORIZATION),
            lambda: review_convergence.record_result(root, "hybrid-slice-execution", "HSE-24,HSE-25,HSE-39", "root", "path", verifier_failed=False, gate_passed=True, previous_fingerprint=str(halted["fingerprint"])),
            lambda: review_convergence.record_failure(root, "hybrid-slice-execution", "HSE-24,HSE-25,HSE-39", "reworded root", "path", previous_fingerprint=str(halted["fingerprint"])),
            lambda: review_convergence.record_failure(root, "hybrid-slice-execution", "HSE-24,HSE-25,HSE-39", "replacement root", "replacement path"),
        )
        for attempt in attempts:
            try:
                attempt()
            except ValueError:
                pass
            else:
                raise AssertionError("halt bypass unexpectedly succeeded")
            assert path.read_bytes() == original
        altered = json.loads(original)
        altered["fingerprints"][halted["fingerprint"]]["failed_remediations"] = 0
        path.write_text(json.dumps(altered), encoding="utf-8")
        reset_bytes = path.read_bytes()
        try:
            review_convergence.resume(root, "hybrid-slice-execution", str(halted["fingerprint"]), AUTHORIZATION)
        except ValueError:
            pass
        else:
            raise AssertionError("inconsistent manually reset state was accepted")
        assert path.read_bytes() == reset_bytes
    finally:
        shutil.rmtree(root)


def test_UT019_resumed_generation_closes_only_on_fresh_independent_pass() -> None:
    root = configured_root()
    try:
        halted = _halted(root)
        review_convergence.resume(root, "hybrid-slice-execution", str(halted["fingerprint"]), AUTHORIZATION)
        args = (root, "hybrid-slice-execution", "HSE-24,HSE-25,HSE-39", "repository-owned request writes state outside repository while canonical exact-once ledger omits git and lease mutations", "a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd")
        open_result = review_convergence.record_result(*args, verifier_failed=False, gate_passed=True, previous_fingerprint=str(halted["fingerprint"]))
        assert open_result["status"] == "open"
        red_gate = review_convergence.record_result(*args, verifier_failed=False, gate_passed=False, previous_fingerprint=str(halted["fingerprint"]), independent=True, evidence_ref=".specs/features/hybrid-slice-execution/validation-s4.md#pass")
        assert red_gate["status"] == "open"
        closed = review_convergence.record_result(*args, verifier_failed=False, gate_passed=True, previous_fingerprint=str(halted["fingerprint"]), independent=True, evidence_ref=".specs/features/hybrid-slice-execution/validation-s4.md#pass")
        assert closed["status"] == "closed"
        assert closed["generations"][0]["status"] == "halted"
        assert closed["generations"][0]["failed_remediations"] == 4
        assert closed["generations"][1]["status"] == "closed"

        second_root = configured_root()
        try:
            second = _halted(second_root)
            review_convergence.resume(second_root, "hybrid-slice-execution", str(second["fingerprint"]), AUTHORIZATION)
            for _ in range(4):
                result = review_convergence.record_failure(second_root, "hybrid-slice-execution", "HSE-24,HSE-25,HSE-39", "repository-owned request writes state outside repository while canonical exact-once ledger omits git and lease mutations", "a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd", previous_fingerprint=str(second["fingerprint"]), gate_passed=True)
            assert result["generations"][1]["failed_remediations"] == 4
            assert result["generations"][1]["status"] == "halted"
        finally:
            shutil.rmtree(second_root)
    finally:
        shutil.rmtree(root)


def test_invalid_halted_generation_reason_is_rejected_without_rewriting_state() -> None:
    for invalid_status, failures in (("halted", 2),):
        root = configured_root()
        try:
            entry = review_convergence.record_failure(root, "fixture", "EXE-08", "root", "path")
            path = review_convergence.state_path(root, "fixture")
            payload = json.loads(path.read_text(encoding="utf-8"))
            stored = payload["fingerprints"][entry["fingerprint"]]
            generation = stored["generations"][0]
            generation["status"] = invalid_status
            generation["failed_remediations"] = failures
            if invalid_status == "halted":
                generation["halt_event"] = {
                    "generation": 1,
                    "failed_remediations": failures,
                    "status": "halted",
                }
                generation["halt_reason"] = "stall_threshold_reached"
            else:
                generation.pop("halt_event", None)
            stored["status"] = invalid_status
            stored["failed_remediations"] = failures
            path.write_text(json.dumps(payload), encoding="utf-8")
            before = path.read_bytes()
            try:
                review_convergence.record_failure(root, "fixture", "EXE-08", "root", "path")
            except ValueError as exc:
                assert "generation" in str(exc)
            else:
                raise AssertionError(f"invalid {invalid_status} generation was accepted")
            assert path.read_bytes() == before
        finally:
            shutil.rmtree(root)


def test_invalid_legacy_thresholds_are_rejected_without_rewriting_state() -> None:
    for invalid_status, failures in (("halted", 2), ("open", 3), ("closed", 3)):
        root = configured_root()
        try:
            path = review_convergence.state_path(root, "fixture")
            path.parent.mkdir(parents=True)
            key = review_convergence.fingerprint("EXE-08", "root", "path")
            payload = {
                "version": 1,
                "feature": "fixture",
                "fingerprints": {
                    key: {
                        "fingerprint": key,
                        "requirement": "exe-08",
                        "root_cause": "root",
                        "failure_path": "path",
                        "failed_remediations": failures,
                        "status": invalid_status,
                    }
                },
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            before = path.read_bytes()
            try:
                review_convergence.record_failure(root, "fixture", "EXE-08", "root", "path")
            except ValueError as exc:
                assert "convergence entry" in str(exc)
            else:
                raise AssertionError(f"invalid legacy {invalid_status} entry was accepted")
            assert path.read_bytes() == before
        finally:
            shutil.rmtree(root)


def test_boolean_failure_counters_are_not_integer_counters() -> None:
    root = configured_root()
    try:
        entry = review_convergence.record_failure(root, "fixture", "EXE-08", "root", "path")
        path = review_convergence.state_path(root, "fixture")
        payload = json.loads(path.read_text(encoding="utf-8"))
        stored = payload["fingerprints"][entry["fingerprint"]]
        stored["failed_remediations"] = True
        stored["generations"][0]["failed_remediations"] = True
        path.write_text(json.dumps(payload), encoding="utf-8")
        before = path.read_bytes()
        try:
            review_convergence.record_failure(root, "fixture", "EXE-08", "root", "path")
        except ValueError as exc:
            assert "generation" in str(exc) or "convergence" in str(exc)
        else:
            raise AssertionError("boolean failure counters must be rejected")
        assert path.read_bytes() == before
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
