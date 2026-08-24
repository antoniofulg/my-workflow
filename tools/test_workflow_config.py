"""Unit contract for central workflow model configuration."""

from __future__ import annotations

import shutil
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


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
