"""Focused tests for the B03 scoping instrument evaluator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "kit" / "instrument"

from evaluator import (  # noqa: E402
    DECISION_FINGERPRINT,
    RISK_FINGERPRINT,
    evaluate,
)


def _load_contract(name: str) -> dict:
    return json.loads((KIT / name).read_text(encoding="utf-8"))


def test_contract_fingerprints_are_stable() -> None:
    rules = _load_contract("decision-rules.json")
    risk = _load_contract("risk-rules.json")
    assert (
        hashlib.sha256(
            json.dumps(rules, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == DECISION_FINGERPRINT
    )
    assert (
        hashlib.sha256(json.dumps(risk, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        == RISK_FINGERPRINT
    )


def test_evaluate_prohibited_t0_fixture() -> None:
    fixtures = json.loads((KIT / "fixtures.json").read_text(encoding="utf-8"))
    case = next(item for item in fixtures["cases"] if item["id"] == "prohibited_t0")
    result = evaluate(case["input"])
    assert result["disposition"] == case["expected"]["disposition"]
    assert result["rule_id"] == case["expected"]["rule_id"]
    assert result["outputs"][0]["value"] == case["expected"]["O01_agent_decision"]


def test_evaluate_is_deterministic_for_authored_fixture() -> None:
    fixtures = json.loads((KIT / "fixtures.json").read_text(encoding="utf-8"))
    case = next(item for item in fixtures["cases"] if item["id"] == "advisory_first_t1")
    first = evaluate(case["input"])
    second = evaluate(case["input"])
    assert first == second


def test_evaluate_rejects_invalid_intake() -> None:
    with pytest.raises(ValueError, match="invalid complete raw intake"):
        evaluate({"answers": {}})
