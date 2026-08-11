# Six-stage deployment lifecycle

**Status:** frozen vendor-neutral kernel

Use the stages in order. A return decision moves to the named earlier stage; it never permits a later gate to infer missing evidence. A rejection, deferral, suspension, transfer, or retirement is a valid terminal disposition when its owner and evidence are recorded.

| Stage | Governing question | Exit decisions |
|---|---|---|
| [1. Qualify](01-qualify.md) | Should this workflow be agentized at all? | `do_not_agentize`, `defer`, or `qualify` |
| [2. Map](02-map.md) | What work, authority, evidence, and ownership design is required? | `return_to_qualify` or `approve_bounded_design` |
| [3. Configure & Integrate](03-configure-integrate.md) | Does one reconstructable candidate implement the approved design? | `return_to_map` or `candidate_ready` |
| [4. Assure & Authorize](04-assure-authorize.md) | Has the candidate earned a bounded operating decision? | `reject`, `not_ready_to_authorize`, `authorize_with_limits`, or `authorize` |
| [5. Operate & Adopt](05-operate-adopt.md) | Can named people operate, challenge, stop, and own it? | `continue`, `contract`, `suspend`, or `return_for_change` |
| [6. Review, Transfer & Retire](06-review-transfer-retire.md) | What should happen next from reconciled evidence? | `continue_or_improve`, `transfer`, or `retire` |

## Ordered procedure and dependencies

1. Stage 1 establishes suitability, baseline, initial tier, and accountable owner.
2. Stage 2 decomposes the work and converts risk into controls, implementation slots, evidence, metrics, and hard ceilings.
3. Stage 3 instantiates only that approved design and records the candidate's complete configuration identity.
4. Stage 4 tests the fixed candidate and grants no more authority than the evidence supports.
5. Stage 5 operates inside that grant while measuring effects, adoption, exceptions, and drift.
6. Stage 6 reconciles the evidence and explicitly continues, changes, transfers, or retires the deployment.

Material design changes return to Stage 2. Material implementation changes return to Stage 3 and create a new risk identity. Missing acceptance evidence returns to Stage 4. Ownership failure, incident, or policy drift contracts or suspends operation before re-entry.

## Common rules

- Apply the [proportionality procedure](../core/proportionality.md) at Stage 1, refine it at Stage 2, and recalculate it after every material change.
- Every stage applies all eight assurance modules at the selected depth; no module disappears merely because its control is lightweight.
- Every gate records the decision, accountable owner, evidence reviewed, open obligations, and next permitted action.
- Use the [waiver and exception procedure](../core/waivers-and-exceptions.md). A waiver never supplies missing authority, makes a prohibited action permissible, or converts unknown evidence into a pass.
- A producing agent or builder may recommend a disposition but cannot independently close its own material acceptance or authorization gate.
- Continue only through the exit gate's acceptance tests. “Work completed” is not a gate result.

The lifecycle, the eight [assurance modules](../assurance/README.md), and the [core contracts](../core/README.md) together form the portable control kernel.
