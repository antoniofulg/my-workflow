# Specify Impact and Designer — decisions made while unattended

Human-handed: `/autonomous` with Cursor delegated roles (implementer `gemini-3.8-flash-high`; verifier, deep review `cursor-grok-4.6-xhigh-fast`); Fable for design.

| Decision | Chosen | Why | Rejected | Cost to change now | Cost to the user today |
| --- | --- | --- | --- | --- | --- |
| Spec approval | Approved as drafted | autonomous run | wait | none | none |
| Gap hunt for this feature | Skipped | Large, not Complex; autonomous rule runs it only for Complex | run it | none | none |
| Claude designer model | `inherit` | Follows the session model (Fable); subagent `model` accepts `inherit` | pin `opus` | none | none |
| Cursor designer model | `claude-fable-5-1-thinking-high` | Fable on Cursor's list | grok | none | none |
| Impact enforcement scope | Large and Complex only | Same sizing as Design and Tasks | all sizes | small | none |
| Two slices, serial | S1 text and validator, S2 designer role | Both touch `tools/test_phase_skills.py`; serial avoids the shared file | parallel worktrees | none | none |
| Remediation model | `cursor-grok-4.6-xhigh-fast` for the test-strength batch | The gemini session died with `resource_exhausted` before writing anything; the verifier re-ran on an unchanged tree | retry gemini | none | none |
