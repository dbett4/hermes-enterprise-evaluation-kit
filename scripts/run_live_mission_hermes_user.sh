#!/usr/bin/env bash
# S1 live mission — hermes-user wrapper with inspectable spend gate (B10 prep).
# Intended invocation on the Hermes host:
#   sudo -u hermes SPEND_AUTHORIZATION_FILE=spend-authorization/<file> \
#     SPEND_CAP_USD=1.00 HERMES_BIN=/path/to/hermes \
#     ./scripts/run_live_mission_hermes_user.sh
#
# Spend enforcement (two layers — both required for a defensible cap):
#   1. Script gate (this file): refuses to start unless SPEND_CAP_USD matches the
#      AUTHORIZED_CAP_USD parsed from SPEND_AUTHORIZATION_FILE (hard exit 3).
#      Auth file is parsed (never sourced) and must live under spend-authorization/.
#   2. Nous Portal per-member spend cap (operator-set): this script does NOT meter
#      tokens or call Portal APIs; set the Portal cap to match before running.
#      The file cap is inert for billing — Portal is the only runtime monetary ceiling.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

AUTH_FILE="${SPEND_AUTHORIZATION_FILE:-}"
CAP_USD="${SPEND_CAP_USD:-}"
OPS_AUTH_DIR="$(cd "$ROOT/spend-authorization" && pwd)"

if [[ -z "$AUTH_FILE" ]]; then
  echo "MISSION_RUN_BLOCKED: SPEND_AUTHORIZATION_FILE not set (no spend authority on disk)" >&2
  exit 3
fi
if [[ -z "$CAP_USD" ]]; then
  echo "MISSION_RUN_BLOCKED: SPEND_CAP_USD not set" >&2
  exit 3
fi

if [[ "$AUTH_FILE" != /* ]]; then
  AUTH_FILE="$ROOT/$AUTH_FILE"
fi
if [[ ! -f "$AUTH_FILE" ]]; then
  echo "MISSION_RUN_BLOCKED: spend authorization file missing: $AUTH_FILE" >&2
  exit 3
fi
if [[ -L "$AUTH_FILE" ]]; then
  echo "MISSION_RUN_BLOCKED: authorization file must not be a symlink" >&2
  exit 3
fi

AUTH_REAL="$(realpath -e -- "$AUTH_FILE")"
case "$AUTH_REAL" in
  "$OPS_AUTH_DIR"/*.authorization) ;;
  *)
    echo "MISSION_RUN_BLOCKED: authorization must be a real *.authorization file under spend-authorization/" >&2
    exit 3
    ;;
esac

AUTH_MODE="$(stat -c '%a' "$AUTH_REAL")"
case "$AUTH_MODE" in
  400|600) ;;
  *)
    echo "MISSION_RUN_BLOCKED: authorization file permissions must be 400 or 600 (found $AUTH_MODE)" >&2
    exit 3
    ;;
esac

read_auth_value() {
  local key="$1"
  local line value
  line="$(grep -E "^${key}=" "$AUTH_REAL" | tail -n 1 || true)"
  if [[ -z "$line" ]]; then
    echo "MISSION_RUN_BLOCKED: ${key} missing in authorization file" >&2
    exit 3
  fi
  value="${line#*=}"
  if [[ "$value" == \"*\" && "$value" == *\" ]]; then
    value="${value:1:${#value}-2}"
  elif [[ "$value" == \'*\' && "$value" == *\' ]]; then
    value="${value:1:${#value}-2}"
  fi
  if [[ "$value" =~ [\`\$\;\\] ]]; then
    echo "MISSION_RUN_BLOCKED: invalid characters in ${key}" >&2
    exit 3
  fi
  printf '%s' "$value"
}

while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "${line//[[:space:]]/}" ]] && continue
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  if [[ ! "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
    echo "MISSION_RUN_BLOCKED: authorization file has non KEY=value line" >&2
    exit 3
  fi
  key="${line%%=*}"
  case "$key" in
    GATE_ID|AUTHORIZED_CAP_USD|AUTHORIZED_BY|AUTHORIZED_AT|SCOPE) ;;
    *)
      echo "MISSION_RUN_BLOCKED: unexpected key ${key} in authorization file" >&2
      exit 3
      ;;
  esac
done < "$AUTH_REAL"

for dup_key in GATE_ID AUTHORIZED_CAP_USD AUTHORIZED_BY AUTHORIZED_AT SCOPE; do
  dup_count="$(grep -cE "^${dup_key}=" "$AUTH_REAL" || true)"
  if [[ "$dup_count" -gt 1 ]]; then
    echo "MISSION_RUN_BLOCKED: duplicate key ${dup_key} in authorization file" >&2
    exit 3
  fi
done

GATE_ID="$(read_auth_value GATE_ID)"
AUTHORIZED_CAP_USD="$(read_auth_value AUTHORIZED_CAP_USD)"
AUTHORIZED_BY="$(read_auth_value AUTHORIZED_BY)"
AUTHORIZED_AT="$(read_auth_value AUTHORIZED_AT)"
SCOPE="$(read_auth_value SCOPE)"

if [[ "$GATE_ID" != "live-run-spend-cap" ]]; then
  echo "MISSION_RUN_BLOCKED: unexpected GATE_ID=$GATE_ID" >&2
  exit 3
fi
if [[ ! "$AUTHORIZED_CAP_USD" =~ ^([1-9][0-9]*(\.[0-9]{1,2})?|0\.(0[1-9]|[1-9][0-9]?))$ ]]; then
  echo "MISSION_RUN_BLOCKED: AUTHORIZED_CAP_USD must be a positive USD amount with at most two decimals" >&2
  exit 3
fi
if [[ -z "$AUTHORIZED_BY" ]]; then
  echo "MISSION_RUN_BLOCKED: AUTHORIZED_BY must not be empty" >&2
  exit 3
fi
if [[ ! "$AUTHORIZED_AT" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
  echo "MISSION_RUN_BLOCKED: AUTHORIZED_AT must be a UTC ISO-8601 timestamp" >&2
  exit 3
fi
if [[ -z "$SCOPE" ]]; then
  echo "MISSION_RUN_BLOCKED: SCOPE must not be empty" >&2
  exit 3
fi
if [[ "$CAP_USD" != "$AUTHORIZED_CAP_USD" ]]; then
  echo "MISSION_RUN_BLOCKED: SPEND_CAP_USD=$CAP_USD does not match AUTHORIZED_CAP_USD=$AUTHORIZED_CAP_USD" >&2
  exit 3
fi

# Fail closed: spend path must use the caller-validated binary, never PATH rediscovery.
HERMES_BIN="${HERMES_BIN:-}"
if [[ -z "$HERMES_BIN" ]]; then
  echo "MISSION_RUN_BLOCKED: HERMES_BIN is required (refusing silent PATH fallback)" >&2
  exit 3
fi
if [[ ! -x "$HERMES_BIN" ]]; then
  echo "MISSION_RUN_BLOCKED: HERMES_BIN is not an executable file: $HERMES_BIN" >&2
  exit 3
fi
export HERMES_BIN

echo "SPEND_GATE_PASS gate=$GATE_ID cap_usd=$CAP_USD authorized_by=$AUTHORIZED_BY at=$AUTHORIZED_AT scope=$SCOPE"
echo "SPEND_GATE_NOTE: Portal per-member cap must match; script gate is preflight only (no token metering)."

exec "$ROOT/scripts/demo_mission_s1.sh" --live
