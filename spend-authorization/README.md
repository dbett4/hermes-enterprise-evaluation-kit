# Live-run spend controls

The live runner will not start unless both of these owner-controlled limits are present:

1. An **authorization file in this directory** showing the run was scoped before Hermes
   starts.
2. A matching **Nous Portal per-member spend cap**. This is the only runtime monetary
   ceiling; the local script does not meter tokens or stop inference at a dollar amount.

## Who may create `*.authorization` files

| Actor | Permitted? |
|-------|------------|
| **Owner (human)** | **Yes** — only permitted creator today |
| Automation agents | **No** — must not create or transcribe chat authorizations into files |
| `hermes` system user | **No** — may *consume* an existing file at run time only |

An agent-created file would defeat the separation. A chat message copied into a file is
not a second owner control. Today the owner must create the file directly; a future
broker could instead derive it from a signed owner identity.

**Do not commit** real `*.authorization` files. Only `*.example` belongs in Git.

## What the script checks

Hard stop (exit 3) before Hermes starts unless:

1. `SPEND_AUTHORIZATION_FILE` points at a file under `spend-authorization/` containing `GATE_ID`, `AUTHORIZED_CAP_USD`, `AUTHORIZED_BY`, `AUTHORIZED_AT` as `KEY=value` lines (parsed, **never sourced** — no shell execution from the file).
2. `SPEND_CAP_USD` **exactly equals** `AUTHORIZED_CAP_USD` in that file.

The file cap is **inert for billing** — only the **Nous Portal per-member cap** bounds runtime spend.

When both values match, the script prints `SPEND_GATE_PASS` and makes one
`demo_mission_s1.sh --live` call. The run's `cost.status` remains `NOT_RUN` until the B10
Portal readback is implemented.

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
