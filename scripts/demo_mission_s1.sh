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
  exec python3 scripts/run_mission_s1.py "$@"
fi

echo "=== Enterprise Agent Deployment Field Kit — S1 vendor exception ==="
echo "Org pack: packs/organizations/nimbus-synthetic"
echo ""

exec python3 scripts/run_mission_s1.py "${MODE[@]}" "$@"
