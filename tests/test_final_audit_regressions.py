"""Regression tests for defects found by the final independent audit."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from hermes_runtime import attest_hermes_runtime, parse_producer_json  # noqa: E402
from run_mission_s1 import build_receipt  # noqa: E402


def test_pinned_hermes_rejects_equals_form_override() -> None:
    env = os.environ.copy()
    env["HERMES_BIN"] = "/bin/true"

    proc = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/demo_mission_s1.sh"),
            "--live",
            "--hermes-binary=/evil",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 3
    assert "refusing --hermes-binary while HERMES_BIN is set" in proc.stderr


def test_version_attestation_rejects_substring_collision(tmp_path: Path) -> None:
    hermes = tmp_path / "hermes"
    hermes.write_text("#!/bin/sh\nprintf 'Hermes Agent v10.20.0\\n'\n", encoding="utf-8")
    hermes.chmod(0o700)

    with pytest.raises(RuntimeError, match="did not match the pinned release"):
        attest_hermes_runtime(str(hermes), accepted_versions=("0.20.0",))


def test_producer_json_accepts_one_object_inside_noise() -> None:
    payload = {"recommendation": "defer-pending-legal", "citations": ["POL-1"]}

    assert parse_producer_json(f"result follows\n{json.dumps(payload)}\nend") == payload


def test_producer_json_rejects_multiple_objects() -> None:
    with pytest.raises(ValueError, match="multiple JSON objects"):
        parse_producer_json('debug={"ignored": true}\n{"recommendation": "approve"}')


def test_live_receipt_marks_inference_cost_as_estimate_pending() -> None:
    receipt = build_receipt(
        run_id="live-test",
        mission={"work_order_id": "WO-TEST"},
        bundle={
            "bundle_id": "bundle-test",
            "bundle_version": "0.1.0",
            "manifest": {"canonicalization": "json-canonical-v1", "sha256": "0" * 64},
            "artifact_refs": [],
            "hermes_profile": {"distribution_ref": "profile-test"},
        },
        org_pack={
            "envelope": {"envelope_id": "env-test"},
            "blueprint": {"blueprint_id": "blueprint-test"},
            "catalog": {"resolver_rule_id": "resolver-test"},
        },
        producer_output={"external_action": False},
        oracle_result={"passed": True, "oracle_id": "oracle-test"},
        execution_mode="live",
        run_mode={"label": "hermes-live-one-shot"},
        preparer={"correlation_id": "hermes-live-test"},
    )

    assert receipt["cost"] == {
        "status": "ESTIMATE_PENDING",
        "usd": None,
        "reason": "Live provider inference occurred; session cost evidence is attached after execution.",
    }
    assert receipt["execution"]["preparer"]["correlation_id"] == "hermes-live-test"


def test_demo_receipt_keeps_cost_not_run() -> None:
    receipt = build_receipt(
        run_id="demo-test",
        mission={"work_order_id": "WO-TEST"},
        bundle={
            "bundle_id": "bundle-test",
            "bundle_version": "0.1.0",
            "manifest": {"canonicalization": "json-canonical-v1", "sha256": "0" * 64},
            "artifact_refs": [],
            "hermes_profile": {"distribution_ref": "profile-test"},
        },
        org_pack={
            "envelope": {"envelope_id": "env-test"},
            "blueprint": {"blueprint_id": "blueprint-test"},
            "catalog": {"resolver_rule_id": "resolver-test"},
        },
        producer_output={"external_action": False},
        oracle_result={"passed": True, "oracle_id": "oracle-test"},
        execution_mode="demo",
        run_mode={"label": "mission-demo"},
        preparer={"correlation_id": "demo-test"},
    )

    assert receipt["cost"]["status"] == "NOT_RUN"
    assert receipt["cost"]["usd"] is None


def test_shipped_live_profile_caps_output_reservation() -> None:
    config = (ROOT / "packs/profiles/profile-decide-vendor-policy/config.yaml").read_text(
        encoding="utf-8"
    )
    assert "max_tokens: 512" in config
