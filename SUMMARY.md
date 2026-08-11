# Project summary

**Updated:** 2026-08-10

**Detailed design:** [SPEC-enterprise-agent-framework.md](SPEC-enterprise-agent-framework.md)

Hermes already provides profiles, goals, approvals, tools, boards, provider routing,
and other useful agent primitives. This project explores the part an organization
still has to build around them: deciding which jobs are appropriate, choosing a known
configuration, checking the result outside the model's own narration, and handing the
system to an accountable operator.

I designed the first version around Hermes rather than hiding it behind a generic
framework. Users describe a job and desired outcome. Organization policy chooses the
model, provider, effort, tools, permissions, and checks from a small approved catalog.
Experts can inspect or override that choice where policy allows.

## What v0.20 provides—and what it does not

The pinned Hermes release passed a 214-test preflight covering profiles, goals and
completion behavior, approvals and deny rules, webhooks, Iron Proxy, managed scope,
Kanban boards, provider routing, and fallback behavior.

I use those pieces where they fit, but do not stretch them into larger claims. Profiles
are unsigned by default. Webhook signatures need a configured secret. Managed scope is
not a sandbox. Goals are judged by the model. Kanban is not an immutable audit log.
Iron Proxy does not replace OS isolation, and provider fallback does not choose the best
model for a task.

## The synthetic exercises

1. **Decide:** review a vendor-policy exception and return a recommendation, not a
   binding decision.
2. **Coordinate:** prepare an employee-offboarding packet without performing destructive
   actions.
3. **Act:** make and verify a reversible rate-limit change in a local staging service,
   while leaving production promotion to a person.

Each exercise starts with the job and organization rules, selects one approved
configuration, separates the produced output from later checking and human review, and
writes enough JSON to reconstruct the run. Public-sector finance remains an optional
workflow pack rather than the foundation of the project.

## Where it stands

The published map contains 318 rows and seven known gaps. Three committed reference
records are dry runs. One older S1 artifact is labeled
`operator-recorded-unattested`: its contents are consistent, but there is no native
runtime identity showing which Hermes binary or release produced it.

The vendor-neutral core is stable. Adaptive model selection remains future work until
there are enough real results to justify it. No Portal cost run or production change is
part of this repository.
