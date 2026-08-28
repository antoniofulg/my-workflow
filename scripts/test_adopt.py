"""Self-check for scripts/adopt.py. Run: python3 scripts/test_adopt.py"""

from __future__ import annotations

import contextlib
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adopt import STENCIL, main
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts"))
import workflow_config

ROOT = Path(__file__).resolve().parent.parent


def run(dest: Path) -> None:
    main(["adopt.py", str(dest)])


def run_skip_agents(dest: Path) -> None:
    main(["adopt.py", "--skip-agents", str(dest)])


def snapshot_tree(root: Path) -> dict[str, tuple[str, bytes | str | None]]:
    snapshot: dict[str, tuple[str, bytes | str | None]] = {}
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            snapshot[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            snapshot[relative] = ("directory", None)
        else:
            snapshot[relative] = ("file", path.read_bytes())
    return snapshot


def set_model_setting(config: str, provider: str, role: str, model: str, effort: str) -> str:
    pattern = re.compile(
        rf"(\[models\.{provider}\.{role}\]\s+model = )\"[^\"]+\"(\s+effort = )\"[^\"]+\""
    )
    updated, count = pattern.subn(rf'\1"{model}"\2"{effort}"', config, count=1)
    assert count == 1
    return updated


def strip_packet_metadata(provider: str, data: bytes) -> bytes:
    text = data.decode("utf-8")
    if provider == "claude":
        lines = [line for line in text.splitlines(keepends=True) if not line.startswith(("model:", "effort:"))]
    elif provider == "codex":
        lines = [line for line in text.splitlines(keepends=True) if not line.startswith(("model =", "model_reasoning_effort ="))]
    else:
        lines = [line for line in text.splitlines(keepends=True) if not line.startswith("model:")]
    return "".join(lines).encode("utf-8")


def test_deep_review_skill_adoption_and_artifact_hygiene() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        for path in (
            ".agents/skills/deep-review/SKILL.md",
            ".agents/skills/deep-review/scripts/build_jobs.py",
            ".agents/skills/deep-review/references/context-pack.md",
            ".agents/skills/deep-review/assets/PROMPT.md",
        ):
            assert (tmp / path).is_file(), path
        assert (tmp / ".claude/skills/deep-review").is_symlink()
        assert os.readlink(tmp / ".claude/skills/deep-review") == (
            "../../.agents/skills/deep-review"
        )
        assert not list((tmp / ".agents/skills/deep-review").rglob("__pycache__"))
        assert not list((tmp / ".agents/skills/deep-review").rglob("*.pyc"))
    finally:
        shutil.rmtree(tmp)


def test_pack_guide_stays_source_only_and_tour_has_no_dead_link() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        assert (ROOT / "docs/workflow/pack.md").is_file()
        assert not (tmp / "docs/workflow/pack.md").exists()
        tour = (tmp / "docs/workflow/README.md").read_text(encoding="utf-8")
        assert "pack.md" not in tour
        for path in (
            "docs/workflow/README.md",
            "docs/workflow/decisions.md",
            "docs/workflow/guidelines.md",
            "docs/workflow/loop.md",
            "docs/workflow/purpose.md",
            "docs/workflow/reviews.md",
        ):
            assert (tmp / path).is_file(), path
    finally:
        shutil.rmtree(tmp)


def test_external_security_step_is_printed_without_installing_security_trees() -> None:
    tmp = Path(tempfile.mkdtemp()).resolve()
    try:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            run(tmp)
        text = output.getvalue()
        for name in (
            "security-best-practices",
            "security-threat-model",
            "security-review",
        ):
            assert not (tmp / ".agents/skills" / name).exists()
        installer = (ROOT / "scripts/install_security_skills.py").resolve()
        assert (
            f"After explicit authorization, run exactly: python3 {installer} {tmp} --yes"
            in text
        )
        assert "external dependencies, not bundled skills" in text
        assert "security gate remains uncovered" in text
        assert not (tmp / ".my-workflow-security-skills.lock").exists()
    finally:
        shutil.rmtree(tmp)


def test_global_tlc_paths_reject_without_mutation() -> None:
    roots = (
        "$(HOME)/.claude/skills/workflow-spec-driven/scripts",
        "${HOME}/.claude/skills/workflow-spec-driven/scripts",
        "$HOME/.claude/skills/workflow-spec-driven/scripts",
        "~/.claude/skills/workflow-spec-driven/scripts",
    )
    for root in roots:
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / "consumer.txt").write_text("consumer\n", encoding="utf-8")
            (tmp / "Makefile").write_text(f"TLC := {root}/validate_tasks.py\n", encoding="utf-8")
            before = snapshot_tree(tmp)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                try:
                    run(tmp)
                except SystemExit as exc:
                    assert exc.code == 1
                else:
                    raise AssertionError(f"expected rejection for {root}")
            assert snapshot_tree(tmp) == before
            assert "use .agents/skills/workflow-spec-driven/scripts/" in stderr.getvalue()
        finally:
            shutil.rmtree(tmp)


def test_project_local_tlc_path_is_accepted() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / "Makefile").write_text(
            "TLC := .agents/skills/workflow-spec-driven/scripts/validate_tasks.py\n",
            encoding="utf-8",
        )
        run(tmp)
        assert (tmp / ".agents/skills/workflow-spec-driven/SKILL.md").is_file()
        assert (tmp / "Makefile").read_text(encoding="utf-8").startswith("TLC := .agents/")
    finally:
        shutil.rmtree(tmp)


def test_fresh_and_refuse() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        config = tmp / ".my-workflow.toml"
        sentinel = (
            "# consumer-owned\n"
            + (ROOT / ".my-workflow.toml.example").read_text(encoding="utf-8").replace(
                'cadence = "grouped.3"', 'cadence = "feature"'
            )
        )
        config.write_text(sentinel, encoding="utf-8")
        original_config = config.read_bytes()
        run(tmp)
        assert config.read_bytes() == original_config
        agents = (tmp / "AGENTS.md").read_text(encoding="utf-8")
        assert STENCIL in agents
        claude = tmp / "CLAUDE.md"
        assert not claude.is_symlink()
        assert claude.read_text(encoding="utf-8") == "@AGENTS.md\n"
        assert (tmp / "docs/guidelines/GATES.md").is_file()
        assert (tmp / "tools/ad-index.py").is_file()
        assert (tmp / ".agents/skills/qa-plan/SKILL.md").is_file()
        assert (tmp / ".agents/skills/qa-execute/SKILL.md").is_file()
        workflow_skill = tmp / ".agents/skills/workflow-config/SKILL.md"
        workflow_resolver = tmp / ".agents/skills/workflow-config/scripts/workflow_config.py"
        assert workflow_skill.is_file()
        assert workflow_resolver.is_file()
        assert workflow_resolver.read_bytes() == (
            ROOT / ".agents/skills/workflow-config/scripts/workflow_config.py"
        ).read_bytes()
        assert (tmp / "docs/qa/README.md").is_file()
        assert (tmp / ".claude/skills/autonomous").is_symlink()
        assert (tmp / ".claude/skills/qa-plan").is_symlink()
        assert (tmp / ".claude/skills/qa-execute").is_symlink()
        assert (tmp / ".cursor/agents/planner.md").is_file()
        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        for entry in (
            "!.deep-review/",
            ".deep-review/*",
            "!.deep-review/learnings.md",
            "graft/",
        ):
            assert ignored.splitlines().count(entry) == 1
        assert ".specs/features/" not in ignored.splitlines()
        search_ignored = (tmp / ".ignore").read_text(encoding="utf-8")
        for entry in ("!graft/", "graft/.cache/", "graft/.graph/"):
            assert search_ignored.splitlines().count(entry) == 1
        for path in (
            ".cursor/agents/explorer.md",
            ".claude/agents/explorer.md",
            ".codex/agents/explorer.toml",
        ):
            assert (tmp / path).is_file()

        run(tmp)
        assert config.read_bytes() == original_config

        (tmp / "AGENTS.md").write_text(
            "# Agent operating system\n\n## What this project is\n\nA shipped product.\n",
            encoding="utf-8",
        )
        before_refusal = snapshot_tree(tmp)
        try:
            run(tmp)
        except SystemExit as exc:
            assert exc.code == 1
            assert snapshot_tree(tmp) == before_refusal
        else:
            raise AssertionError("expected refuse on non-stencil product paragraph")
    finally:
        shutil.rmtree(tmp)


def test_consumer_ad_index_is_preserved_on_readopt() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        ad_index = tmp / "tools/ad-index.py"
        assert ad_index.is_file()
        consumer_version = b"#!/usr/bin/env python3\n# consumer extension\n"
        ad_index.write_bytes(consumer_version)

        run(tmp)

        assert ad_index.read_bytes() == consumer_version
    finally:
        shutil.rmtree(tmp)


def test_skip_agents_preserves_product_files_and_adopts_rest() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        agents = tmp / "AGENTS.md"
        claude = tmp / "CLAUDE.md"
        agents.write_text("# Product instructions\n", encoding="utf-8")
        claude.write_text("# Product Claude instructions\n", encoding="utf-8")
        original_agents = agents.read_bytes()
        original_claude = claude.read_bytes()

        run_skip_agents(tmp)

        assert agents.read_bytes() == original_agents
        assert claude.read_bytes() == original_claude
        assert (tmp / ".agents/skills/deep-review/SKILL.md").is_file()
        assert (tmp / ".cursor/agents/explorer.md").is_file()
        assert (tmp / ".claude/skills/deep-review").is_symlink()
        assert (tmp / "docs/guidelines/GATES.md").is_file()
        assert (tmp / "docs/qa/README.md").is_file()
        assert ".deep-review/*\n" in (tmp / ".gitignore").read_text(encoding="utf-8")
    finally:
        shutil.rmtree(tmp)


def test_skip_agents_preserves_absent_claude_file() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / "AGENTS.md").write_text("# Product instructions\n", encoding="utf-8")
        run_skip_agents(tmp)
        assert not (tmp / "CLAUDE.md").exists()
    finally:
        shutil.rmtree(tmp)


def test_runtime_edits_are_overwritten_from_templates_on_readopt() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        template = tmp / "templates/agents/cursor/planner.md"
        template_before = template.read_bytes()
        pin = tmp / ".cursor/agents/planner.md"
        pin.write_text("Disposable runtime instructions\n", encoding="utf-8")
        explorer = tmp / ".cursor" / "agents" / "explorer.md"
        explorer.unlink()
        run(tmp)
        config = workflow_config._read_config(tmp)
        assert pin.read_bytes() == workflow_config.render_agent_packet(
            "cursor",
            template_before,
            workflow_config.model_setting(config, "cursor", "planner"),
            Path("templates/agents/cursor/planner.md"),
        )
        assert b"Disposable runtime instructions" not in pin.read_bytes()
        assert explorer.read_text(encoding="utf-8") == (
            ROOT / "templates/agents/cursor/explorer.md"
        ).read_text(encoding="utf-8")
        assert template.read_bytes() == template_before
        assert (tmp / "CLAUDE.md").read_text(encoding="utf-8") == "@AGENTS.md\n"
        profile = tmp / "docs/qa/README.md"
        profile.write_text("consumer-owned profile\n", encoding="utf-8")
        run(tmp)
        assert profile.read_text(encoding="utf-8") == "consumer-owned profile\n"
    finally:
        shutil.rmtree(tmp)


def test_adoption_installs_v3_config_and_syncs_fifteen_packets() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        subprocess.run(["git", "init", "-q", str(tmp)], check=True)
        run(tmp)
        config = (tmp / ".my-workflow.toml").read_text(encoding="utf-8")
        assert config.startswith("version = 3\n")
        assert (tmp / ".my-workflow.toml.example").is_file()
        assert (tmp / "templates/agents/claude/planner.md").is_file()
        assert not (tmp / ".my-workflow.toml.example").is_symlink()
        for relative in (
            ".my-workflow.toml",
            ".claude/agents/planner.md",
            ".codex/agents/planner.toml",
            ".cursor/agents/planner.md",
        ):
            assert subprocess.run(
                ["git", "check-ignore", "--no-index", "--quiet", "--", relative],
                cwd=tmp,
                check=False,
            ).returncode == 0
        parsed = workflow_config._read_config(tmp)
        for provider in ("claude", "codex", "cursor"):
            for role in workflow_config.ROLES:
                agent_name = workflow_config.AGENT_NAMES.get(role, role)
                extension = "toml" if provider == "codex" else "md"
                packet = tmp / f".{provider}/agents/{agent_name}.{extension}"
                assert packet.is_file()
                text = packet.read_text(encoding="utf-8")
                actual = workflow_config.packet_setting(provider, text, packet)
                assert actual == workflow_config.model_setting(parsed, provider, role)
    finally:
        shutil.rmtree(tmp)


def test_adoption_installs_hybrid_workflow_and_preserves_consumer_config() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        subprocess.run(["git", "init", "-q", str(tmp)], check=True)
        source = ROOT / "tools/qa_parallel_pilot.py"
        probe_source = ROOT / "tools/orca_assisted_probe.py"
        run(tmp)
        adopted = tmp / "tools/qa_parallel_pilot.py"
        assert adopted.is_file()
        assert adopted.read_bytes() == source.read_bytes()
        probe = tmp / "tools/orca_assisted_probe.py"
        assert probe.is_file()
        assert probe.read_bytes() == probe_source.read_bytes()

        adopted.write_bytes(b"stale managed copy\n")
        legacy = tmp / ".agents/skills/tlc-spec-driven"
        legacy.mkdir(parents=True)
        (legacy / "SKILL.md").write_text("obsolete\n", encoding="utf-8")
        legacy_pointer = tmp / ".claude/skills/tlc-spec-driven"
        legacy_pointer.symlink_to("../../.agents/skills/tlc-spec-driven")
        config = tmp / ".my-workflow.toml"
        config.write_bytes(config.read_bytes() + b"# consumer-owned\n")
        config_before = config.read_bytes()
        profile = tmp / "docs/qa/README.md"
        profile.write_bytes(b"consumer-owned QA profile\n")
        profile_before = profile.read_bytes()
        run(tmp)
        assert adopted.read_bytes() == source.read_bytes()
        assert config.read_bytes() == config_before
        assert profile.read_bytes() == profile_before
        assert not legacy.exists()
        assert not legacy_pointer.exists()

        probe.write_bytes(b"stale managed probe\n")
        pilot_before = adopted.read_bytes()
        run(tmp)
        assert adopted.read_bytes() == pilot_before == source.read_bytes()
        assert probe.read_bytes() == probe_source.read_bytes()
    finally:
        shutil.rmtree(tmp)


def test_adoption_installs_only_new_authority_byte_identically() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        subprocess.run(["git", "init", "-q", str(tmp)], check=True)
        run(tmp)
        for relative in (
            ".agents/skills/workflow-spec-driven",
            ".agents/skills/autonomous",
            ".agents/skills/workflow-config",
            "templates/agents",
            "docs/guidelines",
            "docs/qa/README.md",
            "tools/orca_assisted_probe.py",
            ".my-workflow.toml.example",
        ):
            source = ROOT / relative
            installed = tmp / relative
            assert installed.exists(), relative
            if source.is_dir():
                source_files = {
                    path.relative_to(source)
                    for path in source.rglob("*")
                    if path.is_file() and "__pycache__" not in path.parts and not path.name.endswith(".pyc")
                }
                for child in source_files:
                    assert (installed / child).read_bytes() == (source / child).read_bytes()
            else:
                assert installed.read_bytes() == source.read_bytes()
        assert not (tmp / ".agents/skills/tlc-spec-driven").exists()
        assert not (tmp / ".claude/skills/tlc-spec-driven").exists()
    finally:
        shutil.rmtree(tmp)


def test_adoption_imports_probe_without_orca_effect() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        calls = tmp / "orca.calls"
        fake = tmp / "orca"
        fake.write_text(
            f"#!/bin/sh\nprintf '%s\\n' called >> {calls}\nexit 99\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        env = {**os.environ, "PATH": f"{tmp}:{os.environ.get('PATH', '')}"}
        result = subprocess.run(
            [sys.executable, "-c", "import tools.orca_assisted_probe"],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert not calls.exists() or calls.read_text(encoding="utf-8") == ""
    finally:
        shutil.rmtree(tmp)


def test_adoption_rejects_symlinked_managed_destination_without_mutation() -> None:
    tmp = Path(tempfile.mkdtemp())
    outside = Path(tempfile.mkdtemp())
    try:
        target = tmp / "tools/orca_assisted_probe.py"
        target.parent.mkdir(parents=True)
        target.symlink_to(outside / "probe.py")
        (tmp / ".agents/skills/tlc-spec-driven").mkdir(parents=True)
        before = snapshot_tree(tmp)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            try:
                run(tmp)
            except SystemExit as exc:
                assert exc.code == 1
            else:
                raise AssertionError("expected symlinked destination rejection")
        assert snapshot_tree(tmp) == before
        assert "managed destination" in stderr.getvalue()
        assert "symlink" in stderr.getvalue()
    finally:
        shutil.rmtree(tmp)
        shutil.rmtree(outside)


def test_adoption_rejects_unsafe_generated_destinations_without_mutation() -> None:
    cases = (".gitignore", ".ignore", "tools")
    for relative in cases:
        tmp = Path(tempfile.mkdtemp())
        outside = Path(tempfile.mkdtemp())
        try:
            sentinel = outside / "sentinel"
            sentinel.write_bytes(b"outside consumer data\n")
            target = tmp / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(sentinel if target.name != "tools" else outside)
            before = snapshot_tree(tmp)
            before_sha = hashlib.sha256(sentinel.read_bytes()).hexdigest()
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                try:
                    run(tmp)
                except SystemExit as exc:
                    assert exc.code == 1
                else:
                    raise AssertionError(f"expected unsafe destination rejection for {relative}")
            assert snapshot_tree(tmp) == before
            assert hashlib.sha256(sentinel.read_bytes()).hexdigest() == before_sha
            assert "must not be a symlink" in stderr.getvalue()
        finally:
            shutil.rmtree(tmp)
            shutil.rmtree(outside)

    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / ".gitignore").mkdir()
        before = snapshot_tree(tmp)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            try:
                run(tmp)
            except SystemExit as exc:
                assert exc.code == 1
            else:
                raise AssertionError("expected non-regular merge destination rejection")
        assert snapshot_tree(tmp) == before
        assert "must be a file" in stderr.getvalue()
    finally:
        shutil.rmtree(tmp)


def test_qa_registry_keeps_fake_proof_current_and_live_orca_blocked() -> None:
    adoption = (ROOT / "docs/qa/scenarios/ADP-adopt-workflow-safely.md").read_text(encoding="utf-8")
    fallback = (ROOT / "docs/qa/scenarios/CFG-fallback-unproven-parallel-execution.md").read_text(encoding="utf-8")
    live = (ROOT / "docs/qa/scenarios/QAS-run-resource-free-parallel-orca-slices.md").read_text(encoding="utf-8")
    assert "tools/orca_assisted_probe.py" in adoption
    assert "qa_status: untested" in adoption
    assert "qa_status: pass" in fallback
    assert "qa_status: blocked-verify" in live
    assert "upstream" in live.lower()
    assert "Orca/Codex" in live
    assert "fake" in live.lower()


def test_adoption_rejects_invalid_template_before_runtime_writes() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        template = tmp / "templates/agents/cursor/verifier.md"
        template.write_text(
            template.read_text(encoding="utf-8").replace("model:", "model-old:"),
            encoding="utf-8",
        )
        runtime_before = {
            path: path.read_bytes()
            for provider in workflow_config.PROVIDERS
            for role in workflow_config.ROLES
            for path in [tmp / workflow_config._runtime_relative(provider, role)]
        }
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            try:
                run(tmp)
            except SystemExit as exc:
                assert exc.code == 1
            else:
                raise AssertionError("expected malformed packet rejection")
        assert "verifier" in stderr.getvalue()
        assert "model-old:" in template.read_text(encoding="utf-8")
        assert {path: path.read_bytes() for path in runtime_before} == runtime_before
    finally:
        shutil.rmtree(tmp)


def test_adoption_rejects_malformed_local_config_without_partial_writes() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        config = tmp / ".my-workflow.toml"
        config.write_bytes(b"version = 1\n")
        before = snapshot_tree(tmp)
        runtime_before = {
            path: path.read_bytes()
            for provider in workflow_config.PROVIDERS
            for role in workflow_config.ROLES
            for path in [tmp / workflow_config._runtime_relative(provider, role)]
        }
        sources_before = {
            path: path.read_bytes()
            for path in [tmp / ".my-workflow.toml.example", *sorted((tmp / "templates/agents").rglob("*"))]
            if path.is_file()
        }
        stderr = io.StringIO()
        stdout = io.StringIO()
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            try:
                run(tmp)
            except SystemExit as exc:
                assert exc.code == 1
            else:
                raise AssertionError("expected malformed local config rejection")
        assert stdout.getvalue() == ""
        assert stderr.getvalue() == (
            "adoption could not synchronize agent metadata: "
            "workflow-config: version must be integer 3; refresh the project configuration\n"
        )
        assert snapshot_tree(tmp) == before
        assert config.read_bytes() == b"version = 1\n"
        assert {path: path.read_bytes() for path in runtime_before} == runtime_before
        assert {
            path: path.read_bytes()
            for path in sources_before
        } == sources_before
    finally:
        shutil.rmtree(tmp)


def test_existing_config_drives_all_native_values_and_preserves_non_model_bytes() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        config_path = tmp / ".my-workflow.toml"
        customized = config_path.read_text(encoding="utf-8")
        customized = set_model_setting(customized, "claude", "planner", "claude-target", "medium")
        customized = set_model_setting(customized, "codex", "implementer", "codex-target", "low")
        customized = set_model_setting(customized, "cursor", "verifier", "cursor-target", "high")
        config_path.write_text(customized, encoding="utf-8")
        original_config = config_path.read_bytes()
        original_templates: dict[Path, bytes] = {}
        for provider in workflow_config.PROVIDERS:
            for role in workflow_config.ROLES:
                agent_name = workflow_config.AGENT_NAMES.get(role, role)
                extension = "toml" if provider == "codex" else "md"
                template = tmp / f"templates/agents/{provider}/{agent_name}.{extension}"
                template.write_bytes(template.read_bytes() + b"\n# consumer instruction sentinel\n")
                original_templates[template] = template.read_bytes()

        run(tmp)
        assert config_path.read_bytes() == original_config
        parsed = workflow_config._read_config(tmp)
        for provider in workflow_config.PROVIDERS:
            for role in workflow_config.ROLES:
                agent_name = workflow_config.AGENT_NAMES.get(role, role)
                extension = "toml" if provider == "codex" else "md"
                packet = tmp / f".{provider}/agents/{agent_name}.{extension}"
                actual = workflow_config.packet_setting(provider, packet.read_text(encoding="utf-8"), packet)
                assert actual == workflow_config.model_setting(parsed, provider, role)
                template = tmp / f"templates/agents/{provider}/{agent_name}.{extension}"
                assert strip_packet_metadata(provider, original_templates[template]) == strip_packet_metadata(provider, packet.read_bytes())
    finally:
        shutil.rmtree(tmp)


def test_gitignore_rules_merge_without_overwrite() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / ".gitignore").write_text("consumer-cache/\n", encoding="utf-8")
        run(tmp)
        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        assert "consumer-cache/\n" in ignored
        for entry in (
            "!.deep-review/",
            ".deep-review/*",
            "!.deep-review/learnings.md",
            "graft/",
        ):
            assert ignored.splitlines().count(entry) == 1
        assert ".specs/features/" not in ignored.splitlines()

        (tmp / ".gitignore").write_text(
            "consumer-cache/\n"
            "!.deep-review/learnings.md\n"
            ".deep-review/*\n"
            "consumer-output/\n",
            encoding="utf-8",
        )
        run(tmp)
        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        assert "consumer-cache/\n" in ignored
        assert "consumer-output/\n" in ignored
        assert ignored.splitlines()[-4:] == [
            "!.deep-review/",
            ".deep-review/*",
            "!.deep-review/learnings.md",
            "graft/",
        ]
    finally:
        shutil.rmtree(tmp)


def test_deep_review_learnings_survive_consumer_parent_ignore() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / ".gitignore").write_text(
            ".deep-review/\nconsumer-cache/\n", encoding="utf-8"
        )
        subprocess.run(["git", "init", "-q", str(tmp)], check=True)
        run(tmp)
        (tmp / ".deep-review").mkdir(exist_ok=True)
        (tmp / ".deep-review/learnings.md").write_text("durable\n", encoding="utf-8")
        (tmp / ".deep-review/review.json").write_text("generated\n", encoding="utf-8")

        learnings = subprocess.run(
            ["git", "-C", str(tmp), "check-ignore", "-q", "--", ".deep-review/learnings.md"],
            check=False,
        )
        review = subprocess.run(
            ["git", "-C", str(tmp), "check-ignore", "-q", "--", ".deep-review/review.json"],
            check=False,
        )
        assert learnings.returncode == 1
        assert review.returncode == 0
        merged_ignore = (tmp / ".gitignore").read_text(encoding="utf-8").splitlines()
        assert merged_ignore.count(".deep-review/") == 1
        assert merged_ignore[-4:] == [
            "!.deep-review/",
            ".deep-review/*",
            "!.deep-review/learnings.md",
            "graft/",
        ]

        before = (tmp / ".gitignore").read_bytes()
        run(tmp)
        assert (tmp / ".gitignore").read_bytes() == before
    finally:
        shutil.rmtree(tmp)


def test_feature_specs_are_versioned_and_legacy_ignore_is_removed() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        subprocess.run(["git", "init", "-q", str(tmp)], check=True)
        run(tmp)
        gitignore = tmp / ".gitignore"
        assert ".specs/features/" not in gitignore.read_text(encoding="utf-8").splitlines()

        gitignore.write_text(
            "# keep this consumer comment\n"
            "consumer-cache/\n"
            ".specs/features/\n"
            ".specs/features/\n"
            "consumer-output/\n",
            encoding="utf-8",
        )
        run(tmp)
        migrated = gitignore.read_text(encoding="utf-8")
        assert ".specs/features/" not in migrated.splitlines()
        migrated_lines = migrated.splitlines()
        assert migrated_lines[:3] == [
            "# keep this consumer comment",
            "consumer-cache/",
            "consumer-output/",
        ]
        assert migrated_lines[-4:] == [
            "!.deep-review/",
            ".deep-review/*",
            "!.deep-review/learnings.md",
            "graft/",
        ]

        feature = tmp / ".specs/features/register-user/spec.md"
        feature.parent.mkdir(parents=True)
        feature.write_text("# Register user\n", encoding="utf-8")
        visible = subprocess.run(
            ["git", "check-ignore", "--no-index", "--quiet", "--", str(feature.relative_to(tmp))],
            cwd=tmp,
            check=False,
        )
        assert visible.returncode == 1
        second_before = gitignore.read_bytes()
        run(tmp)
        assert gitignore.read_bytes() == second_before
        assert feature.relative_to(tmp).as_posix() in subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--", ".specs/features"],
            cwd=tmp,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    finally:
        shutil.rmtree(tmp)


def test_graft_ignore_contract_and_search_visibility() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / ".gitignore").write_text("consumer-cache/\n", encoding="utf-8")
        (tmp / ".ignore").write_text("consumer-search-cache/\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(tmp)], check=True)
        run(tmp)

        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        assert "consumer-cache/\n" in ignored
        assert ignored.splitlines().count("graft/") == 1
        search_ignored = (tmp / ".ignore").read_text(encoding="utf-8")
        assert "consumer-search-cache/\n" in search_ignored
        for entry in ("!graft/", "graft/.cache/", "graft/.graph/"):
            assert search_ignored.splitlines().count(entry) == 1

        (tmp / "graft/.cache").mkdir(parents=True)
        (tmp / "graft/.graph").mkdir(parents=True)
        (tmp / "graft/.cache/index.json").write_text("cache\n", encoding="utf-8")
        (tmp / "graft/.graph/wiring.json").write_text("graph\n", encoding="utf-8")
        card = tmp / "graft/cards/adoption.md"
        card.parent.mkdir(parents=True)
        card.write_text("generated adoption card\n", encoding="utf-8")

        for path in ("graft/.cache/index.json", "graft/.graph/wiring.json"):
            result = subprocess.run(
                ["git", "-C", str(tmp), "check-ignore", "-q", "--", path],
                check=False,
            )
            assert result.returncode == 0, path

        search = subprocess.run(
            ["rg", "--files", "--hidden", "--no-ignore-parent"],
            cwd=tmp,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "graft/cards/adoption.md" in search.stdout
        assert "graft/.cache/index.json" not in search.stdout
        assert "graft/.graph/wiring.json" not in search.stdout
    finally:
        shutil.rmtree(tmp)


TESTS = (
    "test_fresh_and_refuse",
    "test_consumer_ad_index_is_preserved_on_readopt",
    "test_skip_agents_preserves_product_files_and_adopts_rest",
    "test_skip_agents_preserves_absent_claude_file",
    "test_runtime_edits_are_overwritten_from_templates_on_readopt",
    "test_adoption_installs_v3_config_and_syncs_fifteen_packets",
    "test_adoption_installs_hybrid_workflow_and_preserves_consumer_config",
    "test_adoption_installs_only_new_authority_byte_identically",
    "test_adoption_imports_probe_without_orca_effect",
    "test_adoption_rejects_symlinked_managed_destination_without_mutation",
    "test_adoption_rejects_unsafe_generated_destinations_without_mutation",
    "test_qa_registry_keeps_fake_proof_current_and_live_orca_blocked",
    "test_adoption_rejects_invalid_template_before_runtime_writes",
    "test_adoption_rejects_malformed_local_config_without_partial_writes",
    "test_existing_config_drives_all_native_values_and_preserves_non_model_bytes",
    "test_gitignore_rules_merge_without_overwrite",
    "test_deep_review_learnings_survive_consumer_parent_ignore",
    "test_feature_specs_are_versioned_and_legacy_ignore_is_removed",
    "test_graft_ignore_contract_and_search_visibility",
    "test_deep_review_skill_adoption_and_artifact_hygiene",
    "test_pack_guide_stays_source_only_and_tour_has_no_dead_link",
    "test_external_security_step_is_printed_without_installing_security_trees",
    "test_global_tlc_paths_reject_without_mutation",
    "test_project_local_tlc_path_is_accepted",
)


def run_registered_tests() -> None:
    defined = {
        name for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    }
    registered = set(TESTS)
    missing = sorted(defined - registered)
    duplicates = sorted({name for name in TESTS if TESTS.count(name) > 1})
    unknown = sorted(registered - defined)
    errors = []
    if missing:
        errors.append(f"missing: {', '.join(missing)}")
    if duplicates:
        errors.append(f"duplicate: {', '.join(duplicates)}")
    if unknown:
        errors.append(f"unknown: {', '.join(unknown)}")
    if errors:
        raise SystemExit("test registry mismatch: " + "; ".join(errors))
    for name in TESTS:
        globals()[name]()


if __name__ == "__main__":
    run_registered_tests()
    print("ok")
