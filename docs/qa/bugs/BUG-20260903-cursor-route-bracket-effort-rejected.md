# BUG-20260903-cursor-route-bracket-effort-rejected

- **Status:** open — out of scope for w-entry-points; decision logged
- **Severity:** major (blocks automated dispatch via Orca Cursor route)
- **Scenario:** `CFG-centralize-agent-model-routing`
- **Expected:** `tools/orca_assisted_probe.py:377` builds a command that `cursor agent` accepts when passing model and effort settings.
- **Observed:** `route_command("cursor", model, effort)` builds `--model "<model>[effort=<effort>]"`. The `cursor-agent` CLI (2026.09.02) rejects the bracketed effort suffix syntax, exiting non-zero. `cursor-agent --list-models` encodes effort directly inside model IDs (e.g. `gpt-5.6-luna-high`, `cursor-grok-4.6-high`), rejecting `[effort=...]`.
- **Adapter:** CLI / `cursor-agent` subprocess
- **Exact path:** `tools/orca_assisted_probe.py:377`
- **Evidence:** probe returned failure when invoking bracketed effort with `cursor agent` CLI

## Details

In `tools/orca_assisted_probe.py`:

```python
    if provider == "cursor":
        cursor_model = f"{model}[effort={effort}]"
        return f"exec cursor agent --model {shlex.quote(cursor_model)}"
```

`cursor-agent` rejects `--model "<model>[effort=<effort>]"`. Instead, `cursor-agent` expects the model identifier directly, and models that support effort levels specify them as part of their identifier or via provider-specific configuration.

## Remediation recommendation

Update `tools/orca_assisted_probe.py:route_command` and any related route construction to avoid appending `[effort=<effort>]` to the Cursor model string, or resolve model IDs to match the `cursor-agent --list-models` scheme directly.
