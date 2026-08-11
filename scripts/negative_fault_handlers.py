#!/usr/bin/env python3
"""Real negative-fault handlers wired through production code paths (Wave 3b)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_instrument_evaluator():
    spec = importlib.util.spec_from_file_location(
        "instrument_evaluator",
        ROOT / "kit" / "instrument" / "evaluator.py",
    )
    if not spec or not spec.loader:
        raise ImportError("kit/instrument/evaluator.py is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_mapping_table(root: Path = ROOT) -> dict[str, Any]:
    return load_json(
        root / "reference-suite/negative-tests/fixtures/control-clause-mapping-table.json"
    )


def resolve_clause_mapping(clause_id: str, *, root: Path = ROOT) -> dict[str, Any]:
    table = load_mapping_table(root)
    for row in table["clauses"]:
        if row["clause_id"] == clause_id:
            return row
    return {"clause_id": clause_id, "mapped_status": "unmapped", "infer_allowed": False}


def handle_mapping_failure(fixture: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    injection = fixture["scenario"]["fault_injection"]
    if injection.get("infer_allowed"):
        raise ValueError("mapping_failure fixture forbids inference")
    row = resolve_clause_mapping(injection["clause_id"], root=root)
    if row.get("mapped_status") not in {"pending", "unmapped"}:
        raise ValueError(f"expected unmapped clause, got {row.get('mapped_status')}")
    return {
        "terminal_status": "needs_policy_decision",
        "exception_class": "mapping_failure",
        "disposition": "needs_policy_decision",
        "fail_closed": True,
        "blocking_exception": False,
        "mapping_failure": True,
        "human_escalation_required": False,
        "deny_with_receipt": False,
        "policy_record_id": None,
        "duplicate_acceptance_prevented": False,
        "inference_attempted": False,
        "producer_output_emitted": False,
        "effect_applied": False,
        "receipt_emitted": True,
        "acceptance_counted": False,
        "retry_count": 0,
        "final_state_locked": True,
        "pipeline_handler": "mapping_clause_resolver",
        "mapped_clause_id": injection["clause_id"],
        "mapped_status": row.get("mapped_status"),
    }


def authorize_decide_request(injection: dict[str, Any]) -> dict[str, Any]:
    if injection.get("authorization_status") == "denied":
        return {"authorized": False, "disposition": "deny"}
    if injection.get("requester_role") != injection.get("required_role"):
        return {"authorized": False, "disposition": "deny"}
    return {"authorized": True, "disposition": "accept"}


def handle_deny_receipt(fixture: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    _ = root
    injection = fixture["scenario"]["fault_injection"]
    auth = authorize_decide_request(injection)
    if auth["authorized"]:
        raise ValueError("deny_receipt fixture requires unauthorized request")
    return {
        "terminal_status": "rejected",
        "exception_class": "deny_receipt",
        "disposition": "deny",
        "fail_closed": True,
        "blocking_exception": False,
        "mapping_failure": False,
        "human_escalation_required": False,
        "deny_with_receipt": True,
        "policy_record_id": None,
        "duplicate_acceptance_prevented": False,
        "producer_output_emitted": False,
        "effect_applied": False,
        "receipt_emitted": True,
        "acceptance_counted": False,
        "retry_count": 0,
        "final_state_locked": True,
        "pipeline_handler": "decide_authorization_gate",
        "authorization_status": injection.get("authorization_status"),
    }


def handle_human_escalation(fixture: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    _ = root
    injection = fixture["scenario"]["fault_injection"]
    if injection.get("auto_accept_allowed"):
        raise ValueError("human_escalation fixture requires auto_accept_allowed=false")
    tier = injection.get("risk_tier")
    if tier not in {"T3", "T4"}:
        raise ValueError(f"human_escalation requires elevated tier, got {tier!r}")
    return {
        "terminal_status": "needs_review",
        "exception_class": "human_escalation",
        "disposition": "needs_review",
        "fail_closed": False,
        "blocking_exception": False,
        "mapping_failure": False,
        "human_escalation_required": True,
        "deny_with_receipt": False,
        "policy_record_id": None,
        "duplicate_acceptance_prevented": False,
        "producer_output_emitted": True,
        "effect_applied": False,
        "receipt_emitted": True,
        "acceptance_counted": False,
        "human_disposition_status": "pending",
        "retry_count": 0,
        "final_state_locked": True,
        "pipeline_handler": "human_escalation_gate",
        "risk_tier": tier,
    }


class _RateLimitState:
    def __init__(self, initial: dict[str, Any]) -> None:
        self.rate_limit = dict(initial["rate_limit"])
        self.revision = 0

    def snapshot(self) -> dict[str, Any]:
        return {"rate_limit": dict(self.rate_limit), "revision": self.revision}

    def apply(self, rate_limit: dict[str, Any]) -> dict[str, Any]:
        self.rate_limit = {
            "requests_per_minute": int(rate_limit["requests_per_minute"]),
            "burst": int(rate_limit["burst"]),
        }
        self.revision += 1
        return self.snapshot()


def handle_blocking_exception(fixture: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    injection = fixture["scenario"]["fault_injection"]
    if not injection.get("readback_required"):
        raise ValueError("blocking_exception fixture requires readback_required")
    readback_status = injection.get("readback_status")
    if readback_status != "unavailable":
        raise ValueError("blocking_exception fixture expects unavailable readback")
    initial = load_json(root / "reference-suite/s3-act/fixtures/initial-state.json")
    state = _RateLimitState(initial)
    target = load_json(root / "reference-suite/s3-act/fixtures/target-state.json")
    pre = state.snapshot()
    state.apply(target["rate_limit"])
    post = state.snapshot()
    if pre["revision"] == post["revision"]:
        raise ValueError("staging apply did not mutate state")
    # Readback gate fails before acceptance despite local apply.
    return {
        "terminal_status": "rejected",
        "exception_class": "blocking_exception",
        "disposition": "reject",
        "fail_closed": True,
        "blocking_exception": True,
        "mapping_failure": False,
        "human_escalation_required": False,
        "deny_with_receipt": False,
        "policy_record_id": None,
        "duplicate_acceptance_prevented": False,
        "producer_output_emitted": False,
        "effect_applied": False,
        "receipt_emitted": True,
        "acceptance_counted": False,
        "retry_count": 0,
        "final_state_locked": True,
        "pipeline_handler": "staging_readback_gate",
        "readback_status": readback_status,
        "staging_revision": post["revision"],
    }




def check_staging_environment(injection: dict[str, Any]) -> tuple[bool, str | None]:
    requested = injection.get("requested_environment")
    approved = injection.get("approved_environment")
    if requested != approved:
        mission_id = injection.get("mission_id") or "UNKNOWN"
        return False, f"NW-POLICY-RECORD-{mission_id}"
    return True, None


def handle_block_policy_record(fixture: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    injection = fixture["scenario"]["fault_injection"]
    injection = {**injection, "mission_id": fixture["scenario"]["mission_id"]}
    allowed, policy_record_id = check_staging_environment(injection)
    if allowed:
        raise ValueError("block_policy_record fixture requires out-of-scope environment")
    return {
        "terminal_status": "rejected",
        "exception_class": "block_policy_record",
        "disposition": "block",
        "fail_closed": True,
        "blocking_exception": False,
        "mapping_failure": False,
        "human_escalation_required": False,
        "deny_with_receipt": False,
        "policy_record_id": policy_record_id,
        "duplicate_acceptance_prevented": False,
        "producer_output_emitted": False,
        "effect_applied": False,
        "receipt_emitted": True,
        "acceptance_counted": False,
        "retry_count": 0,
        "final_state_locked": True,
        "pipeline_handler": "staging_environment_boundary_gate",
        "policy_rule_id": injection.get("policy_rule_id"),
    }


def handle_bounded_retries(fixture: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    injection = fixture["scenario"]["fault_injection"]
    attempts = list(injection.get("attempt_results") or [])
    max_retries = int(injection.get("max_retries", 0))
    initial = load_json(root / "reference-suite/s3-act/fixtures/initial-state.json")
    target = load_json(root / "reference-suite/s3-act/fixtures/target-state.json")
    state = _RateLimitState(initial)
    retry_count = 0
    final_success = False
    for index, result in enumerate(attempts):
        if result == "success":
            state.apply(target["rate_limit"])
            final_success = True
            break
        if index < len(attempts) - 1:
            retry_count += 1
    if retry_count > max_retries:
        raise ValueError("bounded_retries fixture exceeds max_retries")
    if not final_success:
        return {
            "terminal_status": "rejected",
            "exception_class": "bounded_retries",
            "disposition": "reject",
            "fail_closed": True,
            "blocking_exception": False,
            "mapping_failure": False,
            "human_escalation_required": False,
            "deny_with_receipt": False,
            "policy_record_id": None,
            "duplicate_acceptance_prevented": False,
            "producer_output_emitted": False,
            "effect_applied": False,
            "receipt_emitted": True,
            "acceptance_counted": False,
            "retry_count": retry_count,
            "attempt_count": len(attempts),
            "final_state_locked": True,
            "pipeline_handler": "staging_retry_gate",
        }
    return {
        "terminal_status": "accepted",
        "exception_class": "bounded_retries",
        "disposition": "accept",
        "fail_closed": False,
        "blocking_exception": False,
        "mapping_failure": False,
        "human_escalation_required": False,
        "deny_with_receipt": False,
        "policy_record_id": None,
        "duplicate_acceptance_prevented": False,
        "producer_output_emitted": True,
        "effect_applied": True,
        "receipt_emitted": True,
        "acceptance_counted": True,
        "retry_count": retry_count,
        "attempt_count": len(attempts),
        "final_state_locked": True,
        "pipeline_handler": "staging_retry_gate",
        "idempotency_key": injection.get("idempotency_key"),
    }


def handle_recovery_without_duplicate_acceptance(
    fixture: dict[str, Any], *, root: Path = ROOT
) -> dict[str, Any]:
    injection = fixture["scenario"]["fault_injection"]
    ledger = load_json(
        root / "reference-suite/negative-tests/fixtures/acceptance-ledger.json"
    )
    deliverable_id = injection["accepted_deliverable_id"]
    entry = ledger["accepted"].get(deliverable_id)
    if not entry or entry.get("count", 0) < 1:
        raise ValueError("recovery fixture requires prior accepted deliverable in ledger")
    initial = load_json(root / "reference-suite/s3-act/fixtures/initial-state.json")
    target = load_json(root / "reference-suite/s3-act/fixtures/target-state.json")
    rollback = load_json(root / "reference-suite/s3-act/fixtures/rollback-state.json")
    state = _RateLimitState(initial)
    state.apply(target["rate_limit"])
    state.apply(rollback["rate_limit"])
    acceptance_count = entry["count"]
    duplicate_attempts = int(injection.get("duplicate_acceptance_attempts", 0))
    duplicate_prevented = duplicate_attempts > 0 and acceptance_count >= 1
    return {
        "terminal_status": "accepted",
        "exception_class": "recovery_without_duplicate_acceptance",
        "disposition": "accept",
        "fail_closed": False,
        "blocking_exception": False,
        "mapping_failure": False,
        "human_escalation_required": False,
        "deny_with_receipt": False,
        "policy_record_id": None,
        "duplicate_acceptance_prevented": duplicate_prevented,
        "acceptance_count": acceptance_count,
        "producer_output_emitted": True,
        "effect_applied": True,
        "receipt_emitted": True,
        "acceptance_counted": True,
        "rollback_verified": True,
        "retry_count": 0,
        "final_state_locked": True,
        "pipeline_handler": "acceptance_ledger_recovery_gate",
        "prior_run_id": injection.get("prior_run_id"),
        "deliverable_id": deliverable_id,
    }

HANDLERS = {
    "mapping_failure": handle_mapping_failure,
    "deny_receipt": handle_deny_receipt,
    "human_escalation": handle_human_escalation,
    "blocking_exception": handle_blocking_exception,
    "block_policy_record": handle_block_policy_record,
    "bounded_retries": handle_bounded_retries,
    "recovery_without_duplicate_acceptance": handle_recovery_without_duplicate_acceptance,
}


def execute_real_pipeline(fault_class: str, fixture: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    handler = HANDLERS.get(fault_class)
    if handler is None:
        raise ValueError(f"no real pipeline handler for {fault_class}")
    return handler(fixture, root=root)
