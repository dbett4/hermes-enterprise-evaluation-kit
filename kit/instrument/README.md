# B03 scoping and decision instrument

This directory is the deterministic, vendor-neutral intake surface for B03.
`intake-schema.json` defines the machine-readable contract, `blank-intake.json` is the unanswered form, and `completed-example.json` is a synthetic walkthrough.

The ten outputs are emitted in stable order. Apply `decision-rules.json` in order; acceptance-critical unknowns produce `defer`, and unobservable material effects produce `do_not_agentize`. Every output is linked through `trace` to answers, rule IDs, evidence, confidence, and control disposition.

When the workflow map includes cross-principal work, the instrument must also emit a handoff/transfer plan per [handoff-transfer-atr.md](handoff-transfer-atr.md) (Agent Transfer Record fields — B03 extension scaffold, 2026-08-05).

The combined B03 acceptance matrix is six gates × blank/completed/criteria (18 artifacts); gate packages are maintained separately.

The ordinary-user view asks for mission and outcome. Admin/expert questions appear only when risk, ambiguity, or an unsupported combination requires them.

## Enforcement and guarded-import patch (2026-08-06)

| Artifact | Purpose |
|---|---|
| [enforcement-point-contract.md](enforcement-point-contract.md) | B03/B17 enforcement declarations; `boundary_unavailable` vs `denied_by_policy` |
| [handoff-transfer-atr.md](handoff-transfer-atr.md) | ATR + guarded import receive semantics |
| [fixtures/enforcement-negative-denied-sibling-search.json](fixtures/enforcement-negative-denied-sibling-search.json) | Negative oracle fixture |
| [enforcement_oracle.py](enforcement_oracle.py) | Thin oracle implementation (tests only until schema v3) |

These artifacts are derived from an external prior-art review (2026-08-06) of guarded-import and per-user-sandbox patterns.

## B03 v3 wiring (2026-08-06)

Optional intake fields (still `instrument_id` v2):

- `classification_groups.enforcement_point` → emitted on `O07_deployment_boundary`
- `answers.handoff` → emitted on `O07`; ungoverned cross-principal handoff (`atr_required` = `no`/`unknown`) forces `human_process`

Fixtures: `fixtures/s2-coordinate-handoff-intake.json`, `fixtures/s3-act-enforcement-intake.json`, `fixtures/s2-handoff-ungoverned-intake.json`. Exercised by `scripts/run_negative_tests.py` (8 negative cases).
