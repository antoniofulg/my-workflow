"""Canonical adoption checks. Run: python3 scripts/test_adopt.py"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/adopt.py"


def invoke(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, str(target)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def snapshot(root: Path) -> dict[str, bytes | str]:
    result: dict[str, bytes | str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        result[relative] = os.readlink(path) if path.is_symlink() else path.read_bytes() if path.is_file() else "<directory>"
    return result


def temporary_target() -> Path:
    return Path(tempfile.mkdtemp(prefix="my-workflow-adopt-"))


def test_resolves_fixed_layers_and_plan_is_read_only() -> None:
    target = temporary_target()
    try:
        before = snapshot(target)
        result = invoke(target, "plan", "--layers", "quality,parallel,parallel", "--json")
        assert result.returncode == 0, result.stderr
        document = json.loads(result.stdout)
        assert document["requested_layers"] == ["core", "parallel", "quality"]
        assert document["resolved_layers"] == ["core", "parallel", "quality"]
        assert document["status"] == "ready"
        assert any(item["path"] == "tools/orca_assisted_probe.py" for item in document["actions"])
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_full_profile_is_exactly_four_layers_and_legacy_cli_is_rejected() -> None:
    target = temporary_target()
    try:
        result = invoke(target, "plan", "--layers", "full", "--json")
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["resolved_layers"] == ["core", "parallel", "quality", "extras"]
        legacy = subprocess.run([sys.executable, str(SCRIPT), str(target)], text=True, capture_output=True, check=False)
        assert legacy.returncode == 2
        assert "plan" in legacy.stderr and "apply" in legacy.stderr
    finally:
        shutil.rmtree(target)


def test_unknown_layer_and_invalid_manifest_fail_before_target_mutation() -> None:
    target = temporary_target()
    try:
        invalid = invoke(target, "plan", "--layers", "unknown")
        assert invalid.returncode == 2
        assert snapshot(target) == {}
        manifest = target / ".my-workflow/adoption.json"
        manifest.parent.mkdir()
        manifest.write_text(json.dumps({"schema": 1, "workflow_version": "0.7.0", "layers": ["core"], "files": {"../escape": {}}, "blocks": {}}), encoding="utf-8")
        before = snapshot(target)
        result = invoke(target, "status", "--json")
        assert result.returncode == 2
        assert snapshot(target) == before
        manifest.write_text(json.dumps({"schema": 1, "workflow_version": "0.7.0", "layers": ["unknown"], "files": {}, "blocks": {}}), encoding="utf-8")
        result = invoke(target, "status", "--json")
        assert result.returncode == 2
    finally:
        shutil.rmtree(target)


def test_core_apply_records_schema_and_status_detects_drift_without_writes() -> None:
    target = temporary_target()
    try:
        applied = invoke(target, "apply", "--layers", "core", "--json")
        assert applied.returncode == 0, applied.stderr
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text(encoding="utf-8"))
        assert manifest["schema"] == 1
        assert manifest["layers"] == ["core"]
        assert all(len(record["source_sha256"]) == 64 for record in manifest["files"].values())
        clean = invoke(target, "status", "--json")
        assert clean.returncode == 0, clean.stdout + clean.stderr
        owned = target / "tools/knowledge/src/cli.ts"
        owned.write_bytes(owned.read_bytes() + b"\nconsumer drift\n")
        before = snapshot(target)
        drift = invoke(target, "status", "--json")
        assert drift.returncode == 1
        assert json.loads(drift.stdout)["status"] == "drift"
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_manifest_hashes_are_lowercase_sha256() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text(encoding="utf-8"))
        for relative, record in manifest["files"].items():
            assert record["source_sha256"] == hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            if record["ownership"] == "managed":
                assert record["installed_sha256"] == hashlib.sha256((target / relative).read_bytes()).hexdigest()
    finally:
        shutil.rmtree(target)


def test_apply_preserves_consumer_prose_and_writes_managed_blocks() -> None:
    target = temporary_target()
    try:
        (target / "AGENTS.md").write_text("# Product instructions\n\nConsumer-owned prose.\n", encoding="utf-8")
        (target / "CLAUDE.md").write_text("# Consumer Claude\n", encoding="utf-8")
        agents_before = (target / "AGENTS.md").read_bytes()
        claude_before = (target / "CLAUDE.md").read_bytes()
        result = invoke(target, "apply", "--layers", "core", "--json")
        assert result.returncode == 0, result.stderr
        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        assert agents.startswith(agents_before.decode())
        assert "my-workflow:core:start" in agents
        claude = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert claude.startswith(claude_before.decode())
        assert "@AGENTS.md" in claude
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text(encoding="utf-8"))
        assert "AGENTS.md:core" in manifest["blocks"]
        assert "CLAUDE.md:core" in manifest["blocks"]
    finally:
        shutil.rmtree(target)


def test_apply_is_cumulative_and_idempotent() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        assert invoke(target, "apply", "--layers", "parallel").returncode == 0
        first = snapshot(target)
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text(encoding="utf-8"))
        assert manifest["layers"] == ["core", "parallel"]
        assert invoke(target, "apply", "--layers", "quality,extras").returncode == 0
        complete = snapshot(target)
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text(encoding="utf-8"))
        assert manifest["layers"] == ["core", "parallel", "quality", "extras"]
        assert invoke(target, "apply", "--layers", "quality").returncode == 0
        assert snapshot(target) == complete
        assert first["tools/orca_assisted_probe.py"] == (ROOT / "tools/orca_assisted_probe.py").read_bytes()
    finally:
        shutil.rmtree(target)


def test_conflicts_abort_every_write_and_report_all_paths() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        first = target / "tools/knowledge/src/cli.ts"
        first.write_bytes(first.read_bytes() + b"\nconsumer edit\n")
        unowned = target / "tools/orca_assisted_probe.py"
        unowned.parent.mkdir(parents=True, exist_ok=True)
        unowned.write_bytes(b"consumer-owned\n")
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "parallel", "--json")
        assert result.returncode == 1
        document = json.loads(result.stdout)
        assert "tools/knowledge/src/cli.ts" in document["conflicts"]
        assert "tools/orca_assisted_probe.py" in document["conflicts"]
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_skip_agents_leaves_both_instruction_files_byte_identical() -> None:
    target = temporary_target()
    try:
        (target / "AGENTS.md").write_text("consumer agents\n", encoding="utf-8")
        (target / "CLAUDE.md").write_text("consumer claude\n", encoding="utf-8")
        before = {(target / name).read_bytes() for name in ("AGENTS.md", "CLAUDE.md")}
        result = invoke(target, "apply", "--layers", "core", "--skip-agents")
        assert result.returncode == 0, result.stderr
        assert {(target / name).read_bytes() for name in ("AGENTS.md", "CLAUDE.md")} == before
        assert json.loads((target / ".my-workflow/adoption.json").read_text())["blocks"] == {}
    finally:
        shutil.rmtree(target)


def test_edited_managed_block_is_a_conflict() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        agents = target / "AGENTS.md"
        agents.write_bytes(agents.read_bytes().replace(b"Run the adopted", b"Consumer changed the adopted", 1))
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "parallel", "--json")
        assert result.returncode == 1
        assert "AGENTS.md:core" in json.loads(result.stdout)["conflicts"]
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_symlinked_destination_is_rejected_before_external_write() -> None:
    target = temporary_target()
    outside = temporary_target()
    try:
        (target / "tools").mkdir()
        (outside / "probe.py").write_text("outside\n", encoding="utf-8")
        (target / "tools/orca_assisted_probe.py").symlink_to(outside / "probe.py")
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "parallel", "--json")
        assert result.returncode == 2
        assert snapshot(target) == before
        assert (outside / "probe.py").read_text(encoding="utf-8") == "outside\n"
    finally:
        shutil.rmtree(target)
        shutil.rmtree(outside)


def test_full_profile_preserves_complete_capability_inventory_and_links_skills() -> None:
    target = temporary_target()
    try:
        result = invoke(target, "apply", "--layers", "full", "--json")
        assert result.returncode == 0, result.stderr
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text(encoding="utf-8"))
        expected: set[str] = set()
        from adopt import LAYER_MISSING_PATHS, LAYER_PATHS, _source_files

        for layer in ("core", "parallel", "quality", "extras"):
            for relative in (*LAYER_PATHS[layer], *LAYER_MISSING_PATHS[layer]):
                expected.update(_source_files(ROOT, relative))
        assert set(manifest["files"]) == expected
        assert (target / ".claude/skills/autonomous").is_symlink()
        assert os.readlink(target / ".claude/skills/autonomous") == "../../.agents/skills/autonomous"
    finally:
        shutil.rmtree(target)


def test_bun_consumer_boundary_and_probe_import_are_preserved() -> None:
    target = temporary_target()
    try:
        package = target / "package.json"
        lock = target / "bun.lock"
        package.write_text('{"name":"consumer","scripts":{"test":"bun test"}}\n', encoding="utf-8")
        lock.write_text("consumer lock\n", encoding="utf-8")
        package_before, lock_before = package.read_bytes(), lock.read_bytes()
        assert invoke(target, "apply", "--layers", "full").returncode == 0
        assert package.read_bytes() == package_before
        assert lock.read_bytes() == lock_before
        knowledge = subprocess.run(["bun", str(target / "tools/knowledge/src/cli.ts"), str(target)], cwd=target, text=True, capture_output=True, check=False)
        assert knowledge.returncode == 0, knowledge.stderr
        calls = target / "orca.calls"
        fake = target / "orca"
        fake.write_text(f"#!/bin/sh\nprintf '%s\\n' called >> {calls}\n", encoding="utf-8")
        fake.chmod(0o755)
        env = {**os.environ, "PATH": f"{target}:{os.environ.get('PATH', '')}"}
        imported = subprocess.run([sys.executable, "-c", "import tools.orca_assisted_probe"], cwd=target, env=env, text=True, capture_output=True, check=False)
        assert imported.returncode == 0, imported.stderr
        assert not calls.exists()
    finally:
        shutil.rmtree(target)


def test_existing_project_incremental_journey_is_clean() -> None:
    target = temporary_target()
    try:
        plan_core = invoke(target, "plan", "--layers", "core", "--json")
        assert plan_core.returncode == 0
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        assert invoke(target, "status", "--json").returncode == 0
        plan_more = invoke(target, "plan", "--layers", "parallel,quality,extras", "--json")
        assert plan_more.returncode == 0
        assert json.loads(plan_more.stdout)["resolved_layers"] == ["core", "parallel", "quality", "extras"]
        assert invoke(target, "apply", "--layers", "parallel,quality,extras").returncode == 0
        assert invoke(target, "status", "--json").returncode == 0
    finally:
        shutil.rmtree(target)


TESTS = (
    test_resolves_fixed_layers_and_plan_is_read_only,
    test_full_profile_is_exactly_four_layers_and_legacy_cli_is_rejected,
    test_unknown_layer_and_invalid_manifest_fail_before_target_mutation,
    test_core_apply_records_schema_and_status_detects_drift_without_writes,
    test_manifest_hashes_are_lowercase_sha256,
    test_apply_preserves_consumer_prose_and_writes_managed_blocks,
    test_apply_is_cumulative_and_idempotent,
    test_conflicts_abort_every_write_and_report_all_paths,
    test_skip_agents_leaves_both_instruction_files_byte_identical,
    test_edited_managed_block_is_a_conflict,
    test_symlinked_destination_is_rejected_before_external_write,
    test_full_profile_preserves_complete_capability_inventory_and_links_skills,
    test_bun_consumer_boundary_and_probe_import_are_preserved,
    test_existing_project_incremental_journey_is_clean,
)


if __name__ == "__main__":
    for test in TESTS:
        test()
    print(f"ok ({len(TESTS)} tests)")
