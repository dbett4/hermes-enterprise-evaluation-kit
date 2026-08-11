# Deployment lifecycle

The method uses six stages. Skipping ahead does not fill in a missing decision; a
problem sends the work back to the stage that owns it. Stopping, deferring, suspending,
transferring, and retiring are all legitimate results.

| Stage | Question | Possible result |
|---|---|---|
| [1. Qualify](01-qualify.md) | Should an agent do this job at all? | `do_not_agentize`, `defer`, `qualify` |
| [2. Map](02-map.md) | What work, permissions, checks, and ownership are needed? | `return_to_qualify`, `approve_bounded_design` |
| [3. Configure and integrate](03-configure-integrate.md) | Does one identifiable build implement that design? | `return_to_map`, `candidate_ready` |
| [4. Test and authorize](04-assure-authorize.md) | What permission, if any, has this build earned? | `reject`, `not_ready_to_authorize`, `authorize_with_limits`, `authorize` |
| [5. Operate and adopt](05-operate-adopt.md) | Can named people run, challenge, stop, and own it? | `continue`, `contract`, `suspend`, `return_for_change` |
| [6. Review, transfer, or retire](06-review-transfer-retire.md) | Should it continue, change hands, or shut down? | `continue_or_improve`, `transfer`, `retire` |

In practice: first establish that the job is suitable and has an owner. Map its steps,
possible effects, limits, checks, and stop paths. Build exactly that design. Test the
fixed build, including its failure cases, before granting a narrow permission. During
operation, watch the same results and make sure the receiving team can stop and recover
without the builder. Review the full history when the system, owner, or policy changes.

## Ordered procedure and dependencies

A material design change returns to Stage 2. A material implementation change returns
to Stage 3. A missing acceptance result returns to Stage 4. An incident or ownership
failure narrows or suspends the affected operation first.

Every gate records the decision, owner, material reviewed, open work, and next allowed
action. An exception cannot invent missing permission or make a prohibited action safe.
The builder may recommend a result but cannot independently approve a material release.
Every stage applies all eight assurance modules at the depth required by the job's risk
tier.
