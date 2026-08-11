# Run history and traceability

**Status:** frozen vendor-neutral kernel

## Risk signals — pay extra attention when

External effects, regulated or relied-on claims, multiple sources or systems, mutable artifacts, long retention, asynchronous handoffs, missing population denominator, unverifiable source lineage, or producer-controlled custody.

## Control rules

- Assign stable IDs and deterministic links across work order, source, configuration, execution, effect, verification, exception, and disposition.
- Label every material fact as declared, runtime-reported, observed, role-separated, human, or organizationally independent.
- Reconcile the full acceptance-critical population; absence is `unknown`, not zero.
- Preserve source and target readback and the supersession chain.
- Describe custody honestly. Hashes and append-oriented files do not establish immutability or actor-independent custody.

## Implementation slots — where controls can live

Source/target system, evidence relationship service, retention store, independently controlled evidence store where required, and reconstruction procedure.

## Required evidence — what to keep

Input and configuration references; retained artifacts and digests; source/effect readbacks; relationship graph; exception and waiver links; custody classification; population reconciliation; reconstruction result and disposition.

## Metrics and triggers — what to watch

Acceptance-critical population completeness = 100%; broken required links = 0; unexplained source/effect mismatches = 0. Track reconstruction pass rate, evidence latency, stale references, and custody exceptions. A failed reconstruction blocks the dependent claim.

## Tier application — depth by risk

- L1: stable IDs, retained critical inputs/outputs, source basis, disposition, and basic reconstruction.
- L2: population reconciliation, target readback, relationship graph, retention rule, and non-producer reconstruction.
- L3: independently controlled custody where claimed, completeness controls, access/change evidence, and formal retention/hold tests.

## Exit rule — done when

A non-producer must be able to reconstruct the scoped claim without hidden reasoning; the wording may not exceed the proven custody and completeness class.
