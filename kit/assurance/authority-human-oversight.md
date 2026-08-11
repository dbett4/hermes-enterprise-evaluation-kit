# Assurance — Authority & human oversight

**Status:** frozen vendor-neutral kernel

## Risk signals

External effects, money, publication, production, sensitive data, privilege, destructive or irreversible action, broad credential reach, novel action/target pairs, authority-system change, approval fatigue, or segregation-of-duties requirements.

## Control rules

- Default deny when grant, attribute freshness, enforcement point, or target is missing or untrusted.
- Classify each action as `D`, `A`, `H`, `H2`, or eligible `R`; human approval cannot override unconditional denial.
- Scope grants to action class, resource, environment, configuration identity, duration, and purpose; delegation cannot amplify them.
- A new tuple begins with `H`. `A` requires accepted first-occurrence evidence, deterministic bounds, readback/recovery, and policy-owner ratification.
- Show the approver the exact effect and required evidence through an authenticated surface the producing agent cannot rewrite.
- Name stop, suspension, revocation, recertification, exception, and disposition owners.

## Implementation slots

Organization policy, identity/credential service, approval mechanism, tool or target enforcement boundary, human procedure, and operations/incident service.

## Required evidence

Authority Decision Record; grant and evaluated attributes with freshness; exact proposal/diff; authenticated release; prestate/poststate or output evidence; stop/revocation readback; overrides, denials, and disposition.

## Metrics and triggers

Accepted unauthorized or out-of-scope effects = 0. Track denial/bypass attempts, approval/denial/override rates, review latency, reversals, repeated prompts, after-hours concentration, stale grants, and failed revocations. Threshold breach narrows, freezes, rotates, or suspends; it never lowers the bar.

## Tier application

- L1: named owner, explicit read/draft bounds, hard ceilings, and human disposition for material use.
- L2: deterministic enforcement/readback, first-occurrence release, tested stop/recovery, and periodic review.
- L3: stronger credential/release separation, dual control where required, independently controlled evidence where claimed, bypass tests, and formal recertification.

## Exit rule

No material action advances without an attributable authority source, effective enforcement boundary, observed effect route, and accountable disposition owner.
