#!/usr/bin/env python3
"""Plan and apply the fixed, additive workflow adoption layers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

STENCIL = "<!-- product-stencil:"
MANIFEST_SCHEMA = 1
WORKFLOW_VERSION = "0.7.0"
LAYERS = ("core", "parallel", "quality", "extras")
DEPENDENCIES = {"core": (), "parallel": ("core",), "quality": ("core",), "extras": ("core",)}

WORKFLOW_GITIGNORE_ENTRIES = (
    ".my-workflow.toml", ".claude/agents/", ".codex/agents/",
    "!.deep-review/", ".deep-review/*", "!.deep-review/learnings.md", "graft/"
)
LEGACY_WORKFLOW_GITIGNORE_ENTRIES = (".specs/features/",)
WORKFLOW_SEARCHIGNORE_ENTRIES = ("!graft/", "graft/.cache/", "graft/.graph/")
WORKFLOW_DOCS = (
    "docs/workflow/README.md", "docs/workflow/decisions.md", "docs/workflow/guidelines.md",
    "docs/workflow/loop.md", "docs/workflow/purpose.md", "docs/workflow/reviews.md",
)
CORE_PATHS = (
    "docs/guidelines", *WORKFLOW_DOCS, "knowledge/AGENTS.md", "knowledge/raw/README.md",
    "knowledge/wiki", "tools/knowledge/src", "tools/shared/src/frontmatter.ts",
    ".agents/skills/workflow-spec-driven", ".agents/skills/ponytail", ".agents/skills/workflow-config",
    "templates/adoption/agents",
)
CORE_MISSING_PATHS = ("tools/ad-index.py", ".my-workflow.toml.example", "templates/agents")
PARALLEL_PATHS = ("tools/qa_parallel_pilot.py", "tools/orca_assisted_probe.py", ".agents/skills/autonomous")
QUALITY_PATHS = (".agents/skills/deep-review", ".agents/skills/qa-plan", ".agents/skills/qa-execute")
QUALITY_MISSING_PATHS = ("docs/qa/README.md",)
EXTRAS_PATHS = (
    ".agents/skills/ponytail-audit", ".agents/skills/ponytail-debt", ".agents/skills/ponytail-gain",
    ".agents/skills/ponytail-help", ".agents/skills/ponytail-review",
)
LAYER_PATHS = {"core": CORE_PATHS, "parallel": PARALLEL_PATHS, "quality": QUALITY_PATHS, "extras": EXTRAS_PATHS}
LAYER_MISSING_PATHS = {"core": CORE_MISSING_PATHS, "parallel": (), "quality": QUALITY_MISSING_PATHS, "extras": ()}
BLOCK_LAYERS = ("core", "parallel", "quality")
GLOBAL_CLAUDE_ROOT = re.compile(r"(?:\$\(HOME\)|\$\{HOME\}|\$HOME|~)/\.claude(?:/|$)")

# Retained as private migration helpers for consumers that still have unchanged v0.7 suites.
LEGACY_MANAGED_TEST_FILES = {
    "tools/knowledge/tests/check.test.ts": "a77101af4814655f3159f5d231dfcd955f24fbdca4d5c4ecfd173072be61e353",
    "tools/knowledge/tests/cli.test.ts": "849c706b08b358ee978b23d54509acc3eb0ba4eb4977ddb9932106d6b6651dbf",
    "tools/shared/tests/autonomous-parallelization.test.ts": "45c8c57e1774f90c08c3184d4af667426bb3f339acb88cd6f18fee02499e97b1",
    "tools/shared/tests/deep-review-installation.test.ts": "12e13c114d3f998db74431ec9ad7507f5cb570dbb103b40dd39678842d397a07",
    "tools/shared/tests/frontmatter.test.ts": "6f71b2310772ac8ec6afb3542036a5eb3be7ba55387049f458631f8b82f91225",
    "tools/shared/tests/qa-skills.test.ts": "d6cd354f44bbf8dc233bf91237d72490e6e98d07ee155177589b95b06080d101",
    "tools/shared/tests/security-skills-installation.test.ts": "2bf473160592f9121f522129f44cd8dad27831a75da65ec9bd64d64583dcd838",
    "tools/shared/tests/workflow-config.test.ts": "63d738df1b8ffde8b594f152bd07af823e28a44dce121dda1e751217990e0dca",
}
LEGACY_MANAGED_TEST_DIRECTORIES = ("tools/knowledge/tests", "tools/shared/tests")
OBSOLETE_MANAGED_PATHS = (".agents/skills/tlc-spec-driven", ".claude/skills/tlc-spec-driven")


class AdoptionError(ValueError):
    """A user-correctable adoption error."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _die(message: str, code: int = 2) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def _error(message: str) -> AdoptionError:
    return AdoptionError(message)


def remove_legacy_managed_tests(
    dest: Path,
    managed_files: dict[str, str] | None = None,
    managed_directories: tuple[str, ...] | None = None,
) -> None:
    """Remove only the exact historical test bytes owned by the old adopter."""
    files = LEGACY_MANAGED_TEST_FILES if managed_files is None else managed_files
    directories = LEGACY_MANAGED_TEST_DIRECTORIES if managed_directories is None else managed_directories
    def safe(relative: str) -> bool:
        current = dest
        for component in PurePosixPath(relative).parts:
            current /= component
            if current.is_symlink():
                return False
        return True
    for relative, expected in files.items():
        path = dest / relative
        if safe(relative) and path.is_file() and not path.is_symlink() and _sha(path.read_bytes()) == expected:
            path.unlink()
    for relative in directories:
        path = dest / relative
        if safe(relative) and path.is_dir() and not path.is_symlink():
            try:
                path.rmdir()
            except OSError:
                pass


def remove_obsolete_managed_paths(root: Path) -> None:
    for relative in OBSOLETE_MANAGED_PATHS:
        path = root / relative
        current = root
        if any((current := current / part).is_symlink() for part in PurePosixPath(relative).parts):
            continue
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)


def _relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise _error(f"manifest path is unsafe: {value!r}")
    if path.as_posix() != value:
        raise _error(f"manifest path is not normalized: {value!r}")
    return value


def _safe_path(root: Path, relative: str, label: str) -> Path:
    _relative_path(relative)
    path = root / relative
    current = root
    for part in PurePosixPath(relative).parts:
        current /= part
        if current.is_symlink():
            raise _error(f"{label} {relative} uses symlink {current.relative_to(root)}")
        if current != path and current.exists() and not current.is_dir():
            raise _error(f"{label} parent {current.relative_to(root)} must be a directory")
    if path.exists() and not path.is_file():
        raise _error(f"{label} {relative} must be a file")
    return path


def _source_files(root: Path, relative: str) -> list[str]:
    source = root / relative
    if not source.exists():
        raise _error(f"workflow source is missing: {relative}")
    if source.is_symlink():
        raise _error(f"workflow source is a symlink: {relative}")
    if source.is_file():
        return [relative]
    result: list[str] = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_file():
            result.append(path.relative_to(root).as_posix())
    return result


def _dependency_closure(selected: set[str]) -> set[str]:
    closure = set(selected)
    changed = True
    while changed:
        changed = False
        for layer in tuple(closure):
            for dependency in DEPENDENCIES[layer]:
                if dependency not in closure:
                    closure.add(dependency)
                    changed = True
    return closure


def resolve_layers(values: str | list[str]) -> list[str]:
    raw = values.split(",") if isinstance(values, str) else values
    selected = {item.strip() for item in raw if item.strip()}
    if "full" in selected:
        selected.remove("full")
        selected.update(LAYERS)
    unknown = sorted(selected - set(LAYERS))
    if unknown:
        raise _error(f"unknown layer(s): {', '.join(unknown)}; choose core, parallel, quality, extras, or full")
    if not selected:
        raise _error("--layers must name core, parallel, quality, extras, or full")
    closure = _dependency_closure(selected)
    for layer, dependencies in DEPENDENCIES.items():
        if layer not in LAYERS or any(dep not in LAYERS for dep in dependencies):
            raise _error(f"invalid dependency graph at {layer}")
    return [layer for layer in LAYERS if layer in closure]


def _catalog(root: Path, layers: list[str]) -> dict[str, str]:
    entries: dict[str, str] = {}
    for layer in layers:
        for relative in (*LAYER_PATHS[layer], *LAYER_MISSING_PATHS[layer]):
            for path in _source_files(root, relative):
                previous = entries.get(path)
                if previous and previous != layer:
                    raise _error(f"workflow path belongs to multiple layers: {path}")
                entries[path] = layer
    return entries


def _manifest_path(root: Path) -> Path:
    return _safe_path(root, ".my-workflow/adoption.json", "manifest")


def _empty_manifest() -> dict[str, Any]:
    return {"schema": 1, "workflow_version": WORKFLOW_VERSION, "layers": [], "files": {}, "blocks": {}}


def _validate_hash(value: Any, label: str, allow_none: bool = False) -> None:
    if allow_none and value is None:
        return
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise _error(f"manifest {label} must be a lowercase SHA-256 hash")


def load_manifest(root: Path) -> dict[str, Any]:
    path = root / ".my-workflow/adoption.json"
    if not path.exists():
        return _empty_manifest()
    _manifest_path(root)
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise _error(f"adoption manifest contains duplicate key: {key}")
            result[key] = value
        return result
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    except (OSError, json.JSONDecodeError) as exc:
        raise _error(f"invalid adoption manifest: {exc}") from exc
    if not isinstance(data, dict) or set(data) != {"schema", "workflow_version", "layers", "files", "blocks"}:
        raise _error("adoption manifest has an unsupported schema")
    if data["schema"] != 1 or not isinstance(data["workflow_version"], str):
        raise _error("adoption manifest schema must be version 1")
    if not isinstance(data["layers"], list) or any(layer not in LAYERS for layer in data["layers"]):
        raise _error("manifest contains an unknown layer")
    if data["layers"] != sorted(set(data["layers"]), key=LAYERS.index):
        raise _error("manifest layers must be unique and catalog-ordered")
    if not isinstance(data["files"], dict) or not isinstance(data["blocks"], dict):
        raise _error("manifest files and blocks must be objects")
    normalized_paths: set[str] = set()
    for relative in data["files"]:
        normalized = PurePosixPath(relative).as_posix()
        if normalized in normalized_paths:
            raise _error(f"manifest contains duplicate normalized path: {relative}")
        normalized_paths.add(normalized)
    for relative, record in data["files"].items():
        _relative_path(relative)
        if not isinstance(record, dict) or set(record) != {"layer", "ownership", "source_sha256", "installed_sha256"}:
            raise _error(f"manifest file record is invalid: {relative}")
        if record["layer"] not in LAYERS or record["ownership"] not in {"managed", "consumer"}:
            raise _error(f"manifest file record has invalid ownership/layer: {relative}")
        _validate_hash(record["source_sha256"], f"source_sha256 for {relative}")
        _validate_hash(record["installed_sha256"], f"installed_sha256 for {relative}", allow_none=record["ownership"] == "consumer")
        if record["ownership"] == "consumer" and record["installed_sha256"] is not None:
            raise _error(f"consumer record must not hash installed bytes: {relative}")
    for key, record in data["blocks"].items():
        if not isinstance(key, str) or ":" not in key or not isinstance(record, dict) or set(record) != {"sha256"}:
            raise _error(f"manifest block record is invalid: {key}")
        relative, layer = key.rsplit(":", 1)
        _relative_path(relative)
        if layer not in BLOCK_LAYERS:
            raise _error(f"manifest block has invalid layer: {key}")
        _validate_hash(record["sha256"], f"block {key}")
    return data


def _record(layer: str, ownership: str, source: bytes, installed: bytes | None) -> dict[str, Any]:
    return {"layer": layer, "ownership": ownership, "source_sha256": _sha(source), "installed_sha256": None if installed is None else _sha(installed)}


def _classify(root: Path, source_root: Path, selected: list[str], manifest: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, Any], list[str]]:
    catalog = _catalog(source_root, selected)
    missing_paths = {path for layer in selected for item in LAYER_MISSING_PATHS[layer] for path in _source_files(source_root, item)}
    actions: list[dict[str, str]] = []
    records: dict[str, Any] = {}
    conflicts: list[str] = []
    for relative, layer in sorted(catalog.items()):
        source = (source_root / relative).read_bytes()
        installed_source = _adopted_bytes(relative, source)
        destination = _safe_path(root, relative, "managed destination")
        previous = manifest["files"].get(relative)
        exists = destination.exists()
        if relative in missing_paths:
            action = "preserve" if exists else "add"
            actions.append({"path": relative, "action": action, "layer": layer})
            records[relative] = _record(layer, "consumer", source, None)
            continue
        if previous and previous["ownership"] == "consumer":
            actions.append({"path": relative, "action": "preserve", "layer": layer})
            records[relative] = previous
            continue
        if previous:
            current_hash = _sha(destination.read_bytes()) if exists else None
            if current_hash != previous["installed_sha256"]:
                conflicts.append(relative)
                actions.append({"path": relative, "action": "conflict", "layer": layer})
                records[relative] = previous
                continue
            action = "retain" if exists and destination.read_bytes() == installed_source else "update"
        elif not exists:
            action = "add"
        elif destination.read_bytes() == installed_source:
            action = "claim"
        else:
            conflicts.append(relative)
            action = "conflict"
        actions.append({"path": relative, "action": action, "layer": layer})
        records[relative] = _record(layer, "managed", source, installed_source)
    return actions, records, conflicts


def _adopted_bytes(relative: str, source: bytes) -> bytes:
    if relative != "docs/workflow/README.md":
        return source
    return b"".join(line for line in source.splitlines(keepends=True) if b"(pack.md)" not in line)


def _block_span(text: str, layer: str) -> tuple[int, int] | None:
    start = f"<!-- my-workflow:{layer}:start -->"
    end = f"<!-- my-workflow:{layer}:end -->"
    starts = [match.start() for match in re.finditer(re.escape(start), text)]
    ends = [match.start() for match in re.finditer(re.escape(end), text)]
    valid_marker = re.compile(r"<!-- my-workflow:(?:core|parallel|quality):(?:start|end) -->")
    malformed = [line for line in text.splitlines() if "my-workflow:" in line and not valid_marker.fullmatch(line.strip())]
    if malformed or len(starts) > 1 or len(ends) > 1:
        raise _error(f"managed {layer} block is duplicated or altered")
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or starts[0] > ends[0]:
        raise _error(f"managed {layer} block is incomplete or nested")
    return starts[0], ends[0] + len(end)


def _block_content(source_root: Path, layer: str, filename: str) -> str:
    if filename == "CLAUDE.md":
        body = "@AGENTS.md"
    else:
        template = source_root / "templates/adoption/agents" / f"{layer}.md"
        if not template.is_file():
            raise _error(f"missing managed instruction template: {template.relative_to(source_root)}")
        body = template.read_text(encoding="utf-8").rstrip("\n")
    return f"<!-- my-workflow:{layer}:start -->\n{body}\n<!-- my-workflow:{layer}:end -->"


def _compose_blocks(source_root: Path, root: Path, installed: list[str], skip_agents: bool, manifest: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any], list[str]]:
    if skip_agents:
        return {}, {}, []
    outputs: dict[str, bytes] = {}
    records: dict[str, Any] = {}
    conflicts: list[str] = []
    for filename in ("AGENTS.md", "CLAUDE.md"):
        path = root / filename
        if path.exists():
            _safe_path(root, filename, filename)
            original = path.read_text(encoding="utf-8")
        elif filename == "AGENTS.md":
            original = (source_root / filename).read_text(encoding="utf-8")
        else:
            original = ""
        rendered = original
        for layer in BLOCK_LAYERS:
            if layer not in installed:
                continue
            try:
                span = _block_span(rendered, layer)
            except AdoptionError:
                conflicts.append(f"{filename}:{layer}")
                continue
            block = _block_content(source_root, layer, filename)
            if span:
                key = f"{filename}:{layer}"
                recorded = manifest["blocks"].get(key)
                if recorded and _sha(rendered[span[0]:span[1]].encode("utf-8")) != recorded["sha256"]:
                    conflicts.append(key)
                    continue
                rendered = rendered[:span[0]] + block + rendered[span[1]:]
            else:
                if rendered and not rendered.endswith("\n"):
                    rendered += "\n"
                if rendered:
                    rendered += "\n"
                rendered += block + "\n"
            records[f"{filename}:{layer}"] = {"sha256": _sha(block.encode("utf-8"))}
        if rendered.encode("utf-8") != (path.read_bytes() if path.exists() else None):
            outputs[filename] = rendered.encode("utf-8")
    return outputs, records, conflicts


def _merge_ignore(existing: bytes | None, entries: tuple[str, ...], remove: tuple[str, ...] = ()) -> bytes:
    lines = (existing.decode("utf-8") if existing else "").splitlines()
    lines = [line for line in lines if line not in remove]
    kept = [line for line in lines if line not in entries]
    merged = "\n".join(kept).rstrip()
    if merged:
        merged += "\n"
    return (merged + "\n".join(entries) + "\n").encode("utf-8")


def _prepare_sync(source_root: Path, root: Path) -> dict[str, bytes]:
    """Validate and render ignored packets in a scratch root before target writes."""
    resolver_root = source_root / ".agents/skills/workflow-config"
    if not (resolver_root / "scripts/workflow_config.py").is_file():
        return {}
    with tempfile.TemporaryDirectory(prefix="my-workflow-sync-") as name:
        scratch = Path(name)
        for relative in ("templates/agents", ".agents/skills/workflow-config"):
            source = root / relative
            if not source.exists():
                source = source_root / relative
            target = scratch / relative
            shutil.copytree(source, target, symlinks=False)
        local = root / ".my-workflow.toml"
        if local.is_file():
            (scratch / local.name).write_bytes(local.read_bytes())
        else:
            (scratch / ".my-workflow.toml.example").write_bytes((source_root / ".my-workflow.toml.example").read_bytes())
        sys.path.insert(0, str((scratch / ".agents/skills/workflow-config/scripts").resolve()))
        import workflow_config  # type: ignore
        try:
            workflow_config.sync_agents(scratch)
        except Exception as exc:  # workflow-config exposes its own ConfigError type.
            raise _error(str(exc)) from exc
        generated: dict[str, bytes] = {}
        for provider in workflow_config.PROVIDERS:
            for role in workflow_config.ROLES:
                relative = workflow_config._runtime_relative(provider, role).as_posix()
                generated[relative] = (scratch / relative).read_bytes()
        if not local.is_file():
            generated[".my-workflow.toml"] = (scratch / ".my-workflow.toml").read_bytes()
        return generated


def _preflight_special(root: Path, skip_agents: bool) -> None:
    for relative in (".gitignore", ".ignore", ".my-workflow/adoption.json"):
        _safe_path(root, relative, "generated destination")
    if not skip_agents:
        for relative in ("AGENTS.md", "CLAUDE.md"):
            _safe_path(root, relative, "instruction destination")
    skills_root = root / ".claude/skills"
    if skills_root.is_symlink():
        raise _error("generated skills directory must not be a symlink")
    if skills_root.exists() and not skills_root.is_dir():
        raise _error("generated skills directory must be a directory")
    if skills_root.exists():
        for layer in LAYERS:
            for skill in LAYER_PATHS[layer]:
                prefix = ".agents/skills/"
                if not skill.startswith(prefix):
                    continue
                pointer = skills_root / skill.removeprefix(prefix)
                expected = "../../.agents/skills/" + pointer.name
                if pointer.is_symlink() and os.readlink(pointer) != expected:
                    raise _error(f"generated skill pointer {pointer.relative_to(root)} has an unexpected target")
                if pointer.exists() and not pointer.is_symlink() and not pointer.is_file():
                    raise _error(f"generated skill pointer {pointer.relative_to(root)} must be a file or symlink")
    makefile = root / "Makefile"
    if makefile.is_file():
        for line_number, line in enumerate(makefile.read_text(encoding="utf-8").splitlines(), 1):
            match = GLOBAL_CLAUDE_ROOT.search(line)
            if match:
                raise _error(f"{makefile}:{line_number} uses machine-global TLC path {match.group(0)!r}; use .agents/skills/workflow-spec-driven/scripts/...")


def _manifest_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _link_claude_skills(root: Path) -> None:
    agents = root / ".agents/skills"
    if not agents.is_dir():
        return
    skills_root = root / ".claude/skills"
    skills_root.mkdir(parents=True, exist_ok=True)
    for skill in sorted(agents.iterdir()):
        if not skill.is_dir() or skill.is_symlink():
            continue
        pointer = skills_root / skill.name
        if pointer.exists() or pointer.is_symlink():
            if pointer.is_dir() and not pointer.is_symlink():
                raise _error(f"generated skill pointer {pointer.relative_to(root)} must be a file or symlink")
            pointer.unlink()
        pointer.symlink_to(Path("../../.agents/skills") / skill.name)


def _build_plan(source_root: Path, root: Path, selected: list[str], skip_agents: bool) -> tuple[dict[str, Any], dict[str, bytes]]:
    _preflight_special(root, skip_agents)
    manifest = load_manifest(root)
    installed = resolve_layers(manifest["layers"]) if manifest["layers"] else []
    effective = resolve_layers(selected + installed)
    actions, records, conflicts = _classify(root, source_root, effective, manifest)
    block_outputs, block_records, block_conflicts = _compose_blocks(source_root, root, effective, skip_agents, manifest)
    conflicts.extend(block_conflicts)
    special = {
        ".gitignore": _merge_ignore((root / ".gitignore").read_bytes() if (root / ".gitignore").is_file() else None, WORKFLOW_GITIGNORE_ENTRIES, LEGACY_WORKFLOW_GITIGNORE_ENTRIES),
        ".ignore": _merge_ignore((root / ".ignore").read_bytes() if (root / ".ignore").is_file() else None, WORKFLOW_SEARCHIGNORE_ENTRIES),
    }
    for action in actions:
        if action["action"] in {"add", "update"}:
            source = (source_root / action["path"]).read_bytes()
            special[action["path"]] = _adopted_bytes(action["path"], source)
    generated = {} if conflicts else _prepare_sync(source_root, root)
    for relative, content in generated.items():
        _safe_path(root, relative, "generated runtime")
        special[relative] = content
    new_manifest = {"schema": 1, "workflow_version": WORKFLOW_VERSION, "layers": effective, "files": records, "blocks": block_records}
    special[".my-workflow/adoption.json"] = _manifest_bytes(new_manifest)
    special.update(block_outputs)
    result = {
        "command": "",
        "target": str(root),
        "requested_layers": selected,
        "resolved_layers": effective,
        "status": "conflict" if conflicts else "ready",
        "actions": sorted(actions, key=lambda item: (item["path"], item["action"])),
        "conflicts": sorted(set(conflicts)),
    }
    return result, special


def _text_result(result: dict[str, Any]) -> str:
    lines = [f"resolved layers: {', '.join(result['resolved_layers'])}", f"status: {result['status']}"]
    for action in result["actions"]:
        lines.append(f"{action['action']:8} {action['path']} ({action['layer']})")
    if result["conflicts"]:
        lines.append("conflicts:")
        lines.extend(f"- {item}" for item in result["conflicts"])
    return "\n".join(lines)


def _status(source_root: Path, root: Path, as_json: bool) -> int:
    manifest = load_manifest(root)
    if not manifest["layers"]:
        _die("adoption manifest is missing or has no installed layers", 2)
    installed = resolve_layers(manifest["layers"])
    actions: list[dict[str, str]] = []
    conflicts: list[str] = []
    for relative, record in sorted(manifest["files"].items()):
        path = _safe_path(root, relative, "managed destination")
        if not path.exists():
            state = "missing"
        elif record["ownership"] == "consumer":
            state = "retained"
        elif _sha(path.read_bytes()) == record["installed_sha256"]:
            state = "clean"
        else:
            state = "modified"
        actions.append({"path": relative, "action": state, "layer": record["layer"]})
        if state in {"missing", "modified"}:
            conflicts.append(relative)
    for filename in ("AGENTS.md", "CLAUDE.md"):
        path = root / filename
        if not path.exists():
            for key in manifest["blocks"]:
                if key.startswith(filename + ":"):
                    layer = key.rsplit(":", 1)[1]
                    actions.append({"path": key, "action": "missing", "layer": layer})
                    conflicts.append(key)
            continue
        text = path.read_text(encoding="utf-8")
        for layer in BLOCK_LAYERS:
            key = f"{filename}:{layer}"
            if key not in manifest["blocks"]:
                continue
            try:
                span = _block_span(text, layer)
            except AdoptionError:
                actions.append({"path": key, "action": "modified", "layer": layer})
                conflicts.append(key)
                continue
            if span is None:
                state = "missing"
            else:
                block = text[span[0]:span[1]].encode("utf-8")
                state = "clean" if _sha(block) == manifest["blocks"][key]["sha256"] else "modified"
            actions.append({"path": key, "action": state, "layer": key.rsplit(":", 1)[1]})
            if state in {"missing", "modified"}:
                conflicts.append(key)
    result = {"command": "status", "target": str(root), "requested_layers": [], "resolved_layers": installed, "status": "drift" if conflicts else "clean", "actions": sorted(actions, key=lambda item: item["path"]), "conflicts": sorted(set(conflicts))}
    print(json.dumps(result, indent=2, sort_keys=True) if as_json else _text_result(result))
    return 1 if result["status"] == "drift" else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="adopt.py", description="Adopt fixed workflow layers safely.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "apply"):
        command = commands.add_parser(name)
        command.add_argument("target", type=Path)
        command.add_argument("--layers", required=True)
        command.add_argument("--json", action="store_true")
        command.add_argument("--skip-agents", action="store_true")
    command = commands.add_parser("status")
    command.add_argument("target", type=Path)
    command.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args((argv or sys.argv)[1:])
        root = Path(os.path.abspath(args.target))
        if root.is_symlink() or not root.is_dir():
            raise _error(f"not a safe target directory: {root}")
        source_root = Path(__file__).resolve().parent.parent
        if args.command == "status":
            return _status(source_root, root, args.json)
        selected = resolve_layers(args.layers)
        result, staged = _build_plan(source_root, root, selected, args.skip_agents)
        result["command"] = args.command
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else _text_result(result))
        if args.command == "plan" or result["conflicts"]:
            return 1 if result["conflicts"] else 0
        for relative, content in sorted(staged.items()):
            _atomic_write(root / relative, content)
        remove_obsolete_managed_paths(root)
        remove_legacy_managed_tests(root)
        _link_claude_skills(root)
        if not args.json:
            print(f"adopted layers into {root}")
            installer = source_root / "scripts/install_security_skills.py"
            print("Security skills are external dependencies, not bundled skills.")
            print(f"After explicit authorization, run exactly: python3 {installer} {root} --yes")
            print("Until then, the SECURITY.md security gate remains uncovered.")
        return 0
    except AdoptionError as exc:
        _die(str(exc), 2)
    except OSError as exc:
        _die(f"adoption failed before completion: {exc}", 2)


if __name__ == "__main__":
    raise SystemExit(main())
