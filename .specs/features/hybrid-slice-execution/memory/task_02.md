# T2 task memory

- Objective: materialize one allowlisted slice packet and enforce role/slice byte budgets.
- Files: `.agents/skills/workflow-spec-driven/scripts/slice_packet.py` and
  `tools/test_workflow_spec_driven.py`.
- Verification: `python3 tools/test_workflow_spec_driven.py` and the full offline gate; telemetry
  contains counts and reason enums only.
