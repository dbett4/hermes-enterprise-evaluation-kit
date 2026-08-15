#!/usr/bin/env bash
# S3 Act mission against the real Hermes Enterprise Deployment Lab.
#
# The Act archetype needs a target system with genuine approval separation,
# idempotency, and post-commit recovery. Those mechanics live in the sister
# repository and are exercised here, not re-implemented:
#
#   https://github.com/dbett4/hermes-enterprise-deployment-lab
#
# Clone it beside this repository or set HERMES_DEPLOYMENT_LAB. Everything stays
# on loopback: no credentials, no network egress, no model call.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
cd "$ROOT"

echo "=== Hermes Enterprise Evaluation Kit — S3 Act (deployment lab target) ==="

if ! "$PYTHON_BIN" scripts/deployment_lab_backend.py --probe; then
  cat >&2 <<'EOF'
MISSION_S3_UNAVAILABLE: the deployment lab is not resolvable.

  git clone https://github.com/dbett4/hermes-enterprise-deployment-lab
  cd hermes-enterprise-deployment-lab
  python3 -m venv .venv
  .venv/bin/pip install -r requirements-dev.txt \
                        -r workflow-runner/requirements.txt \
                        -r enterprise-mcp/requirements.txt

Then re-run this script, or run the fallback toy target explicitly:
  python3 scripts/run_reference_suite.py --scenario s3-h --staging-backend reference-service
EOF
  exit 3
fi

"$PYTHON_BIN" scripts/run_reference_suite.py --scenario s3-h --staging-backend deployment-lab

RECEIPT="reference-suite/runs/s3-act-h-deployment-lab/golden-path.json"
"$PYTHON_BIN" - "$RECEIPT" <<'PY'
import json
import sys

receipt = json.load(open(sys.argv[1], encoding="utf-8"))
observed = receipt["effect"]["observed_states"]
oracle = receipt["checker"]["oracle_result"]
print()
print(f"target            : {receipt['run_mode']['staging_service']}")
print(f"lab commit        : {receipt['run_mode']['deployment_lab']['commit']}")
print(f"read/plan surface : {observed['tools_under_read_plan_allowlist']}")
print(f"approval request  : no capability returned, side effects "
      f"{observed['prestate_action_count']} -> {observed['post_request_action_count']}")
print(f"operator grant    : {observed['approval_id']} approved by {observed['approver']}")
print(f"injected fault    : {observed['injected_fault']} -> {observed['failure_error_code']}")
print(f"resume            : {observed['resume_status']}, records={observed['final_action_count']}")
print(f"capability reuse  : {observed['terminal_reuse_reason']}")
print(f"oracle            : {oracle['oracle_id']} passed={oracle['passed']}")
print(f"terminal status   : {receipt['terminal_status']}")
if not oracle["passed"]:
    print("MISSION_S3_FAIL", oracle["failures"])
    raise SystemExit(1)
print()
print("MISSION_S3_DEMO_PASS act_target=deployment-lab exactly_one_side_effect=True")
print("The lab enforced approval separation and idempotent resume. This kit only")
print("selected the configuration, ran the mission, and checked the result.")
PY
