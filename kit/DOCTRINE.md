# Product doctrine — Hermes-shaped organizational deployment

**As of:** 2026-08-04<br>
**Status:** Field Kit preview; non-frozen where a build ticket or owner gate remains open<br>
**Governing spec:** [`SPEC-enterprise-agent-framework.md`](../SPEC-enterprise-agent-framework.md)

## Naming and ownership

| Term | Status | Use |
|---|---|---|
| **Enterprise Agent Deployment Field Kit for Hermes** | Dave-owned descriptive asset | This repository's method, cases, instruments, and evidence contracts |
| **Hermes for organizations** | Descriptive phrase | The problem space, not a product or partnership claim |
| **Hermes Assembly** | Proposed, uncleared Nous-owned concept | Strongest working name for a possible organization-facing Hermes product; not official, shipped, endorsed, or Dave-owned |
| **Reconciled Autonomy** | Doctrine | The rule by which an organization may expand or contract an agent's authority |

Never present `Hermes Assembly` as a current Nous product. Never put Hermes in a Dave-owned business brand. If Nous does not adopt the name, the Field Kit remains coherent under its descriptive title.

## North star

**Give Hermes the mission. The organization sets the operating envelope. The system resolves the agents, models, providers, effort, tools, authority, and proof.**

Hermes should be deeply configurable without requiring ordinary users to configure it. The ambition is an adaptive, customizable, formidable, easy-to-use organizational agent system with extensive expert options and sensible vertical integration. Those are design goals, not current market-leadership claims.

The ordinary user's first question is “what outcome do you need?”—not “which model and reasoning tier do you want?”

## Product geometry

### 1. Hermes experience

Hermes is the front door and the reference execution path from day one. Native profiles, skills, goals/completion contracts, approvals, Kanban coordination, webhooks, provider configuration, and sandbox/egress surfaces appear before kit extensions.

This must feel like a more capable Hermes, not a governance portal that happens to launch Hermes.

### 2. Organizational policy resolution

A policy resolver turns a mission plus an operating envelope into a named, preapproved configuration bundle. In v0.1 this is a kit control over a small, explicit bundle set—not a claim that Hermes v0.20 already performs general task-aware model selection.

The resolver owns the seam between ease of use and deep configurability:

- ordinary users do not choose models, providers, effort, tools, or verifier topology;
- administrators approve the envelope and bundle catalog;
- experts define and inspect the exact bundles;
- unsupported combinations stop for a named admin/expert decision; and
- every resolved choice and override appears in the run receipt.

### 3. Portable control kernel

Authority, evidence, lifecycle, proportionality, exception, and disposition semantics remain vendor-neutral. Every kernel claim requires all three of these artifacts:

1. a neutral semantic definition;
2. an explicit Hermes v0.20 mapping on the reference path; and
3. a documented configuration, extension, surrounding-platform, or unsupported-gap treatment when Hermes lacks the control.

This prevents two failure modes: a generic framework with Hermes branding, and a nonportable wrapper coupled to undocumented Hermes internals.

### 4. Enterprise integrations

Identity, durable evidence custody, policy distribution, data-zone enforcement, financial metering, and system-of-record readback may require surrounding infrastructure. Those dependencies stay visible. “Hermes-shaped” does not mean “pretend Hermes natively supplies every enterprise control.”

### 5. Composable packs

The product is horizontal infrastructure, not a preselected industry solution. A versioned Assembly Blueprint composes:

- an **organization pack** for the operating envelope and approved bundle catalog;
- **capability packs** for connectors, verification, evidence, and recovery patterns; and
- a **workflow pack** for mission vocabulary, action contracts, oracles, and fixtures.

Packs inherit the portable kernel and the organization envelope. They may narrow authority but may not expand it, redefine evidence semantics, or hide a material runtime choice from the receipt. Public-sector finance is one optional future workflow pack; it is not the default story or a preview dependency. The detailed contract is in [`architecture.md`](architecture.md) and [`../packs/README.md`](../packs/README.md).

## Progressive disclosure

| Layer | Audience | Visible choices | Hidden but receipted |
|---|---|---|---|
| **Mission** | Ordinary user | Outcome, source material, deadline, material approvals, result and proof | Model, provider, effort, tools, fallback, checker topology |
| **Envelope** | Organization admin / policy owner | Allowed data zones/providers, authority ceiling, budget policy, verification class, retention/custody, integration boundaries, override rules | Prompt/tool implementation detail unless inspected |
| **Assembly** | Expert / FDE / platform owner | Exact profiles, skills, prompts, models, providers, effort, tools, fallbacks, sandboxes, egress, checker design, canonical manifests | Nothing material; this is the inspection layer |

Cost caps, enterprise IAM, signing/pinning, integration management, and evidence retention must be classified as Hermes native, Hermes configuration, extension, surrounding platform, or gap. Their appearance in an admin experience does not make them native Hermes features.

## Policy-resolution contract

Each run follows this contract:

1. **Classify:** derive task class, data zone, action class, reversibility, consequence, and required verification from the mission and intake record.
2. **Constrain:** apply the organization envelope—allowed providers, residency, authority, cost posture, tools, and hard ceilings.
3. **Resolve:** select one named, preapproved configuration bundle. v0.1 uses deterministic policy and a small catalog.
4. **Validate:** reject stale, unsupported, unsigned/unpinned where policy requires assurance, or mutually inconsistent configurations before execution.
5. **Execute:** instantiate the mapped Hermes profile/goal/board/tool surfaces.
6. **Dispose:** reconcile observed effect with verifier and human/policy disposition.
7. **Receipt:** record the resolved bundle, evidence source for every material fact, overrides, exceptions, and terminal disposition.

An override is an explicit policy event. It names the authorizer, reason, affected constraints, duration, and compensating verification. Invisible fallback outside the approved bundle is a defect.

## Reconciled Autonomy

**Definition:** an agent earns bounded authority only when three legs reconcile:

1. **Authorized intent** — a work order and authority grant define what may happen.
2. **Observed effect** — target-system or deterministic evidence records what actually happened.
3. **Disposition** — a separately classified verifier and/or policy owner accepts, rejects, waives, or compensates the result.

The agent's own completion statement is never sufficient evidence.

### Independence is a typed claim

| Claim | Minimum evidence |
|---|---|
| `role-separated` | Distinct process/session/context; fixed producer output; no hidden producer reasoning |
| `model-independent` | Different model/configuration plus role-separation evidence |
| `deterministic-oracle` | Reproducible non-model check with retained inputs and result |
| `human-disposition` | Named authorized person, reviewed criteria/evidence, timestamp, outcome |
| `organizationally-independent` | Separate accountable owner and authority boundary; not implied by technical separation |

A session ID supports role separation; it does not prove independence by itself.

### Promotion, contraction, and novation

- Promotion is scoped to an action class, resource, environment, and configuration family.
- Promotion is a recommendation until a policy owner ratifies it.
- Incidents contract authority immediately within their proven common-mode scope.
- A material configuration change creates a new risk identity. Transfer of authority requires explicit novation: canary, haircut, probation, or rejection.
- A configuration-manifest hash supplies provenance only. It requires canonical serialization, retained referenced artifacts, custody, and change-control evidence before it can support a trust decision.
- Publication, client data, payments, legal hold, destructive production actions, and segregation-of-duties actions may retain hard ceilings that performance history cannot remove.

## Evidence posture

The v0.1 Markdown and JSON records are append-oriented lifecycle artifacts. They are mutable repository files, not immutable audit logs. Stable IDs, hashes, and deterministic links improve reconstruction; they do not create custody, completeness, or non-repudiation.

An immutable or audit-reliance claim requires an independently controlled store, population-completeness controls, access/change evidence, retention policy, and the applicable assessor's acceptance.

## Native-first rule

Use the strongest documented Hermes primitive first. Add a surrounding control only when the preflight identifies a limit or gap. Never weaken a native control merely to make the neutral kernel look symmetrical across vendors.

The governing classification is:

1. `native`
2. `configuration`
3. `extension`
4. `surrounding-platform`
5. `unsupported-gap`

Conditional and scoped capabilities include the condition in their classification. “Webhook support,” for example, does not imply signed delivery without a configured secret.

## v0.1 non-goals

- No claim that Hermes v0.20 ships general task-aware or outcome-aware model selection.
- No claim that Kanban, profiles, goals, or kit receipts form immutable enterprise audit.
- No claim that managed scope replaces OS/container isolation.
- No claim that Iron Proxy alone is the adversarial security boundary.
- No native enterprise IAM/SSO, tenant-isolation, adoption, ROI, or evidence-custody claim.
- No Portal cost figure before an authorized B10 run.
- No Nous partnership or official-name claim in this build slice.
- No claim that one synthetic reference suite proves every industry or workflow; external field trials remain the generality gate.

## Name decision

`Hermes Assembly` remains the recommended product concept name. “Assembly” carries three useful meanings at once: assembled agent configurations, an organization of agents and people, and a governed process that turns components into an ownable system. The name should remain explicitly proposed until Nous clears or rejects it.
