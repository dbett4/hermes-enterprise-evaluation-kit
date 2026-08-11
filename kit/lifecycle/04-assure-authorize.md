# Stage 4 — Test & Authorize

**Status:** frozen vendor-neutral kernel

Test the fixed candidate, including the ways it should fail, and grant no more permission
than the accepted results support.

## Entry conditions — before starting

- Reconstructable Stage 3 candidate with fixed configuration identity
- Preregistered acceptance criteria, negative cases, and critical-regression rule
- Available verifier, policy owner, and target-system evidence route

## Required questions

1. Which criteria require deterministic, role-separated, model-independent, human, or organizationally independent evidence?
2. Are producer outputs fixed before a checker or approver sees them?
3. Did allow, deny, stale-input, unauthorized-role, bypass, stop, rollback, and recovery cases behave as specified?
4. Does observed target state reconcile to authorized intent and the proposed disposition?
5. Which residual risks are accepted, constrained, waived, compensated, or rejected, by whom and until when?
6. What exact action, resource, environment, configuration identity, duration, and contraction trigger would an authorization cover?

## Decision rules

1. A producing agent or builder cannot independently accept its own material output or authorize its own deployment.
2. Self-reported completion is never sufficient. Use the evidence class fixed in Stage 2 and preserve checker context and separation evidence.
3. A critical negative-test failure, unexplained oracle failure, missing effect readback, failed stop/rollback path, or contradictory authority record produces `reject` or `not_ready_to_authorize`.
4. Missing evidence is `unknown`, not pass. A waiver cannot turn unknown acceptance-critical evidence into success.
5. Authorization is scoped to the exact action class, resource, environment, configuration identity, owner, duration, and ceilings tested.
6. The first occurrence of a pre-authorization candidate remains human-released. Only a policy owner may ratify a subsequent bounded pre-authorization rule from the accepted observed record.
7. If every mandatory criterion passes but a bounded residual requires a temporary compensating control, use `authorize_with_limits`; otherwise use `authorize` or return.

## Outputs — what to save

- Criteria-by-criteria and negative-case results
- Producer-fixity and verifier-separation evidence
- Authorized-intent, observed-effect, and disposition reconciliation
- Residual-risk, waiver, compensation, and exception register
- Scoped authority decision, operating envelope, expiry, and contraction triggers
- Explicit reject or not-ready record when authorization is withheld

## Accountable owner — who decides

The policy or authority owner owns the authorize, constrain, waive, or reject decision. The verifier owns only the stated verification result. The builder and producing agent cannot self-authorize.

## Exceptions and escalation

Critical failures are non-waivable for the affected scope. A noncritical waiver follows the common procedure and must identify the reviewed evidence, compensating control, expiry, monitor, and revocation trigger. Conflicting verifier and owner conclusions remain unresolved and escalate; the more convenient conclusion does not win.

## Exit gate and acceptance tests

`authorize` or `authorize_with_limits` passes only when:

- all mandatory acceptance and negative-test criteria pass;
- observed effects reconcile to authorized intent and accepted disposition;
- the decision names scope, configuration identity, owner, duration, ceilings, and contraction triggers;
- every waiver is valid, unexpired, and monitored; and
- operating, stop, support, evidence, and escalation owners are ready.

Negative test: a complete-looking packet with approval after execution must produce `not_ready_to_authorize`; timestamp order is acceptance-critical unless a separately authorized exceptional path applies.
