# Product architecture (proposed name: Hermes Assembly)

**As of:** 2026-08-04<br>
**Status:** product architecture adopted for the generalized-enterprise build; B17 authority-architecture v4 is ratified as design and awaits B02/B03/B05 implementation<br>
**Validated runtime:** Hermes Agent v0.20.0 / tag `v2026.8.3`

Hermes Assembly is the proposed organization-facing product experience. The public asset in this repository remains the **Enterprise Agent Deployment Field Kit for Hermes** unless Nous adopts and clears the product name.

## Product promise

An ordinary user gives Hermes a mission, source material, an expected outcome, and any material approval. The system resolves the agent shape, model, provider, effort, tools, permissions, fallbacks, and proof requirements from organization policy. Experts can inspect and override those choices inside the approved envelope; ordinary users do not need to understand them.

```text
mission
  -> organization envelope
  -> approved Assembly Blueprint
  -> deterministic configuration resolution
  -> Hermes execution
  -> observed effect + independent disposition
  -> reconstructable receipt
  -> continue, improve, transfer, or retire
```

The v0.1 resolver selects among a small catalog of preapproved bundles. It does not claim that Hermes v0.20 performs general task-aware model selection.

## The five layers

| Layer | Owns | Explicit boundary |
|---|---|---|
| **Mission experience** | Outcome intake, status, material approvals, result, proof summary | Does not expose model/provider/effort knobs to ordinary users |
| **Portable control kernel** | Lifecycle, risk and reversibility, authority semantics, evidence requirements, proportionality, disposition, exceptions | Contains no Hermes object names or release-specific assumptions |
| **Pack system** | Organization policy, reusable capabilities, workflow-specific contracts and tests | Packs may narrow authority; they cannot silently expand the organization envelope |
| **Hermes adapter** | Version-pinned mapping to profiles, skills, goals, approvals, Kanban, tools, sandbox/egress, routing, and receipts | Every capability is classified `native`, `configuration`, `extension`, `surrounding-platform`, or `unsupported-gap` |
| **Operations and evidence** | Target-system readback, verification, human disposition, incident handling, ownership, retention, promotion/contraction | Kit records remain mutable until independently controlled custody is actually implemented |

Hermes is the front door and reference execution path. The kernel is portable so enterprise control semantics do not depend on undocumented runtime behavior.

## Pack system

Packs are versioned inputs to an approved **Assembly Blueprint**:

- **Organization pack:** operating envelope, data zones, allowed providers, authority ceilings, budget posture, identity bindings, retention, integration boundaries, and override rules.
- **Capability pack:** a reusable ability such as a connector, verifier topology, evidence-store adapter, browser boundary, or recovery mechanism, with permissions, failure modes, and tests.
- **Workflow pack:** mission vocabulary, source and output contracts, action inventory, deterministic oracles, exception rules, and fixtures for a business workflow.

An Assembly Blueprint pins the kernel schema, Hermes adapter, selected packs, configuration bundles, owners, effective dates, canonicalization method, and manifest hash. The hash establishes provenance only; signing, custody, and enforcement require separately proven controls.

Pack resolution obeys four rules:

1. Organization policy always wins over capability or workflow defaults.
2. Every material choice is explicit in the resolved manifest even when hidden from the ordinary user.
3. Unsupported or internally inconsistent combinations stop with `needs_policy_decision`.
4. A material change to model, prompt, skill, tool, permission, policy, runtime, or verifier creates a new risk identity and requires explicit novation.

Before execution, blueprint validation also requires compatible kernel and adapter pins; an acyclic dependency graph with explicit conflicts and organization-policy precedence; action-class, enforcement-point, bypass, stop, and readback declarations for every action-capable pack; and an oracle, verifier, evidence, and terminal-disposition contract for every acceptance-critical output or effect. Missing, stale, incompatible, or conflicting declarations fail closed with `needs_policy_decision`; load order never resolves policy conflict.

## Progressive disclosure

| Surface | Audience | Visible choices | Hidden but receipted |
|---|---|---|---|
| **Mission** | Ordinary user | Outcome, inputs, deadline, material approvals, status, proof | Models, providers, effort, tool graph, fallbacks, verifier topology |
| **Envelope** | Organization admin / policy owner | Data and provider rules, authority ceiling, verification class, retention, budget and override policy | Prompt and adapter detail unless inspected |
| **Assembly** | Expert / FDE / platform owner | Exact profiles, packs, bundles, models, tools, sandboxes, egress, verifier design, manifests | Nothing material |

The public UX uses plain states such as `blocked`, `runs automatically`, `approval required`, and `two approvals required`. Internal authority codes remain inspection-layer vocabulary.

## Generalized validation strategy

No single domain is allowed to prove the architecture. The v0.1 reference suite exercises three horizontal action archetypes against synthetic data:

| Archetype | What it proves |
|---|---|
| **Decide** | Bounded analysis, source grounding, deterministic policy checks, recommendation, and human disposition |
| **Coordinate** | Multi-owner workflow, state and handoff control, clarification limits, and deliberate limits on autonomy |
| **Act** | A reversible change inside a synthetic environment, target readback, rollback, and a hard boundary before production |

Finance, HR, legal, IT, healthcare, insurance, and other domains are optional workflow packs. Public-sector finance is not a prerequisite, default story, or preview dependency.

## Model and provider integration

The product exposes policy, not a model picker. An administrator approves bundle families such as latency-sensitive, balanced, or assurance-heavy; the resolver chooses only among eligible bundles based on task, data, action, consequence, and verification classes. The receipt records both requested and resolved runtime facts, including fallbacks.

Future adaptive selection must earn promotion from observed results across fixed acceptance criteria. Until that evidence exists, “best model for the task” is prohibited wording.

## Current Hermes boundary

Hermes v0.20 supplies valuable primitives with documented limits: profile distributions, goals/completion contracts, approval and deny rules, smart-approval suggestions, Kanban coordination, webhooks, Iron Proxy for its supported Docker topology, managed scope, provider routing, and fallback. It does not by itself prove enterprise IAM, adversarial isolation, immutable evidence custody, hard tenant isolation, or general outcome-aware model selection. The exact evidence and limits remain in [`preflight/v0.20-preflight-report.md`](preflight/v0.20-preflight-report.md).
