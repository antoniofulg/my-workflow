#!/usr/bin/env python3
"""Regenerate `.specs/AD-INDEX.md` from `.specs/STATE.md`.

One line per AD-NNN. Agents load the index, not the log.

  python3 tools/ad-index.py          write the index
  python3 tools/ad-index.py --check  exit 1 if the index is stale
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".specs" / "STATE.md"
INDEX = ROOT / ".specs" / "AD-INDEX.md"

AD_HEADER = re.compile(r"^### (AD-\d+)\s*$")
FIELD = re.compile(r"^- \*\*(Decision|Status)\*\*: (.*)$")


def first_sentence(text: str, limit: int = 140) -> str:
    collapsed = re.sub(r"\s+", " ", text.replace("**", "")).strip()
    cut = collapsed.find(". ")
    sentence = collapsed[: cut + 1] if cut != -1 else collapsed
    if len(sentence) > limit:
        return sentence[: limit - 1].rstrip() + "…"
    return sentence


def parse(state: str) -> list[tuple[int, str, str, str]]:
    rows: list[tuple[int, str, str, str]] = []
    current: str | None = None
    decision_parts: list[str] = []
    status = "active"
    capturing_decision = False

    def flush() -> None:
        nonlocal current, decision_parts, status, capturing_decision
        if current is None:
            return
        number = int(current.split("-")[1])
        rows.append((number, current, first_sentence(" ".join(decision_parts)), status))
        current = None
        decision_parts = []
        status = "active"
        capturing_decision = False

    for line in state.splitlines():
        header = AD_HEADER.match(line)
        if header:
            flush()
            current = header.group(1)
            continue
        if current is None:
            continue
        if line.startswith("## "):
            flush()
            continue
        field = FIELD.match(line)
        if field:
            name, value = field.group(1), field.group(2)
            if name == "Decision":
                capturing_decision = True
                decision_parts = [value]
            elif name == "Status":
                capturing_decision = False
                status = value.strip()
            else:
                capturing_decision = False
            continue
        if capturing_decision and line.startswith("- **"):
            capturing_decision = False
            continue
        if capturing_decision and line.strip():
            decision_parts.append(line.strip())

    flush()
    rows.sort(key=lambda row: row[0])
    return rows


def render(rows: list[tuple[int, str, str, str]]) -> str:
    lines = [
        "# Project decision index",
        "",
        "One line per `AD-NNN`. The append-only body lives in `.specs/STATE.md`.",
        "",
        "Body: `rg -A 20 '^### AD-NNN' .specs/STATE.md`. Resume: `rg -A 20 '^## Handoff' .specs/STATE.md`.",
        "When recording an `AD-NNN`, run `python3 tools/ad-index.py` in the same commit.",
        "",
        "| ID | Status | Decision |",
        "| --- | --- | --- |",
    ]
    for _number, ident, decision, status in rows:
        escaped = decision.replace("|", "\\|")
        lines.append(f"| `{ident}` | {status} | {escaped} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if not STATE.is_file():
        print(f"missing {STATE}", file=sys.stderr)
        return 1
    text = render(parse(STATE.read_text()))
    check = "--check" in sys.argv[1:]
    if check:
        current = INDEX.read_text() if INDEX.is_file() else ""
        if current != text:
            print("stale .specs/AD-INDEX.md; run python3 tools/ad-index.py", file=sys.stderr)
            return 1
        print("AD-INDEX.md up to date")
        return 0
    INDEX.write_text(text, encoding="utf-8")
    print(f"wrote {INDEX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
