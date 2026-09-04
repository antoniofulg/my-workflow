#!/usr/bin/env python3
"""
check_commit.py - deterministic Conventional Commits validation.

The per-task atomic-commit rule mandates Conventional Commits 1.0.0. This makes
that rule checkable instead of trusting the model to remember the format. Pure
standard library, zero dependencies, agent-agnostic.

It reads the message from (in priority order): a positional file path, --message,
or stdin. The file-path form matches how git passes the message file to a
`commit-msg` hook, so this doubles as an optional git-level guard WITHOUT
coupling the skill to any AI agent:

    ln -s <skill-dir>/scripts/check_commit.py .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg

What it checks:
  ERROR  - header does not match  type(scope)!: description
  ERROR  - type is not one of the allowed Conventional Commits types
  ERROR  - description is empty, starts uppercase, or ends with a period
  ERROR  - `!` breaking marker present but no `BREAKING CHANGE:` footer
  ERROR  - a `Review-Signal:` trailer is present but malformed
  WARN   - header longer than 72 characters

The `Review-Signal` trailer is optional and never required; when present it is
one line recording the delivery's review outcome (AD-025, AD-026):

  Review-Signal: tier=<direct|batch|small|medium|large|complex> slices=<int> \
    verified=<int> sensor=<killed>/<injected> rounds=<int> findings=<int> \
    fixed=<int> dismissed=<int> [remediation-failed=<int>]

`tier` is always required; `tier=direct` and `tier=batch` require nothing else.
Every other tier requires the full key set. Integers are non-negative decimal
digits. `fixed + dismissed == findings`, `verified <= slices`, `slices >= 1`,
and sensor `killed <= injected`.

Usage:
  python3 <skill-dir>/scripts/check_commit.py [msgfile]
  python3 <skill-dir>/scripts/check_commit.py --message "feat(auth): add email validation"
  echo "fix(cart): prevent negative quantity" | python3 <skill-dir>/scripts/check_commit.py

Exit codes: 0 pass, 1 violation, 2 usage error.
"""

import argparse
import re
import sys

TYPES = ["feat", "fix", "refactor", "docs", "test", "style", "perf", "build", "ci", "chore"]
HEADER_RE = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?: (?P<desc>.+)$")
SIGNAL_RE = re.compile(r"^Review-Signal:(.*)$", re.MULTILINE)
SIGNAL_INT_RE = re.compile(r"^[0-9]+$")
SIGNAL_TIERS = ["direct", "batch", "small", "medium", "large", "complex"]
SIGNAL_KEYS = ["tier", "slices", "verified", "sensor", "rounds", "findings", "fixed", "dismissed", "remediation-failed"]
SIGNAL_TIER_KEYS = ["slices", "verified", "sensor", "rounds", "findings", "fixed", "dismissed"]


def read_message(args):
    if args.message is not None:
        return args.message
    if args.msgfile:
        with open(args.msgfile, "r", encoding="utf-8") as f:
            return f.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def check_review_signal(body):
    """Validate the optional Review-Signal trailer. Absent means valid."""
    found = SIGNAL_RE.findall(body)
    if not found:
        return []
    if len(found) > 1:
        return [f"{len(found)} 'Review-Signal:' lines present; exactly one is allowed"]

    errors, values = [], {}
    for field in found[0].split():
        key, sep, value = field.partition("=")
        if not sep:
            errors.append(f"Review-Signal field '{field}' is not 'key=value'")
        elif key not in SIGNAL_KEYS:
            errors.append(f"Review-Signal key '{key}' is unknown; allowed: {', '.join(SIGNAL_KEYS)}")
        elif key in values:
            errors.append(f"Review-Signal key '{key}' appears more than once")
        else:
            values[key] = value

    tier = values.get("tier")
    if tier is None:
        errors.append("Review-Signal is missing required key 'tier'")
    elif tier not in SIGNAL_TIERS:
        errors.append(f"Review-Signal tier '{tier}' is not one of: {', '.join(SIGNAL_TIERS)}")
    elif tier not in ("direct", "batch"):
        for key in SIGNAL_TIER_KEYS:
            if key not in values:
                errors.append(f"Review-Signal tier '{tier}' requires key '{key}'")

    numbers = {}
    for key, value in values.items():
        if key == "tier":
            continue
        if key == "sensor":
            killed, sep, injected = value.partition("/")
            if sep and SIGNAL_INT_RE.match(killed) and SIGNAL_INT_RE.match(injected):
                numbers["killed"], numbers["injected"] = int(killed), int(injected)
            else:
                errors.append(f"Review-Signal sensor '{value}' is not '<killed>/<injected>' non-negative integers")
        elif SIGNAL_INT_RE.match(value):
            numbers[key] = int(value)
        else:
            errors.append(f"Review-Signal {key}='{value}' is not a non-negative integer")

    if {"findings", "fixed", "dismissed"} <= numbers.keys():
        total = numbers["fixed"] + numbers["dismissed"]
        if total != numbers["findings"]:
            errors.append(f"Review-Signal findings={numbers['findings']} but fixed+dismissed={total}")
    if {"verified", "slices"} <= numbers.keys() and numbers["verified"] > numbers["slices"]:
        errors.append(f"Review-Signal verified={numbers['verified']} exceeds slices={numbers['slices']}")
    if numbers.get("slices") == 0:
        errors.append("Review-Signal slices=0; a delivery carries at least one slice")
    if "killed" in numbers and numbers["killed"] > numbers["injected"]:
        errors.append(f"Review-Signal sensor killed={numbers['killed']} exceeds injected={numbers['injected']}")
    return errors


def check(message):
    errors, warnings = [], []
    # Ignore comment lines (git puts '#' comments in the message file).
    lines = [ln for ln in message.splitlines() if not ln.lstrip().startswith("#")]
    # Trim leading blank lines.
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return (["empty commit message"], warnings)

    header = lines[0].rstrip()
    if len(header) > 72:
        warnings.append(f"header is {len(header)} chars (>72): {header[:60]}...")

    m = HEADER_RE.match(header)
    if not m:
        errors.append(f"header does not match 'type(scope): description': {header!r}")
        return (errors, warnings)

    ctype = m.group("type")
    desc = m.group("desc")
    bang = m.group("bang")

    if ctype not in TYPES:
        errors.append(f"type '{ctype}' is not one of: {', '.join(TYPES)}")
    if not desc.strip():
        errors.append("description is empty")
    else:
        if desc[:1].isupper():
            errors.append(f"description should start lowercase: '{desc[:30]}'")
        if desc.rstrip().endswith("."):
            errors.append("description should not end with a period")

    body = "\n".join(lines[1:])
    breaking_footer = bool(re.search(r"^BREAKING CHANGE:", body, re.MULTILINE))
    if bang and not breaking_footer:
        errors.append("'!' breaking marker present but no 'BREAKING CHANGE:' footer")
    errors.extend(check_review_signal(body))

    return (errors, warnings)


def main(argv=None):
    p = argparse.ArgumentParser(prog="check_commit.py", description="Validate a Conventional Commits message.")
    p.add_argument("msgfile", nargs="?", default=None, help="path to a commit message file (as git passes to commit-msg)")
    p.add_argument("--message", default=None, help="the commit message as a string")
    args = p.parse_args(argv)

    message = read_message(args)
    if not message.strip():
        print("check_commit: no message provided (pass a file, --message, or pipe via stdin).", file=sys.stderr)
        return 2

    errors, warnings = check(message)
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    if errors:
        print("\ncheck_commit: FAIL - see https://www.conventionalcommits.org/en/v1.0.0/")
        return 1
    print("check_commit: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
