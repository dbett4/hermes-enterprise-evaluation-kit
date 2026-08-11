#!/usr/bin/env python3
"""Non-producer reconstruction from B09 evidence packets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKETS_DIR = ROOT / "reference-suite/evidence-packets"
DEFAULT_RECONSTRUCTOR_IDENTITY = "independent-scripted-reconstructor-20260806"

sys.path.insert(0, str(ROOT / "scripts"))


def resolve_identity(cli_identity: str | None) -> str:
    if cli_identity:
        return cli_identity
    return os.environ.get("RECONSTRUCTOR_IDENTITY", DEFAULT_RECONSTRUCTOR_IDENTITY)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_packet(packet_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_json(packet_dir / "manifest.json")
    receipt_path = packet_dir / "artifacts" / "golden-path.json"
    receipt = load_json(receipt_path)
    return manifest, receipt


def supporting_artifact_path(
    manifest: dict[str, Any], packet_dir: Path, *, name_suffix: str
) -> Path | None:
    for artifact in manifest.get("artifacts", []):
        if artifact.get("role") != "supporting":
            continue
        path = artifact["path"]
        if path.endswith(name_suffix) or name_suffix in path:
            candidate = packet_dir / path
            if candidate.is_file():
                return candidate
    return None


def verify_artifact_digests(packet_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    failures: list[str] = []
    for artifact in manifest.get("artifacts", []):
        rel_path = artifact["path"]
        file_path = packet_dir / rel_path
        expected = artifact["sha256"]
        if not file_path.is_file():
            actual = None
            passed = False
            failures.append(f"missing artifact file: {rel_path}")
        else:
            actual = sha256_file(file_path)
            passed = actual == expected
            if not passed:
                failures.append(
                    f"digest mismatch for {rel_path}: expected {expected}, got {actual}"
                )
        entries.append(
            {
                "artifact_id": artifact.get("artifact_id", rel_path),
                "path": rel_path,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "passed": passed,
            }
        )
    return {"passed": not failures, "artifacts": entries, "failures": failures}


def producer_identities(receipt: dict[str, Any]) -> set[str]:
    identities: set[str] = set()
    preparer = receipt.get("execution", {}).get("preparer", {})
    if preparer.get("session_id"):
        identities.add(str(preparer["session_id"]))
    checker = receipt.get("checker", {})
    if checker.get("session_id"):
        identities.add(str(checker["session_id"]))
    return identities


class _RateLimitState:
    def __init__(self, initial: dict[str, Any]) -> None:
        self.rate_limit = dict(initial["rate_limit"])

    def snapshot_rpm(self) -> int:
        return int(self.rate_limit["requests_per_minute"])

    def apply(self, rate_limit: dict[str, Any]) -> None:
        self.rate_limit = {
            "requests_per_minute": int(rate_limit["requests_per_minute"]),
            "burst": int(rate_limit["burst"]),
        }


def recompute_s1_outcome(packet_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    from run_reference_suite import evaluate_s1_oracle  # noqa: WPS433
    from s1_producer import produce_s1_vendor_exception  # noqa: WPS433

    questionnaire_path = supporting_artifact_path(
        manifest, packet_dir, name_suffix="questionnaire.json"
    )
    oracle_path = supporting_artifact_path(
        manifest, packet_dir, name_suffix="expected-oracle.json"
    )
    if questionnaire_path is None or oracle_path is None:
        raise ValueError("S1 packet missing questionnaire or oracle supporting artifacts")
    questionnaire = load_json(questionnaire_path)
    oracle = load_json(oracle_path)
    producer = produce_s1_vendor_exception(questionnaire=questionnaire)
    oracle_result = evaluate_s1_oracle(producer, oracle, dry_run=True)
    checker_verdict = "accept" if oracle_result["passed"] else "reject"
    terminal_status = "accepted" if checker_verdict == "accept" else "rejected"
    return {
        "recommendation": producer["recommendation"],
        "external_action": producer.get("external_action", False),
        "checker_verdict": checker_verdict,
        "terminal_status": terminal_status,
        "recompute_basis": "questionnaire+oracle-via-s1_producer",
    }


def recompute_s3_outcome(packet_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    initial_path = supporting_artifact_path(
        manifest, packet_dir, name_suffix="initial-state.json"
    )
    target_path = supporting_artifact_path(
        manifest, packet_dir, name_suffix="target-state.json"
    )
    rollback_path = supporting_artifact_path(
        manifest, packet_dir, name_suffix="rollback-state.json"
    )
    if not all([initial_path, target_path, rollback_path]):
        raise ValueError("S3 packet missing staging fixture supporting artifacts")
    initial = load_json(initial_path)
    target = load_json(target_path)
    rollback = load_json(rollback_path)
    state = _RateLimitState(initial)
    pre_rpm = state.snapshot_rpm()
    state.apply(target["rate_limit"])
    post_rpm = state.snapshot_rpm()
    state.apply(rollback["rate_limit"])
    rollback_rpm = state.snapshot_rpm()
    oracle_passed = (
        pre_rpm == rollback["rate_limit"]["requests_per_minute"]
        and post_rpm == target["rate_limit"]["requests_per_minute"]
        and rollback_rpm == rollback["rate_limit"]["requests_per_minute"]
    )
    checker_verdict = "accept" if oracle_passed else "reject"
    terminal_status = "accepted" if checker_verdict == "accept" else "rejected"
    return {
        "pre_rpm": pre_rpm,
        "post_rpm": post_rpm,
        "rollback_rpm": rollback_rpm,
        "checker_verdict": checker_verdict,
        "terminal_status": terminal_status,
        "recompute_basis": "staging-fixtures-via-rate-limit-state",
    }


def recompute_outcome(packet_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    expected_type = manifest["expected_outcomes"]["type"]
    if expected_type == "decide-recommendation":
        return recompute_s1_outcome(packet_dir, manifest)
    if expected_type == "act-rate-limit":
        return recompute_s3_outcome(packet_dir, manifest)
    raise ValueError(f"unsupported expected outcome type: {expected_type}")


def observed_from_receipt(manifest: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    expected = manifest["expected_outcomes"]
    if expected["type"] == "decide-recommendation":
        return {
            "recommendation": receipt["execution"]["producer_output"]["recommendation"],
            "external_action": receipt["execution"]["producer_output"].get("external_action", False),
            "checker_verdict": receipt["checker"]["verdict"],
            "terminal_status": receipt["terminal_status"],
        }
    states = receipt["effect"]["observed_states"]
    return {
        "pre_rpm": states["prestate"]["rate_limit"]["requests_per_minute"],
        "post_rpm": states["poststate"]["rate_limit"]["requests_per_minute"],
        "rollback_rpm": states["rollback"]["rate_limit"]["requests_per_minute"],
        "checker_verdict": receipt["checker"]["verdict"],
        "terminal_status": receipt["terminal_status"],
    }


def reconstruct(
    manifest: dict[str, Any],
    receipt: dict[str, Any],
    *,
    packet_dir: Path,
    reconstructor_identity: str,
) -> dict[str, Any]:
    digest_verification = verify_artifact_digests(packet_dir, manifest)
    recomputed = recompute_outcome(packet_dir, manifest)
    observed = observed_from_receipt(manifest, receipt)
    compare_keys = [k for k in observed if k in recomputed]
    recomputed_compare = {k: recomputed[k] for k in compare_keys}
    outcome_match = observed == recomputed_compare
    manifest_expected = {
        k: manifest["expected_outcomes"][k] for k in compare_keys if k in manifest["expected_outcomes"]
    }
    manifest_matches_recompute = manifest_expected == recomputed_compare
    identity_distinct = reconstructor_identity not in producer_identities(receipt)
    passed = (
        digest_verification["passed"]
        and outcome_match
        and manifest_matches_recompute
        and identity_distinct
    )
    return {
        "packet_id": manifest["packet_id"],
        "run_id": manifest["run_id"],
        "reconstruction_basis": "supporting-sources-recompute",
        "reconstructor_identity": reconstructor_identity,
        "artifact_digest_verification": digest_verification,
        "recomputed": recomputed,
        "observed": observed,
        "manifest_expected": manifest_expected,
        "outcome_match": outcome_match,
        "manifest_matches_recompute": manifest_matches_recompute,
        "reconstructor_distinct_from_producer": identity_distinct,
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-dir", type=Path, help="Single packet directory")
    parser.add_argument("--all", action="store_true", help="Reconstruct all packets")
    parser.add_argument(
        "--identity",
        help="Reconstructor session identity (overrides RECONSTRUCTOR_IDENTITY env)",
    )
    args = parser.parse_args()
    identity = resolve_identity(args.identity)
    if args.packet_dir:
        dirs = [args.packet_dir]
    elif args.all or not args.packet_dir:
        dirs = sorted(PACKETS_DIR.iterdir())
    else:
        dirs = []
    results = []
    failures = 0
    for packet_dir in dirs:
        if not packet_dir.is_dir() or not (packet_dir / "manifest.json").is_file():
            continue
        manifest, receipt = load_packet(packet_dir)
        result = reconstruct(
            manifest,
            receipt,
            packet_dir=packet_dir,
            reconstructor_identity=identity,
        )
        results.append(result)
        if not result["passed"]:
            failures += 1
        report_path = packet_dir / "reconstruction-report.json"
        report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "reconstructed": len(results),
                "failures": failures,
                "reconstructor_identity": identity,
                "results": results,
            },
            indent=2,
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
