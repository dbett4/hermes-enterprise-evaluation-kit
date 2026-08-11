# Assurance — Identity, security, data & legal

**Status:** frozen vendor-neutral kernel

## Risk signals

Sensitive, regulated, privileged, licensed, or client data; external integrations; secrets; delegated identity; broad credentials; adversarial inputs; production access; geographic or purpose restrictions; orphaned identity; or unclear legal/contractual authority.

## Control rules

- Give every workload a stable identity, bound owner, purpose, environment, scope, credential reference, configuration identity, expiry, recertification date, and lifecycle state.
- Apply least scope, purpose limitation, data minimization, secrets separation, and no-amplification delegation.
- Separate administrative guardrails from adversarial isolation; test the actual execution and egress boundaries relied upon.
- Treat missing, stale, or untrusted identity/data/legal attributes as denial.
- Provision, activate, change with novation, suspend, revoke, retire, and recertify with source-system readback. Suspend orphans automatically.

## Implementation slots

Identity and credential service, policy decision/enforcement point, execution boundary, network/egress boundary, connector, source/target system, and legal/data-governance procedure.

## Required evidence

Identity/grant inventory; owner/purpose and delegation chain; data classification and approved routes; credential and boundary configuration; isolation/egress tests; access review; change/novation decision; suspension/revocation/retirement readback.

## Metrics and triggers

Active orphan identities = 0; expired grants active = 0; impermissible data routes = 0; boundary-test failures accepted = 0. Missed recertification, owner loss, policy drift, or failed revocation suspends or narrows access.

## Tier application

- L1: named identity/owner, bounded data and credential use, basic secret handling, expiry, and revocation path.
- L2: tested execution/egress boundary, point-in-time access inventory, change novation, periodic review, and target readback.
- L3: stronger workload identity, just-in-time or privileged controls as appropriate, adversarial boundary tests, independent review, and formal lifecycle reconciliation.

## Exit rule

No execution proceeds with an orphaned identity, unclassified data route, unbounded credential, unresolved legal restriction, or unproved load-bearing boundary.
