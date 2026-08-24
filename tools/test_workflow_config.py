"""Unit contract for central workflow model configuration."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import hashlib
import json
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


def packet_paths(root: Path) -> list[Path]:
    return [
        root / relative
        for provider in workflow_config.PROVIDERS
        for role in workflow_config.ROLES
        for relative in [Path(workflow_config._agent_file(root, provider, role))]
    ]


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(packet_paths(root)):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def strip_metadata(provider: str, content: bytes) -> bytes:
    text = content.decode("utf-8")
    if provider == "claude":
        lines = [line for line in text.splitlines(keepends=True) if not line.startswith(("model:", "effort:"))]
    elif provider == "codex":
        lines = [
            line for line in text.splitlines(keepends=True)
            if not line.startswith(("model =", "model_reasoning_effort ="))
        ]
    else:
        lines = [line for line in text.splitlines(keepends=True) if not line.startswith("model:")]
    return "".join(lines).encode("utf-8")


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
            lambda c: c["models"]["codex"]["verifier"].pop("model"),
            "models.codex.verifier.model is required",
        ),
        (
            lambda c: c["models"]["codex"]["verifier"].pop("effort"),
            "models.codex.verifier.effort is required",
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
        before = {path: path.read_bytes() for path in packet_paths(root)}
        result = workflow_config.sync_agents(root)
        expected_paths = sorted(path.relative_to(root).as_posix() for path in before)
        assert sorted(result["changed"]) == expected_paths
        assert result["unchanged"] == []
        assert "model: claude-implementer" in (root / ".claude/agents/implementer.md").read_text()
        assert "effort: high" in (root / ".claude/agents/implementer.md").read_text()
        cursor = (root / ".cursor/agents/implementer.md").read_text()
        assert "model: cursor-implementer[effort=high]" in cursor
        codex = (root / ".codex/agents/implementer.toml").read_text()
        assert 'model = "codex-implementer"' in codex
        assert 'model_reasoning_effort = "high"' in codex
        first_digest = tree_digest(root)
        second = workflow_config.sync_agents(root)
        assert second["changed"] == []
        assert sorted(second["unchanged"]) == expected_paths
        assert tree_digest(root) == first_digest
        for path, original in before.items():
            provider = path.parts[-3][1:]
            assert strip_metadata(provider, original) == strip_metadata(provider, path.read_bytes())
    finally:
        shutil.rmtree(root)


def test_sync_preserves_non_model_bytes() -> None:
    root = make_packet_root()
    try:
        before = {path: path.read_bytes() for path in packet_paths(root)}
        workflow_config.sync_agents(root)
        for path, original in before.items():
            provider = path.parts[-3][1:]
            assert strip_metadata(provider, original) == strip_metadata(provider, path.read_bytes())
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


def test_cli_errors_use_public_prefix_exit_two_and_empty_stdout() -> None:
    root = make_packet_root()
    try:
        resolver = Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts/workflow_config.py"
        config = root / ".my-workflow.toml"
        config.write_text(config.read_text(encoding="utf-8").replace('model = "codex-verifier"', 'model = ""', 1), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--sync-agents"],
            text=True, capture_output=True, check=False,
        )
        assert result.returncode == 2
        assert result.stdout == ""
        assert result.stderr.startswith("workflow-config:")

        invalid = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--feature", "bad", "--slices", "0", "--native-provider", "codex"],
            text=True, capture_output=True, check=False,
        )
        assert invalid.returncode == 2
        assert invalid.stdout == ""
        assert invalid.stderr.startswith("workflow-config:")

        conflict = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--sync-agents", "--feature", "conflict", "--slices", "1", "--native-provider", "codex"],
            text=True, capture_output=True, check=False,
        )
        assert conflict.returncode == 2
        assert conflict.stdout == ""
        assert conflict.stderr == "workflow-config: --sync-agents cannot be combined with feature-resolution arguments\n"
    finally:
        shutil.rmtree(root)


def test_sync_invalid_config_and_duplicate_metadata_write_no_packets() -> None:
    root = make_packet_root()
    try:
        before = {path: path.read_bytes() for path in packet_paths(root)}
        config = root / ".my-workflow.toml"
        config.write_text(config.read_text(encoding="utf-8").replace('model = "codex-verifier"', 'model = ""', 1), encoding="utf-8")
        try:
            workflow_config.sync_agents(root)
        except workflow_config.ConfigError:
            pass
        else:
            raise AssertionError("expected invalid config failure")
        assert {path: path.read_bytes() for path in before} == before

        write_config(root)
        duplicate = root / ".claude/agents/verifier.md"
        duplicate.write_text(duplicate.read_text(encoding="utf-8") + "model: duplicate\n", encoding="utf-8")
        before_duplicate = {path: path.read_bytes() for path in packet_paths(root)}
        try:
            workflow_config.sync_agents(root)
        except workflow_config.ConfigError as exc:
            assert "verifier" in str(exc)
        else:
            raise AssertionError("expected duplicate metadata failure")
        assert {path: path.read_bytes() for path in before_duplicate} == before_duplicate
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


def test_resume_uses_frozen_snapshot_when_config_changes_without_sync() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        first = workflow_config.resolve(root=root, feature="config-only", slice_count=1, native_provider="codex")
        models = {provider: {role: dict(setting) for role, setting in values.items()} for provider, values in MODELS.items()}
        models["codex"]["implementer"]["model"] = "codex-config-only"
        write_config(root, models=models)
        resumed = workflow_config.resolve(root=root, feature="config-only", slice_count=8, native_provider="cursor")
        assert resumed == first
    finally:
        shutil.rmtree(root)


def test_resume_rejects_effort_drift_after_sync() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        workflow_config.resolve(root=root, feature="effort-drift", slice_count=1, native_provider="codex")
        models = {provider: {role: dict(setting) for role, setting in values.items()} for provider, values in MODELS.items()}
        models["codex"]["implementer"]["effort"] = "medium"
        write_config(root, models=models)
        workflow_config.sync_agents(root)
        try:
            workflow_config.resolve(root=root, feature="effort-drift", slice_count=1, native_provider="codex")
        except workflow_config.ConfigError as exc:
            assert "run --sync-agents, then explicitly use --refresh" in str(exc)
        else:
            raise AssertionError("expected effort drift failure")
    finally:
        shutil.rmtree(root)


def test_cadence_modes_and_balancing() -> None:
    expected = {
        "slice": {
            1: [[1]], 2: [[1], [2]], 3: [[1], [2], [3]], 4: [[1], [2], [3], [4]],
            5: [[1], [2], [3], [4], [5]], 6: [[1], [2], [3], [4], [5], [6]],
            7: [[1], [2], [3], [4], [5], [6], [7]], 8: [[1], [2], [3], [4], [5], [6], [7], [8]],
        },
        "feature": {
            1: [[1]], 2: [[1, 2]], 3: [[1, 2, 3]], 4: [[1, 2, 3, 4]],
            5: [[1, 2, 3, 4, 5]], 6: [[1, 2, 3, 4, 5, 6]],
            7: [[1, 2, 3, 4, 5, 6, 7]], 8: [[1, 2, 3, 4, 5, 6, 7, 8]],
        },
        "grouped.3": {
            1: [[1]], 2: [[1, 2]], 3: [[1, 2, 3]], 4: [[1, 2], [3, 4]],
            5: [[1, 2, 3], [4, 5]], 6: [[1, 2, 3], [4, 5, 6]],
            7: [[1, 2, 3], [4, 5], [6, 7]], 8: [[1, 2, 3], [4, 5, 6], [7, 8]],
        },
    }
    for cadence, cases in expected.items():
        for slice_count, groups in cases.items():
            assert workflow_config.balanced_groups(slice_count, cadence) == groups
    assert workflow_config.balanced_groups(6, "grouped.2") == [[1, 2], [3, 4], [5, 6]]
    assert workflow_config.balanced_groups(7, "grouped.3") == [[1, 2, 3], [4, 5], [6, 7]]
    assert workflow_config.balanced_groups(8, "grouped.4") == [[1, 2, 3, 4], [5, 6, 7, 8]]
    try:
        workflow_config.balanced_groups(0, "feature")
    except workflow_config.ConfigError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("expected invalid slice count")
    for cadence in ("grouped", "grouped.0", "grouped.x", "other"):
        try:
            workflow_config.balanced_groups(2, cadence)
        except workflow_config.ConfigError:
            pass
        else:
            raise AssertionError(f"expected invalid cadence: {cadence}")


def test_profile_precedence_and_partial_defaults() -> None:
    root = make_packet_root()
    try:
        path = root / ".my-workflow.toml"
        contents = path.read_text(encoding="utf-8")
        marker = "[models.claude.planner]"
        path.write_text(
            contents.replace(
                marker,
                "[profiles.mixed]\nimplementer = 'claude'\nverifier = 'codex'\n\n" + marker,
                1,
            ),
            encoding="utf-8",
        )
        workflow_config.sync_agents(root)
        git_root(root)
        snapshot = workflow_config.resolve(
            root=root, feature="mixed", slice_count=1, native_provider="cursor",
            profile="mixed", overrides=["verifier=claude"],
        )
        assert snapshot["roles"]["implementer"]["provider"] == "claude"
        assert snapshot["roles"]["verifier"]["provider"] == "claude"
        assert snapshot["roles"]["explorer"]["provider"] == "cursor"
    finally:
        shutil.rmtree(root)


def test_invalid_routing_has_no_fallback() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        for kwargs, message in (
            ({"profile": "missing"}, "unknown profile"),
            ({"overrides": ["planner=codex"]}, "invalid role"),
            ({"overrides": ["verifier=unknown"]}, "invalid provider"),
        ):
            try:
                workflow_config.resolve(root=root, feature="invalid", slice_count=1, native_provider="codex", **kwargs)
            except workflow_config.ConfigError as exc:
                assert message in str(exc)
            else:
                raise AssertionError(f"expected {message}")
    finally:
        shutil.rmtree(root)


def test_snapshot_write_failure_preserves_previous_snapshot() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        first = workflow_config.resolve(root=root, feature="atomic", slice_count=2, native_provider="codex")
        path = root / ".specs/features/atomic/workflow.json"
        original = path.read_text(encoding="utf-8")
        real_replace = workflow_config.os.replace
        workflow_config.os.replace = lambda *_args: (_ for _ in ()).throw(OSError("injected"))
        try:
            try:
                workflow_config.resolve(root=root, feature="atomic", slice_count=3, native_provider="codex", refresh=True)
            except OSError as exc:
                assert str(exc) == "injected"
            else:
                raise AssertionError("expected atomic write failure")
        finally:
            workflow_config.os.replace = real_replace
        assert path.read_text(encoding="utf-8") == original
        assert first["version"] == 2
    finally:
        shutil.rmtree(root)


def test_invalid_existing_snapshot_fails_without_mutation() -> None:
    root = make_packet_root()
    try:
        path = root / ".specs/features/truncated/workflow.json"
        path.parent.mkdir(parents=True)
        path.write_text("{}", encoding="utf-8")
        before = path.read_bytes()
        try:
            workflow_config.resolve(root=root, feature="truncated", slice_count=2, native_provider="codex")
        except workflow_config.ConfigError as exc:
            assert "existing snapshot" in str(exc)
        else:
            raise AssertionError("expected malformed snapshot failure")
        assert path.read_bytes() == before
    finally:
        shutil.rmtree(root)


def test_cli_adapter_and_invalid_slice_count() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        resolver = Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts/workflow_config.py"
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--feature", "cli", "--slices", "2", "--native-provider", "codex", "--override", "verifier=claude"],
            text=True, capture_output=True, check=False,
        )
        assert result.returncode == 0
        assert result.stderr == ""
        payload = json.loads(result.stdout)
        assert payload["roles"]["verifier"]["provider"] == "claude"
        assert (root / ".specs/features/cli/workflow.json").is_file()
        invalid = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--feature", "invalid", "--slices", "0", "--native-provider", "codex"],
            text=True, capture_output=True, check=False,
        )
        assert invalid.returncode == 2
        assert invalid.stdout == ""
        assert "workflow-config: slice count must be at least 1" in invalid.stderr
    finally:
        shutil.rmtree(root)


def test_missing_agent_is_rejected_without_fallback() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        (root / ".codex/agents/verifier.toml").unlink()
        try:
            workflow_config.resolve(root=root, feature="missing-agent", slice_count=1, native_provider="codex")
        except workflow_config.ConfigError as exc:
            assert "missing agent file" in str(exc)
        else:
            raise AssertionError("expected missing agent failure")
    finally:
        shutil.rmtree(root)


def test_resume_is_stable_and_preserves_frozen_fallback_agent_path() -> None:
    root = make_packet_root()
    try:
        preferred = root / ".codex/agents/implementer.toml"
        fallback = root / ".codex/agents/implementer.md"
        fallback.write_text(preferred.read_text(encoding="utf-8"), encoding="utf-8")
        preferred.unlink()
        workflow_config.sync_agents(root)
        git_root(root)
        first = workflow_config.resolve(root=root, feature="frozen-route", slice_count=1, native_provider="codex")
        assert first["roles"]["implementer"]["agent_file"] == ".codex/agents/implementer.md"
        preferred.write_text(fallback.read_text(encoding="utf-8"), encoding="utf-8")
        resumed = workflow_config.resolve(root=root, feature="frozen-route", slice_count=8, native_provider="cursor")
        assert resumed == first
    finally:
        shutil.rmtree(root)


def test_invalid_frozen_agent_paths_exit_two_without_snapshot_mutation() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        workflow_config.resolve(root=root, feature="invalid-frozen-path", slice_count=1, native_provider="codex")
        snapshot_path = root / ".specs/features/invalid-frozen-path/workflow.json"
        original = snapshot_path.read_bytes()
        resolver = Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts/workflow_config.py"
        cases = (".codex/agents/verifier.toml", ".codex/agents/missing.toml")
        for invalid_path in cases:
            snapshot = json.loads(original)
            snapshot["roles"]["implementer"]["agent_file"] = invalid_path
            snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            before = snapshot_path.read_bytes()
            result = subprocess.run(
                [sys.executable, str(resolver), "--root", str(root), "--feature", "invalid-frozen-path", "--slices", "1", "--native-provider", "codex"],
                text=True, capture_output=True, check=False,
            )
            assert result.returncode == 2
            assert result.stdout == ""
            assert result.stderr.startswith("workflow-config:")
            assert snapshot_path.read_bytes() == before
    finally:
        shutil.rmtree(root)


def test_distinct_checkouts_sync_only_their_local_configuration() -> None:
    roots = [make_packet_root(), make_packet_root()]
    try:
        for index, root in enumerate(roots, start=1):
            models = {provider: {role: dict(setting) for role, setting in values.items()} for provider, values in MODELS.items()}
            models["codex"]["implementer"]["model"] = f"checkout-{index}"
            write_config(root, models=models)
            workflow_config.sync_agents(root)
        assert workflow_config.packet_setting("codex", (roots[0] / ".codex/agents/implementer.toml").read_text(), Path(".codex/agents/implementer.toml"))["model"] == "checkout-1"
        assert workflow_config.packet_setting("codex", (roots[1] / ".codex/agents/implementer.toml").read_text(), Path(".codex/agents/implementer.toml"))["model"] == "checkout-2"
    finally:
        for root in roots:
            shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
