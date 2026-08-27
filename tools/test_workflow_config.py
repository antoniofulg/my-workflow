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


ROOT = Path(__file__).resolve().parent.parent


MODELS = {
    provider: {
        role: {"model": f"{provider}-{role}", "effort": "high"}
        for role in workflow_config.ROLES
    }
    for provider in workflow_config.PROVIDERS
}


def write_config(
    root: Path,
    *,
    models: dict | None = None,
    cadence: str = "grouped.3",
    extra: str = "",
    filename: str = ".my-workflow.toml",
) -> None:
    lines = ["version = 2", "", "[deep_review]", f'cadence = "{cadence}"', ""]
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
    (root / filename).write_text("\n".join(lines) + extra, encoding="utf-8")


def make_root() -> Path:
    return Path(tempfile.mkdtemp())


def write_packets(root: Path, *, runtime: bool = True) -> None:
    packets = {
        "claude": "---\nname: {role}\nmodel: old-model\neffort: low\ntools: Read\n---\nInstructions for {role}.\n",
        "cursor": "---\nname: {role}\nmodel: old-model[effort=low]\nis_background: true\n---\nInstructions for {role}.\n",
        "codex": 'name = "{role}"\nmodel = "old-model"\nmodel_reasoning_effort = "low"\nsandbox_mode = "read-only"\n\ndeveloper_instructions = "Instructions for {role}."\n',
    }
    for provider, template in packets.items():
        extension = "toml" if provider == "codex" else "md"
        for role in workflow_config.ROLES:
            agent_name = workflow_config.AGENT_NAMES.get(role, role)
            content = template.format(role=agent_name).encode("utf-8")
            template_path = root / "templates" / "agents" / provider / f"{agent_name}.{extension}"
            template_path.parent.mkdir(parents=True, exist_ok=True)
            template_path.write_bytes(content)
            if runtime:
                runtime_path = root / f".{provider}" / "agents" / f"{agent_name}.{extension}"
                runtime_path.parent.mkdir(parents=True, exist_ok=True)
                runtime_path.write_bytes(content)


def make_packet_root() -> Path:
    root = make_root()
    write_config(root)
    write_packets(root)
    return root


def make_repo() -> Path:
    root = make_packet_root()
    workflow_config.sync_agents(root)
    git_root(root)
    return root


def write_parallelization(root: Path, content: str, *, encoding: str = "utf-8") -> None:
    write_config(root, extra="\n" + content)


def write_tasks(root: Path, content: str, feature: str = "fixture") -> Path:
    path = root / ".specs" / "features" / feature / "tasks.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def task_contract(*rows: str, feature_count: int = 1) -> str:
    closures = [
        "| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |",
        "| --- | --- | --- | --- | --- |",
    ]
    for index in range(feature_count):
        slice_id = chr(ord("A") + index)
        closures.append(
            f"| {slice_id} | Capability {slice_id} works alone. | `python3 -m unittest` | yes | Independent value. |"
        )
    return "\n".join(
        [
            "# Fixture tasks",
            "",
            "## Vertical Slice Closure",
            "",
            *closures,
            "",
            "## Task Breakdown",
            "",
            *rows,
            "",
        ]
    )


def task_row(task_id: str, slice_id: str, depends_on: str = "None") -> str:
    return "\n".join(
        [
            f"### {task_id}: Fixture task",
            "",
            f"**Slice:** {slice_id}",
            f"**Depends on:** {depends_on}",
            f"**Where:** src/{task_id.lower()}.py",
            "**Tests:** unit",
            "**Gate:** quick",
            "",
        ]
    )


def frozen_snapshot(snapshot: dict) -> dict:
    return {key: value for key, value in snapshot.items() if key != "remediation"}


def make_provider(root: Path, relative: str = "tools/workflow_resources", *, executable: bool = True) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    if executable:
        path.chmod(0o755)
    return path


def test_defaults_and_native_routing() -> None:
    root = make_repo()
    try:
        rows = "".join(
            task_row(f"T{task_number}", chr(ord("A") + task_number - 1))
            for task_number in range(1, 5)
        )
        write_tasks(root, task_contract(rows, feature_count=4), "default")
        snapshot = workflow_config.resolve(
            root=root, feature="default", slice_count=4, native_provider="codex"
        )
        assert snapshot["parallelization"] == {"mode": "disabled", "resource_provider": None}
        assert snapshot["deep_review"] == {"cadence": "grouped.3", "groups": [[1, 2], [3, 4]]}
        assert all(value["provider"] == "codex" for value in snapshot["roles"].values())
        assert snapshot["roles"]["verifier"]["agent_file"] == ".codex/agents/verifier.toml"
    finally:
        shutil.rmtree(root)


def test_initial_resolution_derives_one_slice_from_tasks() -> None:
    root = make_repo()
    try:
        fixture = ROOT / "tools/fixtures/tlc-validator/merge-alone-one-slice.md"
        write_tasks(root, fixture.read_text(encoding="utf-8"))
        snapshot = workflow_config.resolve(root=root, feature="fixture", native_provider="codex")
        assert snapshot["deep_review"]["groups"] == [[1]]
    finally:
        shutil.rmtree(root)


def test_initial_resolution_derives_two_independent_slices_from_tasks() -> None:
    root = make_repo()
    try:
        write_tasks(root, task_contract(task_row("T1", "A") + task_row("T2", "B"), feature_count=2))
        snapshot = workflow_config.resolve(root=root, feature="fixture", native_provider="codex")
        assert snapshot["deep_review"]["groups"] == [[1, 2]]
    finally:
        shutil.rmtree(root)


def test_slice_assertion_mismatch_fails_before_snapshot_write() -> None:
    root = make_repo()
    try:
        write_tasks(root, task_contract(task_row("T1", "A")))
        try:
            workflow_config.resolve(root=root, feature="fixture", slice_count=2, native_provider="codex")
        except workflow_config.ConfigError as exc:
            assert "does not match derived slice count 1" in str(exc)
        else:
            raise AssertionError("expected slice assertion mismatch")
        assert not (root / ".specs/features/fixture/workflow.json").exists()
    finally:
        shutil.rmtree(root)


def test_non_positive_slice_assertions_fail_before_snapshot_write() -> None:
    for supplied in (0, -1):
        root = make_repo()
        try:
            write_tasks(root, task_contract(task_row("T1", "A")))
            try:
                workflow_config.resolve(
                    root=root,
                    feature="fixture",
                    slice_count=supplied,
                    native_provider="codex",
                )
            except workflow_config.ConfigError as exc:
                assert "slice count must be at least 1" in str(exc)
            else:
                raise AssertionError(f"expected non-positive slice assertion rejection: {supplied}")
            assert not (root / ".specs/features/fixture/workflow.json").exists()
        finally:
            shutil.rmtree(root)


def test_refresh_slice_assertion_mismatch_preserves_snapshot_bytes() -> None:
    root = make_repo()
    try:
        write_tasks(root, task_contract(task_row("T1", "A")))
        workflow_config.resolve(root=root, feature="fixture", native_provider="codex")
        snapshot_path = root / ".specs/features/fixture/workflow.json"
        before = snapshot_path.read_bytes()
        write_tasks(
            root,
            task_contract(task_row("T1", "A") + task_row("T2", "B"), feature_count=2),
        )
        try:
            workflow_config.resolve(
                root=root,
                feature="fixture",
                slice_count=1,
                native_provider="codex",
                refresh=True,
            )
        except workflow_config.ConfigError as exc:
            assert "does not match derived slice count 2" in str(exc)
        else:
            raise AssertionError("expected refresh slice assertion mismatch")
        assert snapshot_path.read_bytes() == before
    finally:
        shutil.rmtree(root)


def test_malformed_refresh_preserves_snapshot_bytes() -> None:
    root = make_repo()
    try:
        write_tasks(root, task_contract(task_row("T1", "A")))
        workflow_config.resolve(root=root, feature="fixture", native_provider="codex")
        snapshot_path = root / ".specs/features/fixture/workflow.json"
        before = snapshot_path.read_bytes()
        write_tasks(root, task_row("T1", "A"))
        try:
            workflow_config.resolve(
                root=root,
                feature="fixture",
                native_provider="codex",
                refresh=True,
            )
        except workflow_config.ConfigError as exc:
            assert "tasks closure validation failed" in str(exc)
            assert "Vertical Slice Closure" in str(exc)
        else:
            raise AssertionError("expected malformed refresh failure")
        assert snapshot_path.read_bytes() == before
    finally:
        shutil.rmtree(root)


def test_missing_tasks_defaults_to_one_slice_without_manual_count() -> None:
    root = make_repo()
    try:
        snapshot = workflow_config.resolve(root=root, feature="no-tasks", native_provider="codex")
        assert snapshot["deep_review"]["groups"] == [[1]]
    finally:
        shutil.rmtree(root)


def test_malformed_tasks_fails_before_snapshot_write() -> None:
    root = make_repo()
    try:
        write_tasks(root, task_row("T1", "A"))
        try:
            workflow_config.resolve(root=root, feature="fixture", native_provider="codex")
        except workflow_config.ConfigError as exc:
            assert "tasks closure validation failed" in str(exc)
            assert "Vertical Slice Closure" in str(exc)
        else:
            raise AssertionError("expected malformed tasks failure")
        assert not (root / ".specs/features/fixture/workflow.json").exists()
    finally:
        shutil.rmtree(root)


def test_resume_returns_frozen_snapshot_without_reading_changed_tasks() -> None:
    for current_tasks in (
        task_contract(task_row("T1", "A") + task_row("T2", "B"), feature_count=2),
        task_row("T1", "A"),
    ):
        root = make_repo()
        try:
            write_tasks(root, task_contract(task_row("T1", "A")), "frozen")
            first = workflow_config.resolve(root=root, feature="frozen", native_provider="codex")
            snapshot_path = root / ".specs/features/frozen/workflow.json"
            before = snapshot_path.read_bytes()
            write_tasks(root, current_tasks, "frozen")
            resumed = workflow_config.resolve(
                root=root, feature="frozen", slice_count=8, native_provider="cursor"
            )
            assert resumed == first
            assert snapshot_path.read_bytes() == before
        finally:
            shutil.rmtree(root)


def test_refresh_rederives_current_slices_without_changing_snapshot_schema() -> None:
    root = make_repo()
    try:
        write_tasks(root, task_contract(task_row("T1", "A")), "refreshable")
        first = workflow_config.resolve(root=root, feature="refreshable", native_provider="codex")
        write_tasks(
            root,
            task_contract(task_row("T1", "A") + task_row("T2", "B"), feature_count=2),
            "refreshable",
        )
        refreshed = workflow_config.resolve(root=root, feature="refreshable", native_provider="codex", refresh=True)
        assert refreshed["deep_review"]["groups"] == [[1, 2]]
        persisted = json.loads(
            (root / ".specs/features/refreshable/workflow.json").read_text(encoding="utf-8")
        )
        assert set(persisted) == set(frozen_snapshot(first))
        assert persisted["version"] == 2
        assert persisted["deep_review"]["groups"] == [[1, 2]]
    finally:
        shutil.rmtree(root)


def test_parallelization_accepts_supported_modes() -> None:
    root = make_repo()
    try:
        resolver = ROOT / ".agents/skills/workflow-config/scripts/workflow_config.py"
        for mode in ("disabled", "safe", "full"):
            write_parallelization(root,
                f"[parallelization]\nmode = '{mode}'\n", encoding="utf-8"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(resolver),
                    "--root",
                    str(root),
                    "--feature",
                    f"mode-{mode}",
                    "--slices",
                    "1",
                    "--native-provider",
                    "codex",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            assert result.returncode == 0
            payload = json.loads(result.stdout)
            assert payload["parallelization"] == {"mode": mode, "resource_provider": None}
            snapshot = json.loads(
                (root / f".specs/features/mode-{mode}/workflow.json").read_text(encoding="utf-8")
            )
            assert snapshot["parallelization"] == {"mode": mode, "resource_provider": None}
    finally:
        shutil.rmtree(root)


def test_parallelization_rejects_invalid_mode_without_replacing_snapshot() -> None:
    root = make_repo()
    try:
        first = workflow_config.resolve(
            root=root, feature="invalid-mode", slice_count=1, native_provider="codex"
        )
        path = root / ".specs/features/invalid-mode/workflow.json"
        original = path.read_bytes()
        write_parallelization(root,
            "[parallelization]\nmode = 'speculative'\n", encoding="utf-8"
        )
        try:
            workflow_config.resolve(
                root=root,
                feature="invalid-mode",
                slice_count=1,
                native_provider="codex",
                refresh=True,
            )
        except workflow_config.ConfigError as exc:
            assert "parallelization.mode" in str(exc)
        else:
            raise AssertionError("expected invalid parallelization mode")
        assert path.read_bytes() == original
        assert json.loads(path.read_text(encoding="utf-8")) == frozen_snapshot(first)
    finally:
        shutil.rmtree(root)


def test_parallelization_resume_uses_frozen_mode_after_config_changes() -> None:
    root = make_repo()
    try:
        write_parallelization(root,
            "[parallelization]\nmode = 'full'\n", encoding="utf-8"
        )
        first = workflow_config.resolve(
            root=root, feature="frozen-mode", slice_count=1, native_provider="codex"
        )
        write_parallelization(root,
            "[parallelization]\nmode = 'disabled'\n", encoding="utf-8"
        )
        resumed = workflow_config.resolve(
            root=root, feature="frozen-mode", slice_count=8, native_provider="cursor"
        )
        assert resumed == first
        assert resumed["parallelization"] == {"mode": "full", "resource_provider": None}
    finally:
        shutil.rmtree(root)


def test_resource_provider_freezes_normalized_repository_relative_executable() -> None:
    root = make_repo()
    try:
        make_provider(root)
        write_parallelization(root,
            "[parallelization]\nmode = 'full'\nresource_provider = 'tools/workflow_resources'\n",
            encoding="utf-8",
        )
        snapshot = workflow_config.resolve(root=root, feature="provider", slice_count=1, native_provider="codex")
        assert snapshot["parallelization"] == {"mode": "full", "resource_provider": "tools/workflow_resources"}
        on_disk = json.loads((root / ".specs/features/provider/workflow.json").read_text(encoding="utf-8"))
        assert on_disk["parallelization"] == snapshot["parallelization"]
    finally:
        shutil.rmtree(root)


def test_resource_provider_rejects_unsafe_inputs_without_replacing_valid_snapshot() -> None:
    root = make_repo()
    try:
        make_provider(root)
        write_parallelization(root,
            "[parallelization]\nresource_provider = 'tools/workflow_resources'\n", encoding="utf-8"
        )
        first = workflow_config.resolve(root=root, feature="provider-invalid", slice_count=1, native_provider="codex")
        path = root / ".specs/features/provider-invalid/workflow.json"
        original = path.read_bytes()
        outside = Path(tempfile.mkdtemp())
        try:
            cases = ("/tmp/provider", "../provider", "tools", "tools/missing")
            for value in cases:
                write_parallelization(root,
                    f"[parallelization]\nresource_provider = {value!r}\n", encoding="utf-8"
                )
                try:
                    workflow_config.resolve(root=root, feature="provider-invalid", slice_count=1, native_provider="codex", refresh=True)
                except workflow_config.ConfigError as exc:
                    assert "resource_provider" in str(exc)
                else:
                    raise AssertionError(f"expected provider rejection: {value}")
                assert path.read_bytes() == original

            non_executable = make_provider(root, "tools/not-executable", executable=False)
            write_parallelization(root,
                "[parallelization]\nresource_provider = 'tools/not-executable'\n", encoding="utf-8"
            )
            try:
                workflow_config.resolve(root=root, feature="provider-invalid", slice_count=1, native_provider="codex", refresh=True)
            except workflow_config.ConfigError as exc:
                assert "resource_provider" in str(exc)
            else:
                raise AssertionError("expected non-executable provider rejection")
            assert path.read_bytes() == original

            outside_provider = outside / "provider"
            outside_provider.write_text("#!/bin/sh\n", encoding="utf-8")
            outside_provider.chmod(0o755)
            symlink = root / "tools/symlink-provider"
            symlink.symlink_to(outside_provider)
            write_parallelization(root,
                "[parallelization]\nresource_provider = 'tools/symlink-provider'\n", encoding="utf-8"
            )
            try:
                workflow_config.resolve(root=root, feature="provider-invalid", slice_count=1, native_provider="codex", refresh=True)
            except workflow_config.ConfigError as exc:
                assert "resource_provider" in str(exc)
            else:
                raise AssertionError("expected symlink provider rejection")
            assert path.read_bytes() == original
            assert json.loads(path.read_text(encoding="utf-8")) == frozen_snapshot(first)
        finally:
            shutil.rmtree(outside)
    finally:
        shutil.rmtree(root)


def test_resource_provider_resume_uses_frozen_path_after_config_changes() -> None:
    root = make_repo()
    try:
        make_provider(root, "tools/frozen-provider")
        write_parallelization(root,
            "[parallelization]\nmode = 'full'\nresource_provider = 'tools/frozen-provider'\n", encoding="utf-8"
        )
        first = workflow_config.resolve(root=root, feature="frozen-provider", slice_count=1, native_provider="codex")
        make_provider(root, "tools/new-provider")
        write_parallelization(root,
            "[parallelization]\nmode = 'disabled'\nresource_provider = 'tools/new-provider'\n", encoding="utf-8"
        )
        resumed = workflow_config.resolve(root=root, feature="frozen-provider", slice_count=8, native_provider="cursor")
        assert resumed == first
        assert resumed["parallelization"]["resource_provider"] == "tools/frozen-provider"
    finally:
        shutil.rmtree(root)


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


def template_paths(root: Path) -> list[Path]:
    return [
        root / workflow_config._template_relative(provider, role)
        for provider in workflow_config.PROVIDERS
        for role in workflow_config.ROLES
    ]


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(packet_paths(root)):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def path_state(path: Path) -> tuple[str, str | bytes | None]:
    if path.is_symlink():
        return ("symlink", str(path.readlink()))
    if path.is_file():
        return ("file", path.read_bytes())
    if path.is_dir():
        return ("directory", None)
    return ("missing", None)


def runtime_state(root: Path) -> dict[Path, tuple[str, str | bytes | None]]:
    relatives = {
        Path(f".{provider}")
        for provider in workflow_config.PROVIDERS
    } | {
        Path(f".{provider}/agents")
        for provider in workflow_config.PROVIDERS
    }
    relatives.update(
        workflow_config._runtime_relative(provider, role)
        for provider in workflow_config.PROVIDERS
        for role in workflow_config.ROLES
    )
    return {relative: path_state(root / relative) for relative in sorted(relatives)}


def tree_state(root: Path) -> dict[Path, tuple[str, str | bytes | None]]:
    state: dict[Path, tuple[str, str | bytes | None]] = {}
    for path in sorted(root.rglob("*")):
        state[path.relative_to(root)] = path_state(path)
    return state


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


def test_sync_initializes_local_config_and_generates_fifteen_runtime_packets() -> None:
    root = make_root()
    try:
        write_config(root, filename=".my-workflow.toml.example")
        write_packets(root, runtime=False)
        example = (root / ".my-workflow.toml.example").read_bytes()
        templates_before = {path: path.read_bytes() for path in template_paths(root)}
        result = workflow_config.sync_agents(root)
        assert (root / ".my-workflow.toml").read_bytes() == example
        assert len(result["changed"]) == 15
        assert result["unchanged"] == []
        assert {path: path.read_bytes() for path in template_paths(root)} == templates_before
        assert len(packet_paths(root)) == 15
    finally:
        shutil.rmtree(root)


def test_sync_preflights_early_and_late_runtime_collisions_before_local_init() -> None:
    cases = (
        ("early", Path(".claude/agents/planner.md"), "destination"),
        ("late", Path(".cursor/agents/deep-reviewer.md"), "destination"),
        ("parent", Path(".codex/agents"), "parent"),
    )
    for _, collision, kind in cases:
        root = make_root()
        try:
            write_config(root, filename=".my-workflow.toml.example")
            write_packets(root)
            runtime_relatives = [
                workflow_config._runtime_relative(provider, role)
                for provider in workflow_config.PROVIDERS
                for role in workflow_config.ROLES
            ]

            def state() -> dict[Path, tuple[str, bytes | None]]:
                result: dict[Path, tuple[str, bytes | None]] = {}
                for relative in runtime_relatives:
                    path = root / relative
                    if path.is_file():
                        result[relative] = ("file", path.read_bytes())
                    elif path.is_dir():
                        result[relative] = ("directory", None)
                    else:
                        result[relative] = ("missing", None)
                return result

            if kind == "destination":
                target = root / collision
                target.unlink()
                target.mkdir()
            else:
                target = root / collision
                shutil.rmtree(target)
                target.write_bytes(b"parent collision\n")
            before = state()
            try:
                workflow_config.sync_agents(root)
            except workflow_config.ConfigError as exc:
                expected = (
                    f"workflow-config: runtime destination {collision.as_posix()} must be a file"
                    if kind == "destination"
                    else f"workflow-config: runtime parent {collision.as_posix()} must be a directory"
                )
                assert str(exc) == expected
            else:
                raise AssertionError(f"expected {kind} collision rejection")
            assert not (root / ".my-workflow.toml").exists()
            assert state() == before
        finally:
            shutil.rmtree(root)


def test_sync_rejects_symlinked_runtime_paths_before_local_init() -> None:
    cases = (
        ("claude parent", Path(".claude"), "runtime parent .claude must not be a symlink"),
        ("agents parent", Path(".codex/agents"), "runtime parent .codex/agents must not be a symlink"),
        (
            "packet destination",
            Path(".cursor/agents/deep-reviewer.md"),
            "runtime destination .cursor/agents/deep-reviewer.md must not be a symlink",
        ),
        (
            "dangling packet destination",
            Path(".codex/agents/planner.toml"),
            "runtime destination .codex/agents/planner.toml must not be a symlink",
        ),
    )
    resolver = Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts/workflow_config.py"
    for name, collision, message in cases:
        root = make_packet_root()
        outside = Path(tempfile.mkdtemp())
        try:
            config = root / ".my-workflow.toml"
            (root / ".my-workflow.toml.example").write_bytes(config.read_bytes())
            (root / ".my-workflow.toml").unlink()
            if collision in (Path(".claude"), Path(".codex/agents")):
                shutil.rmtree(root / collision)
                target = outside / collision.name
                target.mkdir(parents=True)
                (target / "sentinel.txt").write_bytes(b"outside sentinel")
                (root / collision).symlink_to(target, target_is_directory=True)
            else:
                target = outside / "packet.toml"
                if name != "dangling packet destination":
                    target.write_bytes(b"outside packet")
                (root / collision).unlink()
                (root / collision).symlink_to(target)
            before_runtime = runtime_state(root)
            before_outside = tree_state(outside)
            result = subprocess.run(
                [sys.executable, str(resolver), "--root", str(root), "--sync-agents"],
                text=True,
                capture_output=True,
                check=False,
            )
            assert result.returncode == 2, name
            assert result.stdout == "", name
            assert result.stderr == f"workflow-config: {message}\n", name
            assert not (root / ".my-workflow.toml").exists(), name
            assert runtime_state(root) == before_runtime, name
            assert tree_state(outside) == before_outside, name
        finally:
            shutil.rmtree(root)
            shutil.rmtree(outside)


def test_sync_rejects_symlinked_local_sources_before_any_write() -> None:
    cases = (
        ("local config", Path(".my-workflow.toml"), "local config path .my-workflow.toml must not be a symlink"),
        ("config example", Path(".my-workflow.toml.example"), "config example path .my-workflow.toml.example must not be a symlink"),
        (
            "agent template",
            Path("templates/agents/claude/planner.md"),
            "agent template path templates/agents/claude/planner.md must not be a symlink",
        ),
    )
    resolver = Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts/workflow_config.py"
    for name, source, message in cases:
        root = make_packet_root()
        outside = Path(tempfile.mkdtemp())
        try:
            if source.name == ".my-workflow.toml":
                target = outside / source.name
                target.write_bytes((root / source).read_bytes())
                (root / source).unlink()
                (root / source).symlink_to(target)
            else:
                example = root / ".my-workflow.toml"
                if source.name == ".my-workflow.toml.example":
                    target = outside / source.name
                    target.write_bytes(example.read_bytes())
                    example.unlink()
                    (root / source).symlink_to(target)
                else:
                    config = root / ".my-workflow.toml"
                    (root / ".my-workflow.toml.example").write_bytes(config.read_bytes())
                    config.unlink()
                    target = outside / source.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((root / source).read_bytes())
                    (root / source).unlink()
                    (root / source).symlink_to(target)
            before_runtime = runtime_state(root)
            before_outside = tree_state(outside)
            config_before = path_state(root / ".my-workflow.toml")
            result = subprocess.run(
                [sys.executable, str(resolver), "--root", str(root), "--sync-agents"],
                text=True,
                capture_output=True,
                check=False,
            )
            assert result.returncode == 2, name
            assert result.stdout == "", name
            assert result.stderr == f"workflow-config: {message}\n", name
            assert path_state(root / ".my-workflow.toml") == config_before, name
            assert runtime_state(root) == before_runtime, name
            assert tree_state(outside) == before_outside, name
        finally:
            shutil.rmtree(root)
            shutil.rmtree(outside)


def test_sync_rejects_symlinked_root_before_any_external_write() -> None:
    resolver = Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts/workflow_config.py"

    target = make_root()
    link_parent = Path(tempfile.mkdtemp())
    try:
        write_config(target, filename=".my-workflow.toml.example")
        write_packets(target, runtime=False)
        (target / "sentinel.txt").write_bytes(b"external sentinel")
        linked_root = link_parent / "linked-checkout"
        linked_root.symlink_to(target, target_is_directory=True)
        before_target = tree_state(target)
        before_runtime = runtime_state(target)
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(linked_root), "--sync-agents"],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 2
        assert result.stdout == ""
        assert result.stderr == f"workflow-config: root {linked_root.absolute()} must not be a symlink\n"
        assert not (target / ".my-workflow.toml").exists()
        assert runtime_state(target) == before_runtime
        assert tree_state(target) == before_target
    finally:
        shutil.rmtree(target)
        shutil.rmtree(link_parent)

    dangling_parent = Path(tempfile.mkdtemp())
    try:
        dangling_root = dangling_parent / "dangling-checkout"
        missing_target = dangling_parent / "missing-target"
        dangling_root.symlink_to(missing_target, target_is_directory=True)
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(dangling_root), "--sync-agents"],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 2
        assert result.stdout == ""
        assert result.stderr == f"workflow-config: root {dangling_root.absolute()} must not be a symlink\n"
        assert not missing_target.exists()
        assert list(dangling_parent.iterdir()) == [dangling_root]
    finally:
        shutil.rmtree(dangling_parent)


def test_sync_rebuilds_runtime_from_immutable_templates() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        template = root / "templates/agents/claude/planner.md"
        template_before = template.read_bytes()
        runtime = root / ".claude/agents/planner.md"
        runtime.write_bytes(runtime.read_bytes().replace(b"Instructions for planner.", b"Disposable runtime edit."))
        result = workflow_config.sync_agents(root)
        assert ".claude/agents/planner.md" in result["changed"]
        expected = workflow_config.render_agent_packet(
            "claude", template_before, MODELS["claude"]["planner"], Path("templates/agents/claude/planner.md")
        )
        assert runtime.read_bytes() == expected
        assert template.read_bytes() == template_before
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
        target = root / "templates/agents/cursor/verifier.md"
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
        duplicate = root / "templates/agents/claude/verifier.md"
        duplicate.write_text(
            duplicate.read_text(encoding="utf-8").replace(
                "model: old-model\n", "model: old-model\nmodel: duplicate\n", 1
            ),
            encoding="utf-8",
        )
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


def test_cli_rejects_non_roundtrip_model_identifier_before_writes() -> None:
    root = make_packet_root()
    try:
        before = {path: path.read_bytes() for path in packet_paths(root)}
        config = root / ".my-workflow.toml"
        config.write_text(config.read_text(encoding="utf-8").replace('model = "claude-planner"', 'model = "claude planner"', 1), encoding="utf-8")
        resolver = Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts/workflow_config.py"
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--sync-agents"],
            text=True, capture_output=True, check=False,
        )
        assert result.returncode == 2
        assert result.stdout == ""
        assert "models.claude.planner.model must be a valid native model identifier" in result.stderr
        assert {path: path.read_bytes() for path in before} == before
    finally:
        shutil.rmtree(root)


def test_cli_rejects_codex_backslash_model_identifier_before_writes() -> None:
    root = make_packet_root()
    try:
        before = {path: path.read_bytes() for path in packet_paths(root)}
        config = root / ".my-workflow.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'model = "codex-planner"', 'model = "foo\\\\bar"', 1
            ),
            encoding="utf-8",
        )
        resolver = Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts/workflow_config.py"
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--sync-agents"],
            text=True, capture_output=True, check=False,
        )
        assert result.returncode == 2
        assert result.stdout == ""
        assert "models.codex.planner.model must be a valid native model identifier" in result.stderr
        assert {path: path.read_bytes() for path in before} == before
    finally:
        shutil.rmtree(root)


def test_sync_requires_native_header_metadata_for_every_provider() -> None:
    for provider in workflow_config.PROVIDERS:
        for duplicate in (False, True):
            root = make_packet_root()
            try:
                role = "planner"
                agent_name = workflow_config.AGENT_NAMES.get(role, role)
                extension = "toml" if provider == "codex" else "md"
                packet = root / "templates" / "agents" / provider / f"{agent_name}.{extension}"
                text = packet.read_text(encoding="utf-8")
                if provider == "claude":
                    if duplicate:
                        text = text.replace("model: old-model\n", "model: old-model\nmodel: duplicate\n", 1)
                    else:
                        text = text.replace("model: old-model\n", "", 1).replace("---\nInstructions", "---\nmodel: body-model\neffort: low\nInstructions", 1)
                elif provider == "cursor":
                    if duplicate:
                        text = text.replace("model: old-model[effort=low]\n", "model: old-model[effort=low]\nmodel: duplicate[effort=low]\n", 1)
                    else:
                        text = text.replace("model: old-model[effort=low]\n", "", 1).replace("---\nInstructions", "---\nmodel: body-model[effort=low]\nInstructions", 1)
                else:
                    if duplicate:
                        text = text.replace('model = "old-model"\n', 'model = "old-model"\nmodel = "duplicate"\n', 1)
                    else:
                        text = text.replace('model = "old-model"\n', "", 1) + 'model = "body-model"\n'
                packet.write_text(text, encoding="utf-8")
                before = {path: path.read_bytes() for path in packet_paths(root)}
                try:
                    workflow_config.sync_agents(root)
                except workflow_config.ConfigError as exc:
                    assert agent_name in str(exc)
                else:
                    raise AssertionError(f"expected native-header rejection: {provider}, duplicate={duplicate}")
                assert {path: path.read_bytes() for path in before} == before
            finally:
                shutil.rmtree(root)


def test_sync_preserves_crlf_packet_bytes_for_all_providers() -> None:
    root = make_packet_root()
    try:
        for path in template_paths(root):
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        before = {path: path.read_bytes() for path in template_paths(root)}
        workflow_config.sync_agents(root)
        for template, original in before.items():
            provider = template.parts[-2]
            runtime = root / workflow_config._runtime_relative(provider, template.stem)
            current = runtime.read_bytes()
            assert b"\r\n" in current
            assert b"\n" not in current.replace(b"\r\n", b"")
            assert strip_metadata(provider, original) == strip_metadata(provider, current)
    finally:
        shutil.rmtree(root)


def test_codex_ignores_model_like_lines_inside_multiline_toml_text() -> None:
    root = make_packet_root()
    try:
        packet = root / "templates/agents/codex/planner.toml"
        packet.write_bytes(
            (
                'name = "planner"\n'
                '# """ harmless comment\n'
                "# ''' harmless comment\n"
                'summary = "literal # \'\'\' marker with escaped quote: \\"quoted\\""\n'
                'summary_single = \'literal # """ marker\'\n'
                'description = """\n'
                'model = "body-model"\n'
                '"""\n'
                'model = "old\\u002dmodel" # model comment\n'
                'model_reasoning_effort = "low" # effort comment\n'
                'developer_instructions = "Instructions for planner."\n'
            ).replace("\n", "\r\n").encode("utf-8")
        )
        before = packet.read_bytes()
        description_before = before[before.index(b'description = """'):before.index(b'"""', before.index(b'description = """') + 20) + 3]
        workflow_config.sync_agents(root)
        after = (root / ".codex/agents/planner.toml").read_bytes()
        assert workflow_config.packet_setting("codex", after, Path(".codex/agents/planner.toml")) == {
            "model": "codex-planner", "effort": "high"
        }
        assert b'model = "body-model"\r\n' in after
        assert b'model = "codex-planner" # model comment\r\n' in after
        assert b'model_reasoning_effort = "high" # effort comment\r\n' in after
        assert description_before == after[after.index(b'description = """'):after.index(b'"""', after.index(b'description = """') + 20) + 3]
        assert b"\r\n" in after
        assert b"\n" not in after.replace(b"\r\n", b"")
    finally:
        shutil.rmtree(root)


def test_resolve_freezes_delegated_settings_and_omits_planner() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        rows = "".join(
            task_row(f"T{task_number}", chr(ord("A") + task_number - 1))
            for task_number in range(1, 3)
        )
        write_tasks(root, task_contract(rows, feature_count=2), "freeze")
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


def test_resolves_remediation_stall_attempts_without_snapshot_persistence() -> None:
    cases = (
        ("default", "", 3),
        ("positive", "\n[remediation]\nstall_attempts = 5\n", 5),
        ("unbounded", "\n[remediation]\nstall_attempts = 0\n", 0),
    )
    for feature, extra, expected in cases:
        root = make_packet_root()
        try:
            write_config(root, extra=extra)
            workflow_config.sync_agents(root)
            git_root(root)
            resolved = workflow_config.resolve(
                root=root, feature=feature, slice_count=1, native_provider="codex"
            )
            assert resolved["remediation"] == {"stall_attempts": expected}
            persisted = json.loads(
                (root / f".specs/features/{feature}/workflow.json").read_text(encoding="utf-8")
            )
            assert "remediation" not in persisted
        finally:
            shutil.rmtree(root)


def test_rejects_invalid_remediation_before_snapshot_write() -> None:
    cases = (
        ("string", "stall_attempts = '3'\n", "remediation.stall_attempts"),
        ("bool", "stall_attempts = true\n", "remediation.stall_attempts"),
        ("float", "stall_attempts = 3.0\n", "remediation.stall_attempts"),
        ("negative", "stall_attempts = -1\n", "remediation.stall_attempts"),
        ("unknown", "attempts = 3\n", "remediation contains unknown key 'attempts'"),
    )
    for feature, body, message in cases:
        root = make_packet_root()
        try:
            workflow_config.sync_agents(root)
            write_config(root, extra=f"\n[remediation]\n{body}")
            git_root(root)
            try:
                workflow_config.resolve(
                    root=root, feature=feature, slice_count=1, native_provider="codex"
                )
            except workflow_config.ConfigError as exc:
                assert message in str(exc)
            else:
                raise AssertionError(f"expected invalid remediation failure for {feature}")
            assert not (root / f".specs/features/{feature}/workflow.json").exists()
        finally:
            shutil.rmtree(root)


def test_resume_reads_current_remediation_threshold_without_unfreezing_route() -> None:
    root = make_packet_root()
    try:
        write_config(root, extra="\n[remediation]\nstall_attempts = 5\n")
        workflow_config.sync_agents(root)
        git_root(root)
        first = workflow_config.resolve(
            root=root, feature="live-threshold", slice_count=1, native_provider="codex"
        )
        snapshot_path = root / ".specs/features/live-threshold/workflow.json"
        persisted_before = snapshot_path.read_bytes()

        write_config(root, extra="\n[remediation]\nstall_attempts = 7\n")
        resumed = workflow_config.resolve(
            root=root, feature="live-threshold", slice_count=8, native_provider="cursor"
        )

        assert resumed["remediation"] == {"stall_attempts": 7}
        assert {key: resumed[key] for key in first if key != "remediation"} == {
            key: first[key] for key in first if key != "remediation"
        }
        assert snapshot_path.read_bytes() == persisted_before
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
        rows = "".join(
            task_row(f"T{task_number}", chr(ord("A") + task_number - 1))
            for task_number in range(1, 3)
        )
        write_tasks(root, task_contract(rows, feature_count=2), "atomic")
        first = workflow_config.resolve(root=root, feature="atomic", slice_count=2, native_provider="codex")
        path = root / ".specs/features/atomic/workflow.json"
        original = path.read_text(encoding="utf-8")
        real_replace = workflow_config.os.replace
        workflow_config.os.replace = lambda *_args: (_ for _ in ()).throw(OSError("injected"))
        try:
            try:
                workflow_config.resolve(root=root, feature="atomic", slice_count=2, native_provider="codex", refresh=True)
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
            [sys.executable, str(resolver), "--root", str(root), "--feature", "cli", "--slices", "1", "--native-provider", "codex", "--override", "verifier=claude"],
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


def test_cli_loads_configured_cadence_into_json_and_snapshot() -> None:
    root = make_packet_root()
    try:
        workflow_config.sync_agents(root)
        git_root(root)
        resolver = Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts/workflow_config.py"
        cases = (
            ("slice", 4, [[1], [2], [3], [4]], "", 3),
            ("feature", 4, [[1, 2, 3, 4]], "\n[remediation]\nstall_attempts = 5\n", 5),
            ("grouped.2", 6, [[1, 2], [3, 4], [5, 6]], "\n[remediation]\nstall_attempts = 0\n", 0),
            ("grouped.4", 8, [[1, 2, 3, 4], [5, 6, 7, 8]], "", 3),
        )
        for index, (cadence, slice_count, groups, remediation_extra, stall_attempts) in enumerate(cases):
            write_config(root, cadence=cadence, extra=remediation_extra)
            feature = f"configured-cadence-{index}"
            rows = "".join(
                task_row(f"T{task_number}", chr(ord("A") + task_number - 1))
                for task_number in range(1, slice_count + 1)
            )
            write_tasks(root, task_contract(rows, feature_count=slice_count), feature)
            result = subprocess.run(
                [sys.executable, str(resolver), "--root", str(root), "--feature", feature, "--slices", str(slice_count), "--native-provider", "codex"],
                text=True, capture_output=True, check=False,
            )
            assert result.returncode == 0
            assert result.stderr == ""
            expected = {"cadence": cadence, "groups": groups}
            payload = json.loads(result.stdout)
            assert payload["deep_review"] == expected
            assert payload["remediation"] == {"stall_attempts": stall_attempts}
            snapshot = json.loads((root / f".specs/features/{feature}/workflow.json").read_text(encoding="utf-8"))
            assert snapshot["deep_review"] == expected
            assert "remediation" not in snapshot

        feature = "configured-cadence-resume"
        write_config(root, cadence="grouped.2", extra="\n[remediation]\nstall_attempts = 5\n")
        resume_rows = "".join(
            task_row(f"T{task_number}", chr(ord("A") + task_number - 1))
            for task_number in range(1, 7)
        )
        write_tasks(root, task_contract(resume_rows, feature_count=6), feature)
        command = [
            sys.executable, str(resolver), "--root", str(root), "--feature", feature,
            "--slices", "6", "--native-provider", "codex",
        ]
        first_result = subprocess.run(command, text=True, capture_output=True, check=False)
        assert first_result.returncode == 0
        first_payload = json.loads(first_result.stdout)
        snapshot_path = root / f".specs/features/{feature}/workflow.json"
        snapshot_before = snapshot_path.read_bytes()
        write_config(root, cadence="slice", extra="\n[remediation]\nstall_attempts = 7\n")
        resumed_result = subprocess.run(
            [*command[:-3], "8", "--native-provider", "cursor"],
            text=True, capture_output=True, check=False,
        )
        assert resumed_result.returncode == 0
        resumed_payload = json.loads(resumed_result.stdout)
        assert resumed_payload["remediation"] == {"stall_attempts": 7}
        assert resumed_payload["deep_review"] == first_payload["deep_review"]
        assert "remediation" not in json.loads(snapshot_path.read_text(encoding="utf-8"))
        assert snapshot_path.read_bytes() == snapshot_before
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
            assert "missing generated agent file" in str(exc)
        else:
            raise AssertionError("expected missing agent failure")
    finally:
        shutil.rmtree(root)


def test_resolver_rejects_noncanonical_agent_extension_without_fallback() -> None:
    root = make_packet_root()
    try:
        preferred = root / ".codex/agents/implementer.toml"
        fallback = root / ".codex/agents/implementer.md"
        workflow_config.sync_agents(root)
        fallback.write_text(preferred.read_text(encoding="utf-8"), encoding="utf-8")
        preferred.unlink()
        git_root(root)
        try:
            workflow_config.resolve(root=root, feature="frozen-route", slice_count=1, native_provider="codex")
        except workflow_config.ConfigError as exc:
            assert "missing generated agent file" in str(exc)
        else:
            raise AssertionError("expected canonical runtime path failure")
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
        cases = (".codex/agents/verifier.toml", ".codex/agents/implementer.toml")
        for invalid_path in cases:
            if invalid_path.endswith("verifier.toml"):
                verifier_path = root / ".codex/agents/verifier.toml"
                verifier_path.write_text(
                    workflow_config.render_agent_packet(
                        "codex",
                        verifier_path.read_text(encoding="utf-8"),
                        {"model": "codex-implementer", "effort": "high"},
                        Path(".codex/agents/verifier.toml"),
                    ),
                    encoding="utf-8",
                )
            else:
                (root / invalid_path).unlink()
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
            if invalid_path.endswith("verifier.toml"):
                assert "role 'implementer' has an invalid agent_file" in result.stderr
            else:
                assert "role 'implementer' agent_file is missing" in result.stderr
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
