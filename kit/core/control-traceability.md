# Control traceability

**Status:** frozen vendor-neutral kernel

Every material risk completes this chain:

> risk → control rule → implementation slot → evidence → metric → owner disposition

The chain is complete only when each link is specific enough for a non-builder to test. A policy sentence with no implementation location is not a control; a log created by the producing process is not automatically observed effect or independent custody; a metric with no threshold and owner cannot trigger action.

## Minimum trace by assurance module

| Module | Representative risk | Required control rule | Implementation slot | Minimum evidence | Minimum metric and trigger |
|---|---|---|---|---|---|
| Authority & human oversight | An action exceeds the grant or a reviewer releases a hidden/different effect | Default deny; action/resource/environment bounds; exact-effect display; no amplification; stop/revoke owner | Policy decision service, identity/credential service, tool or target boundary, human procedure | Authority Decision Record, evaluated attributes, approval/release record, effect readback, revocation result | Unauthorized attempts and bypasses = 0 accepted; stale grant or failed revocation suspends scope |
| Quality & verification | Plausible output is wrong, incomplete, or self-accepted | Fix criteria and producer output before checking; select declared separation class; run critical negative cases | Deterministic oracle, verification service, human disposition | Fixed output digest, oracle result, checker context/separation proof, criteria verdict | Critical regressions = 0; unexplained oracle failures = 0; threshold breach returns to assurance |
| Evidence & traceability | A reviewer cannot reconstruct the decision or actual effect | Stable IDs; source/effect lineage; population reconciliation; explicit custody class and retention | Source/target system, evidence service, retention process | Input/configuration references, source and effect readbacks, relationship graph, reconstruction result | Acceptance-critical population completeness = 100%; failed reconstruction blocks claim |
| Identity, security, data & legal | Orphaned identity, excessive credential, impermissible data route, or ineffective isolation | Named owner/purpose; least scope; lifecycle/recertification; data-purpose rules; secrets and execution boundaries | Identity/credential service, execution boundary, connector, source/target system | Identity/grant inventory, access review, data classification, boundary test, revocation readback | Orphan identities = 0 active; missed recertification or failed boundary test suspends scope |
| Integration, change & supply chain | Dependency or configuration drift changes behavior or authority silently | Pin and retain critical inputs; classify capability location; explicit novation; conflict and rollback tests | Configuration registry, package/dependency process, connector, release process | Canonical manifest, retained artifacts, change/novation decision, integration and rollback results | Unknown critical components = 0; material drift invalidates configuration identity |
| Reliability & continuity | Retry, partial failure, or outage creates duplicate/unowned effects | Timeouts, bounded retries, idempotency, circuit breaking, stop/safe state, tested recovery and manual path | Execution boundary, tool/connector, target system, operations service | Failure injection, health/readback, duplicate-effect check, recovery/rollback result | Duplicate material effects = 0; recovery objective or liveness breach contracts/suspends scope |
| Economics & value | Inference price is mistaken for total cost or activity for value | Predeclare baseline and accepted-output denominator; measure total delivery/operation cost and quality-adjusted outcome | Usage/cost source, evidence service, owner review | Baseline, accepted outputs, authorized cost receipts, labor/retry/rejection cost, value disposition | Stop when total cost or quality-adjusted value crosses the owner-approved threshold |
| Adoption & ownership | Deployment depends on builder knowledge or has no one able to stop/inherit it | Named accountable and operating owners; training/tabletop; support/escalation; transfer and retirement acceptance | Human procedure, training/support system, operations and governance process | RACI/authority record, runbook, tabletop result, owner acceptance, open-obligation register | Owner vacancies = 0; failed stop/handoff tabletop blocks adoption or transfer |

## Trace record fields

Each implemented row adds: trace ID; tier and module depth; stage; exact risk statement; control rule; implementation component and owner; known bypass; test and expected result; evidence IDs and basis; metric, threshold, window, and action; waiver ID if any; current disposition; review date; and supersession link.

## Completeness checks

- Every Stage 2 material risk has at least one trace.
- Every trace names one or more explicit implementation slots and owners.
- Every acceptance-critical control has a negative or bypass test.
- Every evidence item states whether it is declared, runtime-reported, observed, role-separated, human, or organizationally independent.
- Every metric has a denominator, threshold, time window, and action owner.
- No control is treated as effective after its evidence, owner, or configuration identity becomes stale.
