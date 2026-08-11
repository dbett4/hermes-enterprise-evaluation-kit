#!/usr/bin/env python3
"""Execute B08 negative-test fixtures against deterministic oracles."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NEGATIVE_ROOT = ROOT / "reference-suite" / "negative-tests"
MANIFEST_PATH = NEGATIVE_ROOT / "manifest.json"
FIXTURES_DIR = NEGATIVE_ROOT / "fixtures"
RUNS_DIR = NEGATIVE_ROOT / "runs"
INSTRUMENT_EVALUATOR_FAULTS = frozenset({"fail_closed"})
REAL_PIPELINE_FAULTS = frozenset({
    "mapping_failure",
    "deny_receipt",
    "human_escalation",
    "blocking_exception",
    "recovery_without_duplicate_acceptance",
    "block_policy_record",
    "bounded_retries",
})
EXECUTION_MODE_INSTRUMENT = "instrument_evaluator"
EXECUTION_MODE_PIPELINE = "real_pipeline"
EXECUTION_MODE_SIMULATED = "simulated"


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


def execution_mode_for_fault(fault_class: str) -> str:
    if fault_class in INSTRUMENT_EVALUATOR_FAULTS:
        return EXECUTION_MODE_INSTRUMENT
    if fault_class in REAL_PIPELINE_FAULTS:
        return EXECUTION_MODE_PIPELINE
    return EXECUTION_MODE_SIMULATED


@dataclass(frozen=True)
class OracleResult:
    oracle_id: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    fault_class: str
    suite_member: str
    passed: bool
    outcome: dict[str, Any]
    oracle_results: tuple[OracleResult, ...]
    defects: tuple[str, ...]
    execution_mode: str


def load_manifest(root: Path = ROOT) -> dict[str, Any]:
    path = root / "reference-suite" / "negative-tests" / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_fixture(relative_fixture: str, root: Path = ROOT) -> dict[str, Any]:
    path = root / "reference-suite" / "negative-tests" / relative_fixture
    return json.loads(path.read_text(encoding="utf-8"))


def load_instrument_intake(fixture: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    relative = fixture.get("instrument_intake")
    if not relative:
        raise ValueError(f"fixture {fixture.get('id')} missing instrument_intake for real execution")
    return load_fixture(relative, root=root)


def _outcome_from_instrument(instrument_result: dict[str, Any], fault_class: str) -> dict[str, Any]:
    disposition = instrument_result["disposition"]
    rule_id = instrument_result["rule_id"]

    if fault_class == "fail_closed":
        if disposition != "defer" or rule_id != "R-UNKNOWN":
            raise ValueError(
                f"fail_closed intake must defer via R-UNKNOWN; got disposition={disposition!r} rule_id={rule_id!r}"
            )
        return {
            "terminal_status": "needs_policy_decision",
            "exception_class": "fail_closed",
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
            "retry_count": 0,
            "final_state_locked": True,
            "instrument_rule_id": rule_id,
            "instrument_disposition": disposition,
        }

    raise ValueError(f"unsupported instrument_evaluator fault_class: {fault_class}")


def execute_fault_instrument(fixture: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    evaluator = _load_instrument_evaluator()
    intake = load_instrument_intake(fixture, root=root)
    instrument_result = evaluator.evaluate(intake)
    return _outcome_from_instrument(instrument_result, fixture["fault_class"])


def execute_fault_simulated(fixture: dict[str, Any]) -> dict[str, Any]:
    """Deterministic synthetic executor for simulated negative fault classes."""
    fault = fixture["fault_class"]
    injection = fixture["scenario"]["fault_injection"]
    mission_id = fixture["scenario"]["mission_id"]

    if fault == "fail_closed":
        return {
            "terminal_status": "needs_policy_decision",
            "exception_class": "fail_closed",
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
            "retry_count": 0,
            "final_state_locked": True,
        }

    if fault == "blocking_exception":
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
        }

    if fault == "mapping_failure":
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
        }

    if fault == "human_escalation":
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
        }

    if fault == "recovery_without_duplicate_acceptance":
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
            "duplicate_acceptance_prevented": True,
            "acceptance_count": 1,
            "producer_output_emitted": True,
            "effect_applied": True,
            "receipt_emitted": True,
            "acceptance_counted": True,
            "rollback_verified": True,
            "retry_count": 0,
            "final_state_locked": True,
        }

    if fault == "deny_receipt":
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
        }

    if fault == "block_policy_record":
        return {
            "terminal_status": "rejected",
            "exception_class": "block_policy_record",
            "disposition": "block",
            "fail_closed": True,
            "blocking_exception": False,
            "mapping_failure": False,
            "human_escalation_required": False,
            "deny_with_receipt": False,
            "policy_record_id": f"NW-POLICY-RECORD-{mission_id}",
            "duplicate_acceptance_prevented": False,
            "producer_output_emitted": False,
            "effect_applied": False,
            "receipt_emitted": True,
            "acceptance_counted": False,
            "retry_count": 0,
            "final_state_locked": True,
        }

    if fault == "bounded_retries":
        attempts = _attempt_results(injection)
        max_retries = int(injection.get("max_retries", 0))
        retry_count = max(len(attempts) - 1, 0)
        final_success = bool(attempts) and attempts[-1] == "success"
        return {
            "terminal_status": "accepted" if final_success else "rejected",
            "exception_class": "bounded_retries",
            "disposition": "accept" if final_success else "reject",
            "fail_closed": not final_success,
            "blocking_exception": False,
            "mapping_failure": False,
            "human_escalation_required": False,
            "deny_with_receipt": False,
            "policy_record_id": None,
            "duplicate_acceptance_prevented": False,
            "producer_output_emitted": final_success,
            "effect_applied": final_success,
            "receipt_emitted": True,
            "acceptance_counted": final_success,
            "retry_count": retry_count,
            "attempt_count": len(attempts),
            "final_state_locked": True,
        }

    raise ValueError(f"unsupported fault_class: {fault}")


def _attempt_results(injection: dict[str, Any]) -> list[str]:
    return list(injection.get("attempt_results") or [])


def execute_fault_pipeline(fixture: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from negative_fault_handlers import execute_real_pipeline  # noqa: WPS433

    return execute_real_pipeline(fixture["fault_class"], fixture, root=root)


def execute_fault(fixture: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    fault = fixture["fault_class"]
    mode = execution_mode_for_fault(fault)
    if mode == EXECUTION_MODE_INSTRUMENT:
        return execute_fault_instrument(fixture, root=root)
    if mode == EXECUTION_MODE_PIPELINE:
        return execute_fault_pipeline(fixture, root=root)
    return execute_fault_simulated(fixture)


def _oracle_value(outcome: dict[str, Any], field: str) -> Any:
    return outcome.get(field)


def _evaluate_oracle(outcome: dict[str, Any], oracle: dict[str, Any]) -> OracleResult:
    field = oracle["field"]
    operator = oracle["operator"]
    expected = oracle.get("value")
    actual = _oracle_value(outcome, field)

    if operator == "equals":
        passed = actual == expected
        detail = f"{field}={actual!r} expected {expected!r}"
    elif operator == "lte":
        passed = actual is not None and actual <= expected
        detail = f"{field}={actual!r} expected <= {expected!r}"
    elif operator == "known":
        passed = actual not in (None, "", "unknown", "unavailable")
        detail = f"{field}={actual!r} expected known value"
    else:
        raise ValueError(f"unsupported oracle operator: {operator}")

    return OracleResult(oracle_id=oracle["id"], passed=passed, detail=detail)


def evaluate_fixture(fixture: dict[str, Any], outcome: dict[str, Any]) -> tuple[tuple[OracleResult, ...], tuple[str, ...]]:
    oracle_results = tuple(_evaluate_oracle(outcome, oracle) for oracle in fixture["deterministic_oracles"])
    defects: list[str] = []

    expected = fixture["expected_outcome"]
    for key, value in expected.items():
        actual = outcome.get(key)
        if actual != value:
            defects.append(f"expected_outcome mismatch on {key}: actual={actual!r} expected={value!r}")

    for oracle in oracle_results:
        if not oracle.passed:
            defects.append(f"oracle {oracle.oracle_id} failed: {oracle.detail}")

    if outcome.get("receipt_emitted") is not True:
        defects.append("receipt_emitted must be true for every negative case")

    return oracle_results, tuple(defects)


def run_case(case: dict[str, Any], root: Path = ROOT) -> CaseResult:
    fixture = load_fixture(case["fixture"], root=root)
    execution_mode = execution_mode_for_fault(case["fault_class"])
    outcome = execute_fault(fixture, root=root)
    oracle_results, defects = evaluate_fixture(fixture, outcome)
    passed = not defects
    return CaseResult(
        case_id=case["id"],
        fault_class=case["fault_class"],
        suite_member=case["suite_member"],
        passed=passed,
        outcome=outcome,
        oracle_results=oracle_results,
        defects=defects,
        execution_mode=execution_mode,
    )


def run_all(
    root: Path = ROOT,
    write_run_artifact: bool = True,
    runs_dir: Path | None = None,
) -> dict[str, Any]:
    manifest = load_manifest(root=root)
    case_results = [run_case(case, root=root) for case in manifest["cases"]]
    passed = sum(1 for result in case_results if result.passed)
    total = len(case_results)
    instrument_count = sum(
        1 for result in case_results if result.execution_mode == EXECUTION_MODE_INSTRUMENT
    )
    pipeline_count = sum(
        1 for result in case_results if result.execution_mode == EXECUTION_MODE_PIPELINE
    )
    simulated_count = sum(
        1 for result in case_results if result.execution_mode == EXECUTION_MODE_SIMULATED
    )
    payload = {
        "schema_version": "0.1",
        "ticket": "B08",
        "synthetic_only": False,
        "real_execution_coverage": {
            "instrument_evaluator": instrument_count,
            "real_pipeline": pipeline_count,
            "simulated": simulated_count,
            "total": total,
        },
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "all_passed": passed == total,
        },
        "cases": [
            {
                "case_id": result.case_id,
                "fault_class": result.fault_class,
                "suite_member": result.suite_member,
                "passed": result.passed,
                "execution_mode": result.execution_mode,
                "terminal_status": result.outcome.get("terminal_status"),
                "exception_class": result.outcome.get("exception_class"),
                "defects": list(result.defects),
                "oracle_results": [
                    {"oracle_id": oracle.oracle_id, "passed": oracle.passed, "detail": oracle.detail}
                    for oracle in result.oracle_results
                ],
            }
            for result in case_results
        ],
    }

    if write_run_artifact:
        out_dir = runs_dir or (root / "reference-suite" / "negative-tests" / "runs")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "latest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return payload


def try_reference_suite_hook(root: Path = ROOT) -> None:
    """Call into run_reference_suite.py when that runner exists."""
    script = root / "scripts" / "run_reference_suite.py"
    if not script.is_file():
        return
    spec = importlib.util.spec_from_file_location("run_reference_suite", script)
    if not spec or not spec.loader:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    hook = getattr(module, "register_negative_tests", None)
    if callable(hook):
        hook(run_all)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--no-artifact", action="store_true", help="skip writing runs/latest.json")
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=None,
        help="directory for runs/latest.json (default: reference-suite/negative-tests/runs)",
    )
    args = parser.parse_args(argv)

    payload = run_all(
        root=args.root,
        write_run_artifact=not args.no_artifact,
        runs_dir=args.runs_dir,
    )
    summary = payload["summary"]
    print(
        f"B08 negative tests: {summary['passed']}/{summary['total']} passed "
        f"({'PASS' if summary['all_passed'] else 'FAIL'})"
    )
    for case in payload["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        print(
            f"  [{status}] {case['case_id']} {case['fault_class']} ({case['suite_member']}) "
            f"[{case['execution_mode']}] -> {case['terminal_status']}"
        )
        for defect in case["defects"]:
            print(f"         defect: {defect}")

    try_reference_suite_hook(root=args.root)
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
