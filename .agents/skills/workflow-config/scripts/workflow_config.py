#!/usr/bin/env python3
"""Resolve the consumer workflow configuration and freeze feature state."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.11 is the supported runtime.
    tomllib = None


ROLES = ("planner", "implementer", "verifier", "explorer", "deep_reviewer", "designer")
DELEGATED_ROLES = ("implementer", "verifier", "explorer", "deep_reviewer", "designer")
PROVIDERS = ("claude", "codex", "cursor")
AGENT_NAMES = {"deep_reviewer": "deep-reviewer"}
EFFORTS = ("low", "medium", "high", "xhigh", "max", "ultra")
CADENCE_DEFAULT = "grouped.3"
CADENCE_RE = re.compile(r"^grouped\.(\d+)$")
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
CONFIG_VERSION = 3
SNAPSHOT_VERSION = 3
PARALLELIZATION_DEFAULT = "assisted"
PARALLELIZATION_MODES = ("assisted", "disabled")
MAX_WORKERS_DEFAULT = "auto"
AUTOMATIC_BASELINE = 2
AUTOMATIC_CEILING = 4
CONFIG_KEYS = {"version", "deep_review", "parallelization", "profiles", "models", "remediation"}
DEEP_REVIEW_KEYS = {"cadence"}
PARALLELIZATION_KEYS = {"mode", "max_workers", "resource_provider"}
REMEDIATION_KEYS = {"stall_attempts"}
STALL_ATTEMPTS_DEFAULT = 3
MODEL_PROVIDERS = set(PROVIDERS)
MODEL_KEYS = {"model", "effort"}
MODEL_IDENTIFIER_RE = re.compile(r"^[^\\\s\[\]\"\x00-\x1f\x7f]+$")
FRONTMATTER_RE = re.compile(
    r"\A---(?P<open_newline>\r\n|\n)(?P<header>.*?)(?P<close_newline>\r\n|\n)---(?P<after_newline>\r\n|\n|\Z)",
    re.DOTALL,
)
CLAUDE_SKILLS_RE = re.compile(
    r"^skills:(?P<inline>[^\r\n]*)(?P<block>(?:(?:\r\n|\n)[ \t]*-[^\r\n]*)*)",
    re.MULTILINE,
)
CLAUDE_MODEL_RE = re.compile(
    r"^model:[ \t]*(?P<model>[^\r\n]+?)(?P<suffix>[ \t]*)(?P<newline>\r\n|\n|\Z)",
    re.MULTILINE,
)
CLAUDE_EFFORT_RE = re.compile(
    r"^effort:[ \t]*(?P<effort>[^\r\n]+?)(?P<suffix>[ \t]*)(?P<newline>\r\n|\n|\Z)",
    re.MULTILINE,
)
CODEX_ASSIGNMENT_RE = re.compile(
    r'(?P<prefix>^[ \t]*(?P<key>model|model_reasoning_effort)[ \t]*=[ \t]*")'
    r'(?P<raw>(?:\\.|[^"\\])*)(?P<closing>")'
    r'(?P<suffix>[ \t]*(?:#[^\r\n]*)?)(?P<newline>\r\n|\n|\Z)',
    re.MULTILINE,
)
CURSOR_MODEL_RE = re.compile(
    r"^model:[ \t]*(?P<model>[^\r\n\[]+)\[effort=(?P<effort>[^\]\r\n]+)\](?P<suffix>[ \t]*)(?P<newline>\r\n|\n|\Z)",
    re.MULTILINE,
)


class ConfigError(ValueError):
    """A user-correctable workflow configuration error."""


def _error(message: str) -> ConfigError:
    return ConfigError(f"workflow-config: {message}")


def balanced_groups(slice_count: int, cadence: str) -> list[list[int]]:
    """Return consecutive, balanced 1-based slice groups for a cadence."""
    if slice_count < 1:
        raise _error("slice count must be at least 1")
    if cadence == "slice":
        return [[index] for index in range(1, slice_count + 1)]
    if cadence == "feature":
        return [list(range(1, slice_count + 1))]

    match = CADENCE_RE.fullmatch(cadence)
    if not match:
        raise _error("cadence must be 'slice', 'feature', or 'grouped.N'")
    maximum = int(match.group(1))
    if maximum < 1:
        raise _error("grouped.N requires N to be at least 1")

    group_count = (slice_count + maximum - 1) // maximum
    base, remainder = divmod(slice_count, group_count)
    sizes = [base + (1 if index < remainder else 0) for index in range(group_count)]
    groups: list[list[int]] = []
    next_slice = 1
    for size in sizes:
        groups.append(list(range(next_slice, next_slice + size)))
        next_slice += size
    return groups


def _load_config(path: Path, label: str) -> dict[str, Any]:
    if tomllib is None:  # pragma: no cover
        raise _error(f"Python 3.11 or newer is required to parse {label}")
    try:
        with path.open("rb") as stream:
            config = tomllib.load(stream)
    except tomllib.TOMLDecodeError as exc:
        raise _error(f"invalid {label}: {exc}") from exc
    except FileNotFoundError as exc:
        raise _error(f"{label} is missing") from exc
    if not isinstance(config, dict):
        raise _error(f"{label} must contain a table")
    version = config.get("version")
    if type(version) is not int or version != CONFIG_VERSION:
        raise _error("version must be integer 3; refresh the project configuration")
    _validate_config_schema(config)
    return config


def _read_config(root: Path) -> dict[str, Any]:
    path = root / ".my-workflow.toml"
    if not path.exists():
        raise _error("version must be integer 3; refresh the project configuration; .my-workflow.toml is missing")
    return _load_config(path, ".my-workflow.toml")


def _cadence(config: dict[str, Any]) -> str:
    section = config.get("deep_review") or {}
    return section.get("cadence", CADENCE_DEFAULT)


def _resource_provider(root: Path, value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise _error("parallelization.resource_provider must be a non-empty path or null")
    raw = Path(value)
    if raw.is_absolute() or ".." in raw.parts:
        raise _error("parallelization.resource_provider must stay inside the repository")
    target = root.joinpath(*raw.parts)
    current = root
    for component in raw.parts:
        current /= component
        if current.is_symlink():
            raise _error("parallelization.resource_provider cannot use a symlink")
    resolved = target.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise _error("parallelization.resource_provider must stay inside the repository") from exc
    if not target.is_file():
        raise _error("parallelization.resource_provider must be an executable file")
    if not os.access(target, os.X_OK):
        raise _error("parallelization.resource_provider must be executable")
    return target.relative_to(root).as_posix()


def _parallelization(config: dict[str, Any], root: Path) -> dict[str, Any]:
    section = config.get("parallelization") or {}
    mode = section.get("mode", PARALLELIZATION_DEFAULT)
    max_workers = section.get("max_workers", MAX_WORKERS_DEFAULT)
    return {
        "mode": mode,
        "max_workers": max_workers,
        "automatic_baseline": AUTOMATIC_BASELINE,
        "automatic_ceiling": AUTOMATIC_CEILING,
        "resource_provider": _resource_provider(root, section.get("resource_provider")),
    }

def _stall_attempts(config: dict[str, Any]) -> int:
    section = config.get("remediation") or {}
    return section.get("stall_attempts", STALL_ATTEMPTS_DEFAULT)


def stall_attempts(root: Path) -> int:
    """Read the current remediation stall threshold from the consumer config."""
    return _stall_attempts(_read_config(root.resolve()))


def _profiles(config: dict[str, Any]) -> dict[str, dict[str, str]]:
    return config.get("profiles") or {}


def _validate_role_map(values: dict[str, Any], source: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for role, provider in values.items():
        if role not in DELEGATED_ROLES:
            raise _error(f"{source} contains invalid role {role!r}")
        if not isinstance(provider, str) or provider not in PROVIDERS:
            raise _error(f"{source} role {role!r} has invalid provider {provider!r}")
        result[role] = provider
    return result


def _validate_config_schema(config: dict[str, Any]) -> None:
    version = config.get("version")
    if type(version) is not int or version != CONFIG_VERSION:
        raise _error("version must be integer 3; refresh the project configuration")
    unknown = set(config) - CONFIG_KEYS
    if unknown:
        raise _error(f"contains unknown top-level key {sorted(unknown)[0]!r}")

    deep_review = config.get("deep_review", {})
    if deep_review is None:
        deep_review = {}
    if not isinstance(deep_review, dict):
        raise _error("deep_review must be a table")
    unknown = set(deep_review) - DEEP_REVIEW_KEYS
    if unknown:
        raise _error(f"deep_review contains unknown key {sorted(unknown)[0]!r}")
    cadence = deep_review.get("cadence", CADENCE_DEFAULT)
    if not isinstance(cadence, str):
        raise _error("deep_review.cadence must be a string")

    parallelization = config.get("parallelization", {})
    if parallelization is None:
        parallelization = {}
    if not isinstance(parallelization, dict):
        raise _error("parallelization must be a table")
    unknown = set(parallelization) - PARALLELIZATION_KEYS
    if unknown:
        raise _error(f"parallelization contains unknown key {sorted(unknown)[0]!r}")
    mode = parallelization.get("mode", PARALLELIZATION_DEFAULT)
    if not isinstance(mode, str) or mode not in PARALLELIZATION_MODES:
        raise _error("parallelization.mode must be 'assisted' or 'disabled'")
    max_workers = parallelization.get("max_workers", MAX_WORKERS_DEFAULT)
    if max_workers != MAX_WORKERS_DEFAULT and (type(max_workers) is not int or max_workers < 1):
        raise _error("parallelization.max_workers must be 'auto' or an integer of at least 1")

    remediation = config.get("remediation", {})
    if remediation is None:
        remediation = {}
    if not isinstance(remediation, dict):
        raise _error("remediation must be a table")
    unknown = set(remediation) - REMEDIATION_KEYS
    if unknown:
        raise _error(f"remediation contains unknown key {sorted(unknown)[0]!r}")
    stall_attempts = remediation.get("stall_attempts", STALL_ATTEMPTS_DEFAULT)
    if type(stall_attempts) is not int or stall_attempts < 0:
        raise _error("remediation.stall_attempts must be an integer of at least 0")

    profiles = config.get("profiles", {})
    if profiles is None:
        profiles = {}
    if not isinstance(profiles, dict):
        raise _error("profiles must be a table")
    for name, values in profiles.items():
        if not isinstance(name, str) or not isinstance(values, dict):
            raise _error(f"profile {name!r} must be a table")
        _validate_role_map(values, f"profile {name!r}")

    models = config.get("models")
    if not isinstance(models, dict):
        raise _error("models must be a table containing every provider")
    missing_providers = MODEL_PROVIDERS - set(models)
    if missing_providers:
        provider = sorted(missing_providers)[0]
        raise _error(f"models.{provider} is required")
    unknown_provider = set(models) - MODEL_PROVIDERS
    if unknown_provider:
        provider = sorted(unknown_provider)[0]
        raise _error(f"models contains unknown provider {provider!r}")
    for provider in PROVIDERS:
        provider_values = models[provider]
        if not isinstance(provider_values, dict):
            raise _error(f"models.{provider} must be a table")
        missing_roles = set(ROLES) - set(provider_values)
        if missing_roles:
            role = sorted(missing_roles)[0]
            raise _error(f"models.{provider}.{role} is required")
        unknown_roles = set(provider_values) - set(ROLES)
        if unknown_roles:
            role = sorted(unknown_roles)[0]
            raise _error(f"models.{provider} contains unknown role {role!r}")
        for role in ROLES:
            setting = provider_values[role]
            path = f"models.{provider}.{role}"
            if not isinstance(setting, dict):
                raise _error(f"{path} must be a table")
            unknown = set(setting) - MODEL_KEYS
            if unknown:
                raise _error(f"{path} contains unknown key {sorted(unknown)[0]!r}")
            if "model" not in setting:
                raise _error(f"{path}.model is required")
            model = setting["model"]
            if not isinstance(model, str) or not model.strip():
                raise _error(f"{path}.model must be a non-empty string")
            if not MODEL_IDENTIFIER_RE.fullmatch(model):
                raise _error(f"{path}.model must be a valid native model identifier")
            if "effort" not in setting:
                raise _error(f"{path}.effort is required")
            effort = setting["effort"]
            if not isinstance(effort, str) or effort not in EFFORTS:
                allowed = ", ".join(EFFORTS)
                raise _error(f"{path}.effort must be one of: {allowed}")
            if provider == "claude" and effort == "ultra":
                raise _error(f"{path}.effort 'ultra' is not supported by claude")


def _models(config: dict[str, Any]) -> dict[str, dict[str, dict[str, str]]]:
    return config["models"]


def model_setting(config: dict[str, Any], provider: str, role: str) -> dict[str, str]:
    """Return one validated provider-role model setting."""
    try:
        return _models(config)[provider][role]
    except KeyError as exc:  # pragma: no cover - callers load validated config.
        raise _error(f"models.{provider}.{role} is required") from exc


def _one_match(pattern: re.Pattern[str], content: str, path: Path, label: str) -> re.Match[str]:
    matches = list(pattern.finditer(content))
    if len(matches) != 1:
        raise _error(f"{path.as_posix()} must contain exactly one {label} metadata field")
    return matches[0]


def _header(provider: str, content: str, path: Path) -> tuple[str, int]:
    if provider in ("claude", "cursor"):
        match = FRONTMATTER_RE.match(content)
        if not match:
            raise _error(f"{path.as_posix()} must contain a native YAML frontmatter header")
        return match.group("header"), match.start("header")
    boundary = re.search(r"^developer_instructions[ \t]*=", content, re.MULTILINE)
    end = boundary.start() if boundary else len(content)
    return content[:end], 0


def _preload_skills(header: str) -> list[str]:
    """Skill names from a Claude `skills:` inline or block list."""
    match = CLAUDE_SKILLS_RE.search(header)
    if not match:
        return []
    inline = match.group("inline").strip().strip("[]")
    entries = inline.split(",") if inline else []
    entries += [line.strip().lstrip("-") for line in match.group("block").splitlines()]
    return [name for name in (entry.strip().strip("\"'") for entry in entries) if name]


def _coerce_content(content: str | bytes) -> tuple[str, bool]:
    if isinstance(content, bytes):
        return content.decode("utf-8"), True
    return content, False


def _toml_basic_value(value: str) -> str:
    """Escape a value for an existing TOML basic-string quote pair."""
    encoded = json.dumps(value, ensure_ascii=False)
    return encoded[1:-1]


def _toml_prefix_is_top_level(prefix: str) -> bool:
    if tomllib is None:  # pragma: no cover
        return False
    try:
        parsed = tomllib.loads(prefix + '\n__workflow_top_level_probe = ""\n')
    except tomllib.TOMLDecodeError:
        return False
    return parsed.get("__workflow_top_level_probe") == ""


def _codex_developer_boundary(content: str, path: Path) -> int:
    candidates = [
        match for match in re.finditer(r"^[ \t]*developer_instructions[ \t]*=", content, re.MULTILINE)
        if _toml_prefix_is_top_level(content[:match.start()])
    ]
    if len(candidates) != 1:
        raise _error(f"{path.as_posix()} must contain exactly one top-level developer_instructions assignment")
    return candidates[0].start()


def _codex_fields(content: str, path: Path) -> dict[str, list[tuple[int, int, re.Match[str], str]]]:
    if tomllib is None:  # pragma: no cover
        raise _error("Python 3.11 or newer is required to parse Codex agent packets")
    try:
        parsed = tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:
        raise _error(f"{path.as_posix()} contains invalid TOML: {exc}") from exc
    boundary = _codex_developer_boundary(content, path)
    fields: dict[str, list[tuple[int, int, re.Match[str], str]]] = {"model": [], "effort": []}
    prefix = content[:boundary]
    for match in CODEX_ASSIGNMENT_RE.finditer(prefix):
        if not _toml_prefix_is_top_level(prefix[:match.start()]):
            continue
        try:
            line_parsed = tomllib.loads(content[match.start():match.end()])
        except tomllib.TOMLDecodeError:
            continue
        key = match.group("key")
        if key in line_parsed:
            field = "model" if key == "model" else "effort"
            fields[field].append((match.start(), match.end(), match, line_parsed[key]))
    for field, key in (("model", "model"), ("effort", "model_reasoning_effort")):
        if len(fields[field]) != 1 or parsed.get(key) != fields[field][0][3]:
            fields[field] = []
    return fields


def _codex_field(
    fields: dict[str, list[tuple[int, int, re.Match[str], str]]], key: str, path: Path, label: str
) -> tuple[int, int, re.Match[str], str]:
    matches = fields[key]
    if len(matches) != 1:
        raise _error(f"{path.as_posix()} must contain exactly one {label} metadata field")
    return matches[0]


def packet_setting(provider: str, content: str | bytes, path: Path) -> dict[str, str]:
    """Parse the native model and effort metadata from one packet."""
    text, _ = _coerce_content(content)
    header, _ = _header(provider, text, path)
    if provider == "claude":
        model = _one_match(CLAUDE_MODEL_RE, header, path, "model").group("model").strip()
        effort = _one_match(CLAUDE_EFFORT_RE, header, path, "effort").group("effort").strip()
    elif provider == "codex":
        fields = _codex_fields(text, path)
        _, _, _, model = _codex_field(fields, "model", path, "model")
        _, _, _, effort = _codex_field(fields, "effort", path, "model_reasoning_effort")
    else:
        match = _one_match(CURSOR_MODEL_RE, header, path, "model/effort").groupdict()
        model, effort = match["model"].strip(), match["effort"].strip()
    if not MODEL_IDENTIFIER_RE.fullmatch(model):
        raise _error(f"{path.as_posix()} contains an invalid model identifier")
    return {"model": model, "effort": effort}


def render_agent_packet(
    provider: str, content: str | bytes, setting: dict[str, str], path: Path | None = None
) -> str | bytes:
    """Replace only provider-native model metadata in an agent packet."""
    packet_path = path or Path("agent packet")
    text, as_bytes = _coerce_content(content)
    header, header_offset = _header(provider, text, packet_path)
    if provider == "claude":
        model_pattern, effort_pattern = CLAUDE_MODEL_RE, CLAUDE_EFFORT_RE
    else:
        model_pattern, effort_pattern = CURSOR_MODEL_RE, None

    if provider == "codex":
        fields = _codex_fields(text, packet_path)
        model_start, model_end, model_match, _ = _codex_field(fields, "model", packet_path, "model")
        model_replacement = (
            text[model_start:model_match.start("raw")]
            + _toml_basic_value(setting["model"])
            + text[model_match.end("raw"):model_end]
        )
        rendered = text[:model_start] + model_replacement + text[model_end:]
        new_fields = _codex_fields(rendered, packet_path)
        effort_start, effort_end, new_effort_match, _ = _codex_field(new_fields, "effort", packet_path, "model_reasoning_effort")
        effort_replacement = (
            rendered[effort_start:new_effort_match.start("raw")]
            + _toml_basic_value(setting["effort"])
            + rendered[new_effort_match.end("raw"):effort_end]
        )
        rendered = rendered[:effort_start] + effort_replacement + rendered[effort_end:]
        return rendered.encode("utf-8") if as_bytes else rendered
    model_match = _one_match(model_pattern, header, packet_path, "model")
    if provider == "cursor":
        replacement = (
            f"model: {setting['model']}[effort={setting['effort']}]"
            f"{model_match.group('suffix')}{model_match.group('newline')}"
        )
        start = header_offset + model_match.start()
        end = header_offset + model_match.end()
        rendered = text[:start] + replacement + text[end:]
    else:
        effort_match = _one_match(effort_pattern, header, packet_path, "effort")
        model_value = f"model: {setting['model']}"
        model_replacement = model_value + model_match.group("suffix") + model_match.group("newline")
        start = header_offset + model_match.start()
        end = header_offset + model_match.end()
        rendered = text[:start] + model_replacement + text[end:]
        # Re-find the effort field after replacing the model so offsets remain valid.
        new_header, new_header_offset = _header(provider, rendered, packet_path)
        effort_match = _one_match(effort_pattern, new_header, packet_path, "effort")
        effort_value = (
            f"effort: {setting['effort']}" if provider == "claude"
            else f"effort: {setting['effort']}"
        )
        effort_replacement = effort_value + effort_match.group("suffix") + effort_match.group("newline")
        start = new_header_offset + effort_match.start()
        end = new_header_offset + effort_match.end()
        rendered = rendered[:start] + effort_replacement + rendered[end:]
    return rendered.encode("utf-8") if as_bytes else rendered


def _write_bytes_atomic(path: Path, content: bytes) -> None:
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = stream.name
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def _preflight_destination(root: Path, destination: Path, label: str) -> None:
    relative = destination.relative_to(root).as_posix()
    parent = destination.parent
    while parent != root:
        if parent.is_symlink():
            parent_relative = parent.relative_to(root).as_posix()
            raise _error(f"{label} parent {parent_relative} must not be a symlink")
        if parent.exists() and not parent.is_dir():
            parent_relative = parent.relative_to(root).as_posix()
            raise _error(f"{label} parent {parent_relative} must be a directory")
        parent = parent.parent
    if destination.is_symlink():
        raise _error(f"{label} destination {relative} must not be a symlink")
    if destination.exists() and not destination.is_file():
        raise _error(f"{label} destination {relative} must be a file")


def _preflight_path(root: Path, path: Path, label: str) -> None:
    relative = path.relative_to(root)
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            current_relative = current.relative_to(root).as_posix()
            relation = "path" if current == path else "parent"
            raise _error(f"{label} {relation} {current_relative} must not be a symlink")


def _sync_config(root: Path) -> tuple[dict[str, Any], bytes | None]:
    local = root / ".my-workflow.toml"
    _preflight_path(root, local, "local config")
    if local.exists():
        return _read_config(root), None
    example = root / ".my-workflow.toml.example"
    _preflight_path(root, example, "config example")
    config = _load_config(example, ".my-workflow.toml.example")
    return config, example.read_bytes()


def sync_agents(root: Path) -> dict[str, list[str]]:
    """Validate templates and materialize complete ignored runtime packets."""
    root = root.absolute()
    if root.is_symlink():
        raise _error(f"root {root} must not be a symlink")
    if not root.is_dir():
        raise _error(f"root is not a directory: {root}")
    local_config = root / ".my-workflow.toml"
    _preflight_path(root, local_config, "local config")
    _preflight_destination(root, local_config, "local config")
    config, config_bytes = _sync_config(root)
    plans: list[tuple[Path, bytes]] = []
    for provider in PROVIDERS:
        for role in ROLES:
            relative = _runtime_relative(provider, role)
            template_relative = _template_relative(provider, role)
            template_path = root / template_relative
            _preflight_path(root, template_path, "agent template")
            try:
                template = template_path.read_bytes()
            except FileNotFoundError as exc:
                raise _error(f"missing agent template {template_relative.as_posix()}") from exc
            packet_setting(provider, template, template_relative)
            if provider == "claude":
                header, _ = _header(provider, template.decode("utf-8"), template_relative)
                for skill in _preload_skills(header):
                    if not (root / ".agents" / "skills" / skill / "SKILL.md").is_file():
                        raise _error(
                            f"{template_relative.as_posix()} preloads unknown skill {skill!r}"
                        )
            rendered = render_agent_packet(
                provider, template, model_setting(config, provider, role), template_relative
            )
            assert isinstance(rendered, bytes)
            plans.append((relative, rendered))
    for relative, _ in plans:
        _preflight_destination(root, root / relative, "runtime")
    if config_bytes is not None:
        _write_bytes_atomic(local_config, config_bytes)
    changed: list[str] = []
    unchanged: list[str] = []
    for relative, rendered in plans:
        path = root / relative
        current = path.read_bytes() if path.exists() else None
        if current == rendered:
            unchanged.append(relative.as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            _write_bytes_atomic(path, rendered)
            changed.append(relative.as_posix())
    return {"changed": changed, "unchanged": unchanged}


def _parse_overrides(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        role, separator, provider = value.partition("=")
        if not separator or not role or not provider:
            raise _error("override must use role=provider")
        if role in parsed:
            raise _error(f"duplicate override for role {role!r}")
        parsed.update(_validate_role_map({role: provider}, "override"))
    return parsed


def _git_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.PIPE
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise _error(f"cannot resolve git head in {root}") from exc


def _runtime_relative(provider: str, role: str) -> Path:
    extension = "toml" if provider == "codex" else "md"
    agent_name = AGENT_NAMES.get(role, role)
    return Path(f".{provider}") / "agents" / f"{agent_name}.{extension}"


def _template_relative(provider: str, role: str) -> Path:
    extension = "toml" if provider == "codex" else "md"
    agent_name = AGENT_NAMES.get(role, role)
    return Path("templates") / "agents" / provider / f"{agent_name}.{extension}"


def _agent_file(root: Path, provider: str, role: str) -> str:
    relative = _runtime_relative(provider, role)
    if (root / relative).is_file():
        return relative.as_posix()
    raise _error(
        f"missing generated agent file for provider {provider!r}, role {role!r}; "
        f"run --sync-agents; expected {relative.as_posix()}"
    )


def _agent_candidates(provider: str, role: str) -> tuple[Path, ...]:
    return (_runtime_relative(provider, role),)


def _snapshot_path(root: Path, feature: str) -> Path:
    if not SLUG_RE.fullmatch(feature):
        raise _error("feature must be a lowercase slug")
    return root / ".specs" / "features" / feature / "workflow.json"


def _derived_slice_count(root: Path, feature: str) -> int:
    """Derive the slice count from the validated merge-alone closure contract."""
    tasks_path = root / ".specs" / "features" / feature / "tasks.md"
    if not tasks_path.is_file():
        return 1
    validator = (
        Path(__file__).resolve().parents[2]
        / "workflow-spec-driven"
        / "scripts"
        / "validate_tasks.py"
    )
    result = subprocess.run(
        [sys.executable, str(validator), str(tasks_path), "--slice-contract-json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "invalid slice contract"
        raise _error(f"tasks closure validation failed: {detail}")
    try:
        contract = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise _error("tasks closure validator returned invalid JSON") from exc
    slice_ids = contract.get("slice_ids") if isinstance(contract, dict) else None
    if not isinstance(slice_ids, list) or not slice_ids:
        raise _error("tasks closure validator returned no slices")
    return len(slice_ids)


def _validate_snapshot(root: Path, feature: str, snapshot: Any) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise _error("existing snapshot must be a JSON object")
    if type(snapshot.get("version")) is not int or snapshot.get("version") != SNAPSHOT_VERSION:
        if snapshot.get("version") in (1, 2):
            raise _error("workflow snapshot version is stale; rerun resolution with --refresh")
        raise _error("existing snapshot version must be integer 3")
    required = {
        "version",
        "feature",
        "git_head",
        "profile",
        "overrides",
        "deep_review",
        "parallelization",
        "roles",
    }
    if set(snapshot) != required:
        raise _error("existing snapshot has an incomplete schema")
    if snapshot["feature"] != feature or not isinstance(snapshot["feature"], str):
        raise _error("existing snapshot feature does not match the requested feature")
    if not isinstance(snapshot["git_head"], str) or not snapshot["git_head"]:
        raise _error("existing snapshot git_head must be a non-empty string")
    if snapshot["profile"] is not None and not isinstance(snapshot["profile"], str):
        raise _error("existing snapshot profile must be a string or null")
    overrides = snapshot["overrides"]
    if not isinstance(overrides, dict):
        raise _error("existing snapshot overrides must be a table")
    _validate_role_map(overrides, "existing snapshot overrides")

    deep_review = snapshot["deep_review"]
    if not isinstance(deep_review, dict) or set(deep_review) != {"cadence", "groups"}:
        raise _error("existing snapshot deep_review has an incomplete schema")
    cadence = deep_review["cadence"]
    if not isinstance(cadence, str):
        raise _error("existing snapshot deep_review.cadence must be a string")
    groups = deep_review["groups"]
    if not isinstance(groups, list) or not groups or any(
        not isinstance(group, list)
        or not group
        or any(type(index) is not int or index < 1 for index in group)
        for group in groups
    ):
        raise _error("existing snapshot deep_review.groups must be non-empty integer lists")
    flattened = [index for group in groups for index in group]
    if flattened != list(range(1, len(flattened) + 1)):
        raise _error("existing snapshot deep_review.groups must be consecutive")
    if balanced_groups(len(flattened), cadence) != groups:
        raise _error("existing snapshot deep_review.groups do not match cadence")

    parallelization = snapshot["parallelization"]
    snapshot_parallelization_keys = {
        "mode", "max_workers", "automatic_baseline", "automatic_ceiling", "resource_provider"
    }
    if not isinstance(parallelization, dict) or set(parallelization) != snapshot_parallelization_keys:
        raise _error("existing snapshot parallelization has an incomplete schema")
    mode = parallelization["mode"]
    if not isinstance(mode, str) or mode not in PARALLELIZATION_MODES:
        raise _error("existing snapshot parallelization.mode is invalid")
    max_workers = parallelization["max_workers"]
    if max_workers != MAX_WORKERS_DEFAULT and (type(max_workers) is not int or max_workers < 1):
        raise _error("existing snapshot parallelization.max_workers is invalid")
    if parallelization["automatic_baseline"] != AUTOMATIC_BASELINE:
        raise _error("existing snapshot parallelization.automatic_baseline is invalid")
    if parallelization["automatic_ceiling"] != AUTOMATIC_CEILING:
        raise _error("existing snapshot parallelization.automatic_ceiling is invalid")
    normalized_provider = _resource_provider(root, parallelization.get("resource_provider"))

    roles = snapshot["roles"]
    if not isinstance(roles, dict) or set(roles) != set(DELEGATED_ROLES):
        raise _error("existing snapshot roles must contain every delegated workflow role")
    for role in DELEGATED_ROLES:
        route = roles[role]
        if not isinstance(route, dict) or set(route) != {"provider", "agent_file", "model", "effort"}:
            raise _error(f"existing snapshot role {role!r} has an incomplete schema")
        provider = route["provider"]
        if not isinstance(provider, str) or provider not in PROVIDERS:
            raise _error(f"existing snapshot role {role!r} has an invalid provider")
        agent_file = route["agent_file"]
        if not isinstance(agent_file, str) or not agent_file:
            raise _error(f"existing snapshot role {role!r} agent_file must be a string")
        allowed_paths = _agent_candidates(provider, role)
        if agent_file not in {path.as_posix() for path in allowed_paths}:
            raise _error(f"existing snapshot role {role!r} has an invalid agent_file")
        if not (root / agent_file).is_file():
            raise _error(f"existing snapshot role {role!r} agent_file is missing")
        model = route["model"]
        if not isinstance(model, str) or not model:
            raise _error(f"existing snapshot role {role!r} model must be a non-empty string")
        effort = route["effort"]
        if not isinstance(effort, str) or effort not in EFFORTS:
            raise _error(f"existing snapshot role {role!r} effort is invalid")
        current = packet_setting(provider, (root / agent_file).read_bytes(), Path(agent_file))
        if current != {"model": model, "effort": effort}:
            raise _error(
                f"role {role!r} packet metadata differs from frozen snapshot; "
                "run --sync-agents, then explicitly use --refresh"
            )
    normalized = dict(snapshot)
    normalized["parallelization"] = {
        "mode": mode,
        "max_workers": max_workers,
        "automatic_baseline": AUTOMATIC_BASELINE,
        "automatic_ceiling": AUTOMATIC_CEILING,
        "resource_provider": normalized_provider,
    }
    return normalized


def validate_snapshot(root: Path, feature: str, snapshot: Any) -> dict[str, Any]:
    """Validate the complete frozen v3 snapshot for all runtime readers."""
    return _validate_snapshot(root.resolve(), feature, snapshot)


def _write_snapshot(path: Path, snapshot: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as stream:
            temporary = stream.name
            json.dump(snapshot, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def resolve(
    *,
    root: Path,
    feature: str,
    native_provider: str,
    slice_count: int | None = None,
    profile: str | None = None,
    overrides: list[str] | None = None,
    refresh: bool = False,
) -> dict[str, Any]:
    """Resolve and persist one feature's effective workflow route."""
    root = root.resolve()
    if not root.is_dir():
        raise _error(f"root is not a directory: {root}")
    if native_provider not in PROVIDERS:
        raise _error(f"invalid native provider {native_provider!r}")
    config = _read_config(root)
    remediation = {"stall_attempts": _stall_attempts(config)}
    snapshot_path = _snapshot_path(root, feature)
    if snapshot_path.exists() and not refresh:
        try:
            with snapshot_path.open(encoding="utf-8") as stream:
                snapshot = json.load(stream)
        except (OSError, json.JSONDecodeError) as exc:
            raise _error(f"existing snapshot is invalid: {snapshot_path}") from exc
        resolved = dict(_validate_snapshot(root, feature, snapshot))
        resolved["remediation"] = remediation
        return resolved

    derived_count = _derived_slice_count(root, feature)
    if slice_count is not None:
        if slice_count < 1:
            raise _error("slice count must be at least 1")
        if slice_count != derived_count:
            raise _error(
                f"slice count assertion {slice_count} does not match derived slice count {derived_count}"
            )
    slice_count = derived_count
    cadence = _cadence(config)
    parallelization = _parallelization(config, root)
    groups = balanced_groups(slice_count, cadence)
    profiles = _profiles(config)
    if profile is not None and profile not in profiles:
        raise _error(f"unknown profile {profile!r}")
    selected = profiles.get(profile, {})
    parsed_overrides = _parse_overrides(overrides or [])
    providers = {role: parsed_overrides.get(role, selected.get(role, native_provider)) for role in ROLES}
    for provider in PROVIDERS:
        for role in ROLES:
            agent_file = _agent_file(root, provider, role)
            current = packet_setting(provider, (root / agent_file).read_bytes(), Path(agent_file))
            expected = model_setting(config, provider, role)
            if current != expected:
                raise _error(
                    f"{agent_file} is not synchronized with models.{provider}.{role}; "
                    "run --sync-agents before resolving"
                )
    roles = {}
    for role in DELEGATED_ROLES:
        provider = providers[role]
        agent_file = _agent_file(root, provider, role)
        current = packet_setting(provider, (root / agent_file).read_bytes(), Path(agent_file))
        expected = model_setting(config, provider, role)
        if current != expected:
            raise _error(
                f"{agent_file} is not synchronized with models.{provider}.{role}; "
                "run --sync-agents before resolving"
            )
        roles[role] = {
            "provider": provider,
            "agent_file": agent_file,
            "model": expected["model"],
            "effort": expected["effort"],
        }
    snapshot = {
        "version": SNAPSHOT_VERSION,
        "feature": feature,
        "git_head": _git_head(root),
        "profile": profile,
        "overrides": parsed_overrides,
        "deep_review": {"cadence": cadence, "groups": groups},
        "parallelization": parallelization,
        "roles": roles,
    }
    _write_snapshot(snapshot_path, snapshot)
    resolved = dict(snapshot)
    resolved["remediation"] = remediation
    return resolved


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--feature")
    parser.add_argument("--slices", dest="slice_count", type=int)
    parser.add_argument("--native-provider")
    parser.add_argument("--profile")
    parser.add_argument("--override", dest="overrides", action="append", default=[])
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--sync-agents", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        if arguments.sync_agents:
            if any(
                value is not None
                for value in (arguments.feature, arguments.slice_count, arguments.native_provider,
                              arguments.profile)
            ) or arguments.refresh:
                raise _error("--sync-agents cannot be combined with feature-resolution arguments")
            if arguments.overrides:
                raise _error("--sync-agents cannot be combined with feature-resolution arguments")
            print(json.dumps(sync_agents(arguments.root), indent=2, sort_keys=True))
            return 0
        if arguments.feature is None or arguments.native_provider is None:
            raise _error("--feature and --native-provider are required unless --sync-agents is used")
        values = vars(arguments)
        values.pop("sync_agents")
        snapshot = resolve(**values)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
