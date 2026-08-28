#!/usr/bin/env python3
"""Build bounded, pointer-addressable packets for one implementation slice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "feature",
        "slice",
        "tasks",
        "acceptance_criteria",
        "test_ids",
        "gate",
        "design_excerpt",
        "memory",
    }
)
ROLE_BUDGET_BYTES = 3_072
SLICE_BUDGET_BYTES = 10_240


class PacketError(ValueError):
    """A packet cannot be safely materialized."""


def _strings(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise PacketError(f"invalid_{field}")
    return value


def validate_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise PacketError("request_not_object")
    if set(request) - ALLOWED_FIELDS:
        raise PacketError("unknown_field")
    if request.get("schema_version") != 1:
        raise PacketError("invalid_schema_version")
    for field in ("feature", "slice", "gate", "design_excerpt", "memory"):
        if not isinstance(request.get(field), str) or not request[field].strip():
            raise PacketError(f"invalid_{field}")
    for field in ("tasks", "acceptance_criteria", "test_ids"):
        _strings(request.get(field), field)
    return request


def render_packet(request: dict[str, Any]) -> bytes:
    sections = [
        "# Slice packet",
        f"\n- Feature: `{request['feature']}`",
        f"- Slice: `{request['slice']}`",
        "\n## Tasks\n" + "\n".join(f"- `{item}`" for item in request["tasks"]),
        "\n## Acceptance criteria\n"
        + "\n".join(f"- `{item}`" for item in request["acceptance_criteria"]),
        "\n## Tests\n" + "\n".join(f"- `{item}`" for item in request["test_ids"]),
        f"\n## Gate\n\n```text\n{request['gate']}\n```",
        f"\n## Design excerpt\n\n{request['design_excerpt']}",
        f"\n## Slice memory\n\n{request['memory']}",
        "",
    ]
    return "\n".join(sections).encode("utf-8")


def telemetry(
    *, role_bytes: int, slice_bytes: int, within_budget: bool, error: str | None = None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": 1,
        "role_bytes": role_bytes,
        "slice_bytes": slice_bytes,
        "slice_budget_bytes": SLICE_BUDGET_BYTES,
        "role_budget_bytes": ROLE_BUDGET_BYTES,
        "within_budget": within_budget,
        "components": {"role": role_bytes, "slice": slice_bytes},
        "total_bytes": role_bytes + slice_bytes,
    }
    if error:
        result["error"] = error
    return result


def write_telemetry(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")


def emit_telemetry(path: Path, data: dict[str, Any]) -> None:
    """Best-effort diagnostics that never turn a safe error into a traceback."""
    try:
        write_telemetry(path, data)
    except OSError:
        pass


def build(input_path: Path, output_path: Path, telemetry_path: Path, role_path: Path | None) -> dict[str, Any]:
    try:
        role_bytes = role_path.stat().st_size if role_path and role_path.is_file() else 0
    except OSError:
        role_bytes = 0
    try:
        request = json.loads(input_path.read_text(encoding="utf-8"))
        validate_request(request)
        packet = render_packet(request)
    except (OSError, UnicodeError, json.JSONDecodeError, PacketError) as exc:
        reason = str(exc) if isinstance(exc, PacketError) else "invalid_input"
        result = telemetry(role_bytes=role_bytes, slice_bytes=0, within_budget=False, error=reason)
        emit_telemetry(telemetry_path, result)
        raise PacketError(reason) from exc

    slice_bytes = len(packet)
    if role_bytes > ROLE_BUDGET_BYTES:
        result = telemetry(
            role_bytes=role_bytes, slice_bytes=slice_bytes, within_budget=False, error="role_budget_exceeded"
        )
        emit_telemetry(telemetry_path, result)
        raise PacketError("role_budget_exceeded")
    if slice_bytes > SLICE_BUDGET_BYTES:
        result = telemetry(
            role_bytes=role_bytes, slice_bytes=slice_bytes, within_budget=False, error="slice_budget_exceeded"
        )
        emit_telemetry(telemetry_path, result)
        raise PacketError("slice_budget_exceeded")

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(packet)
    except OSError as exc:
        result = telemetry(role_bytes=role_bytes, slice_bytes=slice_bytes, within_budget=False, error="io_error")
        emit_telemetry(telemetry_path, result)
        raise PacketError("io_error") from exc
    result = telemetry(role_bytes=role_bytes, slice_bytes=slice_bytes, within_budget=True)
    emit_telemetry(telemetry_path, result)
    return result


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build", help="materialize one bounded slice packet")
    build_parser.add_argument("--input", required=True, type=Path)
    build_parser.add_argument("--output", required=True, type=Path)
    build_parser.add_argument("--telemetry", required=True, type=Path)
    build_parser.add_argument("--role-input", type=Path)
    args = parser.parse_args(argv)
    try:
        result = build(args.input, args.output, args.telemetry, args.role_input)
    except PacketError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
