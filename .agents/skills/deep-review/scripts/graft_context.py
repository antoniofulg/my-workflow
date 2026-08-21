"""Best-effort Graft context preparation for deep-review prompts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def graft_binary(repo: Path) -> str | None:
    local = repo / "node_modules" / ".bin" / "graft"
    if local.is_file():
        return str(local)
    return shutil.which("graft")


def _run(binary: str, repo: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [binary, *arguments, str(repo)], cwd=repo, capture_output=True, text=True,
        timeout=45, check=False,
    )


def _fallback(path: Path, reason: str, dot_paths: list[str]) -> dict[str, str]:
    lines = [
        "# Graft context",
        "",
        "status: fallback",
        f"reason: {reason}",
        "",
        "Graft context is unavailable; use plain repository inspection.",
    ]
    if dot_paths:
        lines.extend(["", "Graft does not index dot-directories; inspect these paths plainly:", *[f"- `{item}`" for item in dot_paths]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"status": "fallback", "path": str(path)}


def prepare_graft_context(repo: Path, out: Path, selected_paths: list[str], binary: str | None = None) -> dict[str, str]:
    """Build and query Graft without making review dependent on it."""
    context_path = out / "graft-context.md"
    dot_paths = [path for path in selected_paths if path.startswith(".") or path.startswith("graft/")]
    visible_paths = [path for path in selected_paths if path not in dot_paths]
    binary = binary or graft_binary(repo)
    if binary is None:
        return _fallback(context_path, "pinned Graft CLI is unavailable", dot_paths)
    try:
        built = _run(binary, repo, "build")
    except (OSError, subprocess.SubprocessError) as error:
        return _fallback(context_path, f"Graft build failed: {error}", dot_paths)
    if built.returncode != 0:
        return _fallback(context_path, "Graft build failed", dot_paths)
    try:
        mapped = _run(binary, repo, "map", "--json")
    except (OSError, subprocess.SubprocessError) as error:
        return _fallback(context_path, f"Graft map failed: {error}", dot_paths)
    if mapped.returncode != 0:
        return _fallback(context_path, "Graft map failed", dot_paths)

    query = " ".join(visible_paths[:20]) or "repository structure"
    try:
        asked = _run(binary, repo, "ask", "--json", "--limit", "8", query)
    except (OSError, subprocess.SubprocessError):
        asked = None
    symbols: list[str] = []
    if asked is not None and asked.returncode == 0:
        try:
            hits = json.loads(asked.stdout).get("hits", [])
            symbols = [str(hit.get("title", "")).split(" · ", 1)[0] for hit in hits if hit.get("kind") == "symbol"][:3]
        except (TypeError, ValueError, json.JSONDecodeError):
            symbols = []
    ask_ok = asked is not None and asked.returncode == 0

    lines = [
        "# Graft context", "", "status: ready" if not dot_paths else "status: ready-with-fallback", "",
        "Use this map as review orientation; verify every claim against the checkout.", "",
        "## Repository map", "```json", mapped.stdout[:12000].strip(), "```",
    ]
    if ask_ok:
        lines.extend(["", "## Relevant symbols", "```json", asked.stdout[:12000].strip(), "```"])
    else:
        lines.extend(["", "Graft symbol lookup failed; use plain repository inspection for relevant symbols and callers."])
    blast_failed = False
    if symbols:
        lines.extend(["", "## Blast radius"])
        for symbol in symbols:
            try:
                callers = _run(binary, repo, "callers", "--json", "--depth", "1", symbol)
            except (OSError, subprocess.SubprocessError):
                blast_failed = True
                continue
            if callers.returncode == 0:
                lines.extend([f"### `{symbol}`", "```json", callers.stdout[:6000].strip(), "```"])
            else:
                blast_failed = True
    if blast_failed:
        lines.extend(["", "Graft blast-radius lookup failed; use plain repository inspection for callers."])
    if dot_paths:
        lines.extend(["", "Graft does not index dot-directories; use plain repository inspection for:", *[f"- `{item}`" for item in dot_paths]])
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"status": "ready" if ask_ok and not dot_paths and not blast_failed else "ready-with-fallback", "path": str(context_path)}
