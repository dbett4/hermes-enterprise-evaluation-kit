#!/usr/bin/env python3
"""Verify the committed operator-recorded S1 artifact and its honest limits."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_reference_suite import evaluate_s1_oracle  # noqa: E402

RUN = ROOT / "reference-suite/runs/s1-decide-20260811-025135"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    receipt = load(RUN / "golden-path.json")
    producer = load(RUN / "producer-output.json")
    stdout = json.loads((RUN / "hermes-stdout.txt").read_text(encoding="utf-8"))
    schema = load(ROOT / "reference-suite/golden-path-receipt.schema.json")
    oracle = load(ROOT / "reference-suite/s1-decide/expected-oracle.json")

    Draft202012Validator(schema).validate(receipt)
    require(
        receipt["execution_mode"] == "operator-recorded-unattested",
        "recorded artifact overstates its execution mode",
    )
    require(
        receipt["run_mode"]["label"] == "operator-recorded-unattested",
        "run mode is not explicitly unattested",
    )
    require(receipt["run_mode"]["hermes_daemon"] is None, "daemon use is overstated")
    require(receipt["run_mode"]["live_provider"] is None, "provider use is overstated")
    require(
        receipt["run_mode"]["runtime_attestation"] == "not_captured",
        "missing native attestation is not explicit",
    )
    require(receipt["hermes_release"]["tag"] == "v2026.8.3", "unexpected declared Hermes tag")
    require(receipt["hermes_release"]["commit"] == "3c27eb6234bf91b8ceee9e9071591b31e9b148cb", "unexpected declared Hermes commit")
    require(stdout == producer, "recorded stdout and producer artifact differ")
    require(receipt["execution"]["producer_output"] == producer, "receipt embeds different producer output")

    observed_oracle = evaluate_s1_oracle(producer, oracle, dry_run=False)
    require(observed_oracle["passed"] is True, "committed output fails the current deterministic oracle")
    require(receipt["checker"]["oracle_result"] == observed_oracle, "stored and recomputed oracle results differ")
    require(receipt["human_disposition"]["status"] == "pending", "human disposition was auto-accepted")
    require(receipt["human_disposition"]["review_evidence_ids"] == [], "unproven human evidence is present")
    require(receipt["terminal_status"] == "needs_review", "live run should await human review")
    require(receipt["cost"]["status"] == "NOT_RUN" and receipt["cost"]["usd"] is None, "cost is overstated")
    require(
        any(item.get("id") == "missing-native-runtime-attestation" for item in receipt["exceptions"]),
        "native runtime evidence gap is not recorded",
    )

    print(
        "RECORDED_RECEIPT_PASS "
        f"run_id={receipt['run_id']} declared_hermes={receipt['hermes_release']['tag']} "
        f"runtime_attestation=missing oracle=pass terminal={receipt['terminal_status']} cost=NOT_RUN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
