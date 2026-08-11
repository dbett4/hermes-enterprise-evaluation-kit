# Enforcement point contract — B03 / B17 shared surface

**As of:** 2026-08-06  
**Status:** Spec patch (guarded-import prior-art items #1–2); promoted to `kit/instrument/`  
**Governs:** Every action-capable workflow step and every action-capable Authority Decision Record  
**Prior art:** per-user sandbox designs from external prior-art review, identity-from-gateway-event, `secure_execution_unavailable`

---

## Purpose

Access-control products govern **who may attempt an action**. The Field Kit must also declare **where** that grant is enforced, **how often** it is re-checked, and **what happens** when the enforcement boundary is down.

---

## Required declaration (action-capable steps only)

When `classification_groups.action.action` is `read`, `write`, `execute`, `transfer`, or `handoff`:

```json
{
  "enforcement_point": {
    "identity_source": "authenticated_gateway_event",
    "recheck_cadence": "per_tool_call",
    "enforcement_location": "tool_gateway_before_mutation",
    "boundary_unavailable_behavior": "fail_closed_retryable",
    "mount_semantics": "explicit_grant_only",
    "actor_derivation_rule": "never_from_prompt_or_tool_arguments"
  }
}
```

| Field | Values | Rule |
|---|---|---|
| `identity_source` | `authenticated_gateway_event`, `configured_local_operator`, `delegated_parent_session`, `unknown` | Actor resolves from this source only |
| `recheck_cadence` | `per_tool_call`, `per_turn`, `per_session`, `unknown` | Minimum re-evaluation cadence |
| `enforcement_location` | `tool_gateway_before_mutation`, `credential_proxy`, `target_api`, `human_release_surface`, … | Where fail-closed runs before effect |
| `boundary_unavailable_behavior` | `fail_closed_retryable`, `fail_closed_terminal`, `fail_open_forbidden`, `unknown` | When enforcement plane is down |
| `mount_semantics` | `deny_by_default`, `read_only_default`, `explicit_grant_only`, `unknown` | Filesystem/execution default |
| `actor_derivation_rule` | `never_from_prompt_or_tool_arguments` | Required when gateway-bound |

---

## Terminal states

| State | Meaning | User-facing | Authority actual | Grant preserved |
|---|---|---|---|---|
| `denied_by_policy` | No grant / prohibited | `Blocked` | `D` | N/A |
| `boundary_unavailable` | Grant exists; boundary down | `Temporarily unavailable — retry` | `D` (retryable) | Yes |
| `approved_pending_human` | H-tier; credential withheld | `Approval required` | `H` | N/A |

---

## Mount and search invariants

1. **Denied-sibling search:** Permitted parent search must not leak denied-child metadata — see `fixtures/enforcement-negative-denied-sibling-search.json`.
2. **Approval-gated paths mount `ro`** — writes route through staging + disposition.
3. **Delegation is no-amplification.**
4. **Policy refresh is immediate** — next turn uses new mounts.

---

## B03 output wiring (v3)

| Output | Addition |
|---|---|
| `O06_control_plan` | `enforcement_point_declaration` |
| `O07_deployment_boundary` | `boundary_dependencies` |
| `O10_unresolved_risk_register` | Row when `boundary_unavailable_behavior=unknown` on action-capable step |
