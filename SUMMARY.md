# Project summary

**Updated:** 2026-08-14

**Detailed design:** [SPEC-enterprise-agent-framework.md](SPEC-enterprise-agent-framework.md)

## Thesis

Hermes already provides profiles, goals, approvals, tools, boards, provider routing,
and other useful agent primitives. An organization still has to build the layer
around them:

- decide which jobs are appropriate
- choose a known, approved configuration
- check the result outside the model’s own narration
- hand judgment to an accountable person when required
- leave a reconstructable receipt

This kit is that surrounding layer as a version-pinned prototype — not a customer
deployment and not an official Nous product.

## Flow

User describes a job → org policy narrows choices → resolver picks one approved
setup → Hermes (or a local demo stand-in) runs → independent checks → person
reviews when needed → JSON run record.

The demo’s success state is often **`needs_review`**: the checker passed; a human
still owns the decision.

## What v0.20 provides — and does not

Pinned release: Hermes **v0.20.0 / tag `v2026.8.3`**.

A 214-test preflight covered profiles, goals, approvals, webhooks, Iron Proxy,
managed scope, Kanban, provider routing, and fallback. Result: **`PASS_WITH_LIMITS`**.

I use those pieces where they fit and do not stretch them:

- profiles are unsigned by default
- webhook signatures need a configured secret
- managed scope is not a sandbox
- goals are still partly model-judged
- Kanban is not an immutable audit log
- Iron Proxy does not replace OS isolation
- provider fallback does not choose the best model for a task

The public map has **318 rows** and **seven known gaps**. Those numbers are the
ledger, not the product story.

## Synthetic exercises

1. **Decide:** vendor-policy exception → recommendation, not a binding decision.
2. **Coordinate:** employee-offboarding packet without destructive actions.
3. **Act:** reversible local staging change; production promotion stays human.

Public-sector finance is an optional workflow pack, not the foundation.

## Proof posture

| Artifact | Status |
|---|---|
| Offline `./scripts/proof.sh` | Credential-free; no network; no new live Hermes call |
| Three reference records | Dry runs (local deterministic producers) |
| Older S1 | `operator-recorded-unattested` — not treated as live Hermes proof |
| Newer S1 one-shot | Native-runtime attested; oracle pass; still `needs_review` |
| Cost on live one-shot | ~$0.41 **estimate**, not provider-reported actual |
| External action / human disposition | None / pending |

## Status

Vendor-neutral core is stable. Adaptive model selection stays future work until
there are enough real results to justify it. No production change and no
provider-reported actual billed cost are part of this repository.

For the human-facing story, start with [README.md](README.md). For command-level
claims, use [PROOF.md](PROOF.md).
