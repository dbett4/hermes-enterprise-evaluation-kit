# Stage 2 — Map

**Status:** frozen vendor-neutral kernel

Turn the qualified workflow into a specific design: steps, permissions, checks, failure
paths, and owners.

## Entry conditions — before starting

- Accepted Stage 1 qualification record
- Named outcome and policy owners
- Available source and target-system evidence routes, or explicit open dependencies

## Required questions

1. What are the ordered work steps, decisions, actions, handoffs, exceptions, and failure paths?
2. For each action, who acts for whom, under which grant, on which resource and environment?
3. Which effects are denied, pre-authorized, human-released, dual-released, or exceptional execute-then-review candidates?
4. Where will each authority, data, execution, stop, and readback control operate, and what bypasses remain?
5. What acceptance criterion and evidence class proves each output or effect?
6. Which person or independent process provides terminal disposition?
7. What configuration, supplier, integration, continuity, adoption, cost, and retirement dependencies alter the risk identity?
8. Which metric will reveal success, drift, failure, fatigue, or uneconomic operation?

## Decision rules

1. Decompose every material effect into an action class, resource, environment, consequence, reversibility, authority outcome, enforcement point, readback, stop path, and owner.
2. Default to denial when a grant, required attribute, control location, or evidence route is missing, stale, contradictory, or untrusted.
3. A downstream delegation may only narrow the upstream grant; it cannot amplify it.
4. A new action-class/resource/environment tuple begins with human release. Pre-authorization is available only after an accepted first occurrence, observed effect, tested recovery, and policy-owner ratification of the bounded rule.
5. Assign all eight assurance modules at the depth produced by the proportionality procedure. A module-specific uplift overrides the tier floor.
6. For each material risk, complete one trace: risk → control → implementation slot → evidence → metric. An unmapped link is an open design defect.
7. Return to Stage 1 if the required control burden defeats the value case or the workflow no longer qualifies.

## Outputs — what to save

- Workflow, action, exception, and handoff map
- Authority Decision Record for every executable action class
- Risk tier, module-depth profile, and control traceability matrix
- Data, identity, integration, execution-boundary, and evidence-custody design
- Acceptance criteria, negative cases, verifier/disposition plan, and metrics
- Deployment boundary, hard ceilings, operating-owner plan, and unresolved-risk register

## Accountable owner — who decides

The workflow or domain owner owns the mapped outcome. The policy owner owns authority classifications and waivers. Control specialists own only their recorded advice; they do not inherit outcome accountability.

## Exceptions and escalation

Unmapped effects, bypasses, or unverifiable outcomes remain open defects. A design exception must name the failed rule, compensating control, owner, expiry, and evidence; it cannot waive a prohibited outcome or missing authority. Material disagreements return to Stage 1 or escalate to the named policy owner.

## Exit gate and acceptance tests

`approve_bounded_design` passes only when:

- every material action has an authority source, enforcement point, bypass statement, stop path, observed-effect route, disposition, and owner;
- every assurance module has an assigned depth and complete control trace;
- acceptance criteria and negative tests are fixed before implementation;
- all hard ceilings and unresolved risks are explicit; and
- the design remains inside the Stage 1 qualification and value boundary.

Negative test: an action with a valid-looking approval but no independent final-effect readback must return to mapping; approval alone cannot close the trace.
