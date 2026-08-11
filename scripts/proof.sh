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
echo "FIELD_KIT_PROOF_SCOPE public_mapping=1 instrument=1 negative_tests=8 runtime_guard=1 demo=1"

"$PYTHON_BIN" -m ruff format --check scripts/hermes_runtime.py scripts/verify_public_mapping.py tests/
"$PYTHON_BIN" -m ruff check \
  kit/instrument/evaluator.py \
  scripts/hermes_runtime.py \
  scripts/verify_public_mapping.py \
  tests/
"$PYTHON_BIN" -m pytest -q tests/

"$PYTHON_BIN" scripts/verify_public_mapping.py
"$PYTHON_BIN" scripts/verify_runtime_attestation_guard.py
"$PYTHON_BIN" scripts/check_neutral_core.py
"$PYTHON_BIN" scripts/run_negative_tests.py
"$PYTHON_BIN" scripts/verify_committed_recorded_receipt.py
bash scripts/demo_mission_s1.sh --output-dir "$PROOF_TEMP/demo"

echo "FIELD_KIT_PROOF_PASS mapping_rows=318 negative_tests=8 recorded_receipt=pass runtime_attestation=missing demo=pass lint=pass unit_tests=pass"
echo "FIELD_KIT_LIVE_PROOF_NOTE use scripts/live_proof.sh with LIVE_PROOF_AUTHORIZED=yes plus spend authorization; not part of offline proof"
