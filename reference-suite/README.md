# Generalized enterprise reference suite

**Status:** S1/S3 dry-run exemplars with reconstruction receipts, plus one spend-gated **live** S1 run (`runs/s1-decide-20260811-025135`, `execution_mode: live`). The S2 desk-probe evidence is held outside this public preview; its fixtures and expected oracle ship here.

The reference suite is designed to test the horizontal architecture across **decide**, **coordinate**, and **act**. It uses one clearly fictional organization and synthetic inputs so no client, employer, government, industry, or relationship is load-bearing.

## Suite members

| ID | Archetype | Synthetic scenario | Primary proof |
|---|---|---|---|
| **S1** | Decide | Evaluate a vendor-policy exception from a synthetic policy corpus and questionnaire; produce a bounded recommendation, not an external decision | Source grounding, deterministic policy checks, checker disposition, human release |
| **S2** | Coordinate | Build an employee-offboarding packet across fictional HR, identity, device, ticketing, payroll, and SaaS systems; do not execute destructive effects | Transferability, multi-owner coordination, clarification limits, “not ready to authorize” behavior |
| **S3** | Act | Apply an approved rate-limit change to a local synthetic staging service; verify target state and exercise exact rollback; production promotion remains human-controlled | Pre-authorized bounded action, target readback, recovery, and the staging/production authority boundary |

These scenarios are fixtures, not product verticals. A workflow pack may later replace any fixture without changing the kernel, authority semantics, receipt contract, or Hermes adapter.

## Shared run contract

Every executed suite member must show:

- an authorized mission and approved organization envelope;
- deterministic selection of one preapproved configuration bundle;
- fixed producer output before checker evaluation;
- independently labeled deterministic, role-separated, model-independent, and human checks;
- observed output or target-system evidence outside the producing model's narrative;
- explicit exception and terminal disposition;
- a reconstructable receipt with no hidden model/provider/effort fallback; and
- no immutable-audit, enterprise-IAM, production-conformance, or adaptive-routing claim beyond evidence.

S1 requires one clean accepted run and non-producer reconstruction. S3 requires the accepted H-seed/A-run sequence below and non-producer reconstruction. S2 remains the context-isolated desk probe. B08 distributes the committed negative fault classes across the suite rather than tying them to one domain.

S3's exact action-class/resource/environment tuple first completes an accepted first-occurrence H seed. Only after the policy owner ratifies the observed bounded rule may the subsequent A run demonstrate pre-authorization. The H record and the A record are both part of the suite denominator.

## Acceptance language

The suite passes only when every declared workflow oracle passes, every material discrepancy is explained and dispositioned, and no blocking `unknown` remains. Domain-specific “zero difference” rules belong in workflow packs; they are not universal core semantics.
