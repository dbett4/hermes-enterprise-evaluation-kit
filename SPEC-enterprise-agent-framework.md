# Design notes for the Hermes Enterprise Field Kit

**Updated:** 2026-08-11

## The problem

Hermes v0.20 already provides profiles, goals, tools, approvals, boards, provider
routing, and isolation options. An organization still has to decide which jobs are
appropriate for an agent, choose a known configuration, limit what it can do, check
the result, and hand the system to someone who owns it.

This repository explores that surrounding work. It combines:

- a small set of operating rules that do not depend on Hermes;
- an adapter pinned to Hermes v0.20.0 / tag `v2026.8.3`;
- organization and workflow configuration packs; and
- three fictional jobs that can be run and inspected locally.

A passing test against one tag says something about that release. It does not show
that every installed copy of Hermes has the same code or configuration.

This is an independent project. “Hermes for organizations” describes the problem I
am working on; it is not an official Nous product or endorsement.

## The design

The user supplies the job, inputs, deadline, and any approvals that matter. The
organization supplies a small catalog of allowed configurations. Each configuration
names the model, provider, effort, tools, permissions, and checks.

The resolver chooses one configuration from that catalog. If no approved choice fits,
it stops instead of assembling a new combination on the fly. An expert may override
the choice only where policy allows, and the override is recorded before execution.

Hermes remains the runner. The surrounding code records which configuration was
chosen, runs checks that do not depend on the model's own explanation, and leaves
human decisions to a person. A successful run never widens its own permissions.

The Markdown and JSON records in this preview are ordinary mutable files. Their stable
IDs and hashes make a run easier to reconstruct; they do not provide signing,
immutable storage, or access control.

## Key decisions

- Use six stages: qualify, map, configure, authorize, operate, and transfer or retire.
- Scale the depth of review to the risk of the job rather than applying every control
  at maximum depth.
- Keep the reusable operating rules separate from the Hermes-specific release map.
- Say whether each requirement is handled by Hermes, configuration, this kit,
  surrounding infrastructure, or not at all.
- Use fictional decide, coordinate, and act examples. Public-sector finance remains
  an optional workflow pack rather than a dependency of the core design.
- Keep readable decisions in Markdown and structured run details in JSON.
- Treat a separate session, a different model, a deterministic program, and a human
  reviewer as different kinds of checking. None stands in automatically for another.
- Publish the known gaps instead of filling them with assumptions about private or
  future Hermes capabilities.

## What I checked in Hermes v0.20

The exact-tag preflight ran 214 focused tests across profiles, goals and completion
behavior, approvals and deny rules, webhooks, Iron Proxy, managed scope, Kanban boards,
provider routing, and fallback behavior. Its result is `PASS_WITH_LIMITS`.

Those limits are specific:

- profiles are unsigned by default;
- webhook signatures require a configured secret;
- managed scope is not an OS sandbox;
- goal completion is judged by the model;
- Kanban is not an immutable audit log;
- Iron Proxy does not replace process or container isolation; and
- provider fallback does not choose the best model for an arbitrary job.

The full result is in
[`kit/preflight/v0.20-preflight-report.md`](kit/preflight/v0.20-preflight-report.md).

## The three exercises

1. **Decide:** review a fictional vendor-policy exception and recommend what to do.
   The program may recommend; it cannot make the legal or policy decision.
2. **Coordinate:** prepare a fictional employee-offboarding packet without taking the
   destructive actions described in it.
3. **Act:** change a rate-limit setting in a local staging service, read it back, and
   show how to reverse it. Production promotion remains a human step.

Each exercise begins with the job and organization rules, selects one approved
configuration, keeps production separate from checking and review, and saves enough
information to understand the run later.

S1 has a local deterministic demo. The committed S1 record that names a provider and
model predates the runtime identity guard. Its contents are internally consistent, but
the provider and model fields were entered by the operator. It is not proof that the
declared Hermes release or model produced the output.

## Repository layout

- [`kit/lifecycle/`](kit/lifecycle/README.md) describes the six stages.
- [`kit/instrument/`](kit/instrument/README.md) contains the intake schema and local
  evaluator, including the option to decline an unsuitable job.
- [`kit/mapping/`](kit/mapping/README.md) contains the 318-row Hermes map and seven
  known gaps.
- [`packs/`](packs/README.md) contains fictional organization and workflow settings.
- [`reference-suite/`](reference-suite/README.md) contains the three exercises and
  their checks.
- [`PROOF.md`](PROOF.md) maps the important results to commands anyone can rerun.

## What this project does not show

- a customer deployment or production operating history;
- enterprise SSO, a real identity provider, or hard tenant isolation;
- immutable audit storage or independent record custody;
- adaptive model selection;
- measured adoption, cost savings, or ROI;
- a Portal cost run; or
- compatibility beyond the pinned Hermes release.

## Current state

The public map contains 318 valid rows and seven gaps. Eight negative cases stop in
their expected states. The credential-free S1 demo and the full `./scripts/proof.sh`
check pass. Three committed reference records are dry runs, and the older
operator-recorded S1 record remains explicitly unattested.

The next meaningful step would be a separately authorized live run with native CLI
identity capture, followed by review from someone other than the author. Neither is
claimed by this repository today.
