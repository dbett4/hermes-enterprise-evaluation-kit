# Hermes-native golden path

**As of:** 2026-08-10<br>
**Used by:** B07 generalized reference suite<br>
**Status:** execution contract and draft receipt schema; **three accepted dry-run receipts**; **no live Hermes acceptance yet**

| Run class | Label | Hermes daemon | Accepted? |
|-----------|-------|---------------|-----------|
| Dry-run (`run_reference_suite.py`) | `synthetic/dry-run` | false | Stepping stone only — **three committed dry-run receipts** (S1, S3-H, S3-A); not product proof |
| Demo mission (`run_mission_s1.py --demo`) | `mission-demo` | false | Shows mission→receipt; no Hermes install |
| Live mission (`run_mission_s1.py` without `--demo`) | `hermes-live` | true | **Required** for B07 S1 live acceptance |

Dry-run receipts must not be relabeled as accepted reference runs.

## User experience

The ordinary user supplies a mission, source material, expected outcome, and any required deadline. The user does not select a model, provider, effort tier, toolset, fallback chain, or verifier topology.

The system then follows one visible sequence:

```text
mission
  → organizational envelope
  → named configuration bundle
  → pre-execution policy validation
  → Hermes profile + goal/completion contract + board/tools
  → observed result
  → deterministic/checker/human disposition
  → reconstructable receipt
```

The resolver is a Field Kit control in v0.1. It chooses only among predeclared bundles using explicit policy. It is not evidence that Hermes v0.20 ships general task-aware model selection.

## Configuration-bundle contract

Each allowed bundle contains:

- stable bundle ID and semantic version;
- exact Hermes profile/distribution reference and security posture;
- prompt, skill, tool, and policy artifact references;
- model, provider constraint, effort, auxiliary-model, and fallback settings;
- sandbox, egress, managed-scope, approval, and deny configuration;
- verifier topology and required disposition classes;
- data-zone, action-class, authority, and consequence limits;
- canonical serialization version and SHA-256 manifest hash; and
- owner, approval, effective date, expiry/review date, and supersession link.

The hash is provenance. The retained artifacts, canonicalization method, custody, and change-control record make it useful; the hash alone does not make the configuration immutable or trusted.

## v0.1 resolver rules

1. Derive task, data, action, reversibility, and verification classes from the approved intake record.
2. Intersect those classes with the organization envelope.
3. Select exactly one approved bundle or stop with `needs_policy_decision`.
4. Validate freshness, referenced artifacts, provider/data constraints, authority ceiling, and verifier availability.
5. Record any authorized override before execution.
6. Record the resolved values after provider routing/fallback. Runtime-reported values and independently observed values remain separately labeled.

The initial reference suite should compare two or three approved bundles across its archetypes. The experiment may recommend future selection logic; it cannot advertise “best model for the task” before that logic and its acceptance evidence exist.

## Receipt schema

One JSON sidecar per run: `reference-suite/runs/<run-id>/golden-path.json`.

`observed` means captured from a source outside the producing model's narrative. `runtime_reported` means reported by Hermes/provider/runtime and not independently attested. `declared` means supplied by approved policy/configuration. Every material value carries one of these bases.

```json
{
  "schema_version": "0.1-draft",
  "run_id": "<stable-id>",
  "record_posture": {
    "store": "mutable-kit-artifact",
    "immutable_audit_claim": false
  },
  "hermes_release": {
    "tag": "v2026.8.3",
    "commit": "3c27eb6234bf91b8ceee9e9071591b31e9b148cb",
    "package_version": "0.20.0",
    "evidence_basis": "declared-and-observed"
  },
  "mission": {
    "work_order_id": "<authority-record-id>",
    "task_class": "<class>",
    "data_zone": "<approved-zone>",
    "action_class": "<decide|coordinate|act-subclass>",
    "expected_outcome": "<bounded-outcome>"
  },
  "resolution": {
    "envelope_id": "<approved-envelope-id>",
    "bundle_id": "<bundle-id>",
    "bundle_version": "<semver>",
    "manifest_canonicalization": "<scheme-and-version>",
    "manifest_sha256": "<sha256>",
    "artifact_refs": ["<retained-artifact-id>"],
    "resolver_rule_id": "<deterministic-rule-id>",
    "override": null,
    "evidence_basis": "declared-and-observed"
  },
  "execution": {
    "preparer": {
      "model": "<exact-model-id>",
      "provider_requested": "<provider-or-router>",
      "provider_resolved": "<resolved-provider>",
      "effort": "<tier-or-not-applicable>",
      "tools_manifest_sha256": "<sha256>",
      "session_id": "<session-id>",
      "latency_ms": 0,
      "fallback_event": null,
      "evidence_basis": {
        "model": "runtime_reported",
        "provider_resolved": "runtime_reported",
        "latency_ms": "observed"
      }
    }
  },
  "effect": {
    "output_artifact_ids": ["<artifact-id>"],
    "target_readback_ids": ["<readback-id>"],
    "deterministic_oracle_ids": ["<oracle-result-id>"],
    "evidence_basis": "observed"
  },
  "checker": {
    "session_id": "<different-session-id>",
    "model": "<exact-model-id>",
    "provider_resolved": "<resolved-provider>",
    "separation_claims": ["role-separated", "deterministic-oracle"],
    "separation_evidence_ids": ["<fixed-producer-output-id>", "<context-proof-id>"],
    "verdict": "accept|reject|needs_review",
    "criteria_evidence_ids": ["<criteria-result-id>"],
    "latency_ms": 0
  },
  "human_disposition": {
    "required": true,
    "status": "pending|accept|reject|waive|compensate",
    "approver_authority_id": "<authority-id>",
    "review_evidence_ids": ["<review-record-id>"],
    "recorded_at": "<iso8601-or-null>"
  },
  "cost": {
    "status": "NOT_RUN",
    "usd": null,
    "reason": "B10 Portal measurement requires separate auth/spend authority"
  },
  "exceptions": [],
  "terminal_status": "accepted|rejected|needs_policy_decision|compensated"
}
```

## Required-null semantics

- `NOT_RUN`: the measurement or action was intentionally not executed; include a reason and keep value `null`.
- `not_applicable`: the field cannot apply to the selected bundle; include the policy basis.
- `unknown`: evidence expected but unavailable; the run cannot be accepted if the field is acceptance-critical.
- Empty string and invented zero are never substitutes for missing evidence.

## Acceptance gate

An accepted run must show:

- one authorized mission and one approved configuration bundle;
- all referenced configuration artifacts retained and hash-reconstructable;
- no unresolved unsupported combination or invisible override;
- observed output/effect evidence independent of the producer's narrative;
- exact, non-inflated verifier-separation claims;
- required deterministic/checker/human dispositions;
- zero unexplained oracle failures or undispositioned material discrepancies for the active workflow contract; and
- every absent measurement classified `NOT_RUN`, `not_applicable`, or blocking `unknown`.
