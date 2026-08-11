# Handoff and transfer — Agent Transfer Record (ATR)

**Status:** B03 extension — v2026-08-06 adds guarded import (guarded-import prior art)  
**Source:** community discussion and internal design review (2026-08-06)  
**Claim class:** design pattern — not runtime-enforced until B07/B09 evidence exists

## Problem

Cross-principal agent work fails at the handoff boundary: paste-a-doc, screenshot, or re-ask. The blocker is authority and provenance, not context window size.

## Agent Transfer Record (ATR)

A governed export/import primitive for moving bounded work between principals without silent authority expansion.

### Mandatory fields

| Field | Purpose |
|---|---|
| `atr_id` | Stable transfer identifier |
| `source_principal` | Who produced the artifact |
| `target_principal` | Intended recipient |
| `artifact_refs` | Hash-addressed artifact pointers |
| `authority_grant` | Scoped grant reference (ADR or equivalent) |
| `revision_pointers` | Source revisions for every mutable input |
| `prestate_hash` | Configuration + evidence state before transfer |
| `expiry` | Time-bound validity; stale import fails closed |
| `grant_scope` | `read` / `recommend` / `execute-within-envelope` |
| `disposition_stub` | Required checker/human disposition class on acceptance |

### Export rules

1. Export bundle is hash-addressed; includes ATR envelope + artifact payloads.
2. Secrets never ship in cleartext; redact into review metadata only.
3. Producer reasoning optional; disposition evidence required when claim is operational.

### Import rules (base)

1. Fail closed on missing, expired, unauthorized, or hash-mismatched ATR.
2. Target acceptance recorded separately; transfer incomplete until accepted.
3. Import never expands grant scope beyond ATR envelope.
4. Producer reasoning not required; disposition evidence is.

### Guarded import (receive side — guarded-import prior art)

Applies to archive import (`.tar`, `.tar.gz`, `.tgz`, `.zip`) and cross-runtime handoff receive:

| Step | Behavior |
|---|---|
| Validate envelope | Expiry, principal binding, hash match, grant scope |
| Stage | Artifacts under `<review_root>/atr-import-<id>/`; nothing auto-active |
| Secrets | Copy to `secrets-review/` only; never activate in runtime `.env` |
| MCP / connectors | Import disabled; `requires_review: true` in report |
| Report | `import_report.json`: imported, staged, skipped, denied, traversal_blocked |
| Traversal | Block `..`, symlinks, special files |
| Promotion | Explicit human/policy-owner action per layer (user / team / org pack) |
| Acceptance | Separate disposition record; import ≠ operational |

**Interchange note:** the guarded-export pattern from prior art is a compatible **shape** for user-level memories/skills staging; the ATR envelope wraps org-grade transfers with authority fields that pattern does not supply.

## Instrument integration (B03)

When workflow map includes cross-principal handoff, emit:

- `atr_required` (yes/no/not_applicable)
- source/target principal classes
- minimum `grant_scope`
- verifier/disposition class for import acceptance
- `enforcement_point` per action-capable step (see `enforcement-point-contract.md`)
- negative outcome when handoff cannot be governed → `human_process` or `do_not_agentize`

## Proof hooks

| Ticket | Evidence |
|---|---|
| B07 S2 Coordinate | Offboarding packet; bounded export |
| B08 negative | Unauthorized import fails closed |
| B09 | Non-producer reconstructs handoff from packet |
| B03 v3 | Guarded import fixture + denied-sibling search |

## Mapping status (B05)

Pending adjudication. Hermes profiles/Kanban/approvals → `native`/`configuration`; ATR custody + guarded import → `extension`; target principal IdP binding → `surrounding-platform`.
