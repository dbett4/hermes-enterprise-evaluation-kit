# Product principles

**Updated:** 2026-08-04

**Status:** preview; items with an open build ticket or owner decision are not final

**Detailed specification:** [SPEC-enterprise-agent-framework.md](../SPEC-enterprise-agent-framework.md)

This repository is an independent project called the **Hermes Enterprise Field Kit**.
“Hermes for organizations” is a useful description of the problem, not a product name
or a claim of support from Nous.

## Start with the job, not the knobs

A user should say what they need done and provide the relevant source material. They
should not have to choose a model, provider, effort setting, tool graph, fallback chain,
or checking strategy.

Those choices come from an organization-approved catalog. An administrator sets the
outer limits. An expert defines the exact configurations. The resolver selects one
configuration from that catalog, or stops and asks for a policy decision when none fit.
It does not improvise a new combination.

The first resolver is deliberately boring: explicit rules over a small catalog. Hermes
v0.20 does not provide general task-aware model selection, and this project does not
pretend otherwise.

## Keep Hermes visible

Hermes is the main execution path, not a replaceable logo on a generic portal. The
adapter uses documented profiles, skills, goals, approvals, boards, webhooks, provider
settings, and isolation options before adding something alongside them.

The reusable rules remain independent of Hermes because authority and operational
safety should not depend on undocumented runtime behavior. For each rule, the release
map says whether Hermes supplies it directly, configuration supplies it, the kit adds
it, surrounding infrastructure is needed, or there is still a gap.

Use the strongest documented Hermes feature that fits. Do not weaken it just to make
the generic design look symmetrical.

## Three levels of detail

The project exposes more detail as the audience becomes more technical:

| View | Who it is for | What they work with |
|---|---|---|
| Mission | Person requesting the work | Outcome, inputs, deadline, material approvals, status, result |
| Policy | Administrator or policy owner | Allowed data, providers, permissions, budgets, retention, review requirements |
| Configuration | FDE or platform owner | Exact profile, prompt, model, tools, isolation, routing, checks, and manifest |

The UI can call a state “approval required” while the implementation stores a more
precise authority code. Hiding expert settings from a normal user is fine; hiding them
from the run record is not.

## How one run is chosen

1. Read the mission and classify the work, data, possible actions, reversibility, and
   review needs.
2. Apply the organization's provider, data, permission, cost, and tool limits.
3. Choose exactly one named configuration from the approved catalog.
4. Stop before execution if the choice is stale, unsupported, inconsistent, or missing
   a required signature or pin.
5. Create the mapped Hermes profile, goal, board, and tool configuration.
6. Compare what was requested with target readback and the required checker or human
   decision.
7. Save the selected configuration, inputs, outputs, checks, exceptions, and final
   state.

An override is recorded before execution with its authorizer, reason, scope, duration,
and extra checks. A silent fallback outside the approved configuration is a bug.

## Authority follows observed results

The rule I use is simple: an agent gets permission only for a specific kind of
action when all three facts line up:

- someone with authority asked for that action;
- the target system or a deterministic check shows what actually happened; and
- the required checker or person accepted, rejected, waived, or returned the result.

The producing agent saying “done” is not enough.

Different kinds of checking should not be blurred together. A second session can show
role separation; it does not automatically show organizational independence. A
different model can reduce some common-mode failures; it is still a model. A
deterministic program is repeatable if its inputs and result are retained. A human
decision needs a named authorized person, what they reviewed, a timestamp, and an
outcome.

Successful operation may support a recommendation to widen a permission. It never
widens permission by itself. An incident narrows the affected permission first. A
material model, prompt, tool, policy, runtime, or checker change needs an explicit
decision about whether the old approval still applies.

Publication, client data, payments, legal holds, destructive production changes, and
separation-of-duty actions can still require a person or two-person approval.

## Packs

A deployment combines three kinds of versioned input:

- an organization pack sets the outer policy and approved configuration catalog;
- capability packs add reusable connectors, checkers, storage, or recovery behavior;
- a workflow pack defines the language, inputs, actions, fixtures, and checks for one
  kind of job.

A pack may narrow organization policy. It may not widen it, change the meaning of an
authority decision, or conceal a material runtime choice. The resolved blueprint pins
the selected versions, owners, effective dates, and manifest hash. The hash helps track
which inputs were used; it is not a signature or access-control system.

## Records are not an audit system

The Markdown and JSON files in this preview are normal mutable repository files. Stable
IDs, hashes, and links make a run easier to reconstruct. They do not provide immutable
storage, completeness, retention enforcement, or non-repudiation.

Any audit-reliance claim would need independently controlled storage, population
completeness checks, access and change history, retention rules, and acceptance by the
relevant assessor.

## Things this version does not claim

- Hermes v0.20 does not choose the best model for an arbitrary job.
- Boards, profiles, goals, and repository records are not an immutable enterprise audit
  system.
- Managed scope does not replace OS or container isolation.
- Iron Proxy alone is not the complete adversarial security boundary.
- This kit does not supply native enterprise IAM/SSO, hard tenant isolation, adoption,
  ROI measurement, or independently controlled record custody.
- There is no cost result before an authorized Portal run.
- One synthetic suite does not establish that the method works for every industry.
- This is not an official Nous product, partnership, or endorsement.

Naming an official product belongs to Nous. This repository stays focused on the
engineering method.
