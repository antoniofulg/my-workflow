"""Canonical adoption checks. Run: python3 scripts/test_adopt.py"""

from __future__ import annotations

import hashlib
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/adopt.py"
sys.path.insert(0, str(ROOT / "scripts"))
import adopt
from adopt import LEGACY_MANAGED_TEST_DIRECTORIES, LEGACY_MANAGED_TEST_FILES, remove_legacy_managed_tests

FROZEN_PRE_FEATURE_PATHS = (
    "docs/guidelines", "docs/workflow/README.md", "docs/workflow/decisions.md",
    "docs/workflow/guidelines.md", "docs/workflow/loop.md", "docs/workflow/purpose.md",
    "docs/workflow/reviews.md", "knowledge/AGENTS.md", "knowledge/raw/README.md",
    "knowledge/wiki", "tools/knowledge/src", "tools/qa_parallel_pilot.py",
    "tools/orca_assisted_probe.py", "tools/resource_lock.py", "tools/shared/src/frontmatter.ts",
    ".agents/skills/workflow-spec-driven", ".agents/skills/deep-review", ".agents/skills/ponytail",
    ".agents/skills/ponytail-audit", ".agents/skills/ponytail-debt", ".agents/skills/ponytail-gain",
    ".agents/skills/ponytail-help", ".agents/skills/ponytail-review", ".agents/skills/qa-plan",
    ".agents/skills/qa-execute", ".agents/skills/autonomous", ".agents/skills/workflow-config",
    ".agents/skills/wspecify", ".agents/skills/wdesign", ".agents/skills/wtasks",
    ".agents/skills/wimplement", ".agents/skills/wverify",
    ".agents/skills/wreview", ".agents/skills/wqa",
    "docs/qa/README.md", "tools/ad-index.py", ".my-workflow.toml.example", "templates/agents",
)


def invoke(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, str(target)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def snapshot(root: Path) -> dict[str, tuple[object, ...]]:
    result: dict[str, tuple[object, ...]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        result[relative] = (
            ("symlink", os.readlink(path)) if path.is_symlink()
            else ("file", path.read_bytes(), path.stat().st_mode & 0o7777) if path.is_file()
            else ("directory",)
        )
    return result


def temporary_target() -> Path:
    return Path(tempfile.mkdtemp(prefix="my-workflow-adopt-"))


def commit_target(target: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=target, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "adopt-tests@example.test"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Adoption Tests"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=target, check=True)


def expect_adoption_error(callback: object) -> None:
    try:
        callback()  # type: ignore[operator]
    except adopt.AdoptionError:
        return
    raise AssertionError("expected AdoptionError")


def legacy_target(paths: tuple[str, ...] = ("tools/resource_lock.py",)) -> Path:
    target = temporary_target()
    for relative in paths:
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / relative).read_bytes() + b"\nlegacy project change\n")
    commit_target(target)
    return target


def test_resolves_fixed_layers_and_plan_is_read_only() -> None:
    target = temporary_target()
    try:
        before = snapshot(target)
        result = invoke(target, "plan", "--layers", "quality,parallel,parallel", "--json")
        assert result.returncode == 0, result.stderr
        assert result.stderr == "" and result.stdout.lstrip().startswith("{")
        document = json.loads(result.stdout)
        assert document["requested_layers"] == ["parallel", "quality"]
        assert document["resolved_layers"] == ["core", "parallel", "quality"]
        assert document["status"] == "ready"
        assert any(item["path"] == "tools/orca_assisted_probe.py" for item in document["actions"])
        expected_effects = {".gitignore", ".ignore", ".my-workflow.toml", ".my-workflow/adoption.json", ".claude/agents/planner.md", "AGENTS.md:core", ".claude/skills/workflow-config"}
        assert expected_effects <= {item["path"] for item in document["actions"]}
        assert len(document["actions"]) == len({item["path"] for item in document["actions"]})
        assert next(item["layer"] for item in document["actions"] if item["path"] == "tools/orca_assisted_probe.py") == "parallel"
        assert next(item["layer"] for item in document["actions"] if item["path"] == "docs/guidelines/DX.md") == "core"
        text_result = invoke(target, "plan", "--layers", "parallel")
        assert text_result.returncode == 0
        assert "add      tools/orca_assisted_probe.py (parallel)" in text_result.stdout
        assert "add      docs/guidelines/DX.md (core)" in text_result.stdout
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_core_layer_installs_the_phase_skills() -> None:
    target = temporary_target()
    try:
        result = invoke(target, "plan", "--layers", "core", "--json")
        assert result.returncode == 0, result.stderr
        managed = {item["path"] for item in json.loads(result.stdout)["actions"]}
        for name in ("wspecify", "wdesign", "wtasks", "wimplement", "wverify", "wreview", "wqa"):
            assert f".agents/skills/{name}/SKILL.md" in managed, f"core plan omits .agents/skills/{name}"
            assert f".claude/skills/{name}" in managed, f"core plan omits .claude/skills/{name}"
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


def test_fresh_apply_is_valid_but_missing_manifest_status_is_invalid() -> None:
    target = temporary_target()
    try:
        plan = invoke(target, "plan", "--layers", "core", "--json")
        assert plan.returncode == 0
        status = invoke(target, "status", "--json")
        assert status.returncode == 2 and "manifest" in status.stderr
        applied = invoke(target, "apply", "--layers", "core", "--json")
        assert applied.returncode == 0
        assert (target / ".my-workflow/adoption.json").is_file()
    finally:
        shutil.rmtree(target)


def test_plan_does_not_sync_or_read_malformed_consumer_config() -> None:
    target = temporary_target()
    try:
        (target / ".my-workflow.toml").write_text("version = 1\n")
        before = snapshot(target)
        result = invoke(target, "plan", "--layers", "core", "--json")
        assert result.returncode == 0 and result.stderr == ""
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_core_apply_records_schema_and_status_detects_drift_without_writes() -> None:
    target = temporary_target()
    try:
        applied = invoke(target, "apply", "--layers", "core", "--json")
        assert applied.returncode == 0, applied.stderr
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text(encoding="utf-8"))
        assert manifest["schema"] == 1
        assert manifest["workflow_version"] == "0.8.0"
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


def test_no_newline_and_crlf_consumer_prose_remain_exact_prefixes() -> None:
    for content in (b"consumer prose", b"consumer\r\nprose\r\n"):
        target = temporary_target()
        try:
            agents = target / "AGENTS.md"
            agents.write_bytes(content)
            assert invoke(target, "apply", "--layers", "core").returncode == 0
            assert agents.read_bytes().startswith(content)
        finally:
            shutil.rmtree(target)


def test_nested_cross_layer_markers_abort_before_writes() -> None:
    target = temporary_target()
    try:
        (target / "AGENTS.md").write_text("<!-- my-workflow:core:start -->\n<!-- my-workflow:parallel:start -->\n<!-- my-workflow:core:end -->\n<!-- my-workflow:parallel:end -->\n")
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "parallel", "--json")
        assert result.returncode == 1 and "AGENTS.md:core" in json.loads(result.stdout)["conflicts"]
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_claude_receives_only_core_block_and_custom_skill_pointer_survives() -> None:
    target = temporary_target()
    try:
        (target / "AGENTS.md").write_text("consumer\n")
        (target / "CLAUDE.md").write_text("consumer claude\n")
        custom = target / ".agents/skills/custom"
        custom.mkdir(parents=True)
        pointer = target / ".claude/skills/custom"
        pointer.parent.mkdir(parents=True)
        pointer.write_text("consumer pointer\n")
        before = pointer.read_bytes()
        result = invoke(target, "apply", "--layers", "full", "--json")
        assert result.returncode == 0, result.stderr
        assert pointer.read_bytes() == before
        assert "parallel:start" not in (target / "CLAUDE.md").read_text()
    finally:
        shutil.rmtree(target)


def test_symlinked_local_config_is_rejected_before_read() -> None:
    target, outside = temporary_target(), temporary_target()
    try:
        (outside / "config").write_text("version = 1\n")
        (target / ".my-workflow.toml").symlink_to(outside / "config")
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "core")
        assert result.returncode == 2 and "symlink" in result.stderr
        assert snapshot(target) == before and (outside / "config").read_text() == "version = 1\n"
    finally:
        shutil.rmtree(target)
        shutil.rmtree(outside)


def test_status_rejects_symlinked_instruction_before_external_read() -> None:
    target, outside = temporary_target(), temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        external = outside / "AGENTS.md"
        external.write_bytes((target / "AGENTS.md").read_bytes())
        (target / "AGENTS.md").unlink()
        (target / "AGENTS.md").symlink_to(external)
        before = snapshot(outside)
        result = invoke(target, "status", "--json")
        assert result.returncode == 2 and "symlink" in result.stderr
        assert snapshot(outside) == before
    finally:
        shutil.rmtree(target)
        shutil.rmtree(outside)


def test_manifest_version_and_dependency_closed_layers_are_strict() -> None:
    target = temporary_target()
    try:
        manifest = target / ".my-workflow/adoption.json"
        manifest.parent.mkdir()
        for version, layers, expected in (("1.0", ["core"], 2), ("0.8.0", ["parallel"], 2), ("0.6.0", ["core"], 0)):
            payload = {"schema": 1, "workflow_version": version, "layers": layers, "files": {}, "blocks": {}}
            manifest.write_text(json.dumps(payload))
            result = invoke(target, "status", "--json")
            assert result.returncode == expected
        manifest.write_text(json.dumps({"schema": 1, "workflow_version": "1" * 5001 + ".0.0", "layers": ["core"], "files": {}, "blocks": {}}))
        result = invoke(target, "status", "--json")
        assert result.returncode == 2 and "Traceback" not in result.stderr and "too large" in result.stderr
    finally:
        shutil.rmtree(target)


def test_manifest_block_topology_is_installed_and_supported() -> None:
    target = temporary_target()
    try:
        manifest = target / ".my-workflow/adoption.json"
        manifest.parent.mkdir()
        record = '{"sha256":"' + "0" * 64 + '"}'
        for key in ("README.md:core", "AGENTS.md:parallel", "CLAUDE.md:parallel"):
            payload = {"schema": 1, "workflow_version": "0.7.0", "layers": ["core"], "files": {}, "blocks": {key: json.loads(record)}}
            manifest.write_text(json.dumps(payload))
            before = snapshot(target)
            for command in ("status", "apply"):
                result = invoke(target, command, *(('--layers', 'core') if command == 'apply' else ()))
                assert result.returncode == 2 and "block" in result.stderr
                assert snapshot(target) == before
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
        manifest_path = target / ".my-workflow/adoption.json"
        manifest_mtime = manifest_path.stat().st_mtime_ns
        assert invoke(target, "apply", "--layers", "quality").returncode == 0
        assert snapshot(target) == complete
        assert manifest_path.stat().st_mtime_ns == manifest_mtime
        assert first["tools/orca_assisted_probe.py"][1] == (ROOT / "tools/orca_assisted_probe.py").read_bytes()
    finally:
        shutil.rmtree(target)


def test_invalid_utf8_manifest_is_controlled_and_read_only() -> None:
    target = temporary_target()
    try:
        manifest = target / ".my-workflow/adoption.json"
        manifest.parent.mkdir()
        manifest.write_bytes(b"{\xff")
        before = snapshot(target)
        for command in ("status", "apply"):
            result = invoke(target, command, *(('--layers', 'core') if command == 'apply' else ()))
            assert result.returncode == 2 and "UnicodeDecodeError" not in result.stderr and "Traceback" not in result.stderr
            assert snapshot(target) == before
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


def test_non_directory_parent_is_rejected_before_writes() -> None:
    target = temporary_target()
    try:
        (target / "tools").write_bytes(b"consumer file\n")
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "parallel")
        assert result.returncode == 2 and "must be a directory" in result.stderr
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


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


def test_full_profile_matches_frozen_pre_feature_inventory() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "full").returncode == 0
        expected: set[str] = {"templates/adoption/agents/core.md", "templates/adoption/agents/parallel.md", "templates/adoption/agents/quality.md"}
        for relative in FROZEN_PRE_FEATURE_PATHS:
            source = ROOT / relative
            if source.is_file():
                expected.add(relative)
            else:
                expected.update(path.relative_to(ROOT).as_posix() for path in source.rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc")
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text())
        assert set(manifest["files"]) == expected
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


def test_deep_review_skill_adoption_and_artifact_hygiene() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "quality").returncode == 0
        for relative in (".agents/skills/deep-review/SKILL.md", ".agents/skills/deep-review/scripts/build_jobs.py"):
            assert (target / relative).is_file()
        assert (target / ".claude/skills/deep-review").is_symlink()
        assert not list((target / ".agents/skills/deep-review").rglob("*.pyc"))
    finally:
        shutil.rmtree(target)


def test_pack_guide_stays_source_only_and_tour_has_no_dead_link() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        assert not (target / "docs/workflow/pack.md").exists()
        assert "pack.md" not in (target / "docs/workflow/README.md").read_text()
    finally:
        shutil.rmtree(target)


def test_external_security_step_is_printed_without_installing_security_trees() -> None:
    target = temporary_target()
    try:
        result = invoke(target, "apply", "--layers", "core")
        assert result.returncode == 0
        assert "install_security_skills.py" in result.stdout
        for name in ("security-best-practices", "security-threat-model", "security-review"):
            assert not (target / ".agents/skills" / name).exists()
    finally:
        shutil.rmtree(target)


def test_global_tlc_paths_reject_without_mutation() -> None:
    target = temporary_target()
    try:
        (target / "Makefile").write_text("TLC := $(HOME)/.claude/skills/workflow-spec-driven/scripts/validate_tasks.py\n")
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "core")
        assert result.returncode == 2 and "machine-global" in result.stderr
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_project_local_tlc_path_is_accepted() -> None:
    target = temporary_target()
    try:
        (target / "Makefile").write_text("TLC := .agents/skills/workflow-spec-driven/scripts/validate_tasks.py\n")
        assert invoke(target, "apply", "--layers", "core").returncode == 0
    finally:
        shutil.rmtree(target)


def test_consumer_ad_index_is_preserved_on_readopt() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        path = target / "tools/ad-index.py"
        path.write_bytes(b"consumer-owned\n")
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        assert path.read_bytes() == b"consumer-owned\n"
    finally:
        shutil.rmtree(target)


def test_runtime_edits_are_overwritten_from_templates_on_readopt() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        runtime = target / ".cursor/agents/planner.md"
        runtime.write_text("stale runtime\n")
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        assert runtime.read_bytes() != b"stale runtime\n"
    finally:
        shutil.rmtree(target)


def test_adoption_installs_v3_config_and_syncs_fifteen_packets() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        assert (target / ".my-workflow.toml").is_file()
        packets = list((target / ".claude/agents").glob("*.md")) + list((target / ".codex/agents").glob("*.toml")) + list((target / ".cursor/agents").glob("*.md"))
        assert len(packets) == 15
    finally:
        shutil.rmtree(target)


def test_adoption_installs_hybrid_workflow_and_preserves_consumer_config() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "full").returncode == 0
        config = target / ".my-workflow.toml"
        config.write_bytes(config.read_bytes() + b"# consumer-owned\n")
        before = config.read_bytes()
        assert invoke(target, "apply", "--layers", "full").returncode == 0
        assert config.read_bytes() == before
        assert (target / "tools/qa_parallel_pilot.py").is_file()
        assert (target / "tools/orca_assisted_probe.py").is_file()
        assert (target / ".agents/skills/autonomous/remediation.py").is_file()
    finally:
        shutil.rmtree(target)


def test_parallel_adoption_installs_and_tracks_resource_lock() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core", "--skip-agents").returncode == 0
        core_manifest = json.loads((target / ".my-workflow/adoption.json").read_text(encoding="utf-8"))
        assert not (target / "tools/resource_lock.py").exists()
        assert "tools/resource_lock.py" not in core_manifest["files"]

        applied = invoke(target, "apply", "--layers", "parallel", "--skip-agents", "--json")
        assert applied.returncode == 0, applied.stderr
        installed = target / "tools/resource_lock.py"
        assert installed.read_bytes() == (ROOT / "tools/resource_lock.py").read_bytes()
        manifest_path = target / ".my-workflow/adoption.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        record = manifest["files"]["tools/resource_lock.py"]
        assert record["layer"] == "parallel" and record["ownership"] == "managed"

        before = installed.read_bytes(), manifest_path.read_bytes()
        assert invoke(target, "apply", "--layers", "parallel", "--skip-agents").returncode == 0
        assert (installed.read_bytes(), manifest_path.read_bytes()) == before

        installed.write_bytes(installed.read_bytes() + b"\nconsumer change\n")
        conflict = invoke(target, "apply", "--layers", "parallel", "--skip-agents", "--json")
        assert conflict.returncode == 1
        assert "tools/resource_lock.py" in json.loads(conflict.stdout)["conflicts"]
        assert installed.read_bytes().endswith(b"consumer change\n")
    finally:
        shutil.rmtree(target)


def test_adoption_installs_only_new_authority_byte_identically() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "full").returncode == 0
        for relative in ("tools/qa_parallel_pilot.py", "tools/orca_assisted_probe.py", ".my-workflow.toml.example"):
            assert (target / relative).read_bytes() == (ROOT / relative).read_bytes()
    finally:
        shutil.rmtree(target)


def test_legacy_cleanup_uses_production_paths_and_hashes() -> None:
    assert tuple(LEGACY_MANAGED_TEST_FILES) == (
        "tools/knowledge/tests/check.test.ts", "tools/knowledge/tests/cli.test.ts",
        "tools/shared/tests/autonomous-parallelization.test.ts",
        "tools/shared/tests/deep-review-installation.test.ts", "tools/shared/tests/frontmatter.test.ts",
        "tools/shared/tests/qa-skills.test.ts", "tools/shared/tests/security-skills-installation.test.ts",
        "tools/shared/tests/workflow-config.test.ts",
    )
    assert LEGACY_MANAGED_TEST_DIRECTORIES == ("tools/knowledge/tests", "tools/shared/tests")
    assert all(len(value) == 64 for value in LEGACY_MANAGED_TEST_FILES.values())


def test_legacy_cleanup_removes_owned_tests_and_preserves_consumer_files() -> None:
    target = temporary_target()
    try:
        managed = b"legacy suite\n"
        files = {"tools/knowledge/tests/check.test.ts": hashlib.sha256(managed).hexdigest(), "tools/shared/tests/frontmatter.test.ts": hashlib.sha256(managed).hexdigest()}
        for relative in files:
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(managed)
        (target / "tools/shared/tests/consumer.test.ts").write_bytes(b"consumer\n")
        remove_legacy_managed_tests(target, files)
        assert not (target / "tools/knowledge/tests/check.test.ts").exists()
        assert (target / "tools/shared/tests/consumer.test.ts").exists()
    finally:
        shutil.rmtree(target)


def test_legacy_cleanup_preserves_external_symlinked_test_directories() -> None:
    target, outside = temporary_target(), temporary_target()
    try:
        (target / "tools/knowledge").mkdir(parents=True)
        (target / "tools/knowledge/tests").symlink_to(outside, target_is_directory=True)
        (outside / "check.test.ts").write_text("external\n")
        remove_legacy_managed_tests(target)
        assert (target / "tools/knowledge/tests").is_symlink()
        assert (outside / "check.test.ts").exists()
    finally:
        shutil.rmtree(target)
        shutil.rmtree(outside)


def test_adoption_rejects_unsafe_generated_destinations_without_mutation() -> None:
    target, outside = temporary_target(), temporary_target()
    try:
        sentinel = outside / "sentinel"
        sentinel.write_text("outside\n")
        (target / ".gitignore").symlink_to(sentinel)
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "core")
        assert result.returncode == 2
        assert snapshot(target) == before and sentinel.read_text() == "outside\n"
    finally:
        shutil.rmtree(target)
        shutil.rmtree(outside)


def test_adoption_rejects_invalid_template_before_runtime_writes() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        template = target / "templates/agents/cursor/verifier.md"
        template.write_text(template.read_text().replace("model:", "model-old:"))
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "core")
        assert result.returncode == 2 and "workflow-config" in result.stderr
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_adoption_rejects_malformed_local_config_without_partial_writes() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        (target / ".my-workflow.toml").write_text("version = 1\n")
        before = snapshot(target)
        result = invoke(target, "apply", "--layers", "core")
        assert result.returncode == 2 and "version must be integer 3" in result.stderr
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_gitignore_rules_merge_without_overwrite() -> None:
    target = temporary_target()
    try:
        (target / ".gitignore").write_text("consumer-cache/\n")
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        text = (target / ".gitignore").read_text()
        assert "consumer-cache/" in text and text.splitlines().count("graft/") == 1
    finally:
        shutil.rmtree(target)


def test_deep_review_learnings_survive_consumer_parent_ignore() -> None:
    target = temporary_target()
    try:
        (target / ".gitignore").write_text(".deep-review/\n")
        assert invoke(target, "apply", "--layers", "quality").returncode == 0
        text = (target / ".gitignore").read_text()
        assert text.splitlines().count("!.deep-review/learnings.md") == 1
    finally:
        shutil.rmtree(target)


def test_feature_specs_are_versioned_and_legacy_ignore_is_removed() -> None:
    target = temporary_target()
    try:
        (target / ".gitignore").write_text("consumer\n.specs/features/\n.specs/features/\n")
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        assert ".specs/features/" not in (target / ".gitignore").read_text().splitlines()
    finally:
        shutil.rmtree(target)


def test_graft_ignore_contract_and_search_visibility() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        assert "graft/" in (target / ".gitignore").read_text()
        assert "graft/.cache/" in (target / ".ignore").read_text()
    finally:
        shutil.rmtree(target)


def test_qa_registry_keeps_fake_proof_current_and_live_orca_blocked() -> None:
    scenario = (ROOT / "docs/qa/scenarios/QAS-run-resource-free-parallel-orca-slices.md").read_text()
    assert "blocked-verify" in scenario and "fake" in scenario.lower()


def test_dependency_selection_installs_core_transitively() -> None:
    target = temporary_target()
    try:
        result = invoke(target, "apply", "--layers", "parallel", "--json")
        assert result.returncode == 0
        document = json.loads(result.stdout)
        assert document["resolved_layers"] == ["core", "parallel"]
        assert (target / "docs/guidelines/GATES.md").is_file()
    finally:
        shutil.rmtree(target)


def test_target_root_symlink_is_rejected_before_referent_mutation() -> None:
    parent = temporary_target()
    referent = temporary_target()
    alias = parent / "alias"
    try:
        (referent / "sentinel").write_text("external\n")
        alias.symlink_to(referent, target_is_directory=True)
        before = snapshot(referent)
        for command in ("plan", "apply", "status"):
            args = ("--layers", "core") if command != "status" else ()
            result = invoke(alias, command, *args)
            assert result.returncode == 2
            assert snapshot(referent) == before
    finally:
        shutil.rmtree(parent)
        shutil.rmtree(referent)


def test_duplicate_manifest_keys_are_rejected_for_status_and_apply() -> None:
    target = temporary_target()
    try:
        manifest = target / ".my-workflow/adoption.json"
        manifest.parent.mkdir()
        duplicate = '{"schema":1,"workflow_version":"0.7.0","layers":["core"],"files":{"a":{"layer":"core","ownership":"managed","source_sha256":"' + "0" * 64 + '","installed_sha256":"' + "0" * 64 + '"},"a":{"layer":"core","ownership":"managed","source_sha256":"' + "0" * 64 + '","installed_sha256":"' + "0" * 64 + '"}},"blocks":{}}'
        manifest.write_text(duplicate)
        before = snapshot(target)
        for command in ("status", "apply"):
            result = invoke(target, command, *(('--layers', 'core') if command == 'apply' else ()))
            assert result.returncode == 2 and "duplicate" in result.stderr
            assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_status_uses_only_public_state_vocabulary() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        clean = json.loads(invoke(target, "status", "--json").stdout)
        assert {entry["action"] for entry in clean["actions"]} <= {"clean", "missing", "modified", "retained"}
        managed = target / "tools/knowledge/src/cli.ts"
        managed.unlink()
        before = snapshot(target)
        missing_result = invoke(target, "status", "--json")
        missing = json.loads(missing_result.stdout)
        assert missing_result.returncode == 1 and snapshot(target) == before and missing_result.stderr == ""
        assert any(entry["action"] == "missing" for entry in missing["actions"])
        managed.write_text("modified\n")
        modified = json.loads(invoke(target, "status", "--json").stdout)
        assert any(entry["action"] == "modified" for entry in modified["actions"])
        consumer = target / "tools/ad-index.py"
        consumer.write_text("consumer\n")
        retained = json.loads(invoke(target, "status", "--json").stdout)
        assert any(entry["action"] == "retained" for entry in retained["actions"])
    finally:
        shutil.rmtree(target)


def test_clean_managed_files_update_when_source_bytes_change() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        source = ROOT / "tools/shared/src/frontmatter.ts"
        original = source.read_bytes()
        try:
            source.write_bytes(original + b"\n// source update\n")
            result = invoke(target, "apply", "--layers", "core", "--json")
            assert result.returncode == 0
            assert json.loads(result.stdout)["status"] == "ready"
            assert (target / "tools/shared/src/frontmatter.ts").read_bytes() == source.read_bytes()
        finally:
            source.write_bytes(original)
    finally:
        shutil.rmtree(target)


def test_missing_only_consumer_ownership_is_recorded_without_hashing_content() -> None:
    target = temporary_target()
    try:
        profile = target / "docs/qa/README.md"
        profile.parent.mkdir(parents=True)
        profile.write_text("consumer QA profile\n")
        assert invoke(target, "apply", "--layers", "quality").returncode == 0
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text())
        record = manifest["files"]["docs/qa/README.md"]
        assert record["ownership"] == "consumer" and record["installed_sha256"] is None
        assert profile.read_text() == "consumer QA profile\n"
    finally:
        shutil.rmtree(target)


def test_invalid_fixed_dependency_graph_is_a_controlled_error_before_target_access() -> None:
    target = temporary_target()
    original = adopt.DEPENDENCIES["parallel"]
    try:
        adopt.DEPENDENCIES["parallel"] = ("ghost",)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            try:
                adopt.main(["adopt.py", "plan", str(target), "--layers", "parallel", "--json"])
            except SystemExit as exc:
                assert exc.code == 2
            else:
                raise AssertionError("invalid dependency graph must fail")
        assert "invalid dependency graph" in stderr.getvalue()
        assert snapshot(target) == {}
    finally:
        adopt.DEPENDENCIES["parallel"] = original
        shutil.rmtree(target)


def test_public_publication_publishes_packets_before_manifest_last() -> None:
    target = temporary_target()
    published: list[str] = []
    try:
        def record_write(path: Path, content: bytes) -> None:
            published.append(f"write:{path.relative_to(target).as_posix()}")

        def record_legacy(root: Path) -> None:
            published.append("cleanup:legacy")

        def record_links(root: Path, managed_skills: set[str]) -> None:
            published.append("links:claude")

        with patch.object(adopt, "_atomic_write", side_effect=record_write), patch.object(adopt, "remove_legacy_managed_tests", side_effect=record_legacy), patch.object(adopt, "_link_claude_skills", side_effect=record_links):
            assert adopt.main(["adopt.py", "apply", str(target), "--layers", "core", "--skip-agents"]) == 0
        assert published[-1] == "write:.my-workflow/adoption.json"
        runtime = [index for index, event in enumerate(published) if any(event.startswith(f"write:{prefix}") for prefix in (".claude/agents/", ".codex/agents/", ".cursor/agents/"))]
        assert runtime and max(runtime) < len(published) - 1
        assert all(index < len(published) - 1 for index in range(len(published) - 1))
    finally:
        shutil.rmtree(target)


def test_resolve_publication_writes_adoption_manifest_after_other_entries() -> None:
    target = legacy_target()
    published: list[str] = []
    try:
        def record_write(path: Path, content: bytes) -> None:
            published.append(f"write:{path.relative_to(target).as_posix()}")

        with patch.object(adopt, "_atomic_write", side_effect=record_write), patch.object(adopt, "remove_legacy_managed_tests"), patch.object(adopt, "_link_claude_skills"):
            assert adopt.main(["adopt.py", "resolve", str(target), "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents"]) == 0
        manifest_index = published.index("write:.my-workflow/adoption.json")
        assert "write:tools/resource_lock.py" in published[:manifest_index]
        assert manifest_index == len(published) - 1
    finally:
        shutil.rmtree(target)


def test_cleanup_or_link_failure_rolls_back_live_target_and_manifest() -> None:
    for helper in ("remove_legacy_managed_tests", "_link_claude_skills"):
        target = temporary_target()
        try:
            assert invoke(target, "apply", "--layers", "core").returncode == 0
            before = snapshot(target)
            stderr = io.StringIO()
            with patch.object(adopt, helper, side_effect=RuntimeError("injected publication failure")), contextlib.redirect_stderr(stderr):
                try:
                    adopt.main(["adopt.py", "apply", str(target), "--layers", "core"])
                except SystemExit as exc:
                    assert exc.code == 2
                else:
                    raise AssertionError("injected publication failure must halt")
            assert snapshot(target) == before
            assert "publication failed" in stderr.getvalue()
        finally:
            shutil.rmtree(target)


def test_non_normalized_manifest_paths_are_rejected_independently() -> None:
    target = temporary_target()
    try:
        manifest = target / ".my-workflow/adoption.json"
        manifest.parent.mkdir()
        record = '{"layer":"core","ownership":"managed","source_sha256":"' + "0" * 64 + '","installed_sha256":"' + "0" * 64 + '"}'
        manifest.write_text('{"schema":1,"workflow_version":"0.7.0","layers":["core"],"files":{"a//b":' + record + '},"blocks":{}}')
        before = snapshot(target)
        for command in ("status", "apply"):
            result = invoke(target, command, *(('--layers', 'core') if command == 'apply' else ()))
            assert result.returncode == 2 and "normalized" in result.stderr
            assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_exact_duplicate_manifest_keys_are_rejected_during_parsing() -> None:
    target = temporary_target()
    try:
        manifest = target / ".my-workflow/adoption.json"
        manifest.parent.mkdir()
        record = '{"layer":"core","ownership":"managed","source_sha256":"' + "0" * 64 + '","installed_sha256":"' + "0" * 64 + '"}'
        manifest.write_text('{"schema":1,"workflow_version":"0.7.0","layers":["core"],"files":{"a/b":' + record + ',"a/b":' + record + '},"blocks":{}}')
        before = snapshot(target)
        for command in ("status", "apply"):
            result = invoke(target, command, *(('--layers', 'core') if command == 'apply' else ()))
            assert result.returncode == 2 and "duplicate key" in result.stderr
            assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_fresh_and_refuse() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "full").returncode == 0
        assert (target / "tools/knowledge/src/cli.ts").is_file()
        assert not list((target / "tools").rglob("*.test.ts"))
        agents = target / "AGENTS.md"
        agents.write_text("# Product instructions\n\nA product.\n")
        before = snapshot(target)
        # Product prose remains owned by the target; only managed blocks are changed by adoption.
        result = invoke(target, "apply", "--layers", "core")
        assert result.returncode == 0
        assert (target / "AGENTS.md").read_text().startswith("# Product instructions")
        assert before[".my-workflow/adoption.json"][1] == (target / ".my-workflow/adoption.json").read_bytes()
    finally:
        shutil.rmtree(target)


def test_skip_agents_preserves_product_files_and_adopts_rest() -> None:
    target = temporary_target()
    try:
        (target / "AGENTS.md").write_text("product\n")
        (target / "CLAUDE.md").write_text("claude\n")
        before = {(target / name).read_bytes() for name in ("AGENTS.md", "CLAUDE.md")}
        assert invoke(target, "apply", "--layers", "full", "--skip-agents").returncode == 0
        assert {(target / name).read_bytes() for name in ("AGENTS.md", "CLAUDE.md")} == before
        assert (target / ".agents/skills/deep-review/SKILL.md").is_file()
    finally:
        shutil.rmtree(target)


def test_skip_agents_preserves_absent_claude_file() -> None:
    target = temporary_target()
    try:
        (target / "AGENTS.md").write_text("product\n")
        assert invoke(target, "apply", "--layers", "core", "--skip-agents").returncode == 0
        assert not (target / "CLAUDE.md").exists()
    finally:
        shutil.rmtree(target)


def test_adoption_imports_probe_without_orca_effect() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "parallel", "--skip-agents").returncode == 0
        calls = target / "orca.calls"
        fake = target / "orca"
        fake.write_text(f"#!/bin/sh\nprintf called >> {calls}\n")
        fake.chmod(0o755)
        result = subprocess.run([sys.executable, "-c", "import tools.orca_assisted_probe"], cwd=target, env={**os.environ, "PATH": f"{target}:{os.environ.get('PATH', '')}"}, text=True, capture_output=True, check=False)
        assert result.returncode == 0 and not calls.exists()
    finally:
        shutil.rmtree(target)


def test_adoption_rejects_symlinked_managed_destination_without_mutation() -> None:
    target, outside = temporary_target(), temporary_target()
    try:
        (target / "tools").mkdir()
        destination = target / "tools/orca_assisted_probe.py"
        destination.symlink_to(outside / "probe.py")
        before = snapshot(target)
        assert invoke(target, "apply", "--layers", "parallel").returncode == 2
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)
        shutil.rmtree(outside)


def test_existing_config_drives_all_native_values_and_preserves_non_model_bytes() -> None:
    target = temporary_target()
    try:
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        config = target / ".my-workflow.toml"
        template = target / "templates/agents/claude/planner.md"
        config_before = config.read_bytes() + b"# consumer setting\n"
        template_before = template.read_bytes() + b"\n# consumer instruction\n"
        config.write_bytes(config_before)
        template.write_bytes(template_before)
        assert invoke(target, "apply", "--layers", "core").returncode == 0
        assert config.read_bytes() == config_before
        assert template.read_bytes() == template_before
        assert b"consumer instruction" in (target / ".claude/agents/planner.md").read_bytes()
    finally:
        shutil.rmtree(target)


def test_resolve_exact_conflicts_publishes_manifest_and_normal_apply_is_idempotent() -> None:
    target = legacy_target(("tools/resource_lock.py", "tools/qa_parallel_pilot.py"))
    try:
        (target / "AGENTS.md").write_bytes(b"project agents\r\n")
        (target / "CLAUDE.md").write_bytes(b"project claude\r\n")
        subprocess.run(["git", "add", "AGENTS.md", "CLAUDE.md"], cwd=target, check=True)
        subprocess.run(["git", "commit", "-qm", "instructions"], cwd=target, check=True)
        instructions_before = (target / "AGENTS.md").read_bytes(), (target / "CLAUDE.md").read_bytes()
        plan = invoke(target, "plan", "--layers", "parallel", "--skip-agents", "--json")
        assert plan.returncode == 1
        assert json.loads(plan.stdout)["conflicts"] == ["tools/qa_parallel_pilot.py", "tools/resource_lock.py"]
        result = invoke(
            target, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py",
            "--replace", "tools/qa_parallel_pilot.py", "--skip-agents", "--json",
        )
        assert result.returncode == 0, result.stderr
        document = json.loads(result.stdout)
        assert document["command"] == "resolve"
        assert document["status"] == "ready" and document["conflicts"] == []
        assert document["replacements"] == ["tools/qa_parallel_pilot.py", "tools/resource_lock.py"]
        assert {item["path"] for item in document["actions"] if item["action"] == "replace"} == set(document["replacements"])
        assert ((target / "AGENTS.md").read_bytes(), (target / "CLAUDE.md").read_bytes()) == instructions_before
        manifest = json.loads((target / ".my-workflow/adoption.json").read_text(encoding="utf-8"))
        assert manifest["schema"] == 1 and manifest["layers"] == ["core", "parallel"]
        assert json.loads(invoke(target, "status", "--json").stdout)["status"] == "clean"
        before_apply = snapshot(target)
        assert invoke(target, "apply", "--layers", "parallel", "--skip-agents").returncode == 0
        assert snapshot(target) == before_apply
    finally:
        shutil.rmtree(target)


def test_resolve_incomplete_authorization_reports_all_unresolved_without_writes() -> None:
    target = legacy_target(("tools/resource_lock.py", "tools/qa_parallel_pilot.py"))
    try:
        before = snapshot(target)
        result = invoke(target, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents", "--json")
        assert result.returncode == 1
        document = json.loads(result.stdout)
        assert "tools/qa_parallel_pilot.py" in document["conflicts"]
        assert snapshot(target) == before
        assert not (target / ".my-workflow/adoption.json").exists()
    finally:
        shutil.rmtree(target)


def test_resolve_allows_ignored_files_but_rejects_untracked_files() -> None:
    target = legacy_target()
    try:
        (target / ".gitignore").write_text("cache/\n", encoding="utf-8")
        subprocess.run(["git", "add", ".gitignore"], cwd=target, check=True)
        subprocess.run(["git", "commit", "-qm", "ignore cache"], cwd=target, check=True)
        (target / "cache/dependency.bin").parent.mkdir()
        (target / "cache/dependency.bin").write_bytes(b"ignored\n")
        result = invoke(target, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents")
        assert result.returncode == 0, result.stderr
        assert json.loads(invoke(target, "status", "--json").stdout)["status"] == "clean"

        dirty = legacy_target()
        try:
            (dirty / "untracked.txt").write_text("blocks resolve\n", encoding="utf-8")
            before = snapshot(dirty)
            blocked = invoke(dirty, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents")
            assert blocked.returncode == 2
            assert snapshot(dirty) == before
        finally:
            shutil.rmtree(dirty)
    finally:
        shutil.rmtree(target)


def test_resolve_rejects_non_conflict_extra_and_duplicate_authorizations_without_writes() -> None:
    cases = (
        ("tools/resource_lock.py", "tools/qa_parallel_pilot.py"),
        ("tools/resource_lock.py", "tools/resource_lock.py"),
        ("tools/resource_lock.py", "README.md"),
    )
    for replacements in cases:
        target = legacy_target()
        try:
            before = snapshot(target)
            result = invoke(target, "resolve", "--layers", "parallel", *sum((["--replace", path] for path in replacements), []), "--skip-agents", "--json")
            assert result.returncode == 2
            assert snapshot(target) == before
            assert not (target / ".my-workflow/adoption.json").exists()
        finally:
            shutil.rmtree(target)


def test_resolve_rejects_unsafe_and_managed_block_paths_without_writes() -> None:
    for replacement in ("../x", "/tmp/x", "tools//resource_lock.py", "./tools/resource_lock.py", "AGENTS.md:core"):
        target = legacy_target()
        try:
            before = snapshot(target)
            result = invoke(target, "resolve", "--layers", "parallel", "--replace", replacement, "--skip-agents", "--json")
            assert result.returncode == 2
            assert snapshot(target) == before
        finally:
            shutil.rmtree(target)


def test_resolve_helpers_validate_replacements_and_git_boundary() -> None:
    assert adopt._relative_path("tools/resource_lock.py") == "tools/resource_lock.py"
    for value in ("../x", "/tmp/x", "tools//resource_lock.py", "./tools/resource_lock.py"):
        expect_adoption_error(lambda value=value: adopt._relative_path(value))

    conflicts = ["tools/resource_lock.py", "tools/qa_parallel_pilot.py"]
    catalog = {path: "parallel" for path in conflicts}
    exact, complete = adopt._resolve_replacement_set(conflicts, conflicts, catalog)
    assert exact == set(conflicts) and complete is True
    missing, complete = adopt._resolve_replacement_set(conflicts[:1], conflicts, catalog)
    assert missing == {conflicts[0]} and complete is False
    expect_adoption_error(lambda: adopt._resolve_replacement_set([*conflicts, "README.md"], conflicts, catalog))
    expect_adoption_error(lambda: adopt._resolve_replacement_set([conflicts[0], conflicts[0]], conflicts, catalog))
    expect_adoption_error(lambda: adopt._resolve_replacement_set([conflicts[0], "AGENTS.md:core"], [*conflicts, "AGENTS.md:core"], catalog))


def test_resolve_legacy_target_helper_validates_full_git_boundary() -> None:
    clean = legacy_target()
    dirty = legacy_target()
    no_git = temporary_target()
    missing_head = temporary_target()
    manifest = legacy_target()
    try:
        assert adopt._legacy_target_eligible(clean) is None
        (dirty / "untracked.txt").write_text("dirty\n", encoding="utf-8")
        expect_adoption_error(lambda: adopt._legacy_target_eligible(dirty))
        expect_adoption_error(lambda: adopt._legacy_target_eligible(no_git))
        subprocess.run(["git", "init", "-q"], cwd=missing_head, check=True, capture_output=True, text=True)
        expect_adoption_error(lambda: adopt._legacy_target_eligible(missing_head))
        manifest_path = manifest / ".my-workflow/adoption.json"
        manifest_path.parent.mkdir()
        manifest_path.write_text("{}\n", encoding="utf-8")
        subprocess.run(["git", "add", str(manifest_path.relative_to(manifest))], cwd=manifest, check=True)
        subprocess.run(["git", "commit", "-qm", "manifest baseline"], cwd=manifest, check=True)
        expect_adoption_error(lambda: adopt._legacy_target_eligible(manifest))
    finally:
        for target in (clean, dirty, no_git, missing_head, manifest):
            shutil.rmtree(target)


def test_resolve_rejects_replaceable_leaf_and_parent_symlinks_without_writes() -> None:
    for parent_symlink in (False, True):
        target, outside = legacy_target(), temporary_target()
        try:
            if parent_symlink:
                shutil.rmtree(target / "tools")
                (outside / "tools").mkdir()
                (outside / "tools/resource_lock.py").write_bytes(b"outside\n")
                (target / "tools").symlink_to(outside / "tools", target_is_directory=True)
            else:
                referent = outside / "resource_lock.py"
                referent.write_bytes(b"outside\n")
                (target / "tools/resource_lock.py").unlink()
                (target / "tools/resource_lock.py").symlink_to(referent)
            subprocess.run(["git", "add", "-A"], cwd=target, check=True)
            subprocess.run(["git", "commit", "-qm", "symlink baseline"], cwd=target, check=True)
            before = snapshot(target)
            outside_before = snapshot(outside)
            result = invoke(target, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents")
            assert result.returncode == 2 and "symlink" in result.stderr
            assert snapshot(target) == before
            assert snapshot(outside) == outside_before
        finally:
            shutil.rmtree(target)
            shutil.rmtree(outside)


def test_resolve_uses_trusted_workflow_config_without_importing_target_shadow() -> None:
    target = legacy_target()
    sentinel = target.parent / "target-workflow-config-imported"
    try:
        shadow = target / ".agents/skills/workflow-config/scripts/workflow_config"
        shadow.mkdir(parents=True)
        trusted = ROOT / ".agents/skills/workflow-config/scripts/workflow_config.py"
        shadow.joinpath("__init__.py").write_text(
            f"from pathlib import Path as _SentinelPath\n_SentinelPath({str(sentinel)!r}).write_text('executed')\n"
            "import runpy as _runpy\n"
            f"_trusted = _runpy.run_path({str(trusted)!r})\n"
            "sync_agents = _trusted['sync_agents']\n"
            "PROVIDERS = _trusted['PROVIDERS']\n"
            "ROLES = _trusted['ROLES']\n"
            "_runtime_relative = _trusted['_runtime_relative']\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", str(shadow.relative_to(target))], cwd=target, check=True)
        subprocess.run(["git", "commit", "-qm", "target resolver shadow"], cwd=target, check=True)

        result = invoke(
            target,
            "resolve",
            "--layers",
            "parallel",
            "--replace",
            "tools/resource_lock.py",
            "--skip-agents",
        )
        assert result.returncode == 0, result.stderr
        assert not sentinel.exists()
        assert (target / ".codex/agents/planner.toml").is_file()
        assert json.loads(invoke(target, "status", "--json").stdout)["status"] == "clean"
    finally:
        shutil.rmtree(target)
        if sentinel.exists():
            sentinel.unlink()


def test_resolve_rejects_symlinked_claude_parent_without_external_mutation() -> None:
    target = legacy_target()
    outside = temporary_target()
    try:
        (outside / "sentinel").write_bytes(b"outside\n")
        (target / ".claude").symlink_to(outside, target_is_directory=True)
        subprocess.run(["git", "add", ".claude"], cwd=target, check=True)
        subprocess.run(["git", "commit", "-qm", "claude parent symlink"], cwd=target, check=True)
        before = snapshot(target)
        outside_before = snapshot(outside)
        result = invoke(
            target,
            "resolve",
            "--layers",
            "parallel",
            "--replace",
            "tools/resource_lock.py",
            "--skip-agents",
        )
        assert result.returncode == 2
        assert snapshot(target) == before
        assert snapshot(outside) == outside_before
    finally:
        shutil.rmtree(target)
        shutil.rmtree(outside)


def test_resolve_rejects_dirty_non_git_missing_head_and_manifest_targets_without_writes() -> None:
    dirty = legacy_target()
    no_git = temporary_target()
    missing_head = temporary_target()
    manifest_target = temporary_target()
    try:
        (dirty / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
        dirty_before = snapshot(dirty)
        assert invoke(dirty, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents").returncode == 2
        assert snapshot(dirty) == dirty_before
        no_git_before = snapshot(no_git)
        assert invoke(no_git, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents").returncode == 2
        assert snapshot(no_git) == no_git_before
        subprocess.run(["git", "init", "-q"], cwd=missing_head, check=True, capture_output=True, text=True)
        missing_head_before = snapshot(missing_head)
        assert invoke(missing_head, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents").returncode == 2
        assert snapshot(missing_head) == missing_head_before
        (manifest_target / "baseline.txt").write_text("baseline\n", encoding="utf-8")
        commit_target(manifest_target)
        assert invoke(manifest_target, "apply", "--layers", "core", "--skip-agents").returncode == 0
        subprocess.run(["git", "add", "-A"], cwd=manifest_target, check=True)
        subprocess.run(["git", "commit", "-qm", "adopted baseline"], cwd=manifest_target, check=True)
        before = snapshot(manifest_target)
        result = invoke(manifest_target, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents")
        assert result.returncode == 2 and snapshot(manifest_target) == before
    finally:
        for target in (dirty, no_git, missing_head, manifest_target):
            shutil.rmtree(target)


def test_resolve_skip_agents_preserves_instruction_files() -> None:
    target = legacy_target()
    try:
        agents = target / "AGENTS.md"
        claude = target / "CLAUDE.md"
        agents.write_bytes(b"product instructions\r\n")
        claude.write_bytes(b"product claude\r\n")
        subprocess.run(["git", "add", "AGENTS.md", "CLAUDE.md"], cwd=target, check=True)
        subprocess.run(["git", "commit", "-qm", "instructions"], cwd=target, check=True)
        before = agents.read_bytes(), claude.read_bytes()
        result = invoke(target, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents")
        assert result.returncode == 0, result.stderr
        assert (agents.read_bytes(), claude.read_bytes()) == before
    finally:
        shutil.rmtree(target)


def test_resolve_keeps_altered_instruction_blocks_manual() -> None:
    target = legacy_target()
    try:
        (target / "AGENTS.md").write_text("product\n<!-- my-workflow:core:start -->\nold block\n", encoding="utf-8")
        subprocess.run(["git", "add", "AGENTS.md"], cwd=target, check=True)
        subprocess.run(["git", "commit", "-qm", "instructions"], cwd=target, check=True)
        before = snapshot(target)
        result = invoke(target, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--json")
        assert result.returncode == 1
        assert "AGENTS.md:core" in json.loads(result.stdout)["conflicts"]
        assert snapshot(target) == before
    finally:
        shutil.rmtree(target)


def test_resolve_publication_failure_rolls_back_and_keeps_manifest_absent() -> None:
    target = legacy_target()
    try:
        executable = target / "consumer.sh"
        executable.write_bytes(b"#!/bin/sh\necho consumer\n")
        executable.chmod(0o755)
        subprocess.run(["git", "add", "consumer.sh"], cwd=target, check=True)
        subprocess.run(["git", "commit", "-qm", "executable consumer file"], cwd=target, check=True)
        before = snapshot(target)
        stderr = io.StringIO()
        with patch.object(adopt, "_link_claude_skills", side_effect=RuntimeError("injected publication failure")), contextlib.redirect_stderr(stderr):
            try:
                adopt.main(["adopt.py", "resolve", str(target), "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents"])
            except SystemExit as exc:
                assert exc.code == 2
            else:
                raise AssertionError("injected publication failure must halt")
        assert snapshot(target) == before
        assert executable.stat().st_mode & 0o7777 == 0o755
        assert not (target / ".my-workflow/adoption.json").exists()
        assert "publication failed" in stderr.getvalue()
    finally:
        shutil.rmtree(target)


def test_resolve_rejects_target_dirty_before_publication() -> None:
    target = legacy_target()
    try:
        original_snapshot = adopt._tree_snapshot
        dirtied = False
        dirty_baseline: dict[str, bytes | str] = {}

        def dirty_after_snapshot(root: Path) -> dict[str, tuple[str, bytes | str | None, int | None]]:
            nonlocal dirtied, dirty_baseline
            snapshot_result = original_snapshot(root)
            if not dirtied:
                (root / "dirty.txt").write_text("changed before publication\n", encoding="utf-8")
                dirtied = True
                dirty_baseline = snapshot(root)
            return snapshot_result

        stderr = io.StringIO()
        with patch.object(adopt, "_tree_snapshot", side_effect=dirty_after_snapshot), contextlib.redirect_stderr(stderr):
            try:
                adopt.main(["adopt.py", "resolve", str(target), "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents"])
            except SystemExit as exc:
                assert exc.code == 2
            else:
                raise AssertionError("dirty target must halt before publication")
        assert snapshot(target) == dirty_baseline
        assert not (target / ".my-workflow/adoption.json").exists()
        assert (target / "dirty.txt").read_text(encoding="utf-8") == "changed before publication\n"
        assert "clean Git target" in stderr.getvalue()
    finally:
        shutil.rmtree(target)


def test_resolve_treats_shell_metacharacters_as_literal_argv() -> None:
    target = legacy_target()
    renamed = target.with_name("my-workflow-adopt-shell;touch shell-effect")
    sentinel = target.parent / "shell-effect"
    target.rename(renamed)
    try:
        result = invoke(renamed, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py", "--skip-agents")
        assert result.returncode == 0, result.stderr
        assert not sentinel.exists()
    finally:
        shutil.rmtree(renamed)
        if sentinel.exists():
            sentinel.unlink()


def test_resolve_rejects_shell_metacharacters_in_replacement_as_literal() -> None:
    target = legacy_target()
    sentinel = target.parent / "replacement-shell-effect"
    try:
        result = invoke(target, "resolve", "--layers", "parallel", "--replace", "tools/resource_lock.py;touch replacement-shell-effect", "--skip-agents")
        assert result.returncode == 2
        assert not sentinel.exists()
        assert snapshot(target)["tools/resource_lock.py"][1] == (ROOT / "tools/resource_lock.py").read_bytes() + b"\nlegacy project change\n"
    finally:
        shutil.rmtree(target)
        if sentinel.exists():
            sentinel.unlink()


TESTS = (
    test_resolves_fixed_layers_and_plan_is_read_only,
    test_core_layer_installs_the_phase_skills,
    test_full_profile_is_exactly_four_layers_and_legacy_cli_is_rejected,
    test_unknown_layer_and_invalid_manifest_fail_before_target_mutation,
    test_fresh_apply_is_valid_but_missing_manifest_status_is_invalid,
    test_plan_does_not_sync_or_read_malformed_consumer_config,
    test_core_apply_records_schema_and_status_detects_drift_without_writes,
    test_manifest_hashes_are_lowercase_sha256,
    test_apply_preserves_consumer_prose_and_writes_managed_blocks,
    test_no_newline_and_crlf_consumer_prose_remain_exact_prefixes,
    test_nested_cross_layer_markers_abort_before_writes,
    test_claude_receives_only_core_block_and_custom_skill_pointer_survives,
    test_symlinked_local_config_is_rejected_before_read,
    test_status_rejects_symlinked_instruction_before_external_read,
    test_manifest_version_and_dependency_closed_layers_are_strict,
    test_manifest_block_topology_is_installed_and_supported,
    test_apply_is_cumulative_and_idempotent,
    test_conflicts_abort_every_write_and_report_all_paths,
    test_skip_agents_leaves_both_instruction_files_byte_identical,
    test_edited_managed_block_is_a_conflict,
    test_symlinked_destination_is_rejected_before_external_write,
    test_non_directory_parent_is_rejected_before_writes,
    test_full_profile_preserves_complete_capability_inventory_and_links_skills,
    test_full_profile_matches_frozen_pre_feature_inventory,
    test_bun_consumer_boundary_and_probe_import_are_preserved,
    test_existing_project_incremental_journey_is_clean,
    test_deep_review_skill_adoption_and_artifact_hygiene,
    test_pack_guide_stays_source_only_and_tour_has_no_dead_link,
    test_external_security_step_is_printed_without_installing_security_trees,
    test_global_tlc_paths_reject_without_mutation,
    test_project_local_tlc_path_is_accepted,
    test_consumer_ad_index_is_preserved_on_readopt,
    test_runtime_edits_are_overwritten_from_templates_on_readopt,
    test_adoption_installs_v3_config_and_syncs_fifteen_packets,
    test_adoption_installs_hybrid_workflow_and_preserves_consumer_config,
    test_parallel_adoption_installs_and_tracks_resource_lock,
    test_adoption_installs_only_new_authority_byte_identically,
    test_legacy_cleanup_uses_production_paths_and_hashes,
    test_legacy_cleanup_removes_owned_tests_and_preserves_consumer_files,
    test_legacy_cleanup_preserves_external_symlinked_test_directories,
    test_adoption_rejects_unsafe_generated_destinations_without_mutation,
    test_adoption_rejects_invalid_template_before_runtime_writes,
    test_adoption_rejects_malformed_local_config_without_partial_writes,
    test_gitignore_rules_merge_without_overwrite,
    test_deep_review_learnings_survive_consumer_parent_ignore,
    test_feature_specs_are_versioned_and_legacy_ignore_is_removed,
    test_graft_ignore_contract_and_search_visibility,
    test_qa_registry_keeps_fake_proof_current_and_live_orca_blocked,
    test_dependency_selection_installs_core_transitively,
    test_target_root_symlink_is_rejected_before_referent_mutation,
    test_duplicate_manifest_keys_are_rejected_for_status_and_apply,
    test_status_uses_only_public_state_vocabulary,
    test_clean_managed_files_update_when_source_bytes_change,
    test_missing_only_consumer_ownership_is_recorded_without_hashing_content,
    test_fresh_and_refuse,
    test_skip_agents_preserves_product_files_and_adopts_rest,
    test_skip_agents_preserves_absent_claude_file,
    test_adoption_imports_probe_without_orca_effect,
    test_adoption_rejects_symlinked_managed_destination_without_mutation,
    test_existing_config_drives_all_native_values_and_preserves_non_model_bytes,
    test_invalid_fixed_dependency_graph_is_a_controlled_error_before_target_access,
    test_public_publication_publishes_packets_before_manifest_last,
    test_cleanup_or_link_failure_rolls_back_live_target_and_manifest,
    test_non_normalized_manifest_paths_are_rejected_independently,
    test_exact_duplicate_manifest_keys_are_rejected_during_parsing,
    test_invalid_utf8_manifest_is_controlled_and_read_only,
    test_resolve_exact_conflicts_publishes_manifest_and_normal_apply_is_idempotent,
    test_resolve_incomplete_authorization_reports_all_unresolved_without_writes,
    test_resolve_allows_ignored_files_but_rejects_untracked_files,
    test_resolve_rejects_non_conflict_extra_and_duplicate_authorizations_without_writes,
    test_resolve_rejects_unsafe_and_managed_block_paths_without_writes,
    test_resolve_helpers_validate_replacements_and_git_boundary,
    test_resolve_legacy_target_helper_validates_full_git_boundary,
    test_resolve_rejects_replaceable_leaf_and_parent_symlinks_without_writes,
    test_resolve_uses_trusted_workflow_config_without_importing_target_shadow,
    test_resolve_rejects_symlinked_claude_parent_without_external_mutation,
    test_resolve_rejects_dirty_non_git_missing_head_and_manifest_targets_without_writes,
    test_resolve_skip_agents_preserves_instruction_files,
    test_resolve_keeps_altered_instruction_blocks_manual,
    test_resolve_publication_failure_rolls_back_and_keeps_manifest_absent,
    test_resolve_rejects_target_dirty_before_publication,
    test_resolve_treats_shell_metacharacters_as_literal_argv,
    test_resolve_publication_writes_adoption_manifest_after_other_entries,
    test_resolve_rejects_shell_metacharacters_in_replacement_as_literal,
)


if __name__ == "__main__":
    for test in TESTS:
        test()
    print(f"ok ({len(TESTS)} tests)")
