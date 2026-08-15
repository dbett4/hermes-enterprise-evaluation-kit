#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PROOF_TEMP="$(mktemp -d)"

cleanup() {
  case "$PROOF_TEMP" in
    /tmp/*) rm -rf -- "$PROOF_TEMP" ;;
    *) echo "Refusing to remove unexpected proof directory: $PROOF_TEMP" >&2 ;;
  esac
}
trap cleanup EXIT

cd "$ROOT"

echo "FIELD_KIT_PROOF_OFFLINE credential_free=1 network=0 api_keys=0 hermes_live=0"
echo "FIELD_KIT_PROOF_SCOPE public_mapping=1 instrument=1 negative_tests=8 runtime_guard=1 demo=1 s3_act=deployment-lab-when-present"

"$PYTHON_BIN" -m ruff format --check scripts/hermes_runtime.py scripts/verify_public_mapping.py \
  scripts/deployment_lab_backend.py scripts/deployment_lab_act_client.py tests/
"$PYTHON_BIN" -m ruff check \
  kit/instrument/evaluator.py \
  scripts/hermes_runtime.py \
  scripts/verify_public_mapping.py \
  scripts/deployment_lab_backend.py \
  scripts/deployment_lab_act_client.py \
  tests/
"$PYTHON_BIN" -m pytest -q tests/

"$PYTHON_BIN" scripts/verify_public_mapping.py
"$PYTHON_BIN" scripts/verify_runtime_attestation_guard.py
"$PYTHON_BIN" scripts/check_neutral_core.py
"$PYTHON_BIN" scripts/run_negative_tests.py
"$PYTHON_BIN" scripts/verify_committed_recorded_receipt.py
"$PYTHON_BIN" scripts/verify_committed_attested_receipt.py
bash scripts/demo_mission_s1.sh --output-dir "$PROOF_TEMP/demo"

# S3 Act runs against the real deployment lab when that repository is present.
# Its absence is reported, never silently downgraded to the toy target.
if "$PYTHON_BIN" scripts/deployment_lab_backend.py --probe >/dev/null 2>&1; then
  PYTHON_BIN="$PYTHON_BIN" bash scripts/demo_mission_s3.sh
  ACT_TARGET="deployment-lab"
else
  echo "FIELD_KIT_PROOF_ACT_SKIPPED deployment lab not resolvable; S3 Act not exercised."
  echo "  Clone https://github.com/dbett4/hermes-enterprise-deployment-lab beside this repo"
  echo "  or set HERMES_DEPLOYMENT_LAB to run it."
  ACT_TARGET="not-run"
fi

echo "FIELD_KIT_PROOF_PASS mapping_rows=318 negative_tests=8 recorded_receipt=pass attested_receipt=pass demo=pass s3_act_target=${ACT_TARGET} lint=pass unit_tests=pass"
echo "FIELD_KIT_LIVE_PROOF_NOTE use scripts/live_proof.sh with LIVE_PROOF_AUTHORIZED=yes plus spend authorization; not part of offline proof"
