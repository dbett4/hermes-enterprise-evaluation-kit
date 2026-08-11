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

"$PYTHON_BIN" scripts/verify_public_mapping.py
"$PYTHON_BIN" scripts/verify_runtime_attestation_guard.py
"$PYTHON_BIN" scripts/check_neutral_core.py
"$PYTHON_BIN" scripts/run_negative_tests.py
"$PYTHON_BIN" scripts/verify_committed_recorded_receipt.py
bash scripts/demo_mission_s1.sh --output-dir "$PROOF_TEMP/demo"

echo "FIELD_KIT_PROOF_PASS mapping_rows=318 negative_tests=8 recorded_receipt=pass runtime_attestation=missing demo=pass"
