"""The S3 Act mission must really drive the deployment lab's MCP tools.

The lab is a side-by-side clone (see ``scripts/deployment_lab_backend.py``), so
the end-to-end test skips when it is not present. Everything it needs is
loopback-only: no credentials, no network egress, no model call.
"""

from __future__ import annotations

import deployment_lab_backend as backend
import pytest
import run_reference_suite as suite


def lab_available() -> bool:
    try:
        root = backend.resolve_lab_root()
        backend.check_lab_dependencies(backend.resolve_lab_python(root))
    except backend.DeploymentLabUnavailable:
        return False
    return True


requires_lab = pytest.mark.skipif(
    not lab_available(),
    reason="hermes-enterprise-deployment-lab not resolvable; set HERMES_DEPLOYMENT_LAB",
)


def test_missing_lab_is_a_named_failure_not_a_silent_fallback(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_DEPLOYMENT_LAB", str(tmp_path / "nowhere"))
    monkeypatch.setattr(backend, "DEFAULT_SIBLING", tmp_path / "also-nowhere")
    with pytest.raises(backend.DeploymentLabUnavailable):
        backend.resolve_lab_root()
    # The suite degrades to fixtures rather than pretending an Act target ran.
    assert suite.default_s3_backend() == "fixture"


def test_oracle_rejects_a_run_that_double_writes():
    observed = {
        "tools_under_read_plan_allowlist": ["check_enterprise_api"],
        "prestate_action_count": 0,
        "post_request_action_count": 0,
        "capability_returned_to_requester": False,
        "failure_error_code": "upstream_5xx",
        "resume_status": "replayed",
        "resume_replayed": True,
        "final_action_count": 2,
        "terminal_reuse_reason": "approval_already_applied",
        "post_terminal_action_count": 2,
    }
    result = suite.evaluate_deployment_lab_oracle(observed, "H")
    assert result["passed"] is False
    assert "resume did not leave exactly one side effect" in result["failures"]


def test_oracle_rejects_an_unapproved_side_effect():
    observed = {
        "tools_under_read_plan_allowlist": ["apply_incident_plan"],
        "prestate_action_count": 0,
        "post_request_action_count": 1,
        "capability_returned_to_requester": True,
        "failure_error_code": "upstream_5xx",
        "resume_status": "replayed",
        "resume_replayed": True,
        "final_action_count": 1,
        "terminal_reuse_reason": "approval_already_applied",
        "post_terminal_action_count": 1,
    }
    result = suite.evaluate_deployment_lab_oracle(observed, "H")
    assert result["passed"] is False
    assert "unapproved request changed the target system" in result["failures"]
    assert "mutating tool visible under the read/plan allowlist" in result["failures"]
    assert "approval capability leaked to the requester" in result["failures"]


@requires_lab
def test_act_mission_drives_the_real_lab_tools(tmp_path):
    observed = backend.run_act_mission(workdir=tmp_path, run_id="pytest-s3-act")

    # The mutating tool is decided by the lab's server, not by this kit.
    assert "apply_incident_plan" not in observed["tools_under_read_plan_allowlist"]
    assert "apply_incident_plan" in observed["tools_under_write_allowlist"]

    # Approval separation: the request itself neither writes nor leaks a secret.
    assert observed["post_request_action_count"] == observed["prestate_action_count"]
    assert observed["capability_returned_to_requester"] is False
    assert observed["approval_id"].startswith("apr_")

    # Post-commit failure, then resume without a second record.
    assert observed["failure_status"] == "error"
    assert observed["failure_error_code"] == "upstream_5xx"
    assert observed["resume_status"] == "replayed"
    assert observed["final_action_count"] == 1
    assert observed["terminal_reuse_reason"] == "approval_already_applied"
    assert observed["post_terminal_action_count"] == 1

    assert suite.evaluate_deployment_lab_oracle(observed, "H")["passed"] is True


@requires_lab
def test_s3_receipt_records_the_lab_as_the_act_target(tmp_path):
    receipt = suite.run_s3(
        run_id="pytest-s3-act-receipt",
        authority_mode="H",
        backend="deployment-lab",
        staging_url="http://127.0.0.1:1",  # unused by this backend; must stay unused
        h_seed_run_id=None,
    )
    assert receipt["run_mode"]["label"] == "deployment-lab-observed"
    assert receipt["run_mode"]["staging_service"].endswith("enterprise_mcp.server")
    assert "apply_incident_plan" in receipt["run_mode"]["deployment_lab"]["tools_called"]
    assert receipt["checker"]["oracle_result"]["passed"] is True
    assert receipt["effect"]["observed_states"]["mode"] == "deployment-lab-mcp-observed"
    assert receipt["terminal_status"] == "accepted"
