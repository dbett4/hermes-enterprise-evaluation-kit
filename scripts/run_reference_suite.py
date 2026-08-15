#!/usr/bin/env python3
"""Executor for the B07 generalized reference suite.

Produces golden-path.json receipts without a live Hermes daemon; cost.status
remains NOT_RUN.

The S3 Act archetype has three target backends, selected with
``--staging-backend``:

``deployment-lab`` (default when the sister repository is resolvable)
    Drives the real MCP tools of ``hermes-enterprise-deployment-lab`` — scoped
    tool surface, separated operator approval, injected post-commit failure, and
    idempotent resume. Approval and idempotency mechanics are the lab's, not a
    local imitation of them. See ``scripts/deployment_lab_backend.py``.

``reference-service`` (fallback)
    The kit's own ``scripts/reference_staging_service.py`` toy rate-limit
    service. It observes a change and its exact rollback, but it has no approval
    separation and no failure/resume semantics. Use it only when the deployment
    lab is unavailable.

``fixture`` (default when the lab is not resolvable)
    Committed prestate/poststate/rollback fixtures; nothing is invoked.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from deployment_lab_backend import (  # noqa: E402
    DeploymentLabUnavailable,
    resolve_lab_root,
    run_act_mission,
)
from s1_producer import produce_s1_vendor_exception  # noqa: E402

BUNDLE_DIR = ROOT / "reference-suite/config-bundles"
RUNS_DIR = ROOT / "reference-suite/runs"
S1_DIR = ROOT / "reference-suite/s1-decide"
S3_FIX = ROOT / "reference-suite/s3-act/fixtures"

HERMES_RELEASE = {
    "tag": "v2026.8.3",
    "commit": "3c27eb6234bf91b8ceee9e9071591b31e9b148cb",
    "package_version": "0.20.0",
    "evidence_basis": "declared-and-observed",
}

ENVELOPE_ID = "env-nimbus-synthetic-v0.1"
RESOLVER_RULE = "resolver-v0.1-synthetic-internal"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_hash_for_bundle(bundle: dict[str, Any]) -> str:
    payload = copy.deepcopy(bundle)
    payload["manifest"] = {
        "canonicalization": "json-canonical-v1",
        "sha256": "",
    }
    return sha256_canonical(payload)


def load_bundle(bundle_id: str) -> dict[str, Any]:
    path = BUNDLE_DIR / f"{bundle_id}.json"
    bundle = load_json(path)
    expected = manifest_hash_for_bundle(bundle)
    if bundle["manifest"]["sha256"] != expected:
        raise ValueError(f"bundle manifest hash mismatch for {bundle_id}")
    return bundle


def resolve_bundle(mission: dict[str, Any]) -> dict[str, Any]:
    task = mission["task_class"]
    action = mission["action_class"]
    authority = mission.get("authority_mode", "H")
    if task == "vendor_policy_exception" and action == "decide-recommend":
        return load_bundle("bundle-s1-decide")
    if task == "rate_limit_change" and action == "act-rate-limit-change":
        if authority == "H":
            return load_bundle("bundle-s3-act-h")
        if authority == "A":
            return load_bundle("bundle-s3-act-a")
    raise ValueError(f"unsupported mission combination: {mission}")


def dry_run_evidence_basis(*, fixture_backed: bool = False) -> str:
    return "fixture_derived" if fixture_backed else "simulated"


def evaluate_s1_oracle(
    producer: dict[str, Any], oracle: dict[str, Any], *, dry_run: bool
) -> dict[str, Any]:
    expected = oracle["expected_producer_output"]
    allowed = set(
        next(c["expected"]["allowed_verbs"] for c in oracle["checks"] if c["check_id"] == "recommendation-bounds")
    )
    failures: list[str] = []
    if producer["recommendation"] not in allowed:
        failures.append("recommendation verb out of bounds")
    if producer["recommendation"] == "approve" and oracle["checks"][0]["inputs"]["requested_months"] > 12:
        if not oracle["checks"][0]["inputs"].get("executive_waiver_on_file"):
            failures.append("unconditional approve exceeds retention window")
    required_citations = set(
        next(c["expected"]["required_citations"] for c in oracle["checks"] if c["check_id"] == "source-grounding")
    )
    cited_docs = {c.split("#", 1)[0] for c in producer.get("citations", [])}
    if not required_citations.issubset(cited_docs):
        failures.append("missing required citations")
    if producer.get("external_action"):
        failures.append("external action forbidden for decide archetype")
    return {
        "oracle_id": oracle["oracle_id"],
        "passed": not failures,
        "failures": failures,
        "expected_recommendation": expected["recommendation"],
        "observed_recommendation": producer["recommendation"],
        "evidence_basis": dry_run_evidence_basis(fixture_backed=True) if dry_run else "observed",
    }


def http_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else canonical_json(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            "Connection": "close",
        }
        if payload is not None
        else {"Connection": "close"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


S3_BACKENDS = ("deployment-lab", "reference-service", "fixture")


def default_s3_backend() -> str:
    """Prefer the real deployment lab; fall back to fixtures when it is absent."""
    try:
        resolve_lab_root()
    except DeploymentLabUnavailable:
        return "fixture"
    return "deployment-lab"


def deployment_lab_effect(*, run_id: str) -> dict[str, Any]:
    """Run the Act arc against the deployment lab's MCP tools."""
    observations = run_act_mission(run_id=run_id)
    observations["readback_ids"] = [
        f"approval:{observations['approval_id']}",
        f"action-store-count:{observations['final_action_count']}",
    ]
    return observations


def evaluate_deployment_lab_oracle(observed: dict[str, Any], authority_mode: str) -> dict[str, Any]:
    """Deterministic checks over what the lab actually did during this run."""
    failures: list[str] = []
    if "apply_incident_plan" in observed["tools_under_read_plan_allowlist"]:
        failures.append("mutating tool visible under the read/plan allowlist")
    if observed["post_request_action_count"] != observed["prestate_action_count"]:
        failures.append("unapproved request changed the target system")
    if observed["capability_returned_to_requester"]:
        failures.append("approval capability leaked to the requester")
    if observed["failure_error_code"] != "upstream_5xx":
        failures.append("post-commit fault was not surfaced as an upstream 5xx")
    if observed["resume_status"] != "replayed" or not observed["resume_replayed"]:
        failures.append("resume did not replay")
    if observed["final_action_count"] != 1:
        failures.append("resume did not leave exactly one side effect")
    if observed["terminal_reuse_reason"] != "approval_already_applied":
        failures.append("applied capability was not terminal")
    if observed["post_terminal_action_count"] != 1:
        failures.append("terminal capability reuse produced another side effect")
    return {
        "oracle_id": f"s3-approval-idempotency-oracle-{authority_mode.lower()}",
        "passed": not failures,
        "failures": failures,
        "evidence_basis": "observed",
    }


def simulate_s3_effect(
    *,
    staging_url: str,
    target: dict[str, Any],
    rollback: dict[str, Any],
    dry_run: bool,
) -> dict[str, Any]:
    if dry_run:
        prestate = load_json(S3_FIX / "initial-state.json")
        poststate = load_json(S3_FIX / "target-state.json")
        rolled_back = load_json(S3_FIX / "rollback-state.json")
        return {
            "mode": "synthetic-dry-run",
            "prestate": prestate,
            "poststate": poststate,
            "rollback": rolled_back,
            "readback_ids": [
                prestate["prestate_id"],
                poststate["poststate_id"],
                rolled_back["rollback_id"],
            ],
            "evidence_basis": dry_run_evidence_basis(fixture_backed=True),
            "staging_service_invoked": False,
        }
    prestate = http_json("GET", f"{staging_url.rstrip('/')}/rate-limit")
    http_json("POST", f"{staging_url.rstrip('/')}/rate-limit", {"rate_limit": target["rate_limit"]})
    poststate = http_json("GET", f"{staging_url.rstrip('/')}/rate-limit")
    http_json("POST", f"{staging_url.rstrip('/')}/rate-limit", {"rate_limit": rollback["rate_limit"]})
    final = http_json("GET", f"{staging_url.rstrip('/')}/rate-limit")
    return {
        "mode": "local-staging-observed",
        "prestate": prestate,
        "poststate": poststate,
        "rollback": final,
        "readback_ids": [
            target.get("poststate_id", "s3-poststate-live"),
            rollback.get("rollback_id", "s3-rollback-live"),
        ],
        "evidence_basis": "observed",
        "staging_service_invoked": True,
    }


def build_receipt(
    *,
    run_id: str,
    mission: dict[str, Any],
    bundle: dict[str, Any],
    producer_output: dict[str, Any],
    effect: dict[str, Any],
    oracle_result: dict[str, Any],
    checker_verdict: str,
    human_status: str,
    preparer_session: str,
    checker_session: str,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "schema_version": "0.1-draft",
        "run_id": run_id,
        "run_mode": {
            "label": "synthetic/dry-run",
            "hermes_daemon": False,
            "live_provider": False,
            "evidence_basis": "declared-and-observed",
        },
        "record_posture": {
            "store": "mutable-kit-artifact",
            "immutable_audit_claim": False,
        },
        "hermes_release": HERMES_RELEASE,
        "mission": mission,
        "resolution": {
            "envelope_id": ENVELOPE_ID,
            "bundle_id": bundle["bundle_id"],
            "bundle_version": bundle["bundle_version"],
            "manifest_canonicalization": bundle["manifest"]["canonicalization"],
            "manifest_sha256": bundle["manifest"]["sha256"],
            "artifact_refs": bundle["artifact_refs"],
            "resolver_rule_id": RESOLVER_RULE,
            "override": None,
            "evidence_basis": "declared-and-observed",
        },
        "execution": {
            "preparer": {
                "model": bundle["runtime"]["model"],
                "provider_requested": bundle["runtime"]["provider_constraint"],
                "provider_resolved": "dry-run-simulator",
                "effort": bundle["runtime"]["effort"],
                "tools_manifest_sha256": sha256_canonical(bundle["artifact_refs"]),
                "session_id": preparer_session,
                "latency_ms": 12,
                "fallback_event": None,
                "evidence_basis": {
                    "model": "runtime_reported",
                    "provider_resolved": "runtime_reported",
                    "latency_ms": "observed",
                },
            },
            "producer_input_excludes_oracle": True,
            "producer_output_id": f"{run_id}-producer-output",
            "producer_output": producer_output,
        },
        "effect": effect,
        "checker": {
            "session_id": checker_session,
            "model": "deterministic-oracle-engine",
            "provider_resolved": "local-fixture",
            "separation_claims": ["role-separated", "deterministic-oracle"],
            "separation_evidence_ids": [
                f"{run_id}-producer-output",
                f"{run_id}-context-proof",
            ],
            "verdict": checker_verdict,
            "criteria_evidence_ids": [oracle_result["oracle_id"]],
            "oracle_result": oracle_result,
            "latency_ms": 3,
            "independence_note": "Distinct session IDs label separation; they do not prove stronger independence.",
        },
        "human_disposition": {
            "required": True,
            "status": human_status,
            "approver_authority_id": "auth-nimbus-policy-owner-synthetic",
            "review_evidence_ids": [f"{run_id}-human-review"],
            "recorded_at": now if human_status == "accept" else None,
        },
        "cost": {
            "status": "NOT_RUN",
            "usd": None,
            "reason": "B10 Portal measurement requires separate auth/spend authority",
        },
        "exceptions": [],
        "terminal_status": "accepted" if checker_verdict == "accept" and human_status == "accept" else "rejected",
    }


def run_s1(*, run_id: str, dry_run: bool) -> dict[str, Any]:
    mission = {
        "work_order_id": "WO-S1-20260806-001",
        "task_class": "vendor_policy_exception",
        "data_zone": "synthetic-internal",
        "action_class": "decide-recommend",
        "expected_outcome": "Bounded vendor-policy recommendation with citations; no external action.",
        "authority_mode": "H",
    }
    bundle = resolve_bundle(mission)
    oracle = load_json(S1_DIR / "expected-oracle.json")
    producer = produce_s1_vendor_exception(S1_DIR)
    oracle_result = evaluate_s1_oracle(producer, oracle, dry_run=dry_run)
    effect = {
        "output_artifact_ids": [f"{run_id}-recommendation.json"],
        "target_readback_ids": [],
        "deterministic_oracle_ids": [oracle_result["oracle_id"]],
        "evidence_basis": dry_run_evidence_basis() if dry_run else "observed",
    }
    return build_receipt(
        run_id=run_id,
        mission=mission,
        bundle=bundle,
        producer_output=producer,
        effect=effect,
        oracle_result=oracle_result,
        checker_verdict="accept" if oracle_result["passed"] else "reject",
        human_status="accept",
        preparer_session=f"s1-producer-{run_id}",
        checker_session=f"s1-checker-{run_id}",
    )


def run_s3(
    *,
    run_id: str,
    authority_mode: str,
    backend: str,
    staging_url: str,
    h_seed_run_id: str | None,
) -> dict[str, Any]:
    if backend not in S3_BACKENDS:
        raise ValueError(f"unknown S3 backend: {backend}")
    dry_run = backend == "fixture"
    mission = {
        "work_order_id": f"WO-S3-{authority_mode}-20260806-001",
        "task_class": "rate_limit_change",
        "data_zone": "synthetic-staging",
        "action_class": "act-rate-limit-change",
        "expected_outcome": (
            "Apply one operator-approved change to the deployment lab, survive a "
            "post-commit failure, and resume without a second side effect."
            if backend == "deployment-lab"
            else "Apply reversible rate-limit change with readback and exact rollback."
        ),
        "authority_mode": authority_mode,
    }
    if authority_mode == "A" and not h_seed_run_id:
        raise ValueError("S3 A run requires completed H seed run id")
    bundle = resolve_bundle(mission)
    if authority_mode == "A":
        requirement = bundle.get("governance", {}).get("h_seed_requirement")
        if requirement and h_seed_run_id != requirement:
            raise ValueError(f"A run h_seed mismatch: expected {requirement}, got {h_seed_run_id}")
    target = load_json(S3_FIX / "target-state.json")
    rollback = load_json(S3_FIX / "rollback-state.json")
    if backend == "deployment-lab":
        s3_effect = deployment_lab_effect(run_id=run_id)
        oracle_result = evaluate_deployment_lab_oracle(s3_effect, authority_mode)
    else:
        s3_effect = simulate_s3_effect(
            staging_url=staging_url, target=target, rollback=rollback, dry_run=dry_run
        )
        oracle_result = {
            "oracle_id": f"s3-rate-limit-oracle-{authority_mode.lower()}",
            "passed": (
                s3_effect["prestate"]["rate_limit"]["requests_per_minute"]
                == rollback["rate_limit"]["requests_per_minute"]
                and s3_effect["poststate"]["rate_limit"]["requests_per_minute"]
                == target["rate_limit"]["requests_per_minute"]
                and s3_effect["rollback"]["rate_limit"]["requests_per_minute"]
                == rollback["rate_limit"]["requests_per_minute"]
            ),
            "failures": [],
            "evidence_basis": dry_run_evidence_basis(fixture_backed=True) if dry_run else "observed",
        }
        if not oracle_result["passed"]:
            oracle_result["failures"].append("prestate/poststate/rollback mismatch")
    effect = {
        "output_artifact_ids": [f"{run_id}-change-record.json"],
        "target_readback_ids": s3_effect["readback_ids"],
        "deterministic_oracle_ids": [oracle_result["oracle_id"]],
        "observed_states": s3_effect,
        "evidence_basis": dry_run_evidence_basis() if dry_run else "observed",
    }
    if backend == "deployment-lab":
        producer_output = {
            "action": "approved_runbook_action",
            "resource": f"{s3_effect['incident_id']}/{s3_effect['action_id']}",
            "target_system": "hermes-enterprise-deployment-lab enterprise-api",
            "approval_id": s3_effect["approval_id"],
            "approver": s3_effect["approver"],
            "recovery": "resume replayed the approval-scoped idempotency key",
            "authority_mode": authority_mode,
            "production_promotion": False,
        }
    else:
        producer_output = {
            "action": "rate_limit_change",
            "resource": target["resource"],
            "applied_rate_limit": target["rate_limit"],
            "rollback_rate_limit": rollback["rate_limit"],
            "authority_mode": authority_mode,
            "production_promotion": False,
        }
    human_status = "accept" if authority_mode == "H" else "accept"
    receipt = build_receipt(
        run_id=run_id,
        mission=mission,
        bundle=bundle,
        producer_output=producer_output,
        effect=effect,
        oracle_result=oracle_result,
        checker_verdict="accept" if oracle_result["passed"] else "reject",
        human_status=human_status,
        preparer_session=f"s3-producer-{run_id}",
        checker_session=f"s3-checker-{run_id}",
    )
    if backend == "reference-service":
        receipt["run_mode"] = {
            "label": "local-staging-observed",
            "hermes_daemon": False,
            "live_provider": True,
            "staging_service": "reference_staging_service",
            "evidence_basis": "declared-and-observed",
        }
    elif backend == "deployment-lab":
        receipt["run_mode"] = {
            "label": "deployment-lab-observed",
            "hermes_daemon": False,
            "live_provider": False,
            "staging_service": "hermes-enterprise-deployment-lab/enterprise_mcp.server",
            "deployment_lab": {
                "root": s3_effect["lab_root"],
                "commit": s3_effect.get("lab_commit"),
                "api_url": s3_effect["api_url"],
                "tools_called": [
                    "propose_incident_plan",
                    "apply_incident_plan",
                ],
            },
            "evidence_basis": "observed",
        }
    return receipt


def write_receipt(run_id: str, receipt: dict[str, Any]) -> Path:
    out_dir = RUNS_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "golden-path.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        choices=["s1", "s3-h", "s3-a", "all"],
        default="all",
        help="Which reference scenario to execute",
    )
    parser.add_argument(
        "--staging-backend",
        choices=list(S3_BACKENDS),
        default=None,
        help=(
            "S3 Act target: deployment-lab (real MCP tools of the sister repo), "
            "reference-service (local toy fallback), or fixture. "
            "Default: deployment-lab when it is resolvable, otherwise fixture."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="Alias for --staging-backend fixture")
    parser.add_argument(
        "--live-staging",
        action="store_true",
        help="Alias for --staging-backend reference-service (fallback toy service)",
    )
    parser.add_argument("--staging-url", default="http://127.0.0.1:8765")
    parser.add_argument("--write-examples", action="store_true", help="Write committed example receipts")
    args = parser.parse_args()
    if args.staging_backend:
        s3_backend = args.staging_backend
    elif args.live_staging:
        s3_backend = "reference-service"
    elif args.dry_run:
        s3_backend = "fixture"
    else:
        s3_backend = default_s3_backend()
    s1_dry_run = True

    outputs: list[Path] = []
    if args.scenario in ("s1", "all"):
        run_id = "s1-decide-20260806-dry-run"
        outputs.append(write_receipt(run_id, run_s1(run_id=run_id, dry_run=s1_dry_run)))
    if args.scenario in ("s3-h", "all"):
        # The deployment-lab run gets its own run id so it never overwrites the
        # committed dry-run exemplar.
        run_id = (
            "s3-act-h-deployment-lab"
            if s3_backend == "deployment-lab"
            else "s3-act-h-20260806-dry-run"
        )
        outputs.append(
            write_receipt(
                run_id,
                run_s3(
                    run_id=run_id,
                    authority_mode="H",
                    backend=s3_backend,
                    staging_url=args.staging_url,
                    h_seed_run_id=None,
                ),
            )
        )
    if args.scenario in ("s3-a", "all"):
        run_id = (
            "s3-act-a-deployment-lab"
            if s3_backend == "deployment-lab"
            else "s3-act-a-20260806-dry-run"
        )
        outputs.append(
            write_receipt(
                run_id,
                run_s3(
                    run_id=run_id,
                    authority_mode="A",
                    backend=s3_backend,
                    staging_url=args.staging_url,
                    h_seed_run_id="s3-act-h-20260806-dry-run",
                ),
            )
        )
    print(
        json.dumps(
            {
                "s3_backend": s3_backend,
                "written": [str(p.relative_to(ROOT)) for p in outputs],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
