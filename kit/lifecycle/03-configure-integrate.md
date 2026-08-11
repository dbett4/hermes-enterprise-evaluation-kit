# Stage 3 — Configure & Integrate

**Status:** frozen vendor-neutral kernel

**Purpose:** instantiate the approved design as one reconstructable deployment candidate.

## Entry conditions

- Approved Stage 2 design and control traceability matrix
- Fixed acceptance plan and negative cases
- Named configuration, integration, and release owners

## Required questions

1. Which exact runtime, models, prompts, tools, policies, integrations, identities, and verifier components implement the approved design?
2. Are versions, artifacts, dependencies, conflicts, and organization-policy precedence explicit and reconstructable?
3. Where are credentials delivered, data constrained, actions mediated, egress bounded, effects read back, and execution stopped?
4. Which implementation claims are native, configured, extended, supplied by a surrounding platform, or unsupported?
5. Can the candidate be installed, tested, rolled back, and reconstructed without hidden builder knowledge?
6. Does any change create a new risk identity or require an explicit authority novation?

## Decision rules

1. Implement only the approved design. Any material new capability, action, provider, data route, or authority returns to Stage 2.
2. Resolve one complete configuration manifest before testing; load order may not silently resolve a policy conflict.
3. Pin or otherwise identify every acceptance-critical component and retain referenced artifacts. A digest without canonical serialization and retained inputs proves neither reconstruction nor custody.
4. Fail closed when a required component, policy, attribute, secret boundary, stop mechanism, readback, or verifier is missing, stale, incompatible, or contradictory.
5. Use the implementation-mapping contract to distinguish capability location from marketing similarity.
6. A material implementation change creates a new configuration identity. Its prior authority is `none`, `haircut`, `probation`, or explicitly approved carryover—never silent inheritance.

## Outputs

- Canonical configuration manifest and retained artifact references
- Configuration identity and supersession/novation record
- Implementation-location and gap map
- Integration, identity, data-route, stop, readback, and rollback tests
- Release candidate plus reconstruction and rollback procedure
- Updated unresolved-risk, bypass, and exception registers

## Accountable owner

The configuration or release owner owns the candidate identity, artifact set, integration record, and rollback readiness. System and policy owners remain accountable for their respective controls.

## Exceptions and escalation

An implementation override must precede execution, stay inside the approved authority and risk ceiling, and record reason, owner, expiry, compensating control, and changed configuration identity. An invisible runtime, provider, tool, data, verifier, or authority change invalidates the candidate.

## Exit gate and acceptance tests

`candidate_ready` passes only when:

- the manifest reconstructs and every referenced artifact exists;
- implementation-location claims have evidence and all gaps have owners;
- policy, deny, stop, readback, integration, and rollback tests pass for the scoped boundary;
- no material implementation choice exceeds the Stage 2 design; and
- the fixed candidate and its configuration identity are supplied to Stage 4.

Negative test: deleting or changing one acceptance-critical referenced artifact must invalidate reconstruction and prevent `candidate_ready`.
