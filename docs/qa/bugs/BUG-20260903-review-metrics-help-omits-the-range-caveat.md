# BUG-20260903-review-metrics-help-omits-the-range-caveat

- **Status:** fixed in `a1a6e37` — verified by the coordinator, not the author: `python3 tools/review-metrics.py --help` exits 0 and prints the delivery definition, the `unsigned` definition, and the default-branch range caveat AD-027 relies on
- **Severity:** major (usability)
- **Scenario:** `QAS-report-the-reviewed-fraction-from-git`
- **Expected:** `--help` tells the operator what a delivery is, what `unsigned` means, and that the default range reads the whole history — the caveat AD-027 explicitly relies on.
- **Observed:** `--help` prints one sentence. `tools/review-metrics.py:116` passes `__doc__.splitlines()[0]` as the argparse description, so the four paragraphs at `tools/review-metrics.py:6-16` that define a delivery, define `unsigned`, and warn that a feature branch is the wrong range are visible only in the source file.
- **Adapter:** CLI/manual, from the active checkout
- **Exact path:** `python3 tools/review-metrics.py --help`
- **Evidence:** `docs/qa/evidence/2026-09-03-review-signal-trailer/01-noargs.log`

## Why this is load-bearing rather than cosmetic

AD-027 accepts a known pessimistic bias in the default range and names its mitigation in the
decision text: *"a reader who wants the post-adoption number passes a range. A reader who does not
pass one, and does not read the help text, will read a number lower than the truth."* The mitigation
the decision leans on is the help text — and the help text does not carry it. On this repository the
default reads `Deliveries in HEAD: 67 (signalled 0, unsigned 67)` with nothing on screen explaining
that six of those predate the process, or that `HEAD` on a feature branch counts each task commit as
its own delivery.

## Improvement

`tools/review-metrics.py:116` — show the docstring that already exists:

```python
parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
)
```

No new prose, no new flag, no new behaviour. The explanation is already written and already correct;
it is simply not reaching the person who needs it.

## Second observation on the same surface (same fix owner, separate line)

`tools/review-metrics.py:105-106` renders `Reviewed fraction: 4/4 slices verified (100.0%)` while
two of six deliveries carried no signal at all. Unsigned deliveries contribute zero slices, so they
cannot lower the percentage — the headline number is the one that gets quoted into a status update,
and it reads flatteringly high for exactly the history AD-027 worried would read pessimistically
low. Suggested minimal change: carry the coverage into the same line, e.g. append
`across 4 of 6 deliveries`, using numbers the report already computes.
