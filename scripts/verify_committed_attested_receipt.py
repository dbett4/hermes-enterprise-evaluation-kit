#!/usr/bin/env python3
"""Verify the committed live S1 receipt and its recorded exceptions offline."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_reference_suite import evaluate_s1_oracle  # noqa: E402

RUN_ID = "s1-decide-20260812-owner-chat-authorized"
RUN = ROOT / "reference-suite/runs" / RUN_ID


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    receipt = load(RUN / "golden-path.json")
    producer = load(RUN / "producer-output.json")
    invocation = load(RUN / "hermes-invocation.json")
    session = load(RUN / "hermes-session-evidence.json")
    stdout_path = RUN / "hermes-stdout.txt"
    stdout = json.loads(stdout_path.read_text(encoding="utf-8"))
    schema = load(ROOT / "reference-suite/golden-path-receipt.schema.json")
    oracle = load(ROOT / "reference-suite/s1-decide/expected-oracle.json")

    Draft202012Validator(schema).validate(receipt)
    require(receipt["run_id"] == RUN_ID, "unexpected run ID")
    require(receipt["execution_mode"] == "live", "receipt is not labeled live")
    require(receipt["run_mode"]["label"] == "hermes-live-one-shot", "unexpected live mode")
    require(receipt["run_mode"]["hermes_daemon"] is False, "one-shot overstates daemon use")
    require(receipt["run_mode"]["live_provider"] is True, "provider call is not recorded")
    require(receipt["run_mode"]["runtime_attestation"] == invocation["runtime_attestation"], "runtime attestation copies differ")
    require(invocation["returncode"] == 0, "Hermes invocation was not successful")
    require(invocation["stdout_sha256"] == sha256(stdout_path), "stdout digest mismatch")
    require(stdout == producer, "stdout and frozen producer output differ")
    require(receipt["execution"]["producer_output"] == producer, "receipt and producer output differ")
    require(receipt["execution"]["preparer"]["native_session_id"] == "20260811_203745_6bd41b", "native session ID is missing")
    require(session["native_session_id"] == receipt["execution"]["preparer"]["native_session_id"], "session sidecar ID differs")
    require(session["message_count"] == 2, "native session should contain one prompt and one response")
    require(session["messages"][0]["content_sha256"] == invocation["prompt_sha256"], "session prompt digest mismatch")
    require(session["stdout_binding"]["stdout_sha256"] == invocation["stdout_sha256"], "session stdout digest mismatch")
    require(session["stdout_binding"]["normalized_stdout_matches_assistant_content"] is True, "session response binding is missing")
    normalized_stdout = stdout_path.read_text(encoding="utf-8").removesuffix("\n")
    require(
        hashlib.sha256(normalized_stdout.encode("utf-8")).hexdigest()
        == session["messages"][1]["content_sha256"],
        "native assistant response digest mismatch",
    )
    require(receipt["execution"]["preparer"]["provider_resolved"] == "nous", "runtime provider readback changed")
    require(receipt["execution"]["preparer"]["model"] == "anthropic/claude-fable-5", "runtime model readback changed")

    observed_oracle = evaluate_s1_oracle(producer, oracle, dry_run=False)
    require(observed_oracle["passed"] is True, "producer output fails the deterministic oracle")
    require(receipt["checker"]["oracle_result"] == observed_oracle, "stored and recomputed oracle results differ")
    require(producer["external_action"] is False, "producer output claims an external action")
    require(receipt["human_disposition"]["status"] == "pending", "human disposition was auto-accepted")
    require(receipt["terminal_status"] == "needs_review", "terminal state must await human review")
    require(receipt["cost"]["status"] == "ESTIMATED", "live inference cost status is false")
    require(receipt["cost"]["estimated_usd"] == 0.406986, "stored estimate changed")
    require(receipt["cost"]["actual_usd"] is None, "actual billed USD was not provider-reported")
    require(session["usage"]["cost_status"] == "estimated", "session ledger does not classify cost as estimated")
    require(session["usage"]["estimated_cost_usd"] == 0.406986, "session estimate changed")
    require(session["usage"]["api_call_count"] == 1, "expected exactly one provider API call")
    require(receipt["authorization"]["mode"] == "direct-owner-chat", "authorization route is missing")
    require(receipt["authorization"]["authorization_file_used"] is False, "receipt fabricates an authorization file")
    require(receipt["authorization"]["portal_cap_verified"] is False, "receipt fabricates Portal cap verification")

    exception_ids = {item["id"] for item in receipt["exceptions"]}
    require(
        exception_ids
        == {
            "legacy-file-gate-bypassed-by-owner-directive",
            "provider-constraint-mismatch",
        },
        "execution-time exceptions changed",
    )

    print(
        "ATTESTED_RECEIPT_PASS "
        f"run_id={RUN_ID} native_session=20260811_203745_6bd41b "
        "runtime=0.20.0 provider=nous model=anthropic/claude-fable-5 "
        "oracle=pass external_action=false human=pending cost=ESTIMATED:0.406986 "
        "exceptions=2"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
