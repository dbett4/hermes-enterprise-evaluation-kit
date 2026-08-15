# Architecture

**Updated:** 2026-08-04

**Validated runtime:** Hermes Agent v0.20.0 / tag `v2026.8.3`

The Evaluation Kit is an independent deployment prototype, not an official Nous product.
Its job is to turn an ordinary mission into a known Hermes configuration and a result
that another person or program can inspect.

```text
mission
  -> organization policy
  -> one approved configuration
  -> Hermes execution
  -> target readback and checks
  -> checker or human decision
  -> JSON run record
  -> continue, change, hand over, or retire
```

The v0.1 resolver selects from a small catalog using explicit rules. It does not claim
that Hermes v0.20 performs general task-aware model selection.

## Components

| Component | Responsibility | Limit |
|---|---|---|
| Mission view | Collect the outcome, inputs, deadline, approvals, and status | Normal users do not configure models or tool graphs |
| Reusable core | Define lifecycle, risk tiers, permissions, review, exceptions, and retirement | Contains no Hermes release assumptions |
| Packs | Add organization policy, reusable capabilities, and workflow-specific rules | May narrow organization policy, never widen it |
| Hermes adapter | Map the approved configuration to profiles, skills, goals, tools, isolation, and routing | Every requirement is tied to the pinned release and its known limits |
| Operations | Read target state, handle incidents, track ownership, and decide what happens next | Repository records remain mutable until separate custody is implemented |

Hermes is the front door and reference runner. The reusable core is separate so the
operating rules do not depend on accidental runtime behavior.

## Packs and blueprints

An **organization pack** defines data zones, providers, permission ceilings, budget
rules, identities, retention, and the configurations an administrator has approved.

A **capability pack** adds one reusable piece such as a connector, checker, storage
adapter, browser restriction, or recovery mechanism. It includes permissions, failure
modes, and tests.

A **workflow pack** describes one kind of job: its vocabulary, input and output format,
possible actions, deterministic checks, exceptions, and fixtures.

The resolved **Assembly Blueprint** records the exact core schema, Hermes adapter,
pack versions, configuration, owners, effective dates, serialization method, and
manifest hash. The hash identifies the inputs. It does not prove signing, safe custody,
or enforcement.

Before a run starts, the validator checks that:

- versions and dependencies are compatible and the dependency graph has no cycles;
- organization policy wins every conflict rather than relying on load order;
- every possible action names its permission, enforcement location, bypasses, stop
  behavior, and target readback; and
- every important output has a compatible checker and a final state.

Missing, stale, or conflicting information stops with `needs_policy_decision`.

## Configuration selection

The administrator approves a few configuration families—for example, latency-sensitive,
balanced, or assurance-heavy. The resolver can choose only among configurations allowed
for the task, data, action, consequence, and review requirements. The run record stores
both requested and resolved provider/runtime details, including fallbacks.

Any future adaptive selector has to earn its place through results against fixed tests.
Until then, “best model for the task” is wording this project deliberately avoids.

## Three synthetic jobs

The first suite uses horizontal action types rather than one industry story:

| Job | What it exercises |
|---|---|
| Decide | Source-grounded analysis, deterministic policy checks, a recommendation, and human review |
| Coordinate | Work across several fictional owners, bounded clarification, and handoff without destructive action |
| Act | One operator-approved change in the deployment lab, target readback, idempotent resume after a post-commit failure, and a stop before production |

Finance, HR, legal, IT, healthcare, and other domains can be added as workflow packs.
Public-sector finance is optional, not the default or a requirement for this preview.

## Current Hermes limits

Hermes v0.20 provides useful profiles, goals, approvals, deny rules, boards, webhooks,
Iron Proxy, managed scope, provider routing, and fallback behavior. It does not by
itself establish enterprise IAM, adversarial isolation, immutable record custody, hard
tenant isolation, or outcome-aware model selection.

The exact tests and qualifications are in
[`preflight/v0.20-preflight-report.md`](preflight/v0.20-preflight-report.md).
