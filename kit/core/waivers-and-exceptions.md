# Waivers and exceptions

**Status:** frozen vendor-neutral kernel

A waiver is an attributable, time-bounded decision to accept a specific residual after reviewing evidence and installing any required compensating control. An exception is the observed condition that departs from a rule or expected state. Neither term means “ignore the gate.”

## Non-waivable conditions

No waiver may:

- make a prohibited or unlawful purpose permissible;
- supply missing authority, ownership, or required human independence;
- override an unconditional denial or required dual-control rule;
- convert missing, stale, contradictory, untrusted, or otherwise unknown acceptance-critical evidence into a pass;
- accept an unbounded material effect, unknown target, or unavailable stop/readback path;
- conceal a material change, bypass, incident, or conflict of interest;
- relabel mutable evidence as independently controlled or immutable; or
- expand authority beyond the qualifying scope or policy ceiling.

If one of these conditions applies, narrow, return, defer, suspend, reject, or do not agentize.

## Required waiver record

Every waiver records:

1. stable waiver ID, stage, gate, requirement, and affected scope;
2. exact exception and why ordinary remediation is not presently used;
3. evidence reviewed and evidence basis;
4. consequence, residual risk, and affected tier/module depth;
5. compensating control, implementation slot, owner, and known bypass;
6. authorized decision-maker and proof of authority;
7. issue time, effective time, expiry, review cadence, and maximum renewals;
8. monitoring metric, threshold, suspension/revocation trigger, and incident route;
9. remediation owner, target date, and closure evidence; and
10. disposition: approved, rejected, expired, revoked, remediated, or superseded.

The builder or producing agent cannot approve its own material waiver. Silence, continued operation, or repeated approval never renews a waiver.

## Procedure

1. Contain any active effect that is outside the current authority or safe boundary.
2. Classify the exception and test the non-waivable list.
3. Prefer remediation, scope reduction, safer implementation, or human release.
4. If waiver remains permissible, assemble the required record and compensating-control evidence.
5. Obtain the decision before execution. A separately designed exceptional execute-then-review path is not a retroactive waiver.
6. Validate the waiver at every affected gate and run; fail closed when it is missing, stale, revoked, or out of scope.
7. Close through remediation, expiry, revocation, or supersession and preserve the linked history.

## Gate behavior

- A valid noncritical waiver can produce a constrained pass only where the gate explicitly allows it.
- Critical acceptance failures remain reject or not-ready outcomes.
- A compensating control has its own evidence and metric; prose is not implementation.
- Repeated similar waivers trigger design review. They do not normalize the exception or lower the tier.
