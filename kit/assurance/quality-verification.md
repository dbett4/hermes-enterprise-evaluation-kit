# Quality and verification

**Status:** frozen vendor-neutral kernel

## Risk signals — pay extra attention when

Model judgment, ambiguous sources, high exception rate, complex transformation, safety or legal consequence, weak deterministic oracles, mutable producer output, correlated producer/checker failure, or human reviewer overload.

## Control rules

- Fix acceptance criteria, materiality, negative cases, and critical-regression rules before execution.
- Freeze producer output before checking and preserve the exact checker input and context.
- Match evidence class to consequence: deterministic, role-separated, model-independent, human, or organizationally independent.
- Treat self-reported completion as producer evidence only.
- Keep every discrepancy; classify, remediate, waive validly, or reject it.

## Implementation slots — where controls can live

Deterministic oracle, verification service, separate checker process, authenticated human-review process, and target-system readback.

## Required evidence — what to keep

Criteria version; fixed output identity; oracle inputs/results; checker identity, context, configuration and separation proof; discrepancy register; human disposition; rerun or remediation record.

## Metrics and triggers — what to watch

Critical regressions = 0 and unexplained oracle failures = 0. Track accepted-output rate, false accept/reject findings, discrepancy age, reviewer reversal, and checker disagreement. Threshold breach returns to Stage 3 or 4 and blocks promotion.

## Tier application — depth by risk

- L1: explicit criteria, one appropriate check, discrepancy owner, and human disposition for material use.
- L2: fixed producer output, deterministic or role-separated checking, negative cases, and criteria-by-criteria verdict.
- L3: multiple independent evidence classes as needed, adversarial cases, organizationally independent review where claimed, and formal regression gates.

## Exit rule — done when

No recognized output or effect advances on producer narrative alone; the declared evidence class must pass every mandatory criterion.
