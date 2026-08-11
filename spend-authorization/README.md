# Spend authorization files (B10 prep)

Live inference requires **two independent owner controls**:

1. **Authorization file on disk** (this directory) — proves the owner scoped the run before Hermes starts.
2. **Nous Portal per-member spend cap** — the only runtime monetary ceiling. This script does **not** meter tokens or stop inference when spend is exhausted.

## Who may create `*.authorization` files

| Actor | Permitted? |
|-------|------------|
| **Owner (human)** | **Yes** — only permitted creator today |
| Automation agents | **No** — must not create or transcribe chat authorizations into files |
| `hermes` system user | **No** — may *consume* an existing file at run time only |

An agent-written file is an authorization **latch**, not a second factor: an ambiguous chat message is not an authorization, and an agent transcribing one into a file would defeat the interlock. The interlock is real only when the owner creates the file (or a future brokered mechanism derives from the owner's signed identity).

**Do not commit** real `*.authorization` files — they are spend authority on disk. Only `*.example` belongs in git.

## Script gate (`run_live_mission_hermes_user.sh`)

Hard stop (exit 3) before Hermes starts unless:

1. `SPEND_AUTHORIZATION_FILE` points at a file under `spend-authorization/` containing `GATE_ID`, `AUTHORIZED_CAP_USD`, `AUTHORIZED_BY`, `AUTHORIZED_AT` as `KEY=value` lines (parsed, **never sourced** — no shell execution from the file).
2. `SPEND_CAP_USD` **exactly equals** `AUTHORIZED_CAP_USD` in that file.

The file cap is **inert for billing** — only the **Nous Portal per-member cap** bounds runtime spend.

On pass: `SPEND_GATE_PASS` then one-shot `demo_mission_s1.sh --live`. Receipt `cost.status` stays `NOT_RUN` until B10 portal readback.

## Owner-only: create authorization file

Run **as the owner** from the repo root (not via an agent). Replace the date suffix if needed.

```bash
cd /path/to/hermes-enterprise-field-kit

AUTH=spend-authorization/live-s1-$(date -u +%Y%m%d).authorization
umask 077
cat > "$AUTH" <<'EOF'
GATE_ID=live-run-spend-cap
AUTHORIZED_CAP_USD=1.00
AUTHORIZED_BY=owner
AUTHORIZED_AT=REPLACE_WITH_UTC_ISO8601
SCOPE="One S1 live mission single one-shot"
EOF
chmod 600 "$AUTH"
ls -l "$AUTH"
```

Set `AUTHORIZED_AT` to the actual UTC timestamp before saving (e.g. `2026-08-10T20:00:00Z`).

Then set the **Nous Portal per-member cap** to the same USD value.

## Owner-only: execute live S1

```bash
sudo -u hermes env \
  SPEND_AUTHORIZATION_FILE=spend-authorization/live-s1-<YYYYMMDD>.authorization \
  SPEND_CAP_USD=1.00 \
  ./scripts/run_live_mission_hermes_user.sh
```
