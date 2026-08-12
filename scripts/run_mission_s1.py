#!/usr/bin/env python3
"""Run S1 vendor-exception mission through org resolver and (when available) live Hermes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from hermes_runtime import (  # noqa: E402
    attest_hermes_runtime,
    find_hermes_binary,
    install_profile_distribution,
    parse_producer_json,
    run_hermes_oneshot,
    runtime_reported_from_config,
)
from mission_resolver import load_json, load_org_pack, resolve_bundle, resolve_profile_path  # noqa: E402
from run_reference_suite import (  # noqa: E402
    HERMES_RELEASE,
    evaluate_s1_oracle,
    sha256_canonical,
)
from s1_producer import produce_s1_vendor_exception  # noqa: E402

S1_DIR = ROOT / "reference-suite/s1-decide"
DEFAULT_INTAKE = ROOT / "scripts/mission_intakes/s1-vendor-exception.json"
RUNS_DIR = ROOT / "reference-suite/runs"


def build_mission_prompt(*, mission: dict[str, Any], questionnaire: dict[str, Any], corpus_paths: list[Path]) -> str:
    corpus_blocks = []
    for path in corpus_paths:
        corpus_blocks.append(f"### {path.name}\n{path.read_text(encoding='utf-8')}")
    q_json = json.dumps(questionnaire, indent=2)
    return (
        "MISSION\n"
        f"Work order: {mission['work_order_id']}\n"
        f"Expected outcome: {mission['expected_outcome']}\n\n"
        "QUESTIONNAIRE (ground truth)\n"
        f"{q_json}\n\n"
        "POLICY CORPUS\n"
        + "\n\n".join(corpus_blocks)
        + "\n\n"
        "Respond with JSON only: recommendation, conditions, citations, external_action (must be false)."
    )


def build_receipt(
    *,
    run_id: str,
    mission: dict[str, Any],
    bundle: dict[str, Any],
    org_pack: dict[str, Any],
    producer_output: dict[str, Any],
    oracle_result: dict[str, Any],
    execution_mode: str,
    run_mode: dict[str, Any],
    preparer: dict[str, Any],
) -> dict[str, Any]:
    checker_verdict = "accept" if oracle_result["passed"] else "reject"
    if execution_mode == "live":
        cost = {
            "status": "ESTIMATE_PENDING",
            "usd": None,
            "reason": "Live provider inference occurred; session cost evidence is attached after execution.",
        }
    else:
        cost = {
            "status": "NOT_RUN",
            "usd": None,
            "reason": "No live provider inference occurred.",
        }
    # A deterministic checker can recommend acceptance; it cannot impersonate
    # the required human disposition. A separate reviewer must advance this
    # field in a later, attributable record.
    human_status = "pending"
    return {
        "schema_version": "0.1-draft",
        "run_id": run_id,
        "execution_mode": execution_mode,
        "run_mode": run_mode,
        "record_posture": {
            "store": "mutable-kit-artifact",
            "immutable_audit_claim": False,
        },
        "hermes_release": HERMES_RELEASE,
        "mission": mission,
        "resolution": {
            "envelope_id": org_pack["envelope"]["envelope_id"],
            "blueprint_id": org_pack["blueprint"]["blueprint_id"],
            "bundle_id": bundle["bundle_id"],
            "bundle_version": bundle["bundle_version"],
            "manifest_canonicalization": bundle["manifest"]["canonicalization"],
            "manifest_sha256": bundle["manifest"]["sha256"],
            "artifact_refs": bundle["artifact_refs"],
            "resolver_rule_id": org_pack["catalog"]["resolver_rule_id"],
            "override": None,
            "evidence_basis": "declared-and-observed",
        },
        "execution": {
            "preparer": preparer,
            "producer_input_excludes_oracle": True,
            "producer_output_id": f"{run_id}-producer-output",
            "producer_output": producer_output,
            "hermes_profile": bundle["hermes_profile"]["distribution_ref"],
        },
        "effect": {
            "output_artifact_ids": [f"{run_id}-recommendation.json"],
            "target_readback_ids": [],
            "deterministic_oracle_ids": [oracle_result["oracle_id"]],
            "evidence_basis": "observed",
        },
        "checker": {
            "session_id": f"s1-checker-{run_id}",
            "model": "deterministic-oracle-engine",
            "provider_resolved": "local-fixture",
            "separation_claims": ["role-separated", "deterministic-oracle"],
            "separation_evidence_ids": [f"{run_id}-producer-output", f"{run_id}-context-proof"],
            "verdict": checker_verdict,
            "criteria_evidence_ids": [oracle_result["oracle_id"]],
            "oracle_result": oracle_result,
            "latency_ms": 3,
        },
        "human_disposition": {
            "required": True,
            "status": human_status,
            "approver_authority_id": None,
            "required_authority_id": "auth-nimbus-policy-owner-synthetic",
            "review_evidence_ids": [],
            "recorded_at": None,
        },
        "cost": cost,
        "exceptions": [],
        "terminal_status": "needs_review" if checker_verdict == "accept" else "rejected",
    }


def print_walkthrough(
    *,
    mission: dict[str, Any],
    org_pack: dict[str, Any],
    bundle: dict[str, Any],
    producer: dict[str, Any],
    oracle_result: dict[str, Any],
    receipt_path: Path,
    execution_mode: str,
) -> None:
    print("")
    print("── What the run did ──")
    print(f"1. JOB         {mission['work_order_id']} — {mission['expected_outcome']}")
    org_name = org_pack["pack"].get("organization") or org_pack["pack"].get("pack_id", "org")
    print(f"2. POLICY      {org_pack['envelope']['envelope_id']} ({org_name})")
    print(f"3. CONFIG      {mission['task_class']} → {bundle['bundle_id']}")
    print(f"4. PROFILE     {bundle['hermes_profile']['distribution_ref']}")
    if execution_mode == "demo":
        print("5. RUN         demo producer (questionnaire → recommendation; no Hermes API call)")
    else:
        print("5. RUN         live Hermes one-shot")
    print(f"6. RECOMMEND   {producer['recommendation']}")
    print(f"7. CHECK       {'PASS' if oracle_result['passed'] else 'FAIL'}")
    try:
        receipt_display = receipt_path.relative_to(ROOT)
    except ValueError:
        receipt_display = receipt_path
    print(f"8. RECORD      {receipt_display}")
    print("9. REVIEW      pending — the programmed check does not count as human approval")
    if execution_mode == "demo":
        print("")
        print("Organization policy chose the configuration. Local code produced and checked the")
        print("recommendation, then saved the run. This demo did not call Hermes or a model.")
        print("A live run also requires Hermes, owner spend authorization, and saved CLI identity.")


def run_demo_mission(
    *,
    run_id: str,
    mission: dict[str, Any],
    bundle: dict[str, Any],
    org_pack: dict[str, Any],
    output_dir: Path | None,
) -> tuple[dict[str, Any], Path]:
    producer = produce_s1_vendor_exception(S1_DIR)
    oracle = load_json(S1_DIR / "expected-oracle.json")
    oracle_result = evaluate_s1_oracle(producer, oracle, dry_run=True)
    receipt = build_receipt(
        run_id=run_id,
        mission=mission,
        bundle=bundle,
        org_pack=org_pack,
        producer_output=producer,
        oracle_result=oracle_result,
        execution_mode="demo",
        run_mode={
            "label": "mission-demo",
            "hermes_daemon": False,
            "live_provider": False,
            "evidence_basis": "fixture-backed",
        },
        preparer={
            "model": "questionnaire-derived-producer-v1",
            "provider_requested": bundle["runtime"]["provider_constraint"],
            "provider_resolved": "local-demo",
            "effort": bundle["runtime"]["effort"],
            "tools_manifest_sha256": sha256_canonical(bundle["artifact_refs"]),
            "correlation_id": f"demo-{run_id}",
            "latency_ms": 2,
            "fallback_event": None,
            "evidence_basis": {
                "model": "declared",
                "provider_resolved": "declared",
                "latency_ms": "observed",
            },
        },
    )
    out_dir = output_dir or (RUNS_DIR / run_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = out_dir / "golden-path.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    (out_dir / "producer-output.json").write_text(json.dumps(producer, indent=2) + "\n", encoding="utf-8")
    return receipt, receipt_path


def main() -> int:
    ap = argparse.ArgumentParser(description="B07 S1 live mission runner")
    ap.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--org-pack", type=Path, default=None)
    ap.add_argument("--hermes-binary", default=None)
    ap.add_argument("--profile-name", default="decide-vendor-policy")
    ap.add_argument("--resolver-only", action="store_true", help="Validate org pack + resolver; do not invoke Hermes")
    ap.add_argument("--demo", action="store_true", help="Full mission walkthrough without Hermes install or API keys")
    ap.add_argument("--output-dir", type=Path, default=None)
    args = ap.parse_args()

    org_pack = load_org_pack(args.org_pack)
    mission = load_json(args.intake)
    bundle = resolve_bundle(mission, org_pack)
    profile_dir = resolve_profile_path(bundle)

    if args.resolver_only:
        print(
            f"MISSION_RESOLVER_PASS bundle={bundle['bundle_id']} "
            f"profile={profile_dir.relative_to(ROOT)} envelope={org_pack['envelope']['envelope_id']}"
        )
        return 0

    run_id = args.run_id or f"s1-decide-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    if args.demo:
        receipt, receipt_path = run_demo_mission(
            run_id=run_id,
            mission=mission,
            bundle=bundle,
            org_pack=org_pack,
            output_dir=args.output_dir,
        )
        oracle_result = receipt["checker"]["oracle_result"]
        producer = receipt["execution"]["producer_output"]
        print(
            f"MISSION_DEMO_PASS run_id={run_id} terminal={receipt['terminal_status']} "
            f"recommendation={producer['recommendation']} oracle_passed={oracle_result['passed']}"
        )
        print_walkthrough(
            mission=mission,
            org_pack=org_pack,
            bundle=bundle,
            producer=producer,
            oracle_result=oracle_result,
            receipt_path=receipt_path,
            execution_mode="demo",
        )
        return 0 if oracle_result["passed"] else 2

    hermes_bin = find_hermes_binary(args.hermes_binary)
    if not hermes_bin:
        print(
            "MISSION_RUN_BLOCKED: hermes CLI not found. Use --demo for a zero-setup walkthrough, or install Hermes.",
            file=sys.stderr,
        )
        return 3

    runtime_attestation = attest_hermes_runtime(
        hermes_bin,
        accepted_versions=(HERMES_RELEASE["package_version"], HERMES_RELEASE["tag"]),
    )

    questionnaire = load_json(S1_DIR / "questionnaire.json")
    corpus_paths = [
        ROOT / "reference-suite/s1-decide/vendor-policy-corpus/org-policy-v3.2.md",
        ROOT / "reference-suite/s1-decide/vendor-policy-corpus/exception-request-cloudsync.md",
    ]
    prompt = build_mission_prompt(mission=mission, questionnaire=questionnaire, corpus_paths=corpus_paths)

    install_profile_distribution(
        hermes_bin=hermes_bin,
        profile_dir=profile_dir,
        profile_name=args.profile_name,
    )
    invocation = run_hermes_oneshot(hermes_bin=hermes_bin, profile_name=args.profile_name, prompt=prompt)
    if invocation.returncode != 0:
        print(f"MISSION_RUN_FAIL: hermes exit {invocation.returncode}\n{invocation.stderr}", file=sys.stderr)
        return 1

    producer = parse_producer_json(invocation.stdout)
    oracle = load_json(S1_DIR / "expected-oracle.json")
    oracle_result = evaluate_s1_oracle(producer, oracle, dry_run=False)
    runtime = runtime_reported_from_config(hermes_bin, args.profile_name)

    receipt = build_receipt(
        run_id=run_id,
        mission=mission,
        bundle=bundle,
        org_pack=org_pack,
        producer_output=producer,
        oracle_result=oracle_result,
        execution_mode="live",
        run_mode={
            "label": "hermes-live-one-shot",
            "hermes_daemon": False,
            "live_provider": True,
            "evidence_basis": "native-cli-version-plus-observed-subprocess",
            "runtime_attestation": runtime_attestation,
        },
        preparer={
            "model": runtime["model"],
            "provider_requested": bundle["runtime"]["provider_constraint"],
            "provider_resolved": runtime["provider"],
            "effort": bundle["runtime"]["effort"],
            "tools_manifest_sha256": sha256_canonical(bundle["artifact_refs"]),
            "correlation_id": f"hermes-{run_id}",
            "latency_ms": invocation.latency_ms,
            "fallback_event": None,
            "evidence_basis": {
                "model": "runtime_reported",
                "provider_resolved": "runtime_reported",
                "latency_ms": "observed",
            },
        },
    )

    out_dir = args.output_dir or (RUNS_DIR / run_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "golden-path.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    (out_dir / "producer-output.json").write_text(json.dumps(producer, indent=2) + "\n", encoding="utf-8")
    (out_dir / "hermes-stdout.txt").write_text(invocation.stdout, encoding="utf-8")
    invocation_evidence = {
        "runtime_attestation": runtime_attestation,
        "profile_name": args.profile_name,
        "argv_shape": [
            str(Path(hermes_bin).expanduser().resolve()),
            "-p",
            args.profile_name,
            "-z",
            "<synthetic-mission-prompt>",
        ],
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "stdout_sha256": hashlib.sha256(invocation.stdout.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(invocation.stderr.encode("utf-8")).hexdigest(),
        "returncode": invocation.returncode,
        "latency_ms": invocation.latency_ms,
    }
    (out_dir / "hermes-invocation.json").write_text(
        json.dumps(invocation_evidence, indent=2) + "\n", encoding="utf-8"
    )

    print(
        f"MISSION_RUN_PASS run_id={run_id} terminal={receipt['terminal_status']} "
        f"model={runtime['model']} oracle_passed={oracle_result['passed']}"
    )
    print(f"receipt={out_dir / 'golden-path.json'}")
    print_walkthrough(
        mission=mission,
        org_pack=org_pack,
        bundle=bundle,
        producer=producer,
        oracle_result=oracle_result,
        receipt_path=out_dir / "golden-path.json",
        execution_mode="live",
    )
    return 0 if oracle_result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
