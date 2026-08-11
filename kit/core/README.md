# Reusable core

This part of the project describes how to qualify, design, build, approve, run, and
retire an agent deployment without depending on one runtime or model provider. An
adapter may implement these rules; it cannot quietly redefine them or hide a missing
capability.

## Documents

- [Qualification](../lifecycle/01-qualify.md) is the suitability and intake procedure.
- [Lifecycle](../lifecycle/README.md) provides the ordered process and cross-stage dependencies;
  the linked stage files hold the per-stage questions.
- [Risk tiers](proportionality.md) define risk-tiered applicability and determine how
  much control and review a job needs.
- The stage decisions and [waiver rules](waivers-and-exceptions.md) cover acceptance,
  negative-test, rejection, and exception behavior.
- [Control traceability](control-traceability.md) connects a risk to a rule, its
  implementation, a check, a metric, and an owner.
- [Implementation mapping](implementation-mapping-contract.md) provides version-pinned
  capability and gap classification.
- [Examples and counterexamples](examples-and-counterexamples.md) show concrete cases.
- [Review areas](../assurance/README.md) lists the eight concerns checked at every
  lifecycle stage.

The original design names for those pieces remain: **Suitability and intake procedure**,
**Ordered process and cross-stage dependencies**, **Per-stage questions**,
**Risk-tiered applicability**, **Acceptance, negative-test, rejection, and waiver
rules**, **Control traceability**, **Version-pinned capability and gap classification**,
and **Examples and counterexamples**.

## Terms used in the detailed files

An **authorized request** says what may happen and who asked. An **observed result**
comes from the target system, a deterministic program, or another controlled source. A
**decision** accepts, rejects, waives, compensates, or returns that result. The three
must agree, or the remaining difference needs a name and owner. The producing agent's
summary is not an observed result or an independent decision.

Permissions use these internal codes:

| Code | Meaning | Plain-language state |
|---|---|---|
| `D` | Not allowed, out of scope, stale, or not safely enforceable | `blocked` |
| `A` | Allowed automatically within a narrow, previously approved rule | `runs automatically` |
| `H` | A named person releases the exact action through a separate mechanism | `approval required` |
| `H2` | Two people use separate credentials for a defined critical action | `two approvals required` |
| `R` | A predesigned reversible emergency action runs first and is reviewed immediately | `emergency path` |

`R` is available only when its trigger, deadline, notification, compensation, and stop
mechanism are implemented and tested. A person cannot approve something policy
unconditionally denies.

The detailed files distinguish configured facts, runtime self-reports, target readback,
separate-session checks, different-model checks, human decisions, and genuinely separate
organizational ownership. These are not interchangeable.

## Rules that do not change

- Missing or contradictory facts that matter to acceptance stop the affected work.
- Delegation can narrow permission but cannot widen it.
- A material configuration change needs a new decision about whether prior approval
  still applies.
- A hash helps identify retained canonical inputs; by itself it proves neither custody
  nor enforcement.
- An important effect needs target readback or a deterministic check.
- The producer's self-report cannot advance a material deliverable by itself.
- Successful operation may support a recommendation to widen a permission; a policy
  owner still has to approve the exact change.
- An incident narrows the affected permission before recovery work begins.
- New records supersede old ones by link instead of silently rewriting history.
