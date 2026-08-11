# Stage 6 — Review, Transfer & Retire

**Status:** frozen vendor-neutral kernel

Use the operating history to decide whether to continue, change, transfer, or retire the
system.

## Entry conditions — before starting

- Defined review trigger, cadence, expiry, incident, or ownership event
- Reconciled run, incident, adoption, cost, authority, and residual-risk evidence
- Current accountable owner and identified continuation, transfer, or retirement authority

## Required questions

1. Does the evidence support continuation, contraction, improvement, transfer, or retirement?
2. Has any model, prompt, tool, policy, runtime, integration, verifier, environment, owner, or supplier change created a new risk identity?
3. Which grants, credentials, sessions, schedules, integrations, data, records, and open obligations must move or close?
4. Can a receiving owner prove acceptance and operate, challenge, stop, recover, and retire the deployment?
5. What evidence must be retained, transferred, archived, or disposed, under which custody and retention rule?
6. Has final target and identity readback proved that retired effects and access are actually closed?

## Decision rules

1. `continue_or_improve`: retain or contract the current authority; send material design changes to Stage 2 and material implementation changes to Stage 3. Promotion remains a scoped recommendation until ratified.
2. `transfer`: keep accountability with the current owner until the receiving owner accepts the exact configuration, authority, evidence, support, and open-obligation set. Transfer cannot silently novate authority.
3. `retire`: stop execution, revoke grants and credentials, close schedules and integrations, reconcile target state, preserve required evidence, and disposition every open obligation.
4. An identity identifier is never reused after retirement. Unresolved ownership or revocation proof blocks transfer or retirement completion.
5. Evidence history is appended and linked to superseding decisions; a later decision does not rewrite the earlier record.

## Outputs — what to save

- Branch decision, rationale, evidence reviewed, and owner
- Updated risk, authority, configuration, and lifecycle records
- Change/novation record or transfer acceptance
- Stop, revocation, target-state, integration, and retirement readbacks
- Retention/disposition record and closed/open obligation register
- Next review date or terminal closure record

## Accountable owner — who decides

The current accountable owner retains responsibility until a receiving owner accepts transfer or the retirement evidence closes every required obligation. A platform or support operator cannot unilaterally declare ownership transferred.

## Exceptions and escalation

An incomplete transfer remains with the prior owner. A retention or legal obligation cannot be waived by deleting evidence. If revocation, stop, target state, or ownership cannot be proved, suspend the affected scope, record the exception owner, and escalate rather than declaring closure.

## Exit gate and acceptance tests

A branch completes only when:

- its decision and accountable owner are explicit;
- authority, configuration identity, integrations, evidence custody, and open obligations reconcile to the selected branch;
- a transfer has receiving-owner acceptance, or retirement has stop and revocation readback; and
- every remaining exception has an owner, expiry or review date, and bounded consequence.

Negative test: removing a local deployment record without revoking its external credential must fail retirement and leave the prior owner accountable.
