# Portable control kernel

**Status:** frozen vendor-neutral kernel

This layer defines how to qualify, design, implement, authorize, operate, and retire an organizational agent deployment without depending on any one runtime or provider. Product adapters may implement these rules; they may not redefine them or conceal a gap.

## Kernel contents

| Framework element | Governing artifact |
|---|---|
| Suitability and intake procedure, including a no-agent outcome | [Stage 1 — Qualify](../lifecycle/01-qualify.md) |
| Ordered process and cross-stage dependencies | [Six-stage lifecycle](../lifecycle/README.md) |
| Per-stage questions, decision rules, outputs, ownership, exceptions, and exit tests | [Lifecycle stages](../lifecycle/README.md) |
| Risk-tiered applicability and module depth | [Proportionality](proportionality.md) |
| Acceptance, negative-test, rejection, and waiver rules | Stage exit gates and [waivers and exceptions](waivers-and-exceptions.md) |
| Risk → control → implementation-slot → evidence → metric traceability | [Control traceability](control-traceability.md) |
| Version-pinned capability and gap classification | [Implementation-mapping contract](implementation-mapping-contract.md) |
| Examples and counterexamples usable without tacit knowledge | [Examples and counterexamples](examples-and-counterexamples.md) |

The [eight assurance modules](../assurance/README.md) apply across all stages at a depth selected by proportionality.

## Common vocabulary

### Terminal facts

- **Authorized intent:** an attributable work order and authority decision define what may happen.
- **Observed effect:** a source or target system, deterministic oracle, or independently controlled observer records what actually happened.
- **Disposition:** an actor or process with the declared separation class accepts, rejects, waives, compensates, or returns the result.
- **Reconciled result:** authorized intent, observed effect, and disposition agree, or every residual is explicitly classified and owned.

An agent's narrative is neither observed effect nor independent disposition.

### Authority outcomes

| Code | Neutral meaning | User-facing state |
|---|---|---|
| `D` | Denied because the action is prohibited, ungranted, stale, untrusted, or outside a proven enforcement boundary | `blocked` |
| `A` | Pre-authorized within deterministic, ratified bounds after an accepted first-occurrence human release | `runs automatically` |
| `H` | A named human releases the exact effect through an authenticated mechanism the producing agent cannot rewrite | `approval required` |
| `H2` | Two attributable releases through distinct credentials for a defined critical subset | `two approvals required` |
| `R` | Exceptional execute-then-review for a predesignated reversible time-critical action with a tested suspender | `emergency path` |

`R` is unavailable unless every trigger, deadline, notification, compensation, and suspender requirement is implemented and tested. Human approval cannot override an unconditional denial.

### Evidence classes

- **Declared:** asserted by a plan, manifest, producer, or configuration.
- **Runtime-reported:** emitted by the executing process about itself.
- **Observed:** read from a target, deterministic oracle, or separately controlled observer.
- **Role-separated:** produced by a separate process/session/context over fixed producer output.
- **Model-independent:** produced by a different model/configuration with separation evidence.
- **Human disposition:** attributable decision by an authorized person who saw the required evidence.
- **Organizationally independent:** separate accountable ownership and authority boundary; never inferred from technical separation alone.

### Implementation slots

Controls are assigned to one or more explicit locations:

1. human or process procedure;
2. organization policy and decision service;
3. identity, credential, or approval service;
4. execution boundary;
5. tool, connector, or integration boundary;
6. source or target system;
7. verification or disposition service;
8. evidence and retention service; and
9. operations, monitoring, or incident service.

A control description without a location, owner, known bypass, and evidence route is incomplete.

## Invariants

- Missing, stale, contradictory, or untrusted acceptance-critical facts fail closed.
- Delegation cannot amplify authority.
- A material change creates a new risk identity and an explicit novation decision.
- A hash establishes provenance only when canonical inputs and referenced artifacts are retained; it does not prove custody or enforcement.
- No material effect is accepted without target or deterministic readback.
- No recognized deliverable advances solely on producer self-report.
- Promotion is scoped and remains a recommendation until an authorized policy owner ratifies it.
- Incidents contract authority within their proven common-mode scope before recovery.
- Evidence history is append-oriented; supersession links records rather than rewriting them.
