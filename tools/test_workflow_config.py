"""Unit contract for central workflow model configuration."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts"))
import workflow_config


MODELS = {
    provider: {
        role: {"model": f"{provider}-{role}", "effort": "high"}
        for role in workflow_config.ROLES
    }
    for provider in workflow_config.PROVIDERS
}


def write_config(root: Path, *, models: dict | None = None, extra: str = "") -> None:
    lines = ["version = 2", "", "[deep_review]", 'cadence = "grouped.3"', ""]
    for provider in workflow_config.PROVIDERS:
        for role in workflow_config.ROLES:
            setting = (models or MODELS)[provider][role]
            lines.extend(
                [
                    f"[models.{provider}.{role}]",
                    f'model = "{setting["model"]}"',
                    f'effort = "{setting["effort"]}"',
                    "",
                ]
            )
    (root / ".my-workflow.toml").write_text("\n".join(lines) + extra, encoding="utf-8")


def make_root() -> Path:
    return Path(tempfile.mkdtemp())


def write_packets(root: Path) -> None:
    packets = {
        "claude": "---\nname: {role}\nmodel: old-model\neffort: low\ntools: Read\n---\nInstructions for {role}.\n",
        "cursor": "---\nname: {role}\nmodel: old-model[effort=low]\nis_background: true\n---\nInstructions for {role}.\n",
        "codex": 'name = "{role}"\nmodel = "old-model"\nmodel_reasoning_effort = "low"\nsandbox_mode = "read-only"\n\ndeveloper_instructions = "Instructions for {role}."\n',
    }
    for provider, template in packets.items():
        extension = "toml" if provider == "codex" else "md"
        agents = root / f".{provider}" / "agents"
        agents.mkdir(parents=True)
        for role in workflow_config.ROLES:
            agent_name = workflow_config.AGENT_NAMES.get(role, role)
            (agents / f"{agent_name}.{extension}").write_text(
                template.format(role=agent_name), encoding="utf-8"
            )


def make_packet_root() -> Path:
    root = make_root()
    write_config(root)
    write_packets(root)
    return root


def git_root(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)


def test_parses_complete_v2_matrix() -> None:
    root = make_root()
    try:
        write_config(root)
        config = workflow_config._read_config(root)
        assert config["version"] == 2
        for provider in workflow_config.PROVIDERS:
            for role in workflow_config.ROLES:
                assert workflow_config.model_setting(config, provider, role) == MODELS[provider][role]
    finally:
        shutil.rmtree(root)


def test_rejects_invalid_matrix() -> None:
    cases = [
        (lambda c: c.__setitem__("version", 1), "version must be integer 2"),
        (lambda c: c["models"].pop("cursor"), "models.cursor is required"),
        (lambda c: c["models"]["codex"].pop("verifier"), "models.codex.verifier is required"),
        (
            lambda c: c["models"]["codex"].__setitem__("reviewer", {"model": "x", "effort": "high"}),
            "models.codex contains unknown role 'reviewer'",
        ),
        (
            lambda c: c["models"]["codex"]["verifier"].__setitem__("extra", True),
            "models.codex.verifier contains unknown key 'extra'",
        ),
        (
            lambda c: c["models"]["codex"]["verifier"].__setitem__("model", ""),
            "models.codex.verifier.model must be a non-empty string",
        ),
        (
            lambda c: c["models"]["codex"]["verifier"].__setitem__("effort", "bogus"),
            "models.codex.verifier.effort must be one of",
        ),
        (
            lambda c: c["models"]["claude"]["verifier"].__setitem__("effort", "ultra"),
            "models.claude.verifier.effort 'ultra' is not supported by claude",
        ),
    ]
    for mutate, message in cases:
        root = make_root()
        try:
            write_config(root)
            config = workflow_config._read_config(root)
            mutate(config)
            try:
                workflow_config._validate_config_schema(config)
            except workflow_config.ConfigError as exc:
                assert message in str(exc)
            else:
                raise AssertionError(f"expected {message}")
        finally:
            shutil.rmtree(root)


def test_rejects_unknown_top_level_and_missing_config() -> None:
    root = make_root()
    try:
        write_config(root)
        config_path = root / ".my-workflow.toml"
        config_path.write_text("bogus = true\n" + config_path.read_text(encoding="utf-8"), encoding="utf-8")
        try:
            workflow_config._read_config(root)
        except workflow_config.ConfigError as exc:
            assert "unknown top-level key 'bogus'" in str(exc)
        else:
            raise AssertionError("expected unknown key failure")
        (root / ".my-workflow.toml").unlink()
        try:
            workflow_config._read_config(root)
        except workflow_config.ConfigError as exc:
            assert "version must be integer 2" in str(exc)
        else:
            raise AssertionError("expected missing config failure")
    finally:
        shutil.rmtree(root)


def test_sync_renders_all_native_metadata_and_reports_changes() -> None:
    root = make_packet_root()
    try:
        result = workflow_config.sync_agents(root)
        assert len(result["changed"]) == 15
        assert result["unchanged"] == []
        assert "model: claude-implementer" in (root / ".claude/agents/implementer.md").read_text()
        assert "effort: high" in (root / ".claude/agents/implementer.md").read_text()
        cursor = (root / ".cursor/agents/implementer.md").read_text()
        assert "model: cursor-implementer[effort=high]" in cursor
        codex = (root / ".codex/agents/implementer.toml").read_text()
        assert 'model = "codex-implementer"' in codex
        assert 'model_reasoning_effort = "high"' in codex
        second = workflow_config.sync_agents(root)
        assert second == {"changed": [], "unchanged": result["changed"]}
    finally:
        shutil.rmtree(root)


def test_sync_preserves_non_model_bytes() -> None:
    root = make_packet_root()
    try:
        before = {
            path: path.read_text(encoding="utf-8")
            for path in (root / ".claude/agents").glob("*.md")
        }
        workflow_config.sync_agents(root)
        for path, original in before.items():
            current_lines = path.read_text(encoding="utf-8").splitlines()
            original_lines = original.splitlines()
            assert [line for line in current_lines if not line.startswith(("model:", "effort:"))] == [
                line for line in original_lines if not line.startswith(("model:", "effort:"))
            ]
    finally:
        shutil.rmtree(root)


def test_sync_rejects_malformed_packet_before_any_write() -> None:
    root = make_packet_root()
    try:
        target = root / ".cursor/agents/verifier.md"
        target.write_text(target.read_text(encoding="utf-8").replace("model:", "model-old:"), encoding="utf-8")
        before = {
            path: path.read_bytes()
            for provider in workflow_config.PROVIDERS
            for path in (root / f".{provider}/agents").glob("*")
        }
        try:
            workflow_config.sync_agents(root)
        except workflow_config.ConfigError as exc:
            assert "verifier" in str(exc)
        else:
            raise AssertionError("expected malformed packet failure")
        assert {path: path.read_bytes() for path in before} == before
    finally:
        shutil.rmtree(root)


def test_resolve_freezes_delegated_settings_and_omits_planner() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        snapshot = workflow_config.resolve(root=root, feature="freeze", slice_count=2, native_provider="codex")
        assert snapshot["version"] == 2
        assert set(snapshot["roles"]) == set(workflow_config.DELEGATED_ROLES)
        for role in workflow_config.DELEGATED_ROLES:
            assert snapshot["roles"][role] == {
                "provider": "codex",
                "agent_file": f".codex/agents/{workflow_config.AGENT_NAMES.get(role, role)}.toml",
                "model": f"codex-{role}",
                "effort": "high",
            }
    finally:
        shutil.rmtree(root)


def test_resume_rejects_drift_and_refresh_freezes_new_settings() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        first = workflow_config.resolve(root=root, feature="drift", slice_count=1, native_provider="codex")
        models = {provider: {role: dict(setting) for role, setting in values.items()} for provider, values in MODELS.items()}
        models["codex"]["implementer"]["model"] = "codex-implementer-v2"
        write_config(root, models=models)
        workflow_config.sync_agents(root)
        try:
            workflow_config.resolve(root=root, feature="drift", slice_count=1, native_provider="codex")
        except workflow_config.ConfigError as exc:
            assert "run --sync-agents, then explicitly use --refresh" in str(exc)
        else:
            raise AssertionError("expected resume drift failure")
        refreshed = workflow_config.resolve(
            root=root, feature="drift", slice_count=1, native_provider="codex", refresh=True
        )
        assert refreshed["roles"]["implementer"]["model"] == "codex-implementer-v2"
        assert refreshed["roles"]["implementer"]["effort"] == first["roles"]["implementer"]["effort"]
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
