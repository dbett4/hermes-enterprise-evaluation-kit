# Moving work between people or agents

**Updated:** 2026-08-06

**Status:** design pattern added to B03; it is not runtime-enforced until B07/B09 tests it

Cross-person agent work often falls apart at the handoff: someone pastes a document,
sends a screenshot, or starts the job again from scratch. More context does not solve
the harder questions: who created the material, what permission travels with it, which
version is current, and what the recipient may do next.

This design uses an **Agent Transfer Record (ATR)** to move work without silently
widening permission.

## Transfer fields

| Field | Purpose |
|---|---|
| `atr_id` | Stable transfer ID |
| `source_principal` | Person or agent that produced the material |
| `target_principal` | Intended recipient |
| `artifact_refs` | Hash-addressed pointers to transferred files |
| `authority_grant` | Reference to the narrow permission that allows the transfer |
| `revision_pointers` | Source revision for every mutable input |
| `prestate_hash` | Configuration and run-state hash before transfer |
| `expiry` | Time after which import stops |
| `grant_scope` | `read`, `recommend`, or `execute-within-envelope` |
| `disposition_stub` | Checker or human decision required before acceptance |

## Sending

1. The bundle contains the ATR and its files and is addressed by hash.
2. Secrets never appear in clear text. Only redacted review metadata may travel.
3. Private model reasoning is optional. An operational result still needs the required
   checker or person to decide on it.

## Receiving

1. Reject a missing, expired, unauthorized, or hash-mismatched ATR.
2. Record the recipient's acceptance separately; sending is not acceptance.
3. Import never expands the permission recorded in `grant_scope`.
4. Private reasoning is not required, but the result of required review is.

Archive formats (`.tar`, `.tar.gz`, `.tgz`, and `.zip`) and cross-runtime transfers are
staged rather than activated:

| Step | Behavior |
|---|---|
| Validate | Check expiry, recipient, hashes, and grant scope |
| Stage | Put files under `<review_root>/atr-import-<id>/`; activate nothing |
| Secrets | Copy only to `secrets-review/`; never update a live `.env` |
| MCP/connectors | Keep disabled and set `requires_review: true` |
| Report | Write `import_report.json` with imported, staged, skipped, denied, and traversal-blocked items |
| Path safety | Reject `..`, symlinks, and special files |
| Promote | Require an explicit person or policy-owner action at the user, team, or organization-pack level |
| Accept | Write a separate decision; import is not operation |

The earlier guarded-export pattern is useful for staging user memories or skills. The
ATR wraps that shape with the identity, permission, revision, and expiry fields needed
for an organization-level transfer.

## Intake output

When a workflow crosses from one person or agent to another, intake records:

- whether an ATR is required;
- source and recipient classes;
- minimum `grant_scope`;
- the checker or human decision required at import;
- the action's enforcement point; and
- `human_process` or `do_not_agentize` when the handoff cannot be controlled.

## Build links

| Ticket | Planned check |
|---|---|
| B07 S2 | Export the fictional offboarding packet within a narrow grant |
| B08 | Reject an unauthorized import |
| B09 | Have a non-producer reconstruct the handoff from the packet |
| B03 v3 | Run the guarded-import and denied-sibling-search fixtures |

Mapping is still pending: Hermes profiles, boards, and approvals are expected to map to
`native` or `configuration`; ATR custody and guarded import to `extension`; and binding
the receiving person to an identity provider to `surrounding-platform`.
