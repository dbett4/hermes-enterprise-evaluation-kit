#!/usr/bin/env bash
# Guarded live Hermes mission proof. Requires explicit owner authorization and budget.
# This script calls a real model and spends money when all gates pass.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${LIVE_PROOF_AUTHORIZED:-}" != "yes" ]]; then
  echo "LIVE_PROOF_BLOCKED: set LIVE_PROOF_AUTHORIZED=yes to acknowledge spend risk" >&2
  exit 3
fi

AUTH_FILE="${SPEND_AUTHORIZATION_FILE:-}"
CAP_USD="${SPEND_CAP_USD:-}"
HERMES_BIN="${HERMES_BIN:-}"

if [[ -z "$AUTH_FILE" || -z "$CAP_USD" || -z "$HERMES_BIN" ]]; then
  echo "LIVE_PROOF_BLOCKED: SPEND_AUTHORIZATION_FILE, SPEND_CAP_USD, and HERMES_BIN are required" >&2
  exit 3
fi

if [[ ! -x "$HERMES_BIN" ]]; then
  echo "LIVE_PROOF_BLOCKED: HERMES_BIN is not an executable file: $HERMES_BIN" >&2
  exit 3
fi

echo "LIVE_PROOF_ARMED spend_cap_usd=$CAP_USD hermes_bin=$HERMES_BIN"
echo "LIVE_PROOF_NOTE: this path invokes the real Hermes mission runner and may incur provider cost."

export HERMES_BIN
exec "$ROOT/scripts/run_live_mission_hermes_user.sh"
