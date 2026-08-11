# Intake and decision rules

This directory turns a workflow description into a deterministic qualification result.
`intake-schema.json` defines the input, `blank-intake.json` is the empty form, and
`completed-example.json` walks through a fictional case.

The evaluator emits ten outputs in a stable order and applies `decision-rules.json` from
top to bottom. A missing fact that matters to acceptance returns `defer`. An important
effect that cannot be observed returns `do_not_agentize`. Each output points back to the
answers and rule IDs that produced it.

Normal users see questions about the job and desired result. Administrator or expert
questions appear only when risk, ambiguity, or an unsupported combination requires
them.

Cross-person workflows also include the transfer plan described in
[handoff-transfer-atr.md](handoff-transfer-atr.md). The full matrix is six gates, each
with a blank form, completed example, and criteria document: 18 files maintained with
the gate packages.

## Enforcement additions from 2026-08-06

- [enforcement-point-contract.md](enforcement-point-contract.md) distinguishes a policy
  denial from an enforcement service that is temporarily unavailable.
- [handoff-transfer-atr.md](handoff-transfer-atr.md) defines staged, guarded import.
- `fixtures/enforcement-negative-denied-sibling-search.json` checks that an allowed
  parent search does not leak a denied child.
- `enforcement_oracle.py` implements the current test-only checker pending schema v3.

Optional v3 inputs still use `instrument_id` v2:

- `classification_groups.enforcement_point` appears on `O07_deployment_boundary`.
- `answers.handoff` also appears on `O07`; a cross-person handoff with `atr_required`
  set to `no` or `unknown` falls back to a human process.

The three related fixtures are `s2-coordinate-handoff-intake.json`,
`s3-act-enforcement-intake.json`, and `s2-handoff-ungoverned-intake.json`. They are part
of the eight cases run by `scripts/run_negative_tests.py`.
