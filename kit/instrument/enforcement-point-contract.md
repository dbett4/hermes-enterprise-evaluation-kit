# Describing where an action is enforced

**Updated:** 2026-08-06

**Status:** design added to B03/B17 after review of guarded-import and per-user sandbox patterns

An access rule says who may try an action. For an action-capable workflow I also need to
know where that rule is enforced, how often it is checked, and what happens when the
enforcement service is unavailable.

## Fields for an action-capable step

When `classification_groups.action.action` is `read`, `write`, `execute`, `transfer`, or
`handoff`, include:

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

| Field | Values | Meaning |
|---|---|---|
| `identity_source` | `authenticated_gateway_event`, `configured_local_operator`, `delegated_parent_session`, `unknown` | The only source from which the actor may be resolved |
| `recheck_cadence` | `per_tool_call`, `per_turn`, `per_session`, `unknown` | How often the permission is evaluated again |
| `enforcement_location` | `tool_gateway_before_mutation`, `credential_proxy`, `target_api`, `human_release_surface`, … | Where the action is stopped before it changes anything |
| `boundary_unavailable_behavior` | `fail_closed_retryable`, `fail_closed_terminal`, `fail_open_forbidden`, `unknown` | What happens if that enforcement component is down |
| `mount_semantics` | `deny_by_default`, `read_only_default`, `explicit_grant_only`, `unknown` | Default file/execution access |
| `actor_derivation_rule` | `never_from_prompt_or_tool_arguments` | Required when identity comes from a gateway |

## Final states

| State | Meaning | What the user sees | Permission state | Existing grant retained? |
|---|---|---|---|---|
| `denied_by_policy` | No grant exists or policy prohibits the action | `Blocked` | `D` | Not applicable |
| `boundary_unavailable` | A grant exists but its enforcement component is down | `Temporarily unavailable — retry` | Retryable `D` | Yes |
| `approved_pending_human` | The action needs a person's release and the credential is withheld | `Approval required` | `H` | Not applicable |

The distinction between policy denial and a temporary service outage matters: neither
permits the action, but only one should be retried without changing policy.

## File and search rules

1. A permitted search at a parent path must not reveal metadata about a denied child.
   `fixtures/enforcement-negative-denied-sibling-search.json` is the failure case.
2. A path that needs approval is mounted read-only. Changes go through staging and a
   separate decision.
3. Delegation can narrow permission but cannot widen it.
4. A policy refresh affects the next turn's mounts.

## B03 v3 output

| Output | Addition |
|---|---|
| `O06_control_plan` | `enforcement_point_declaration` |
| `O07_deployment_boundary` | `boundary_dependencies` |
| `O10_unresolved_risk_register` | A row when an action-capable step has `boundary_unavailable_behavior=unknown` |
