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


ROLES = ("planner", "implementer", "verifier", "explorer", "deep_reviewer")
DELEGATED_ROLES = ("implementer", "verifier", "explorer", "deep_reviewer")
PROVIDERS = ("claude", "codex", "cursor")
AGENT_NAMES = {"deep_reviewer": "deep-reviewer"}
EFFORTS = ("low", "medium", "high", "xhigh", "max", "ultra")
CADENCE_DEFAULT = "grouped.3"
CADENCE_RE = re.compile(r"^grouped\.(\d+)$")
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
CONFIG_KEYS = {"version", "deep_review", "profiles", "models"}
DEEP_REVIEW_KEYS = {"cadence"}
MODEL_PROVIDERS = set(PROVIDERS)
MODEL_KEYS = {"model", "effort"}
CLAUDE_MODEL_RE = re.compile(r"^model:[ \t]*(?P<model>\S+)[ \t]*$", re.MULTILINE)
CLAUDE_EFFORT_RE = re.compile(r"^effort:[ \t]*(?P<effort>\S+)[ \t]*$", re.MULTILINE)
CODEX_MODEL_RE = re.compile(r'^model[ \t]*=[ \t]*"(?P<model>[^"]+)"[ \t]*$', re.MULTILINE)
CODEX_EFFORT_RE = re.compile(
    r'^model_reasoning_effort[ \t]*=[ \t]*"(?P<effort>[^"]+)"[ \t]*$', re.MULTILINE
)
CURSOR_MODEL_RE = re.compile(
    r"^model:[ \t]*(?P<model>\S+)\[effort=(?P<effort>[^\]]+)\][ \t]*$", re.MULTILINE
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


def _read_config(root: Path) -> dict[str, Any]:
    path = root / ".my-workflow.toml"
    if not path.exists():
        raise _error("version must be integer 2; .my-workflow.toml is missing")
    if tomllib is None:  # pragma: no cover
        raise _error("Python 3.11 or newer is required to parse .my-workflow.toml")
    try:
        with path.open("rb") as stream:
            config = tomllib.load(stream)
    except tomllib.TOMLDecodeError as exc:
        raise _error(f"invalid .my-workflow.toml: {exc}") from exc
    if not isinstance(config, dict):
        raise _error(".my-workflow.toml must contain a table")
    version = config.get("version")
    if type(version) is not int or version != 2:
        raise _error("version must be integer 2")
    _validate_config_schema(config)
    return config


def _cadence(config: dict[str, Any]) -> str:
    section = config.get("deep_review") or {}
    return section.get("cadence", CADENCE_DEFAULT)


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
    if type(version) is not int or version != 2:
        raise _error("version must be integer 2")
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


def packet_setting(provider: str, content: str, path: Path) -> dict[str, str]:
    """Parse the native model and effort metadata from one packet."""
    if provider == "claude":
        model = _one_match(CLAUDE_MODEL_RE, content, path, "model").group("model")
        effort = _one_match(CLAUDE_EFFORT_RE, content, path, "effort").group("effort")
    elif provider == "codex":
        model = _one_match(CODEX_MODEL_RE, content, path, "model").group("model")
        effort = _one_match(CODEX_EFFORT_RE, content, path, "model_reasoning_effort").group("effort")
    else:
        match = _one_match(CURSOR_MODEL_RE, content, path, "model/effort").groupdict()
        model, effort = match["model"], match["effort"]
    return {"model": model, "effort": effort}


def render_agent_packet(provider: str, content: str, setting: dict[str, str], path: Path | None = None) -> str:
    """Replace only provider-native model metadata in an agent packet."""
    packet_path = path or Path("agent packet")
    if provider == "claude":
        model_match = _one_match(CLAUDE_MODEL_RE, content, packet_path, "model")
        effort_match = _one_match(CLAUDE_EFFORT_RE, content, packet_path, "effort")
        content = content[:model_match.start()] + f"model: {setting['model']}" + content[model_match.end():]
        # Re-find after model replacement because offsets may change.
        effort_match = _one_match(CLAUDE_EFFORT_RE, content, packet_path, "effort")
        return content[:effort_match.start()] + f"effort: {setting['effort']}" + content[effort_match.end():]
    if provider == "codex":
        model_match = _one_match(CODEX_MODEL_RE, content, packet_path, "model")
        content = content[:model_match.start()] + f'model = "{setting["model"]}"' + content[model_match.end():]
        effort_match = _one_match(CODEX_EFFORT_RE, content, packet_path, "model_reasoning_effort")
        return content[:effort_match.start()] + f'model_reasoning_effort = "{setting["effort"]}"' + content[effort_match.end():]
    match = _one_match(CURSOR_MODEL_RE, content, packet_path, "model/effort")
    return content[:match.start()] + f"model: {setting['model']}[effort={setting['effort']}]" + content[match.end():]


def _write_text_atomic(path: Path, content: str) -> None:
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as stream:
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


def sync_agents(root: Path) -> dict[str, list[str]]:
    """Validate and synchronize all provider packets from the central matrix."""
    root = root.resolve()
    config = _read_config(root)
    plans: list[tuple[Path, str]] = []
    for provider in PROVIDERS:
        for role in ROLES:
            relative = Path(_agent_file(root, provider, role))
            path = root / relative
            content = path.read_text(encoding="utf-8")
            packet_setting(provider, content, relative)
            rendered = render_agent_packet(provider, content, model_setting(config, provider, role), relative)
            plans.append((relative, rendered))
    changed: list[str] = []
    unchanged: list[str] = []
    for relative, rendered in plans:
        path = root / relative
        current = path.read_text(encoding="utf-8")
        if current == rendered:
            unchanged.append(relative.as_posix())
        else:
            _write_text_atomic(path, rendered)
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


def _agent_file(root: Path, provider: str, role: str) -> str:
    candidates = _agent_candidates(provider, role)
    for relative in candidates:
        if (root / relative).is_file():
            return relative.as_posix()
    expected = ", ".join(relative.as_posix() for relative in candidates)
    raise _error(f"missing agent file for provider {provider!r}, role {role!r}; expected {expected}")


def _agent_candidates(provider: str, role: str) -> tuple[Path, ...]:
    agent_name = AGENT_NAMES.get(role, role)
    extensions = ("toml", "md") if provider == "codex" else ("md", "toml")
    return tuple(
        Path(f".{provider}") / "agents" / f"{agent_name}.{extension}"
        for extension in extensions
    )


def _snapshot_path(root: Path, feature: str) -> Path:
    if not SLUG_RE.fullmatch(feature):
        raise _error("feature must be a lowercase slug")
    return root / ".specs" / "features" / feature / "workflow.json"


def _validate_snapshot(root: Path, feature: str, snapshot: Any) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise _error("existing snapshot must be a JSON object")
    required = {
        "version",
        "feature",
        "git_head",
        "profile",
        "overrides",
        "deep_review",
        "roles",
    }
    if set(snapshot) != required:
        raise _error("existing snapshot has an incomplete schema")
    if type(snapshot["version"]) is not int or snapshot["version"] != 2:
        raise _error("existing snapshot version must be integer 2")
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
        current = packet_setting(provider, (root / agent_file).read_text(encoding="utf-8"), Path(agent_file))
        if current != {"model": model, "effort": effort}:
            raise _error(
                f"role {role!r} packet metadata differs from frozen snapshot; "
                "run --sync-agents, then explicitly use --refresh"
            )
    return snapshot


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
    slice_count: int,
    native_provider: str,
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
    snapshot_path = _snapshot_path(root, feature)
    if snapshot_path.exists() and not refresh:
        try:
            with snapshot_path.open(encoding="utf-8") as stream:
                snapshot = json.load(stream)
        except (OSError, json.JSONDecodeError) as exc:
            raise _error(f"existing snapshot is invalid: {snapshot_path}") from exc
        return _validate_snapshot(root, feature, snapshot)

    config = _read_config(root)
    cadence = _cadence(config)
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
            current = packet_setting(
                provider, (root / agent_file).read_text(encoding="utf-8"), Path(agent_file)
            )
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
        current = packet_setting(provider, (root / agent_file).read_text(encoding="utf-8"), Path(agent_file))
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
        "version": 2,
        "feature": feature,
        "git_head": _git_head(root),
        "profile": profile,
        "overrides": parsed_overrides,
        "deep_review": {"cadence": cadence, "groups": groups},
        "roles": roles,
    }
    _write_snapshot(snapshot_path, snapshot)
    return snapshot


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
        if arguments.feature is None or arguments.slice_count is None or arguments.native_provider is None:
            raise _error("--feature, --slices, and --native-provider are required unless --sync-agents is used")
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
