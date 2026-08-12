#!/usr/bin/env bash
# B07 S1 mission demo — vendor policy exception through org resolver.
# Default: --demo (no Hermes install, no API keys). Pass --live for real Hermes.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -n "${HERMES_HOME:-}" && -x "${HERMES_HOME}/hermes-agent/venv/bin/hermes" ]]; then
  export PATH="${HERMES_HOME}/hermes-agent/venv/bin:${PATH}"
fi

MODE=(--demo)
if [[ "${1:-}" == "--live" ]]; then
  shift
  # When HERMES_BIN is set (live_proof / spend gate), pin that exact binary.
  # Reject CLI --hermes-binary so a duplicate arg cannot override the validated path.
  if [[ -n "${HERMES_BIN:-}" ]]; then
    for arg in "$@"; do
      if [[ "$arg" == "--hermes-binary" || "$arg" == --hermes-binary=* ]]; then
        echo "MISSION_RUN_BLOCKED: refusing --hermes-binary while HERMES_BIN is set" >&2
        exit 3
      fi
    done
    exec python3 scripts/run_mission_s1.py --hermes-binary "$HERMES_BIN" "$@"
  fi
  exec python3 scripts/run_mission_s1.py "$@"
fi

echo "=== Hermes Enterprise Evaluation Kit — S1 vendor exception ==="
echo "Org pack: packs/organizations/nimbus-synthetic"
echo ""

exec python3 scripts/run_mission_s1.py "${MODE[@]}" "$@"
