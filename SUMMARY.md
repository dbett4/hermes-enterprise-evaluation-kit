# Enterprise Agent Deployment Field Kit for Hermes — the simple version

**As of:** 2026-08-10 · Governing detail: [SPEC-enterprise-agent-framework.md](SPEC-enterprise-agent-framework.md)

## The idea

Hermes already has serious agent primitives. The missing layer is a repeatable way for an organization to decide what work an agent should do, resolve a safe configuration, prove the result, and own the agent after handoff.

This repository builds that method around Hermes first. It is not a generic framework wearing Hermes colors, and it does not make enterprise claims that Hermes v0.20 cannot support.

## The product shape

- **Public asset:** Enterprise Agent Deployment Field Kit for Hermes.
- **Descriptor:** Hermes for organizations.
- **Proposed Nous product name:** Hermes Assembly—strongest working name, but uncleared and not official.
- **Doctrine:** Reconciled Autonomy—agents earn bounded authority only from reconciled evidence, not from volume or self-reported success.
- **Experience:** users state the mission and outcome; organization policy resolves model, provider, effort, tools, permissions, and verification; experts can inspect and override within policy.

## What Hermes v0.20 gives us

The exact tagged release passed a focused 214-test preflight covering profile distributions, goals/completion contracts, approvals and deny rules, outbound webhook paths, Iron Proxy, managed scope, Kanban boards, configured provider routing, and fallbacks.

Those primitives are useful but bounded. Profiles are unsigned by default; webhook signatures require a secret; managed scope is not a sandbox; goals are model-judged; Kanban is not immutable audit; Iron Proxy does not replace OS isolation; provider fallback is availability recovery, not task-aware model choice. The kit supplies the missing authority, policy-resolution, evidence, lifecycle, and handoff contracts around those limits.

## The reference suite

The preview foundation is a synthetic, cross-industry suite rather than a finance case:

1. **Decide:** evaluate a vendor-policy exception and produce a bounded recommendation.
2. **Coordinate:** produce an employee-offboarding packet without executing destructive effects.
3. **Act:** apply and verify a reversible rate-limit change in a local synthetic staging service while keeping production promotion human-controlled.

Each executed path begins with a mission and organization envelope, resolves one preapproved configuration bundle, runs through Hermes, separates producer output from deterministic/checker/human disposition, and emits a reconstructable receipt. Public-sector finance is an optional future workflow pack, not the product foundation.

No Portal cost run or production change is part of this slice.

## Current status

B03 is connected into the B05 map and the map is materialized (318 rows, 7 unsupported-gap, 0 native). Three dry-run reference receipts exist for S1 and S3 (labeled honestly — not live Hermes proof), and one live S1 mission run through canonical Hermes is committed under `reference-suite/runs/`.

Authority-architecture v4 remains ratified; the vendor-neutral control kernel is frozen. Adaptive configuration selection stays a future claim until broader live evidence exists.
