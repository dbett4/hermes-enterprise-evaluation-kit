# Stage 1 — Qualify

**Status:** frozen vendor-neutral kernel

Decide whether an agent is a sensible way to improve the workflow before spending time
designing one.

## Entry conditions — before starting

- A named workflow or domain owner can describe the intended outcome.
- Candidate sources, current process, affected people, and possible targets can be inventoried.
- Known legal, contractual, publication, spend, production, and safety boundaries are available or can be assigned for discovery.

## Required questions

1. What measurable outcome is sought, and what current baseline will it be compared with?
2. Is an agent needed, or would a deterministic control, conventional automation, process repair, or no change be simpler and safer?
3. Which sources are authoritative, and who may resolve conflicting or missing source facts?
4. Could the workflow read sensitive data, cause an external effect, spend money, change privileges, alter production, publish, or create an irreversible consequence?
5. Can every material effect be bounded, stopped, read back from its target, and reversed or brought to a named safe state?
6. Who owns the outcome, operating decision, unresolved risks, and eventual retirement?
7. Which facts remain unknown, and what evidence would resolve them?

## Decision rules

1. Choose `do_not_agentize` when the requested outcome is prohibited; no accountable owner exists; the work depends on concealed or impermissible data use; a material effect cannot be bounded or observed; or the control burden would exceed the plausible value.
2. Choose a conventional process or deterministic automation when the work is stable, fully specified, and gains no material value from model judgment or tool-directed adaptation.
3. Choose `defer` when ownership, source authority, target readback, legal basis, baseline, or another acceptance-critical fact is unknown. Record the owner and exact resume trigger; uncertainty never lowers the tier.
4. Choose `qualify` only when the bounded outcome, baseline, initial action inventory, owner, and hard ceilings are explicit.
5. Apply the proportionality procedure. The highest applicable trigger sets the initial tier; missing facts force deferral rather than a lower classification.

## Outputs — what to save

- Qualification record and disposition
- Outcome, baseline, and value hypothesis
- Candidate workflow, source, target, and effect inventory
- Initial risk tier and module-depth profile
- Named outcome owner and discovery owners
- Hard ceilings, scope exclusions, unresolved facts, and resume triggers

## Accountable owner — who decides

The workflow or domain owner owns the qualification decision. An evaluator may recommend a path but cannot supply business ownership or waive a hard ceiling.

## Exceptions and escalation

Discovery may proceed under a time-bounded exception only when it creates no material effect and does not cross a prohibited data, credential, spend, publication, or production boundary. Record the exception under the common waiver procedure. Escalate conflicting authority, legal, safety, or ownership claims to the named policy owner; otherwise defer.

## Exit gate and acceptance tests

`qualify` passes only when all of the following are true:

- the outcome, baseline, accountable owner, and source authority are named;
- agent use has a stated advantage over the simpler alternatives;
- known effects and immediate disqualifiers have been inventoried;
- the initial tier is reproducible from recorded facts; and
- every unresolved fact has an owner and does not block safe mapping.

Negative test: a candidate with no target-system readback for a material effect must produce `do_not_agentize` or `defer`, never `qualify`.
